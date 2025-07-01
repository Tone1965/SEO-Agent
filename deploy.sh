#!/bin/bash
# =====================================
# DEPLOY.SH - DIGITAL OCEAN DEPLOYMENT SCRIPT
# =====================================

set -e  # Exit on any error

echo "🚀 Starting SEO Agent System deployment to Digital Ocean..."

# Check if required environment variables are set
check_env_vars() {
    local required_vars=("ANTHROPIC_API_KEY" "OPENAI_API_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "❌ Error: $var environment variable is not set"
            echo "Please set it with: export $var='your_key_here'"
            exit 1
        fi
    done
    echo "✅ Required environment variables are set"
}

# Create environment file for Docker Compose
create_env_file() {
    echo "📝 Creating .env file for Docker Compose..."
    cat > .env << EOF
# SEO Agent System Environment Variables
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GITHUB_TOKEN=${GITHUB_TOKEN:-}
FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY:-}

# Docker configuration
COMPOSE_PROJECT_NAME=seo-agent
DOCKER_BUILDKIT=1

# Timezone
TZ=UTC
EOF
    echo "✅ Environment file created"
}

# Build and deploy with Docker Compose
deploy_services() {
    echo "🔨 Building and deploying services..."
    
    # Stop any existing services
    docker-compose down --remove-orphans
    
    # Build images
    echo "🔧 Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    echo "🚀 Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_health
}

# Check if services are running correctly
check_health() {
    echo "🔍 Checking service health..."
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Containers are running"
    else
        echo "❌ Some containers failed to start"
        docker-compose ps
        docker-compose logs
        exit 1
    fi
    
    # Check health endpoints
    local max_attempts=30
    local attempt=1
    
    echo "🏥 Checking health endpoint..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/health >/dev/null 2>&1; then
            echo "✅ SEO Agent API is healthy"
            break
        else
            echo "⏳ Attempt $attempt/$max_attempts: Waiting for API to be ready..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ API health check failed after $max_attempts attempts"
        echo "📋 Container logs:"
        docker-compose logs seo-agent
        exit 1
    fi
}

# Show deployment information
show_deployment_info() {
    echo ""
    echo "🎉 SEO Agent System deployed successfully!"
    echo ""
    echo "📊 Service URLs:"
    echo "   • Main Application: http://your-server-ip:5000"
    echo "   • API Health Check: http://your-server-ip:5000/health"
    echo "   • Celery Monitoring: http://your-server-ip:5555"
    echo ""
    echo "🐳 Docker Services:"
    docker-compose ps
    echo ""
    echo "📋 Useful commands:"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Restart services: docker-compose restart"
    echo "   • Stop services: docker-compose down"
    echo "   • Update services: ./deploy.sh"
    echo ""
    echo "🔧 To configure SSL/domain:"
    echo "   1. Update nginx.conf with your domain name"
    echo "   2. Add SSL certificates to ./ssl/ directory"
    echo "   3. Restart nginx: docker-compose restart nginx"
    echo ""
}

# Cleanup function for failures
cleanup_on_failure() {
    echo "❌ Deployment failed. Cleaning up..."
    docker-compose down --remove-orphans
    exit 1
}

# Set trap for cleanup on failure
trap cleanup_on_failure ERR

# Main deployment flow
main() {
    echo "🔍 Pre-deployment checks..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check environment variables
    check_env_vars
    
    # Create environment file
    create_env_file
    
    # Deploy services
    deploy_services
    
    # Show deployment information
    show_deployment_info
}

# Run main function
main "$@"