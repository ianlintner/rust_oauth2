# Logging

The server uses `tracing` for structured logging.

## Log format

Logs can be emitted in structured JSON format (recommended for production).

## Filtering

Use `RUST_LOG` to control verbosity.

Examples:

- Minimal:
  - `RUST_LOG=info`
- More detail for this crate:
  - `RUST_LOG=rust_oauth2_server=debug,info`

## Correlation

Where applicable, logs include correlation IDs and request context. Combine logs with traces for full request-to-database visibility.
