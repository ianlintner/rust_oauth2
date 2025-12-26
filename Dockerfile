# Multi-stage build for Rust OAuth2 Server

# Stage 1: Builder
FROM rust:1.75-slim as builder

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Create dummy source to cache dependencies
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy actual source code
COPY src ./src
COPY templates ./templates
COPY static ./static

# Build the application
RUN touch src/main.rs && cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the built binary from builder
COPY --from=builder /app/target/release/rust_oauth2_server /app/oauth2_server

# Copy templates and static files
COPY templates ./templates
COPY static ./static

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Set environment variables
ENV OAUTH2_SERVER_HOST=0.0.0.0
ENV OAUTH2_SERVER_PORT=8080
ENV OAUTH2_DATABASE_URL=sqlite:/app/data/oauth2.db
ENV RUST_LOG=info

# Run the binary
CMD ["/app/oauth2_server"]
