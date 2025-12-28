# CI/CD

CI is implemented with GitHub Actions.

## Workflows

- `/.github/workflows/ci.yml`
  - formatting (rustfmt)
  - linting (clippy)
  - tests (all features)
  - security checks (audit/deny)
  - integration tests (PostgreSQL)
  - Mongo feature tests (testcontainers)
  - E2E on KIND

- `/.github/workflows/e2e-kind.yml`
  - manual trigger for KIND E2E runs

## Running CI checks locally

Recommended local pre-push checks:

```bash
cargo fmt -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```
