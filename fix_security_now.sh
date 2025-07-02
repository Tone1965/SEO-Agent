#!/bin/bash
# Quick security fixes before deployment

echo "🔒 Fixing security issues..."

# 1. Remove exposed API keys from .env.example
echo "Cleaning .env.example..."
cat > .env.example << 'EOF'
# Copy this file to .env and add your actual API keys

# AI API Keys (REQUIRED)
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database (OPTIONAL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Digital Ocean (OPTIONAL)
DO_API_TOKEN=your_digital_ocean_token_here
DO_DROPLET_IP=your_droplet_ip_here

# Redis & Celery (Default for local development)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True

# Security (REQUIRED for production)
MASTER_API_KEY=your_master_api_key_here
FLASK_SECRET_KEY=generate_random_secret_key_here
ALLOWED_ORIGINS=http://localhost:5000,https://yourdomain.com

# Optional Services
GITHUB_TOKEN=your_github_token_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
SENTRY_DSN=your_sentry_dsn_here

# Web Scraping & Analysis
BRIGHTDATA_API_KEY=your_brightdata_api_key_here
BRIGHTDATA_CUSTOMER_ID=your_brightdata_customer_id_here
BRIGHTDATA_HOST=brd.superproxy.io
BRIGHTDATA_PORT=9222
BRIGHTDATA_SELENIUM_PORT=9515
BRIGHTDATA_USERNAME=your_brightdata_username_here
BRIGHTDATA_PASSWORD=your_brightdata_password_here
BRIGHTDATA_PUPPETEER_URL=wss://username:password@brd.superproxy.io:9222
BRIGHTDATA_SELENIUM_URL=https://username:password@brd.superproxy.io:9515
JINA_API_KEY=your_jina_api_key_here

# Alert System
ALERT_EMAIL=your_email@gmail.com
ALERT_PHONE=+1234567890
SMTP_EMAIL=your_smtp_email@gmail.com
SMTP_PASSWORD=your_app_password_here
DAILY_BUDGET=50

# Monitoring
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_token_here
TWILIO_PHONE=+1234567890
YOUR_PHONE=+1234567890
EOF

# 2. Create production config
echo "Creating production config..."
cat > .env.production.example << 'EOF'
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=False

# Generate these for production:
MASTER_API_KEY=generate-strong-api-key-here
FLASK_SECRET_KEY=generate-random-64-char-string-here
ALLOWED_ORIGINS=https://yourdomain.com

# Use strong passwords in production
EOF

# 3. Update .gitignore
echo "Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Security
.env.production
*.key
*.pem
*.cert
secrets/
EOF

# 4. Create minimal auth check
echo "Creating auth check..."
cat > check_auth.py << 'EOF'
import os

def check_security_config():
    """Check if security is properly configured"""
    issues = []
    
    if not os.getenv('MASTER_API_KEY') or os.getenv('MASTER_API_KEY') == 'your_master_api_key_here':
        issues.append("MASTER_API_KEY not set")
    
    if not os.getenv('FLASK_SECRET_KEY') or len(os.getenv('FLASK_SECRET_KEY', '')) < 16:
        issues.append("FLASK_SECRET_KEY not set or too short")
    
    if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG') == 'True':
        issues.append("Debug mode enabled in production!")
    
    return issues

if __name__ == "__main__":
    issues = check_security_config()
    if issues:
        print("⚠️ Security issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Security config looks good")
EOF

echo "✅ Security fixes complete!"
echo ""
echo "Next steps:"
echo "1. Add MASTER_API_KEY to your .env file"
echo "2. Generate FLASK_SECRET_KEY: python -c 'import os; print(os.urandom(24).hex())'"
echo "3. Run: python check_auth.py"
echo "4. Then push to git"