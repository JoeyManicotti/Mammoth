#!/bin/bash

# Start Mammoth in production mode with Docker

echo "🦣 Starting Mammoth in production mode..."
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker found"
echo "✅ Docker Compose found"
echo ""

# Build and start the production container
echo "🔨 Building and starting production container..."
$COMPOSE_CMD up mammoth-prod --build

# Cleanup on exit
trap "$COMPOSE_CMD down" EXIT
