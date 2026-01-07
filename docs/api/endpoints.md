# API Endpoints

Complete reference for all OAuth2 Server REST API endpoints.

## Base URL

```
http://localhost:8080
```

For production, use your deployed server URL with HTTPS:

```
https://oauth.your-domain.com
```

## Endpoint Categories

```mermaid
graph LR
    A[API Endpoints] --> B[OAuth2]
    A --> C[Client Management]
    A --> D[Token Management]
    A --> E[Admin]
    A --> F[Observability]
    A --> G[Discovery]
  A --> H[Eventing]

    style A fill:#ff9800,color:#fff
    style B fill:#4caf50,color:#fff
    style C fill:#2196f3,color:#fff
    style D fill:#9c27b0,color:#fff
    style H fill:#607d8b,color:#fff
```

## OAuth2 Endpoints

### Authorization Endpoint

Initiate the authorization code flow.

**Endpoint:** `GET /oauth/authorize`

**Parameters:**

| Parameter               | Type   | Required    | Description               |
| ----------------------- | ------ | ----------- | ------------------------- |
| `response_type`         | string | Yes         | Must be `code`            |
| `client_id`             | string | Yes         | Client identifier         |
| `redirect_uri`          | string | Yes         | Callback URL              |
| `scope`                 | string | No          | Space-separated scopes    |
| `state`                 | string | Recommended | CSRF protection token     |
| `code_challenge`        | string | Yes         | PKCE challenge (required) |
| `code_challenge_method` | string | Yes         | Must be `S256`            |

**Example:**

```http
GET /oauth/authorize?response_type=code&client_id=abc123&redirect_uri=http://localhost:3000/callback&scope=read%20write&state=xyz789 HTTP/1.1
```

**Response:**

```http
HTTP/1.1 302 Found
Location: http://localhost:3000/callback?code=AUTH_CODE&state=xyz789
```

### Token Endpoint

Exchange an authorization code or client credentials for an access token.

**Endpoint:** `POST /oauth/token`

**Content-Type:** `application/x-www-form-urlencoded`

#### Authorization Code Grant

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
code_verifier=CODE_VERIFIER&
redirect_uri=http://localhost:3000/callback&
client_id=abc123&
client_secret=secret123
```

#### Client Credentials Grant

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=abc123&
client_secret=secret123&
scope=read
```

#### Refresh Token Grant

!!! warning "Disabled by default"
The `refresh_token` grant is intentionally disabled by default (OAuth 2.0 Security BCP). Requests will be rejected with `unsupported_grant_type`.

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=REFRESH_TOKEN&
client_id=abc123&
client_secret=secret123
```

#### Password Grant

!!! warning "Disabled by default"
The Resource Owner Password Credentials (ROPC) grant (`password`) is intentionally disabled by default. Requests will be rejected with `unsupported_grant_type`.

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=password&
username=user@example.com&
password=password123&
client_id=abc123&
client_secret=secret123
```

**Success Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

**Error Response:**

```json
{
  "error": "invalid_grant",
  "error_description": "The authorization code is invalid"
}
```

### Token Introspection

Validate and get metadata about an access token.

**Endpoint:** `POST /oauth/introspect`

**Parameters:**

| Parameter       | Type   | Required | Description         |
| --------------- | ------ | -------- | ------------------- |
| `token`         | string | Yes      | Token to introspect |
| `client_id`     | string | No       | Client identifier   |
| `client_secret` | string | No       | Client secret       |

**Example:**

```bash
curl -X POST http://localhost:8080/oauth/introspect \
  -d "token=ACCESS_TOKEN" \
  -d "client_id=abc123" \
  -d "client_secret=secret123"
```

**Response (Active Token):**

```json
{
  "active": true,
  "scope": "read write",
  "client_id": "abc123",
  "username": "user@example.com",
  "exp": 1704067200,
  "iat": 1704063600,
  "sub": "user-id-123"
}
```

**Response (Inactive Token):**

```json
{
  "active": false
}
```

### Token Revocation

Revoke an access or refresh token.

**Endpoint:** `POST /oauth/revoke`

**Parameters:**

| Parameter         | Type   | Required | Description                       |
| ----------------- | ------ | -------- | --------------------------------- |
| `token`           | string | Yes      | Token to revoke                   |
| `token_type_hint` | string | No       | `access_token` or `refresh_token` |
| `client_id`       | string | Yes      | Client identifier                 |
| `client_secret`   | string | Yes      | Client secret                     |

**Example:**

```bash
curl -X POST http://localhost:8080/oauth/revoke \
  -d "token=ACCESS_TOKEN" \
  -d "client_id=abc123" \
  -d "client_secret=secret123"
```

**Response:**

```http
HTTP/1.1 200 OK
```

## Client Management

### Register Client

Register a new OAuth2 client.

**Endpoint:** `POST /clients/register`

**Request Body:**

```json
{
  "client_name": "My Application",
  "redirect_uris": [
    "http://localhost:3000/callback",
    "http://localhost:3000/silent-renew"
  ],
  "grant_types": ["authorization_code", "client_credentials"],
  "scope": "read write profile"
}
```

**Response:**

