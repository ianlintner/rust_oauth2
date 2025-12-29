# Kubernetes Deployment

Kubernetes manifests live under `k8s/` and are managed with Kustomize overlays.

## Quick start

```bash
# Development
kubectl apply -k k8s/overlays/dev

# Staging
kubectl apply -k k8s/overlays/staging

# Production
kubectl apply -k k8s/overlays/production
```

See the repo’s Kubernetes guide:

- [`k8s/README.md`](https://github.com/ianlintner/rust_oauth2_server/blob/main/k8s/README.md)

## E2E on KIND

A local + CI-friendly end-to-end script is provided:

- `scripts/e2e_kind.sh`

It builds/loads the image into KIND, applies the `k8s/overlays/e2e-kind` overlay, waits for migrations + rollout, then runs a small OAuth2 smoke test.

See [Testing](../development/testing.md) for details.

## Local observability with KIND

You can reuse the local observability stack (Prometheus + Grafana + Jaeger) while running the server inside a KIND cluster.

### Option A (simple): Prometheus scrapes via port-forward

1. Bring up the KIND environment (see `scripts/e2e_kind.sh`).
2. In a separate terminal, port-forward the Kubernetes service:

```bash
kubectl -n oauth2-server port-forward svc/oauth2-server 18080:80
```

3. Start the observability stack with the KIND Prometheus config override:

```bash
docker compose -f docker-compose.observability.yml -f docker-compose.observability.kind.yml up -d
```

This uses `observability/prometheus/prometheus.kind.yml`, which scrapes `host.docker.internal:18080`.

> Note: `host.docker.internal` works out of the box on macOS/Windows. On Linux you may need a different host gateway setup.

### Generating demo traffic (for dashboards/SLOs)

To generate synthetic traffic **inside** the cluster (so Prometheus/Grafana have something to show), run:

```bash
./scripts/kind_generate_traffic.sh --duration 10m
```

This creates a short-lived Kubernetes Job that hits `POST /oauth/token` (success + invalid secret) and `GET /health`/`GET /ready`.
