# Testing

This repository includes multiple layers of tests.

## Unit tests

Run all unit tests:

```bash
cargo test
```

## Integration tests (PostgreSQL)

Integration tests expect a PostgreSQL database. In CI, Postgres is provided via a GitHub Actions service container.

Locally, you can run Postgres via Docker and set:

- `OAUTH2_DATABASE_URL=postgresql://...`

Then run:

```bash
cargo test --test integration
```

## BDD tests

BDD tests are implemented with `cucumber`.

Run:

```bash
cargo test --test bdd
```

## Testcontainers-based tests

Some tests use Testcontainers and require Docker.

Enable those tests by setting:

- `RUN_TESTCONTAINERS=1`

Then run the relevant test targets (for example, Mongo storage tests):

```bash
RUN_TESTCONTAINERS=1 cargo test --test mongo_storage --features mongo
```

## E2E (KIND)

A local + CI-compatible E2E runner is available:

- `scripts/e2e_kind.sh`

Prerequisites:

- Docker
- kind
- kubectl
- kustomize
- jq

The script:

1. Creates a KIND cluster
2. Builds and loads the OAuth2 server image
3. Deploys `k8s/overlays/e2e-kind`
4. Waits for Postgres + Flyway migrations
5. Runs a small HTTP smoke test (register client → token → introspect)

Tip: pass `--keep-cluster` to inspect a failed cluster.
