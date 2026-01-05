# roauth2 load test

This folder contains a small, venv-friendly load test for the public server:

- `https://roauth2.cat-herding.net`

It can optionally create a client via dynamic registration, reuse cached client credentials across runs, and will **revoke** (clean up) tokens it creates.

## Setup (venv)

From repo root:

- Create a venv: `python3 -m venv .venv`
- Install deps: `./.venv/bin/python -m pip install -r scripts/loadtest/requirements.txt`

## Run

### Reuse an existing client (recommended)

If you already have a client:

- `./.venv/bin/python scripts/loadtest/roauth2_load_test.py --base-url https://roauth2.cat-herding.net --client-id ... --client-secret ... --duration-s 30 --concurrency 10 --rps 20`

### Create/cache a client automatically

If you do not pass `--client-id/--client-secret`, the script will:

1. `POST /clients/register`
2. Cache credentials to `scripts/loadtest/.client.json`
3. Use that client for the test

Example:

- `./.venv/bin/python scripts/loadtest/roauth2_load_test.py --base-url https://roauth2.cat-herding.net --duration-s 30 --concurrency 10 --rps 20`

## Cleanup semantics

- The server supports token revocation: `POST /oauth/revoke`
- This script records every `access_token` issued during the run and **revokes them at the end** (default).

Notes:

- Revocation marks tokens as revoked; it does not necessarily delete token records from storage.
- The public API does not currently expose a client-deletion endpoint. To avoid leaving lots of registered clients behind, prefer reusing cached credentials.

## Tips

- If you run a very large test (many thousands of tokens), the revoke phase can take time. You can disable revocation with `--no-revoke`.
- If you suspect ingress auth got re-enabled, the script will fail fast if it sees redirects to `/_oauth2/`.
