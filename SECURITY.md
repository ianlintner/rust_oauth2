# Security Configuration Guide

This document outlines the required security configurations for deploying the OAuth2 server.

## Required Environment Variables

### JWT Secret (REQUIRED)

The server will **NOT start** without a valid JWT secret configured:

```bash
# Generate a secure random secret (minimum 32 characters)
export OAUTH2_JWT_SECRET=$(openssl rand -hex 32)
```

**Why this is required:**
- JWT tokens are signed with this secret
- Weak or default secrets compromise the entire authentication system
- The server explicitly requires this to be set via environment variable

### Session Key (RECOMMENDED for Production)

For production deployments, set a persistent session key to maintain sessions across server restarts:

```bash
# Generate a 64-byte (128 hex character) session key
export OAUTH2_SESSION_KEY=$(openssl rand -hex 64)
```

**Why this is important:**
- Without this, a random key is generated on each startup
- Users will be logged out when the server restarts
- Sessions won't work properly in multi-instance deployments

### Database Credentials

Update default database credentials before production:

```sql
-- V5__insert_default_data.sql contains INSECURE defaults
-- Generate secure credentials:
openssl rand -hex 32  # For client secrets
```

**Action items:**
1. Remove or regenerate the default client credentials in the migration
2. Generate proper Argon2 password hashes for test users
3. Consider removing V5__insert_default_data.sql entirely in production

## Security Best Practices

### 1. Client Secret Validation

The server uses **constant-time comparison** for client secrets to prevent timing attacks:

```rust
use subtle::ConstantTimeEq;
let secret_match = client.client_secret.as_bytes()
    .ct_eq(msg.client_secret.as_bytes())
    .into();
```

### 2. Token Storage

**DO NOT** store access tokens in localStorage (XSS vulnerability). The application uses:
- httpOnly cookies for session management
- Server-side token storage
- Secure cookie flags in production

### 3. PKCE for Authorization Code Flow

PKCE (RFC 7636) is implemented using S256 challenge method:
- Prevents authorization code interception attacks
- Required for public clients
- Recommended for all clients

### 4. Flyway Docker Image Pinning

The migration script uses a **pinned Docker image digest** to prevent supply chain attacks:

```bash
FLYWAY_IMAGE="flyway/flyway:10-alpine@sha256:..."
```

**Update process:**
1. Review Flyway release notes
2. Test migrations in staging
3. Update the digest in scripts/migrate.sh
4. Document the change in git commit

## Production Checklist

Before deploying to production:

- [ ] Set `OAUTH2_JWT_SECRET` (minimum 32 characters)
- [ ] Set `OAUTH2_SESSION_KEY` (128 hex characters)
- [ ] Remove or secure default credentials in V5__insert_default_data.sql
- [ ] Enable HTTPS (configure reverse proxy)
- [ ] Set up proper database with authentication
- [ ] Configure CORS appropriately for your domains
- [ ] Review and update redirect URIs for OAuth clients
- [ ] Set up rate limiting (see TODO.md)
- [ ] Enable audit logging
- [ ] Configure monitoring and alerting
- [ ] Rotate secrets regularly (implement key rotation)

## Monitoring Security

### Metrics to Monitor

```
oauth2_server_oauth_failed_authentications  # Failed login attempts
oauth2_server_oauth_token_revoked_total     # Revoked tokens
oauth2_server_http_requests_total           # Request patterns
```

### Log Analysis

Watch for:
- Multiple failed authentication attempts from same IP
- Unusual token issuance patterns
- Invalid client credential attempts
- Suspicious redirect URIs

## Incident Response

If credentials are compromised:

1. **Immediately:**
   - Rotate `OAUTH2_JWT_SECRET`
   - Rotate `OAUTH2_SESSION_KEY`
   - Revoke all active tokens
   - Review audit logs

2. **Within 24 hours:**
   - Notify affected users
   - Rotate client secrets
   - Update documentation
   - Implement additional monitoring

3. **Post-incident:**
   - Conduct security review
   - Update security procedures
   - Consider implementing 2FA (see TODO.md)

## References

- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [RFC 7636 - PKCE](https://tools.ietf.org/html/rfc7636)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
