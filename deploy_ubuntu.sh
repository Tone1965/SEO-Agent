#!/bin/bash
# Deployment script for Ubuntu server

echo "🚀 SEO-Agent Ubuntu Deployment Script"
echo "====================================="

# Update system
echo "Updating system packages..."
sudo apt update

# Install Python3 and pip if not present
echo "Installing Python dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev

# Install Redis if not present
if ! command -v redis-server &> /dev/null; then
    echo "Installing Redis..."
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
fi

# Install required system packages for Playwright
echo "Installing system dependencies for Playwright..."
sudo apt install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libatspi2.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 libxcb1 libxkbcommon0 \
    libgtk-3-0 libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
    libasound2

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Create required directories
echo "Creating directories..."
mkdir -p logs outputs agent_data .cache

# Set up environment file
if [ ! -f .env ]; then
    echo "Setting up .env file..."
    cp .env.example .env
    
    # Generate secure keys
    FLASK_SECRET=$(python3 -c 'import os; print(os.urandom(24).hex())')
    MASTER_KEY=$(python3 -c 'import os; print(os.urandom(32).hex())')
    
    # Update .env with secure keys
    sed -i "s/your_flask_secret_key_here/$FLASK_SECRET/g" .env
    sed -i "s/your_master_api_key_here/$MASTER_KEY/g" .env
    
    echo "✅ Generated secure keys"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - JINA_API_KEY (get from jina.ai)"
fi

# Create systemd service for production
echo "Creating systemd service..."
sudo tee /etc/systemd/system/seo-agent.service > /dev/null <<EOF
[Unit]
Description=SEO Agent System
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment="PATH=$PWD/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PWD/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Celery service
sudo tee /etc/systemd/system/seo-agent-celery.service > /dev/null <<EOF
[Unit]
Description=SEO Agent Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment="PATH=$PWD/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PWD/venv/bin/celery -A main.celery worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx config if nginx is installed
if command -v nginx &> /dev/null; then
    echo "Creating nginx configuration..."
    sudo tee /etc/nginx/sites-available/seo-agent > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $PWD/frontend;
        expires 1d;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/seo-agent /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
fi

echo ""
echo "✅ Deployment setup complete!"
echo ""
echo "To start the services:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl start seo-agent"
echo "  sudo systemctl start seo-agent-celery"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable seo-agent"
echo "  sudo systemctl enable seo-agent-celery"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u seo-agent -f"
echo "  sudo journalctl -u seo-agent-celery -f"
echo ""
echo "First, make sure to:"
echo "1. Edit .env and add your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python preflight_check.py"