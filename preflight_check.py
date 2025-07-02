#!/usr/bin/env python3
"""
Pre-flight Check for SEO-Agent System
Run this before deployment to ensure everything works
"""
import os
import sys
import subprocess
import importlib
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_status(status, message):
    if status == "OK":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def check_python_version():
    """Check Python version"""
    print(f"\n{Colors.BOLD}Checking Python Version...{Colors.END}")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status("OK", f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("ERROR", f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print(f"\n{Colors.BOLD}Checking Dependencies...{Colors.END}")
    
    required_packages = [
        ('flask', 'Flask'),
        ('celery', 'Celery'),
        ('redis', 'redis-py'),
        ('anthropic', 'Anthropic'),
        ('openai', 'OpenAI'),
        ('playwright', 'Playwright'),
        ('bs4', 'beautifulsoup4'),
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('jinja2', 'Jinja2'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing = []
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print_status("OK", f"{package_name} installed")
        except ImportError:
            print_status("ERROR", f"{package_name} not installed")
            missing.append(package_name)
    
    if missing:
        print_status("INFO", f"Install missing packages: pip install {' '.join(missing)}")
        return False
    return True

def check_environment_variables():
    """Check required environment variables"""
    print(f"\n{Colors.BOLD}Checking Environment Variables...{Colors.END}")
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'ANTHROPIC_API_KEY': ('Critical', 'Claude AI access'),
        'OPENAI_API_KEY': ('Critical', 'GPT-4 access'),
        'REDIS_URL': ('Critical', 'Task queue'),
        'JINA_API_KEY': ('Important', 'Live search data'),
        'FLASK_SECRET_KEY': ('Important', 'Session security'),
        'MASTER_API_KEY': ('Important', 'API authentication')
    }
    
    optional_vars = {
        'BRIGHTDATA_USERNAME': 'Web scraping fallback',
        'SUPABASE_URL': 'Database storage',
        'DO_API_TOKEN': 'Digital Ocean deployment'
    }
    
    missing_critical = []
    missing_important = []
    
    # Check required
    for var, (level, desc) in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print_status("OK", f"{var} set ({desc})")
        else:
            if level == 'Critical':
                print_status("ERROR", f"{var} not set - {desc}")
                missing_critical.append(var)
            else:
                print_status("WARNING", f"{var} not set - {desc}")
                missing_important.append(var)
    
    # Check optional
    print(f"\n{Colors.BOLD}Optional Services:{Colors.END}")
    for var, desc in optional_vars.items():
        if os.getenv(var):
            print_status("OK", f"{var} set ({desc})")
        else:
            print_status("INFO", f"{var} not set ({desc})")
    
    return len(missing_critical) == 0

def check_redis():
    """Check if Redis is running"""
    print(f"\n{Colors.BOLD}Checking Redis...{Colors.END}")
    try:
        import redis
        r = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        r.ping()
        print_status("OK", "Redis is running")
        return True
    except Exception as e:
        print_status("ERROR", "Redis not running - start with: redis-server")
        return False

def check_directories():
    """Check and create required directories"""
    print(f"\n{Colors.BOLD}Checking Directories...{Colors.END}")
    
    required_dirs = [
        'logs',
        'outputs',
        'agent_data',
        'frontend',
        '.cache'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_status("OK", f"{dir_name}/ exists")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_status("OK", f"{dir_name}/ created")
            except Exception as e:
                print_status("ERROR", f"Cannot create {dir_name}/: {e}")
                return False
    return True

def check_files():
    """Check if all critical files exist"""
    print(f"\n{Colors.BOLD}Checking Critical Files...{Colors.END}")
    
    critical_files = [
        'main.py',
        'requirements.txt',
        '.env',
        'frontend/index.html',
        'frontend/workshop.html',
        'frontend/workshop_enhanced.html',
        'workshop_api.py',
        'enhanced_workshop_api.py'
    ]
    
    missing = []
    for file in critical_files:
        if Path(file).exists():
            print_status("OK", file)
        else:
            print_status("ERROR", f"{file} not found")
            missing.append(file)
    
    return len(missing) == 0

def check_playwright():
    """Check if Playwright browsers are installed"""
    print(f"\n{Colors.BOLD}Checking Playwright Browsers...{Colors.END}")
    try:
        import playwright
        # Check if chromium is installed
        browser_path = Path.home() / '.cache' / 'ms-playwright'
        if browser_path.exists() and any(browser_path.iterdir()):
            print_status("OK", "Playwright browsers installed")
            return True
        else:
            print_status("WARNING", "Playwright browsers not installed")
            print_status("INFO", "Install with: python -m playwright install chromium")
            return True  # Not critical
    except ImportError:
        print_status("WARNING", "Playwright not installed")
        return True  # Not critical

def check_api_endpoints():
    """Test if Flask app can start"""
    print(f"\n{Colors.BOLD}Checking Flask App...{Colors.END}")
    try:
        from main import app
        print_status("OK", "Flask app imports successfully")
        
        # Check routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        important_routes = ['/api/generate', '/workshop', '/workshop-pro', '/api/find-opportunities']
        
        for route in important_routes:
            if any(route in r for r in routes):
                print_status("OK", f"Route {route} registered")
            else:
                print_status("WARNING", f"Route {route} not found")
        
        return True
    except Exception as e:
        print_status("ERROR", f"Flask app error: {str(e)[:50]}")
        return False

def check_security():
    """Check security configuration"""
    print(f"\n{Colors.BOLD}Checking Security...{Colors.END}")
    
    issues = []
    
    # Check .env.example for exposed keys
    if Path('.env.example').exists():
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'sk-ant-api03-' in content or 'sk-proj-' in content:
                print_status("ERROR", "Real API keys found in .env.example!")
                issues.append("exposed_keys")
            else:
                print_status("OK", ".env.example contains placeholders only")
    
    # Check Flask secret key
    secret_key = os.getenv('FLASK_SECRET_KEY')
    if not secret_key or len(secret_key) < 16:
        print_status("WARNING", "FLASK_SECRET_KEY not set or too short")
        issues.append("weak_secret")
    else:
        print_status("OK", "FLASK_SECRET_KEY configured")
    
    # Check debug mode
    if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG') == 'True':
        print_status("ERROR", "Debug mode enabled in production!")
        issues.append("debug_in_prod")
    else:
        print_status("OK", "Debug mode configured correctly")
    
    return len([i for i in issues if i == 'exposed_keys']) == 0

def generate_startup_script():
    """Generate a startup script if all checks pass"""
    script_content = """#!/bin/bash
# SEO-Agent Startup Script - Generated by preflight check

echo "🚀 Starting SEO-Agent System..."

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# Start Celery Worker
echo "Starting Celery Worker..."
celery -A main.celery worker --loglevel=info &
CELERY_PID=$!
sleep 2

# Start Flask App
echo "Starting Flask Application..."
python main.py &
FLASK_PID=$!

echo ""
echo "✅ System started!"
echo "📊 Dashboard: http://localhost:5000"
echo "🔧 Workshop: http://localhost:5000/workshop"
echo "🚀 Workshop Pro: http://localhost:5000/workshop-pro"
echo ""
echo "PIDs: Celery=$CELERY_PID, Flask=$FLASK_PID"
echo "Stop with: kill $CELERY_PID $FLASK_PID"
"""
    
    with open('start.sh', 'w') as f:
        f.write(script_content)
    os.chmod('start.sh', 0o755)
    print_status("OK", "Created start.sh script")

def main():
    """Run all checks"""
    print(f"{Colors.BOLD}🔍 SEO-Agent Pre-Flight Check{Colors.END}")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Redis Server", check_redis),
        ("Directories", check_directories),
        ("Critical Files", check_files),
        ("Playwright", check_playwright),
        ("Flask App", check_api_endpoints),
        ("Security", check_security)
    ]
    
    failed = []
    warnings = []
    
    for name, check_func in checks:
        try:
            if not check_func():
                failed.append(name)
        except Exception as e:
            print_status("ERROR", f"{name} check failed: {e}")
            failed.append(name)
    
    # Summary
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print("=" * 50)
    
    if not failed:
        print(f"{Colors.GREEN}✅ All checks passed! System ready to run.{Colors.END}")
        generate_startup_script()
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print("1. Run: ./start.sh")
        print("2. Open: http://localhost:5000/workshop-pro")
        return True
    else:
        print(f"{Colors.RED}❌ {len(failed)} checks failed:{Colors.END}")
        for check in failed:
            print(f"  - {check}")
        print(f"\n{Colors.BOLD}Fix these issues before running the system.{Colors.END}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)