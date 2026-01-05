# Smoke scripts

These scripts are small, manual smoke tests intended for quick validation against:

- a port-forwarded service (recommended for clusters behind an auth proxy), or
- a public hostname (when the hostname is not protected by oauth2-proxy).

## Virtualenv

We use a Python virtual environment for repeatability.

- Create a venv at repo root (recommended): `.venv/`
- Install deps from `scripts/smoke/requirements.txt`

## roauth2_smoke.py

`roauth2_smoke.py` does three things:

1. Fetches `/.well-known/openid-configuration` and fails fast if the request ends up under `/_oauth2/`.
2. Registers a new dynamic client via `/clients/register`.
3. Runs a loop of `client_credentials` requests to `/oauth/token`.

If you see an error mentioning an auth-proxy redirect, the gateway is still protecting that hostname.
