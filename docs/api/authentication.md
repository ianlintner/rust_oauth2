# Authentication

This page explains how to authenticate to APIs protected by this OAuth2 server.

## Access tokens

The server issues **Bearer** access tokens (JWT by default).

Use the token in the `Authorization` header:

```http
GET /some-protected-resource HTTP/1.1
Host: example
Authorization: Bearer <ACCESS_TOKEN>
```

## Token introspection (RFC 7662)

If your resource server prefers introspection instead of validating JWTs locally, call:

- **Endpoint:** `POST /oauth/introspect`
- **Content-Type:** `application/x-www-form-urlencoded`

Example:

```bash
curl -X POST http://localhost:8080/oauth/introspect \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=ACCESS_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

A successful response includes:

- `active: true|false`
- `scope` (space-delimited)
- `client_id`
- `exp`, `iat`, `sub` (when available)

## Scopes

Scopes are granted at token issuance time and returned in the token response.

- Request a scope during token issuance (e.g. `scope=read write`).
- The server returns the granted scope in the token response.
- Resource servers should enforce scope checks for protected endpoints.

## Revocation (RFC 7009)

To revoke tokens:

- **Endpoint:** `POST /oauth/revoke`

See the full endpoint reference in [API Endpoints](endpoints.md).
