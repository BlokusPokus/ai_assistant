#!/bin/bash

# 🚀 Bloop Personal Assistant - Docker Deployment Script
# This script automates the Docker deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in docker directory
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Please run this script from the docker directory"
    exit 1
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    log_warning "Environment file $ENV_FILE not found"
    log_info "Creating from example..."
    cp env.prod.example "$ENV_FILE"
    log_warning "Please update $ENV_FILE with your actual values before continuing"
    exit 1
fi

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p nginx/html
mkdir -p nginx/logs
mkdir -p nginx/ssl/prod
mkdir -p backups
mkdir -p logs

# Set proper permissions
log_info "Setting permissions..."
chmod 755 nginx/html
chmod 755 nginx/logs
chmod 755 logs
chmod 777 logs  # For application logs

# Copy environment file for docker-compose
log_info "Setting up environment files..."
cp "$ENV_FILE" .env

# Build and start services
log_info "Building Docker images..."
docker-compose -f "$COMPOSE_FILE" build

log_info "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 30

# Run database migrations
log_info "Running database migrations..."
docker exec personal_assistant_api_prod python -m alembic upgrade head

# Check service status
log_info "Checking service status..."
docker-compose -f "$COMPOSE_FILE" ps

# Health checks
log_info "Running health checks..."
echo "Frontend: $(curl -k -s -o /dev/null -w "%{http_code}" https://ianleblanc.ca/ || echo "FAILED")"
echo "API Health: $(curl -k -s -o /dev/null -w "%{http_code}" https://ianleblanc.ca/api/health || echo "FAILED")"

log_success "Deployment completed!"
log_info "Access your application at: https://ianleblanc.ca"
