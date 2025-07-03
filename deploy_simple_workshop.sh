#!/bin/bash
# Deploy simplified workshop interface

echo "🚀 Deploying Simplified Workshop Interface"
echo "========================================"

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating Python environment..."
source venv/bin/activate

# Check if any new dependencies
echo "📦 Checking dependencies..."
pip install -r requirements.txt 2>/dev/null || echo "Dependencies up to date"

# Find running process
echo "🔍 Finding current SEO-Agent process..."
CURRENT_PID=$(ps aux | grep "[p]ython.*main.py\|[p]ython.*start_on_free_port.py" | awk '{print $2}')

if [ ! -z "$CURRENT_PID" ]; then
    echo "⏹️  Stopping current process (PID: $CURRENT_PID)..."
    kill $CURRENT_PID
    sleep 2
fi

# Start on free port
echo "🚀 Starting SEO-Agent on available port..."
nohup python start_on_free_port.py > logs/seo-agent.log 2>&1 &
NEW_PID=$!

sleep 3

# Check if started successfully
if ps -p $NEW_PID > /dev/null; then
    echo "✅ SEO-Agent started successfully (PID: $NEW_PID)"
    echo ""
    echo "📱 Access the simplified workshop at:"
    PORT=$(grep "Starting SEO-Agent on port" logs/seo-agent.log | tail -1 | grep -oP '\d{4}')
    echo "   http://142.93.194.81:${PORT}/workshop-simple"
    echo ""
    echo "🔧 Other interfaces:"
    echo "   Original Workshop: http://142.93.194.81:${PORT}/workshop"
    echo "   Workshop Pro: http://142.93.194.81:${PORT}/workshop-pro"
    echo "   Main Dashboard: http://142.93.194.81:${PORT}/"
else
    echo "❌ Failed to start SEO-Agent"
    echo "Check logs/seo-agent.log for details"
fi