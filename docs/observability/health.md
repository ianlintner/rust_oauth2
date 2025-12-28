# Health Checks

The server provides Kubernetes-friendly health endpoints.

## Endpoints

- `GET /health` – liveness-style check (server is running)
- `GET /ready` – readiness-style check (server is ready to accept traffic)

If eventing is enabled, you can also check event backend health:

- `GET /events/health`

## Kubernetes

Use `/health` for `livenessProbe` and `/ready` for `readinessProbe`.

## Troubleshooting

- If `/ready` fails, check database connectivity and migrations.
- If `/events/health` fails, verify event backend configuration and feature flags.
