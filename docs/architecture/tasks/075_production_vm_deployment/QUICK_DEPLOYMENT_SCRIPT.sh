#!/bin/bash

# 🚀 Bloop Personal Assistant - Quick Deployment Script
# This script automates the deployment process for future updates

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DROPLET_IP="165.227.38.1"
SSH_KEY="~/.ssh/do_personal_assistant"
DOMAIN="ianleblanc.ca"
PROJECT_DIR="/home/deploy/ai_assistant"

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

# Check if running locally or on server
if [[ "$(hostname)" == *"ubuntu"* ]]; then
    # Running on server
    log_info "Running on production server"
    ON_SERVER=true
else
    # Running locally
    log_info "Running locally, will SSH to server"
    ON_SERVER=false
fi

# Main deployment function
deploy() {
    log_info "Starting Bloop Personal Assistant deployment..."
    
    if [ "$ON_SERVER" = false ]; then
        log_info "Connecting to production server..."
        ssh -i $SSH_KEY deploy@$DROPLET_IP "bash -s" < "$0" --on-server
        return
    fi
    
    # Server-side deployment
    log_info "Executing deployment on server..."
    
    # Step 1: Navigate to project directory
    log_info "Navigating to project directory..."
    cd $PROJECT_DIR
    
    # Step 2: Pull latest code
    log_info "Pulling latest code from Git..."
    git pull origin main
    log_success "Code updated successfully"
    
    # Step 3: Check for environment file updates
    log_info "Checking environment configuration..."
    if [ -f "config/production.env" ]; then
        cp docker/.env.prod docker/.env
        log_success "Environment files updated"
    fi
    
    # Step 4: Navigate to docker directory
    cd docker
    
    # Step 5: Run database migrations
    log_info "Running database migrations..."
    docker exec personal_assistant_api_prod python -m alembic upgrade head
    log_success "Database migrations completed"
    
    # Step 6: Check if frontend needs rebuilding
    log_info "Checking frontend build status..."
    if [ -d "../src/apps/frontend" ]; then
        log_info "Building frontend..."
        cd ../src/apps/frontend
        npx vite build
        cp -r dist/* ../../docker/nginx/html/
        log_success "Frontend built and deployed"
        cd ../../docker
    fi
    
    # Step 7: Rebuild and restart services
    log_info "Rebuilding and restarting services..."
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    log_success "Services restarted"
    
    # Step 8: Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Step 9: Verify deployment
    log_info "Verifying deployment..."
    
    # Check service status
    log_info "Checking service status..."
    docker-compose -f docker-compose.prod.yml ps
    
    # Test frontend
    log_info "Testing frontend..."
    if curl -k -s https://$DOMAIN/ | grep -q "Vite + React + TS"; then
        log_success "Frontend is loading"
    else
        log_warning "Frontend may not be loading correctly"
    fi
    
    # Test API
    log_info "Testing API..."
    API_RESPONSE=$(curl -k -s https://$DOMAIN/api/health)
    if echo "$API_RESPONSE" | grep -q "Authentication required"; then
        log_success "API is responding"
    else
        log_warning "API may not be responding correctly"
    fi
    
    # Test static assets
    log_info "Testing static assets..."
    if curl -k -s https://$DOMAIN/assets/ | grep -q "404"; then
        log_warning "Static assets may not be loading correctly"
    else
        log_success "Static assets are loading"
    fi
    
    log_success "Deployment completed successfully!"
    log_info "You can now access your application at: https://$DOMAIN"
}

# Rollback function
rollback() {
    log_info "Starting rollback process..."
    
    if [ "$ON_SERVER" = false ]; then
        log_info "Connecting to production server for rollback..."
        ssh -i $SSH_KEY deploy@$DROPLET_IP "bash -s" < "$0" --rollback
        return
    fi
    
    # Server-side rollback
    log_info "Executing rollback on server..."
    
    cd $PROJECT_DIR
    
    # Revert to previous commit
    log_info "Reverting to previous commit..."
    git log --oneline -5
    read -p "Enter the commit hash to rollback to: " COMMIT_HASH
    git reset --hard $COMMIT_HASH
    
    # Rebuild and restart
    cd docker
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "Rollback completed!"
}

# Health check function
health_check() {
    log_info "Running health check..."
    
    if [ "$ON_SERVER" = false ]; then
        ssh -i $SSH_KEY deploy@$DROPLET_IP "bash -s" < "$0" --health-check
        return
    fi
    
    # Server-side health check
    cd $PROJECT_DIR/docker
    
    log_info "Service Status:"
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "Resource Usage:"
    docker stats --no-stream
    
    log_info "Disk Usage:"
    df -h
    
    log_info "Testing endpoints:"
    echo "Frontend: $(curl -k -s -o /dev/null -w "%{http_code}" https://$DOMAIN/)"
    echo "API Health: $(curl -k -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health)"
    echo "Assets: $(curl -k -s -o /dev/null -w "%{http_code}" https://$DOMAIN/assets/)"
}

# Main script logic
case "${1:-deploy}" in
    --on-server)
        deploy
        ;;
    --rollback)
        rollback
        ;;
    --health-check)
        health_check
        ;;
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|health]"
        echo ""
        echo "Commands:"
        echo "  deploy     - Deploy latest changes (default)"
        echo "  rollback   - Rollback to previous version"
        echo "  health     - Run health check"
        echo ""
        echo "Examples:"
        echo "  $0                    # Deploy latest changes"
        echo "  $0 deploy             # Deploy latest changes"
        echo "  $0 rollback           # Rollback to previous version"
        echo "  $0 health             # Run health check"
        exit 1
        ;;
esac
