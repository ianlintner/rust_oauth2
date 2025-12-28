# Tracing

The server supports distributed tracing via OpenTelemetry.

## What’s instrumented

- Incoming HTTP requests (middleware)
- Core handler/actor operations
- Eventing publishes (best-effort) carry W3C trace context in the event envelope

## OTLP export

By default, traces can be exported to an OTLP collector.

A common local setup is Jaeger all-in-one:

```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Then visit Jaeger UI at `http://localhost:16686`.

## Context propagation

Incoming requests that include W3C headers:

- `traceparent`
- `tracestate`

will have that context propagated into server spans and (when events are emitted) into `EventEnvelope` fields.

See [Eventing](../eventing.md) for the envelope structure.
