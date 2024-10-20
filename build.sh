#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname $0)" && pwd)"

cd "$SCRIPT_DIR"

docker build \
    -f Dockerfile.backend \
    -t espanol_backend:latest \
    .


docker build \
    -f Dockerfile.frontend \
    -t espanol_frontend:latest \
    .
