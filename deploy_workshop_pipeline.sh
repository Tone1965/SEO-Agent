#!/bin/bash
# Deploy the rebuilt workshop pipeline

echo "🚀 Deploying Workshop Pipeline with Live Data"
echo "==========================================="

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating Python environment..."
source venv/bin/activate

# Install any new dependencies
echo "📦 Checking dependencies..."
pip install -r requirements.txt 2>/dev/null || echo "Dependencies up to date"

# Find and kill current process
echo "🔍 Finding current process..."
CURRENT_PID=$(ps aux | grep "[p]ython.*main.py\|[p]ython.*start_on_free_port.py" | awk '{print $2}')

if [ ! -z "$CURRENT_PID" ]; then
    echo "⏹️  Stopping current process (PID: $CURRENT_PID)..."
    kill $CURRENT_PID
    sleep 2
fi

# Start with the pipeline workshop
echo "🚀 Starting Workshop Pipeline..."
nohup python start_on_free_port.py > logs/seo-agent.log 2>&1 &
NEW_PID=$!

sleep 3

# Check if started
if ps -p $NEW_PID > /dev/null; then
    PORT=$(grep "Starting SEO-Agent on port" logs/seo-agent.log | tail -1 | grep -oP '\d{4}')
    echo "✅ Workshop Pipeline started successfully!"
    echo ""
    echo "🎯 Access the new workshop at:"
    echo "   http://142.93.194.81:${PORT}/workshop-pipeline"
    echo ""
    echo "Features:"
    echo "✓ Visual pipeline showing all agents"
    echo "✓ Live Google data from Jina/BrightData"
    echo "✓ Control each agent's output"
    echo "✓ Edit and approve at each step"
    echo "✓ See real competitor data"
    echo ""
else
    echo "❌ Failed to start. Check logs/seo-agent.log"
fi