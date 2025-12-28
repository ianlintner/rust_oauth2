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
