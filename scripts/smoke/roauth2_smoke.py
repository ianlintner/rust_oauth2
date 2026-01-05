#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class ClientCredentials:
    client_id: str
    client_secret: str


def _die(msg: str, *, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _check_no_redirect(resp: requests.Response, *, where: str) -> None:
    # requests follows redirects by default; if we got here we can't see a 302.
    # Instead, detect oauth2-proxy sign-in by final URL/path.
    final_url = str(resp.url)
    if "/_oauth2/" in final_url:
        _die(
            f"Unexpected auth-proxy redirect while fetching {where}:\n"
            f"  final_url={final_url}\n"
            "This host is still protected by the gateway oauth2-proxy filter."
        )


def fetch_discovery(base_url: str, *, verify_tls: bool, timeout_s: float) -> dict[str, Any]:
    url = f"{base_url}/.well-known/openid-configuration"
    resp = requests.get(url, timeout=timeout_s, verify=verify_tls)
    _check_no_redirect(resp, where=url)
    if resp.status_code != 200:
        _die(f"Discovery failed: status={resp.status_code} body={resp.text[:500]}")
    try:
        return resp.json()
    except Exception as e:  # noqa: BLE001
        _die(f"Discovery returned non-JSON: {e}: {resp.text[:500]}")


def register_client(
    base_url: str,
    *,
    verify_tls: bool,
    timeout_s: float,
    redirect_uris: list[str],
) -> ClientCredentials:
    url = f"{base_url}/clients/register"
    payload = {
        "client_name": "smoke-test",
        "redirect_uris": redirect_uris,
        "token_endpoint_auth_method": "client_secret_post",
        "grant_types": ["client_credentials"],
        "response_types": [],
        "scope": "read",
    }
    resp = requests.post(url, json=payload, timeout=timeout_s, verify=verify_tls)
    _check_no_redirect(resp, where=url)
    if resp.status_code not in (200, 201):
        _die(f"Client registration failed: status={resp.status_code} body={resp.text[:500]}")
    data = resp.json()
    cid = data.get("client_id")
    csec = data.get("client_secret")
    if not cid or not csec:
        _die(f"Client registration response missing credentials: {json.dumps(data)[:500]}")
    return ClientCredentials(client_id=str(cid), client_secret=str(csec))


def token_request(
    base_url: str,
    creds: ClientCredentials,
    *,
    verify_tls: bool,
    timeout_s: float,
    scope: str,
) -> dict[str, Any]:
    url = f"{base_url}/oauth/token"
    form = {
        "grant_type": "client_credentials",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scope": scope,
    }
    resp = requests.post(
        url,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=timeout_s,
        verify=verify_tls,
    )
    _check_no_redirect(resp, where=url)
    if resp.status_code != 200:
        _die(f"Token request failed: status={resp.status_code} body={resp.text[:500]}")
    return resp.json()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Smoke-test the OAuth2 server via a base URL. "
            "This is designed to catch gateway auth-proxy redirects and to exercise the /oauth/token loop."
        )
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="e.g. https://roauth2.cat-herding.net or http://127.0.0.1:62061",
    )
    parser.add_argument(
        "--no-verify-tls",
        action="store_true",
        help="Disable TLS verification (useful for local port-forwards with self-signed certs).",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds.")
    parser.add_argument("--count", type=int, default=50, help="How many token requests to run.")
    parser.add_argument("--scope", default="read", help="Scope to request.")
    parser.add_argument(
        "--redirect-uri",
        action="append",
        default=["https://example.com/callback"],
        help="Redirect URI(s) to include in dynamic client registration (repeatable).",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    verify_tls = not args.no_verify_tls

    discovery = fetch_discovery(base_url, verify_tls=verify_tls, timeout_s=args.timeout)
    issuer = discovery.get("issuer")
    print(f"discovery ok: issuer={issuer}")

    creds = register_client(
        base_url,
        verify_tls=verify_tls,
        timeout_s=args.timeout,
        redirect_uris=list(args.redirect_uri),
    )
    print("client registered")

    started = time.time()
    for i in range(1, args.count + 1):
        _ = token_request(
            base_url,
            creds,
            verify_tls=verify_tls,
            timeout_s=args.timeout,
            scope=args.scope,
        )
        if i % 10 == 0 or i == args.count:
            print(f"ok {i}/{args.count}")

    elapsed = time.time() - started
    print(f"all {args.count} token requests succeeded in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
