# Rust OAuth2 Server

Welcome to the documentation for the Rust OAuth2 Server - a complete, production-ready OAuth2 authorization server built with Rust and Actix-web.

## Features

- ✅ Complete OAuth2 implementation with all standard flows
- 🎭 Actor model for concurrent request handling
- 🔒 Type-safe Rust implementation
- 📊 Prometheus metrics and OpenTelemetry tracing
- 📚 OpenAPI documentation with Swagger UI
- 🎨 Admin control panel
- 🗄️ Flyway database migrations
- 🐳 Docker and Kubernetes ready

## Architecture Overview

```mermaid
graph TB
    Client[OAuth2 Client] -->|HTTP Request| Gateway[Actix Web Server]
    Gateway --> Middleware[Middleware Layer]
    Middleware --> Metrics[Metrics Middleware]
    Middleware --> Auth[Auth Middleware]
    Middleware --> Tracing[Tracing Middleware]
    
    Metrics --> Prometheus[Prometheus Exporter]
    Tracing --> OTLP[OpenTelemetry Collector]
    
    Gateway --> Handlers[HTTP Handlers]
    Handlers --> TokenHandler[Token Handler]
    Handlers --> AuthHandler[Auth Handler]
    Handlers --> ClientHandler[Client Handler]
    
    TokenHandler --> TokenActor[Token Actor]
    AuthHandler --> AuthActor[Auth Actor]
    ClientHandler --> ClientActor[Client Actor]
    
    TokenActor --> DB[(Database)]
    AuthActor --> DB
    ClientActor --> DB
    
    style Client fill:#e1f5ff
    style Gateway fill:#fff3e0
    style DB fill:#f3e5f5
    style Prometheus fill:#e8f5e9
    style OTLP fill:#fff9c4
```

## OAuth2 Flows

The server supports all standard OAuth2 flows:

### Authorization Code Flow with PKCE

```mermaid
sequenceDiagram
    participant Client
    participant Browser
    participant AuthServer as OAuth2 Server
    participant ResourceOwner as User
    
    Client->>Browser: Redirect to /oauth/authorize
    Browser->>AuthServer: GET /oauth/authorize?<params>
    AuthServer->>ResourceOwner: Show consent page
    ResourceOwner->>AuthServer: Approve
    AuthServer->>Browser: Redirect with code
    Browser->>Client: Return with code
    Client->>AuthServer: POST /oauth/token (exchange code)
    AuthServer->>Client: Return access_token
```

### Client Credentials Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthServer as OAuth2 Server
    
    Client->>AuthServer: POST /oauth/token<br/>(client_credentials)
    AuthServer->>AuthServer: Validate client
    AuthServer->>Client: Return access_token
```

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [API Reference](api/endpoints.md)
- [Admin Panel](admin/dashboard.md)
- [Metrics & Observability](observability/metrics.md)

## Example Usage

### Register a Client

```bash
curl -X POST http://localhost:8080/clients/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "My App",
    "redirect_uris": ["http://localhost:3000/callback"],
    "grant_types": ["authorization_code"],
    "scope": "read write"
  }'
```

### Get Access Token

```bash
curl -X POST http://localhost:8080/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

## Monitoring

Access the admin dashboard at `http://localhost:8080/admin` to view:

- Active tokens and clients
- Request metrics
- System health
- Recent activity

View Prometheus metrics at `http://localhost:8080/metrics`.

## Support

For issues, questions, or contributions, please visit our [GitHub repository](https://github.com/ianlintner/rust_oauth2).
