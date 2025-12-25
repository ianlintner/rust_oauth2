#!/bin/bash
# Script to run Flyway migrations

set -e

echo "Running Flyway migrations..."

# Pin Flyway Docker image to specific digest for security
# Update this digest when intentionally upgrading Flyway
FLYWAY_IMAGE="flyway/flyway:10-alpine@sha256:8c2e1e9ad14d0d1b24ab3026cc6a64e6dd0c45c8e2e5ee3c4e1f9e8d4f2a5b6c"

# Check if Flyway is available
if ! command -v flyway &> /dev/null; then
    echo "Flyway not found. Using Docker to run migrations..."
    
    # Run Flyway via Docker with pinned image digest
    docker run --rm \
        -v "$(pwd)/migrations/sql:/flyway/sql" \
        -v "$(pwd)/flyway.conf:/flyway/conf/flyway.conf" \
        "${FLYWAY_IMAGE}" \
        migrate
else
    echo "Using local Flyway installation..."
    flyway -configFiles=flyway.conf migrate
fi

echo "Migrations completed successfully!"
