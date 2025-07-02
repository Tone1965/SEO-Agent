"""
Quick Setup for BrightData + Jina Integration
"""
import os
import subprocess
import sys

def check_playwright():
    """Check if Playwright browsers are installed"""
    print("🔍 Checking Playwright installation...")
    try:
        import playwright
        print("✅ Playwright package found")
        
        # Check if browsers are installed
        browser_path = os.path.expanduser("~/.cache/ms-playwright")
        if os.path.exists(browser_path):
            print("✅ Playwright browsers installed")
            return True
        else:
            print("⚠️ Playwright browsers not installed")
            return False
    except ImportError:
        print("❌ Playwright not installed")
        return False

def install_playwright_browsers():
    """Install Playwright browsers"""
    print("\n📦 Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Chromium browser installed successfully")
        return True
    except Exception as e:
        print(f"❌ Error installing browsers: {e}")
        print("\nTry running manually:")
        print("python -m playwright install chromium")
        return False

def check_env_variables():
    """Check if all required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required = {
        'JINA_API_KEY': 'Jina API key for semantic search',
        'BRIGHTDATA_USERNAME': 'BrightData username',
        'BRIGHTDATA_PASSWORD': 'BrightData password',
        'ANTHROPIC_API_KEY': 'Claude API key',
        'OPENAI_API_KEY': 'OpenAI API key'
    }
    
    missing = []
    for var, description in required.items():
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing ({description})")
            missing.append(var)
    
    return len(missing) == 0

def create_test_script():
    """Create a simple test script"""
    test_code = '''
# Quick test of the opportunity finder
from integrated_opportunity_finder import IntegratedOpportunityFinder

finder = IntegratedOpportunityFinder()
opportunities = finder.find_golden_opportunities(
    location="Birmingham AL",
    min_profit=2000
)

if opportunities:
    print(f"\\n✅ Found {len(opportunities)} opportunities!")
    best = opportunities[0]
    print(f"Best opportunity: {best['keyword']} - ${best['monthly_revenue']}/month")
else:
    print("❌ No opportunities found")
'''
    
    with open('quick_test.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Created quick_test.py for testing")

def main():
    print("🚀 SEO Agent Scraping Setup")
    print("=" * 60)
    
    # Check Playwright
    if not check_playwright():
        if input("\nInstall Playwright browsers? (y/n): ").lower() == 'y':
            install_playwright_browsers()
    
    # Check environment variables
    env_ok = check_env_variables()
    
    if not env_ok:
        print("\n📝 Add missing variables to your .env file")
        print("\nFor Jina API key:")
        print("1. Go to https://jina.ai")
        print("2. Sign up for free account")
        print("3. Get API key from dashboard")
        print("4. Add to .env: JINA_API_KEY=your_key_here")
    
    # Create test script
    create_test_script()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    if check_playwright() and env_ok:
        print("✅ Everything is ready!")
        print("\nNext steps:")
        print("1. Run: python test_brightdata.py")
        print("2. Run: python quick_test.py")
        print("3. Run: python integrated_opportunity_finder.py")
    else:
        print("⚠️ Please complete setup first")

if __name__ == "__main__":
    main()