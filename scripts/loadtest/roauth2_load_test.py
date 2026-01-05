#!/usr/bin/env python3
"""Load test for roauth2.cat-herding.net that can revoke tokens it creates.

Design goals:
- venv-friendly (requests)
- low ceremony: can auto-register a client and cache credentials
- safe-ish cleanup: revoke all access tokens it created

This is not a full-featured load testing framework; it's a practical smoke/load harness.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class ClientCredentials:
    client_id: str
    client_secret: str


@dataclass(frozen=True)
class TokenResult:
    ok: bool
    status: int
    latency_s: float
    error: str | None
    access_token: str | None


def _die(msg: str, *, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _check_no_redirect(resp: requests.Response, *, where: str) -> None:
    # requests follows redirects by default; check where we ended up.
    final = str(resp.url)
    if "/_oauth2/" in final:
        _die(
            f"Unexpected auth redirect while calling {where}: final_url={final} status={resp.status_code}"
        )


def _http_session(*, verify_tls: bool, timeout_s: float) -> requests.Session:
    s = requests.Session()
    s.verify = verify_tls
    # Keep timeouts explicit per-request.
    s.headers.update({"User-Agent": "roauth2-loadtest/1.0"})
    return s


def discover(base_url: str, *, session: requests.Session, timeout_s: float) -> dict[str, Any]:
    url = f"{base_url}/.well-known/openid-configuration"
    resp = session.get(url, timeout=timeout_s)
    _check_no_redirect(resp, where=url)
    if resp.status_code != 200:
        _die(f"Discovery failed: status={resp.status_code} body={resp.text[:500]}")
    return resp.json()


def register_client(
    base_url: str,
    *,
    session: requests.Session,
    timeout_s: float,
    client_name: str,
    redirect_uris: list[str],
    scope: str,
) -> ClientCredentials:
    url = f"{base_url}/clients/register"
    payload = {
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "token_endpoint_auth_method": "client_secret_post",
        "grant_types": ["client_credentials"],
        "response_types": [],
        "scope": scope,
    }
    resp = session.post(url, json=payload, timeout=timeout_s)
    _check_no_redirect(resp, where=url)
    if resp.status_code not in (200, 201):
        _die(f"Client registration failed: status={resp.status_code} body={resp.text[:500]}")

    data = resp.json()
    cid = data.get("client_id")
    csec = data.get("client_secret")
    if not cid or not csec:
        _die(f"Client registration response missing credentials: {json.dumps(data)[:500]}")
    return ClientCredentials(client_id=cid, client_secret=csec)


def load_cached_client(path: str) -> ClientCredentials | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cid = data.get("client_id")
        csec = data.get("client_secret")
        if not cid or not csec:
            return None
        return ClientCredentials(client_id=str(cid), client_secret=str(csec))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def save_cached_client(path: str, creds: ClientCredentials) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"client_id": creds.client_id, "client_secret": creds.client_secret}, f)
        f.write("\n")
    os.replace(tmp, path)


def request_token(
    base_url: str,
    *,
    session: requests.Session,
    timeout_s: float,
    creds: ClientCredentials,
    scope: str,
) -> TokenResult:
    url = f"{base_url}/oauth/token"
    form = {
        "grant_type": "client_credentials",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scope": scope,
    }

    t0 = time.perf_counter()
    try:
        resp = session.post(
            url,
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout_s,
        )
        latency = time.perf_counter() - t0
        _check_no_redirect(resp, where=url)

        if resp.status_code != 200:
            return TokenResult(
                ok=False,
                status=resp.status_code,
                latency_s=latency,
                error=resp.text[:300],
                access_token=None,
            )

        data = resp.json()
        tok = data.get("access_token")
        if not tok:
            return TokenResult(
                ok=False,
                status=200,
                latency_s=latency,
                error=f"missing access_token in response: {json.dumps(data)[:300]}",
                access_token=None,
            )

        return TokenResult(
            ok=True,
            status=200,
            latency_s=latency,
            error=None,
            access_token=str(tok),
        )
    except requests.RequestException as e:
        latency = time.perf_counter() - t0
        return TokenResult(
            ok=False,
            status=0,
            latency_s=latency,
            error=str(e),
            access_token=None,
        )


def revoke_token(
    base_url: str,
    *,
    session: requests.Session,
    timeout_s: float,
    creds: ClientCredentials,
    token: str,
) -> tuple[bool, int, str | None]:
    url = f"{base_url}/oauth/revoke"
    form = {
        "token": token,
        "token_type_hint": "access_token",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
    }

    try:
        resp = session.post(
            url,
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=timeout_s,
        )
        _check_no_redirect(resp, where=url)
        if resp.status_code == 200:
            return True, 200, None
        return False, resp.status_code, resp.text[:300]
    except requests.RequestException as e:
        return False, 0, str(e)


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    if p <= 0:
        return sorted_vals[0]
    if p >= 100:
        return sorted_vals[-1]
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1


def main() -> int:
    ap = argparse.ArgumentParser(description="Load test roauth2 token issuance with cleanup")
    ap.add_argument("--base-url", default="https://roauth2.cat-herding.net")
    ap.add_argument("--verify-tls", action="store_true", default=True)
    ap.add_argument("--no-verify-tls", action="store_false", dest="verify_tls")
    ap.add_argument("--timeout-s", type=float, default=10.0)

    ap.add_argument("--client-id")
    ap.add_argument("--client-secret")
    ap.add_argument(
        "--client-cache-file",
        default="scripts/loadtest/.client.json",
        help="Where to cache dynamically-registered client credentials (repo-relative path is fine)",
    )
    ap.add_argument(
        "--no-client-cache",
        action="store_true",
        help="Do not read/write cached client credentials (forces dynamic registration unless client creds provided)",
    )
    ap.add_argument(
        "--client-name-prefix",
        default="load-test",
        help="Prefix used when dynamically registering a client",
    )

    ap.add_argument("--scope", default="read")
    ap.add_argument("--redirect-uri", action="append", default=["http://localhost/callback"])

    ap.add_argument("--duration-s", type=float, default=30.0)
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument(
        "--rps",
        type=float,
        default=0.0,
        help="Target global requests/sec (best effort). 0 means 'as fast as possible'.",
    )

    ap.add_argument(
        "--revoke",
        action="store_true",
        default=True,
        help="Revoke every access token created during the run (default)",
    )
    ap.add_argument(
        "--no-revoke",
        action="store_false",
        dest="revoke",
        help="Do not revoke tokens created during the run",
    )
    ap.add_argument(
        "--revoke-concurrency",
        type=int,
        default=20,
        help="Concurrency for the revoke phase",
    )

    args = ap.parse_args()

    if args.concurrency <= 0:
        _die("--concurrency must be > 0")
    if args.duration_s <= 0:
        _die("--duration-s must be > 0")
    if args.rps < 0:
        _die("--rps must be >= 0")

    session = _http_session(verify_tls=args.verify_tls, timeout_s=args.timeout_s)

    # Fail fast if ingress auth is misconfigured again.
    _ = discover(args.base_url, session=session, timeout_s=args.timeout_s)

    creds: ClientCredentials | None = None

    if args.client_id and args.client_secret:
        creds = ClientCredentials(args.client_id, args.client_secret)
    elif not args.no_client_cache:
        creds = load_cached_client(args.client_cache_file)

    created_client = False
    if creds is None:
        suffix = f"{int(time.time())}-{random.randint(1000, 9999)}"
        client_name = f"{args.client_name_prefix}-{suffix}"
        creds = register_client(
            args.base_url,
            session=session,
            timeout_s=args.timeout_s,
            client_name=client_name,
            redirect_uris=list(args.redirect_uri),
            scope=args.scope,
        )
        created_client = True
        if not args.no_client_cache:
            save_cached_client(args.client_cache_file, creds)

    if created_client and args.no_client_cache:
        print(
            "NOTE: this run dynamically registered a new client. "
            "The public API does not currently provide a client deletion endpoint; "
            "consider using --client-cache-file to reuse a single client across runs.",
            file=sys.stderr,
        )

    stop_at = time.monotonic() + float(args.duration_s)

    # Best-effort global rate limiting.
    next_allowed = time.monotonic()
    rate_lock = threading.Lock()

    tokens: list[str] = []
    tokens_lock = threading.Lock()

    results: list[TokenResult] = []
    results_lock = threading.Lock()

    def worker() -> None:
        nonlocal next_allowed
        # Each thread uses its own session (requests sessions aren't strictly thread-safe).
        s = _http_session(verify_tls=args.verify_tls, timeout_s=args.timeout_s)
        while time.monotonic() < stop_at:
            if args.rps > 0:
                with rate_lock:
                    now = time.monotonic()
                    if now < next_allowed:
                        sleep_s = next_allowed - now
                    else:
                        sleep_s = 0.0
                    # schedule next slot
                    next_allowed = max(next_allowed, now) + (1.0 / args.rps)
                if sleep_s > 0:
                    time.sleep(sleep_s)

            r = request_token(
                args.base_url,
                session=s,
                timeout_s=args.timeout_s,
                creds=creds,
                scope=args.scope,
            )
            with results_lock:
                results.append(r)
            if r.ok and r.access_token:
                with tokens_lock:
                    tokens.append(r.access_token)

    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(worker) for _ in range(args.concurrency)]
        for f in as_completed(futs):
            # propagate any unexpected exceptions
            f.result()
    t_total = time.perf_counter() - t_start

    # Summary
    ok = [r for r in results if r.ok]
    bad = [r for r in results if not r.ok]
    lat = sorted([r.latency_s for r in results])

    total = len(results)
    ok_n = len(ok)
    bad_n = len(bad)

    achieved_rps = (total / t_total) if t_total > 0 else 0.0

    print("== roauth2 load test results ==")
    print(f"base_url: {args.base_url}")
    print(f"duration_s: {args.duration_s:.2f} (wall {t_total:.2f}s)")
    print(f"concurrency: {args.concurrency}")
    print(f"target_rps: {args.rps if args.rps > 0 else 'unlimited'}")
    print(f"requests: {total} (ok {ok_n}, err {bad_n})")
    print(f"achieved_rps: {achieved_rps:.2f}")

    if total:
        p50 = _percentile(lat, 50)
        p95 = _percentile(lat, 95)
        p99 = _percentile(lat, 99)
        mean = statistics.fmean(lat)
        print("latency_s:")
        print(f"  mean: {mean:.4f}")
        print(f"  p50:  {p50:.4f}")
        print(f"  p95:  {p95:.4f}")
        print(f"  p99:  {p99:.4f}")

    if bad_n:
        # show a few representative failures
        print("sample_errors:")
        for r in bad[: min(5, bad_n)]:
            print(f"  status={r.status} latency_s={r.latency_s:.4f} err={r.error}")

    # Cleanup phase: revoke tokens
    if args.revoke:
        toks = list(tokens)
        print(f"== cleanup: revoking {len(toks)} access tokens ==")
        revoke_ok = 0
        revoke_err = 0

        def revoke_one(tok: str) -> tuple[bool, int, str | None]:
            s = _http_session(verify_tls=args.verify_tls, timeout_s=args.timeout_s)
            return revoke_token(
                args.base_url,
                session=s,
                timeout_s=args.timeout_s,
                creds=creds,
                token=tok,
            )

        with ThreadPoolExecutor(max_workers=args.revoke_concurrency) as ex:
            futs = [ex.submit(revoke_one, t) for t in toks]
            for f in as_completed(futs):
                ok_rev, status, err = f.result()
                if ok_rev:
                    revoke_ok += 1
                else:
                    revoke_err += 1
                    if revoke_err <= 5:
                        print(f"  revoke failed: status={status} err={err}")

        print(f"revoked_ok: {revoke_ok}")
        print(f"revoked_err: {revoke_err}")

    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