```json
{
  "client_id": "abc123def456",
  "client_secret": "secret_xyz789",
  "client_name": "My Application",
  "redirect_uris": [
    "http://localhost:3000/callback",
    "http://localhost:3000/silent-renew"
  ],
  "grant_types": ["authorization_code", "client_credentials"],
  "scope": "read write profile",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Discovery Endpoint

### OpenID Configuration

Get OAuth2 server metadata.

**Endpoint:** `GET /.well-known/openid-configuration`

**Response:**

```json
{
  "issuer": "http://localhost:8080",
  "authorization_endpoint": "http://localhost:8080/oauth/authorize",
  "token_endpoint": "http://localhost:8080/oauth/token",
  "introspection_endpoint": "http://localhost:8080/oauth/introspect",
  "revocation_endpoint": "http://localhost:8080/oauth/revoke",
  "jwks_uri": "http://localhost:8080/.well-known/jwks.json",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "client_credentials"],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["HS256"],
  "scopes_supported": ["read", "write", "profile", "email"],
  "token_endpoint_auth_methods_supported": [
    "client_secret_post",
    "client_secret_basic"
  ],
  "code_challenge_methods_supported": ["S256"]
}
```

## Admin Endpoints

### Admin Dashboard

Web-based administration interface.

**Endpoint:** `GET /admin`

**Response:** HTML dashboard page

### Health Check

Check if the server is healthy.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Readiness Check

Check if the server is ready to accept requests.

**Endpoint:** `GET /ready`

**Response:**

```json
{
  "ready": true,
  "database": "ready",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Metrics

Prometheus metrics endpoint.

**Endpoint:** `GET /metrics`

**Response:** Prometheus text format metrics

## Eventing Endpoints

These endpoints are only useful when eventing is enabled (`OAUTH2_EVENTS_ENABLED=true`).

### Event System Health

Check event backend/plugin health.

**Endpoint:** `GET /events/health`

**Response (disabled):**

```json
{
  "enabled": false,
  "plugins": []
}
```

**Response (enabled):**

```json
{
  "enabled": true,
  "plugins": [
    {
      "name": "console",
      "healthy": true
    }
  ]
}
```

### Ingest External Event

Submit an externally-produced event envelope to the server.

**Endpoint:** `POST /events/ingest`

**Headers:**

- `Content-Type: application/json`
- `Idempotency-Key: <string>` (recommended)

**Body:** `EventEnvelope` JSON (see `docs/eventing.md` for structure)

**Response (accepted):**

```json
{
  "status": "accepted",
  "idempotency_key": "your-key",
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (duplicate):**

```json
{
  "status": "duplicate",
  "idempotency_key": "your-key",
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (eventing disabled):**

```json
{
  "error": "eventing_disabled"
}
```

## Social Login Endpoints

### Google Login

Initiate Google OAuth2 login.

**Endpoint:** `GET /auth/login/google`

### Microsoft Login

Initiate Microsoft/Azure AD login.

**Endpoint:** `GET /auth/login/microsoft`

### GitHub Login

Initiate GitHub OAuth login.

**Endpoint:** `GET /auth/login/github`

### OAuth Callback

Handle OAuth provider callbacks.

**Endpoint:** `GET /auth/callback/{provider}`

**Parameters:**

| Parameter  | Type   | Description                                     |
| ---------- | ------ | ----------------------------------------------- |
| `provider` | string | Provider name (google, microsoft, github, etc.) |

### Logout

End user session.

**Endpoint:** `POST /auth/logout`

**Response:**

```http
HTTP/1.1 302 Found
Location: /auth/login
```

## Swagger UI

Interactive API documentation.

**Endpoint:** `GET /swagger-ui`

**Response:** HTML Swagger UI page

## Rate Limiting

All endpoints are subject to rate limiting:

- **Authorization endpoint**: 10 requests per minute per IP
- **Token endpoint**: 20 requests per minute per client
- **Introspection**: 100 requests per minute per client
- **Other endpoints**: 100 requests per minute per IP

**Rate Limit Response:**

```json
{
  "error": "rate_limit_exceeded",
  "error_description": "Too many requests. Please try again later."
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "error_code",
  "error_description": "Human-readable error description"
}
```

### Common Error Codes

| Code                      | HTTP Status | Description                              |
| ------------------------- | ----------- | ---------------------------------------- |
| `invalid_request`         | 400         | Malformed or missing parameters          |
| `invalid_client`          | 401         | Invalid client credentials               |
| `invalid_grant`           | 400         | Invalid authorization code or token      |
| `unauthorized_client`     | 400         | Client not authorized for this operation |
| `unsupported_grant_type`  | 400         | Grant type not supported                 |
| `invalid_scope`           | 400         | Requested scope is invalid               |
| `server_error`            | 500         | Internal server error                    |
| `temporarily_unavailable` | 503         | Server temporarily unavailable           |

## Authentication

Most endpoints require client authentication via:

### 1. Client Credentials in Body

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

client_id=abc123&client_secret=secret123&...
```

### 2. Basic Authentication

```http
POST /oauth/token
Authorization: Basic YWJjMTIzOnNlY3JldDEyMw==
Content-Type: application/x-www-form-urlencoded

grant_type=...
```

### 3. Bearer Token

For protected resources:

```http
GET /api/resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Next Steps

- [Authentication Details](authentication.md) - Token usage and scopes
- [Error Handling](errors.md) - Comprehensive error reference
- [OAuth2 Flows](../flows/authorization-code.md) - Flow documentation
- [API Examples](../getting-started/quickstart.md) - Usage examples
