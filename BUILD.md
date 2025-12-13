# Building Docker Images

This project uses a **multi-stage Dockerfile** at the root that can build all services.

## Building Individual Services

### Build User Service
```bash
docker build --target user-service -t neuralbets-user-service:latest .
```

### Build Bet Service
```bash
docker build --target bet-service -t neuralbets-bet-service:latest .
```

## Building All Services

You can build both services in sequence:

```bash
# Build user-service
docker build --target user-service -t neuralbets-user-service:latest .

# Build bet-service
docker build --target bet-service -t neuralbets-bet-service:latest .
```

## Using with Docker Compose

The `docker-compose.yml` still uses the individual Dockerfiles in each service directory. To use the root Dockerfile instead, you can modify docker-compose.yml:

```yaml
services:
  user-service:
    build:
      context: .
      dockerfile: Dockerfile
      target: user-service
    # ... rest of config
```

## Using with Cloud Build

The `cloudbuild.yaml` is configured to use the root Dockerfile with targets:

```yaml
- name: 'gcr.io/cloud-builders/docker'
  args:
    - 'build'
    - '--target'
    - 'user-service'
    - '-f'
    - 'Dockerfile'
    - '.'
```

## Benefits of Multi-Stage Build

1. **Shared Base Layer**: Common dependencies (shared_utils, Python base) are built once
2. **Faster Builds**: Docker caches the base stage, speeding up subsequent builds
3. **Consistency**: All services use the same base configuration
4. **Single Source of Truth**: One Dockerfile to maintain instead of multiple

## Build Cache Optimization

The Dockerfile is structured to maximize cache hits:

1. Base stage (shared utilities) - changes rarely
2. Requirements installation - changes when dependencies update
3. Application code - changes most frequently

This means code changes won't invalidate the base and dependency layers.


