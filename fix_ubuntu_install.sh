#!/bin/bash
# Fix installation issues on Ubuntu server

echo "🔧 Fixing SEO-Agent Installation Issues..."
echo "========================================"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install build tools
echo "Installing build tools..."
pip install --upgrade pip setuptools wheel

# Install numpy compatible with Python 3.12
echo "Installing numpy..."
pip install numpy==1.26.4

# Install packages one by one to avoid conflicts
echo "Installing core packages..."
pip install flask==3.0.0
pip install celery==5.3.4
pip install redis==5.0.1
pip install anthropic==0.8.1
pip install openai==1.3.8

# Install Playwright
echo "Installing Playwright..."
pip install playwright==1.40.0

# Install other essential packages
echo "Installing additional packages..."
pip install beautifulsoup4==4.12.2
pip install requests
pip install aiohttp
pip install python-dotenv
pip install jinja2
pip install pandas
pip install sqlalchemy
pip install psycopg2-binary

# Try to install remaining packages
echo "Installing remaining packages..."
pip install -r requirements.txt || echo "Some packages failed, but continuing..."

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Install missing system dependency
echo "Installing system dependencies..."
sudo apt install -y libasound2t64

# Create directories if missing
mkdir -p logs outputs agent_data .cache

# Check if everything is working
echo ""
echo "🔍 Running preflight check..."
python preflight_check.py

echo ""
echo "✅ Installation fixed!"
echo ""
echo "To start the system:"
echo "1. Start Redis: sudo systemctl start redis-server"
echo "2. In one terminal: celery -A main.celery worker --loglevel=info"
echo "3. In another terminal: python main.py"
echo ""
echo "Or use systemd services:"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl start seo-agent"
echo "sudo systemctl start seo-agent-celery"