# Error Handling

This server follows standard OAuth2 error response formats where applicable.

## OAuth2 error responses

OAuth2 endpoints typically return a JSON body with:

- `error` (required)
- `error_description` (optional)
- `error_uri` (optional)

Example:

```json
{
  "error": "invalid_grant",
  "error_description": "The authorization code is invalid"
}
```

Common OAuth2 errors include (see RFC 6749):

- `invalid_request`
- `invalid_client`
- `invalid_grant`
- `unauthorized_client`
- `unsupported_grant_type`
- `invalid_scope`

## HTTP status codes

Typical mappings:

- `400 Bad Request` – malformed or invalid parameters
- `401 Unauthorized` – authentication failed (e.g. invalid client credentials)
- `403 Forbidden` – authenticated but not authorized
- `404 Not Found` – unknown route
- `500 Internal Server Error` – unexpected server error

## Tracing and diagnostics

For debugging production issues:

- Enable structured logging (`tracing`)
- Export OpenTelemetry spans (see [Tracing](../observability/tracing.md))
- Use correlation IDs and request IDs from logs
