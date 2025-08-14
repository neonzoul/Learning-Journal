#!/bin/bash
# Production deployment script for Accounting Automation Backend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env"
DEPLOYMENT_DIR="${PROJECT_ROOT}/deployment"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Accounting Automation Backend Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found at $ENV_FILE"
    print_error "Please copy .env.example to .env and configure it"
    exit 1
fi

print_status "Found .env file"

# Validate configuration
print_status "Validating configuration..."
cd "$PROJECT_ROOT"

if python scripts/validate_config.py; then
    print_status "Configuration validation passed"
else
    print_error "Configuration validation failed"
    exit 1
fi

# Check required environment variables
print_status "Checking required environment variables..."
source "$ENV_FILE"

required_vars=("N8N_WEBHOOK_URL" "N8N_API_KEY" "CALLBACK_SECRET_TOKEN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        print_error "  - $var"
    done
    exit 1
fi

print_status "All required environment variables are set"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Build and deploy
print_status "Building Docker images..."
cd "$DEPLOYMENT_DIR"

if docker-compose build; then
    print_status "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down

# Start services
print_status "Starting services..."
if docker-compose up -d; then
    print_status "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check service health
print_status "Checking service health..."
if docker-compose ps | grep -q "Up (healthy)"; then
    print_status "Services are healthy"
else
    print_warning "Some services may not be healthy yet"
    print_status "Check service status with: docker-compose ps"
fi

# Display service URLs
print_status "Deployment completed successfully!"
echo ""
echo -e "${GREEN}Service URLs:${NC}"
echo -e "  API: http://localhost:8000"
echo -e "  Health Check: http://localhost:8000/health"
echo -e "  Queue Dashboard: http://localhost:8000/rq"
echo -e "  Queue Status: http://localhost:8000/monitoring/queue"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo -e "  View logs: docker-compose logs -f"
echo -e "  Check status: docker-compose ps"
echo -e "  Stop services: docker-compose down"
echo -e "  Restart services: docker-compose restart"
echo ""
echo -e "${BLUE}Deployment completed at $(date)${NC}"