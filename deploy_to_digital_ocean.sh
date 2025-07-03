#!/bin/bash
# Deploy to Digital Ocean script

echo "🚀 Deploying SEO-Agent to Digital Ocean"
echo "========================================"

# SSH into server and pull latest changes
echo "📦 Pulling latest changes on server..."
ssh seo-agent-do << 'ENDSSH'
cd /root/SEO-Agent
git pull origin main

# Rebuild Docker images with new code
echo "🔨 Rebuilding Docker images..."
docker-compose down
docker-compose build --no-cache

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Check status
echo "✅ Checking service status..."
docker-compose ps

# Show logs
echo "📄 Recent logs:"
docker-compose logs --tail=50 seo-agent
ENDSSH

echo "✅ Deployment complete!"
echo "🌐 Check site at: http://142.93.194.81:5000/"