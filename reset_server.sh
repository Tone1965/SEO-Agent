#!/bin/bash
echo "🔧 Complete Server Reset Script for SEO Agent"
echo "============================================"
echo ""
echo "SSH into your server (142.93.194.81) and run these commands:"
echo ""
echo "# 1. Stop all containers and clean up"
echo "cd /root/SEO-Agent"
echo "docker-compose down"
echo "docker system prune -a -f"
echo ""
echo "# 2. Pull latest code"
echo "git pull origin main"
echo ""
echo "# 3. Rebuild everything fresh"
echo "docker-compose build --no-cache"
echo ""
echo "# 4. Start all services"
echo "docker-compose up -d"
echo ""
echo "# 5. Check if services are running"
echo "docker-compose ps"
echo ""
echo "# 6. Check logs if needed"
echo "docker-compose logs seo-agent"
echo ""
echo "After running these commands:"
echo "- Main site: http://142.93.194.81/"
echo "- Workshop: http://142.93.194.81/workshop.html"
echo ""
echo "If still having issues, check:"
echo "- docker-compose logs redis"
echo "- docker-compose logs nginx"
echo "- docker-compose logs celery-worker"