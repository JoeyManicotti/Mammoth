# Docker Setup for Mammoth

This document explains how to run Mammoth using Docker.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)

## Quick Start

### Using Convenience Scripts (Easiest)

```bash
# Development mode (with hot reload)
./start-dev.sh

# Production mode
./start-prod.sh
```

### Development Mode (with hot reload)

```bash
# Build and run the development container
docker compose -f docker-compose.dev.yml up --build

# Or using the main docker-compose file
docker compose up mammoth-dev --build
```

The application will be available at `http://localhost:3000`

### Production Mode

```bash
# Build and run the production container
docker compose up mammoth-prod --build
```

The application will be available at `http://localhost:3001`

## Docker Commands

### Build the Image

```bash
# Development image
docker build --target development -t mammoth:dev .

# Production image
docker build --target production -t mammoth:prod .
```

### Run a Container

```bash
# Development container
docker run -p 3000:3000 -v $(pwd)/src:/app/src mammoth:dev

# Production container
docker run -p 3000:3000 mammoth:prod
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build

# Remove volumes
docker-compose down -v
```

## Multi-Stage Build

The Dockerfile uses a multi-stage build with three stages:

1. **Builder**: Compiles the TypeScript and builds production assets
2. **Production**: Serves the built static files using `serve`
3. **Development**: Runs the Vite dev server with hot module replacement

## Volume Mounts (Development)

In development mode, the following directories are mounted for hot reload:
- `./src` - Source code
- `./public` - Public assets
- `./index.html` - HTML template
- Configuration files (vite.config.ts, tsconfig.json, etc.)

Node modules are stored in a named volume to avoid conflicts between host and container.

## Environment Variables

- `NODE_ENV`: Set to `development` or `production`
- Port: Default is 3000 (configurable in docker-compose.yml)

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, modify the port mapping in docker-compose.yml:

```yaml
ports:
  - "3001:3000"  # Host:Container
```

### Permission Issues

If you encounter permission issues with volumes, ensure your user has proper permissions:

```bash
sudo chown -R $USER:$USER .
```

### Clear Everything and Start Fresh

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Image Size

- Development image: ~400-500 MB (includes all dev dependencies)
- Production image: ~150-200 MB (optimized, only runtime dependencies)

## Health Check

The production container includes a health check that runs every 30 seconds:

```bash
# Check container health status
docker ps
docker inspect mammoth-prod | grep Health
```

## Best Practices

1. Use development mode for local development with hot reload
2. Use production mode for testing the optimized build
3. Always rebuild after dependency changes: `docker-compose up --build`
4. Clean up unused images regularly: `docker system prune`
5. Use `.dockerignore` to exclude unnecessary files from the build context
