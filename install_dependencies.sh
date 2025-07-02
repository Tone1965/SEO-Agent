#!/bin/bash
# Install all dependencies for SEO-Agent

echo "📦 Installing SEO-Agent Dependencies..."
echo "===================================="

# Update pip
echo "Updating pip..."
python -m pip install --upgrade pip

# Install from requirements.txt
echo "Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Create required directories
echo "Creating directories..."
mkdir -p logs outputs agent_data .cache

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis not installed!"
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  macOS: brew install redis"
    echo "  Windows: Use WSL or Docker"
fi

# Generate secure keys if not exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    
    # Generate secure keys
    FLASK_SECRET=$(python -c 'import os; print(os.urandom(24).hex())')
    MASTER_KEY=$(python -c 'import os; print(os.urandom(32).hex())')
    
    # Add to .env if not present
    if ! grep -q "FLASK_SECRET_KEY=" .env; then
        echo "FLASK_SECRET_KEY=$FLASK_SECRET" >> .env
    fi
    
    if ! grep -q "MASTER_API_KEY=" .env; then
        echo "MASTER_API_KEY=$MASTER_KEY" >> .env
    fi
    
    echo "✅ Generated secure keys in .env"
fi

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env file:"
echo "   - JINA_API_KEY (get from jina.ai)"
echo "   - Keep your existing ANTHROPIC and OPENAI keys"
echo ""
echo "2. Start Redis: redis-server"
echo ""
echo "3. Run preflight check: python preflight_check.py"