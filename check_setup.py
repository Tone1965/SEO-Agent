"""
Check Web Scraping Setup
Shows exactly what's configured and working
"""
import os
import requests
from datetime import datetime

def check_setup():
    """Check all scraping configurations"""
    
    print("🔧 WEB SCRAPING SETUP CHECK")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Check Jina
    print("\n1️⃣ JINA API")
    print("-" * 40)
    
    jina_key = os.getenv('JINA_API_KEY')
    if jina_key:
        print("✅ API Key: Set")
        print(f"   Key preview: {jina_key[:20]}...")
        
        # Test Jina
        try:
            headers = {"Authorization": f"Bearer {jina_key}"}
            response = requests.get("https://s.jina.ai/test", headers=headers, timeout=5)
            if response.status_code == 200:
                print("✅ API Status: Working")
            else:
                print(f"⚠️ API Status: Error {response.status_code}")
        except Exception as e:
            print(f"❌ API Status: Failed - {str(e)[:50]}")
        
        print("\n   Capabilities:")
        print("   • Search Google: https://s.jina.ai/[query]")
        print("   • Scrape URLs: https://r.jina.ai/[url]")
        print("   • Clean content extraction")
        print("   • No browser needed")
    else:
        print("❌ API Key: Not configured")
        print("\n   To fix:")
        print("   1. Go to https://jina.ai")
        print("   2. Sign up for free")
        print("   3. Get API key")
        print("   4. Add to .env: JINA_API_KEY=your_key")
    
    # Check BrightData
    print("\n\n2️⃣ BRIGHTDATA")
    print("-" * 40)
    
    bd_configs = {
        'Customer ID': os.getenv('BRIGHTDATA_CUSTOMER_ID'),
        'Username': os.getenv('BRIGHTDATA_USERNAME'),
        'Password': os.getenv('BRIGHTDATA_PASSWORD'),
        'Puppeteer URL': os.getenv('BRIGHTDATA_PUPPETEER_URL'),
        'Selenium URL': os.getenv('BRIGHTDATA_SELENIUM_URL')
    }
    
    configured = all([
        bd_configs['Customer ID'],
        bd_configs['Username'],
        bd_configs['Password']
    ])
    
    if configured:
        print("✅ Credentials: Set")
        print(f"   Customer ID: {bd_configs['Customer ID']}")
        print(f"   Username: {bd_configs['Username'][:30]}...")
        
        print("\n   Capabilities:")
        print("   • Premium web scraping")
        print("   • Bypass anti-bot protection")
        print("   • Residential proxies")
        print("   • JavaScript rendering")
        
        # Check if Playwright is installed
        try:
            import playwright
            print("\n✅ Playwright: Installed")
        except ImportError:
            print("\n⚠️ Playwright: Not installed")
            print("   Run: pip install playwright")
            print("   Then: python -m playwright install chromium")
    else:
        print("❌ Credentials: Not fully configured")
        missing = [k for k, v in bd_configs.items() if not v]
        print(f"   Missing: {', '.join(missing)}")
    
    # Check priority order
    print("\n\n3️⃣ FALLBACK STRATEGY")
    print("-" * 40)
    
    if jina_key and configured:
        print("✅ Both services configured!")
        print("\n   Priority order:")
        print("   1. Try Jina first (faster, cheaper)")
        print("   2. If Jina fails → BrightData (more reliable)")
        print("   3. Always get data, no matter what")
        
        print("\n   When Jina might fail:")
        print("   • Rate limits reached")
        print("   • Complex JavaScript sites")
        print("   • Anti-bot protection")
        
        print("\n   BrightData handles:")
        print("   • All the above cases")
        print("   • Any website, guaranteed")
    elif jina_key:
        print("⚠️ Only Jina configured")
        print("   No fallback if Jina fails")
    elif configured:
        print("⚠️ Only BrightData configured")
        print("   Will use BrightData for everything")
    else:
        print("❌ No scraping service configured!")
    
    # Usage examples
    print("\n\n4️⃣ HOW TO USE")
    print("-" * 40)
    
    print("Option 1: Automatic fallback (recommended)")
    print("```python")
    print("from scraping_manager import ScrapingManager")
    print("scraper = ScrapingManager()")
    print("")
    print("# Automatically uses Jina → BrightData fallback")
    print("results = scraper.search('emergency plumber Birmingham')")
    print("content = scraper.scrape('https://competitor.com')")
    print("```")
    
    print("\nOption 2: Direct Jina usage")
    print("```python")
    print("from jina_complete import JinaComplete")
    print("jina = JinaComplete()")
    print("")
    print("# Fast and simple")
    print("results = jina.search('weekend electrician')")
    print("content = jina.scrape('https://example.com')")
    print("```")
    
    print("\nOption 3: Money finder with fallback")
    print("```python")
    print("from scraping_manager import MoneyFinderWithFallback")
    print("finder = MoneyFinderWithFallback()")
    print("")
    print("# Finds opportunities using best available service")
    print("opportunities = finder.find_opportunities('Birmingham AL')")
    print("```")
    
    # Files created
    print("\n\n5️⃣ FILES AVAILABLE")
    print("-" * 40)
    
    files = {
        'jina_complete.py': 'Full Jina integration with all features',
        'brightdata_scraper.py': 'BrightData browser automation',
        'scraping_manager.py': 'Automatic fallback system',
        'find_money_now.py': 'Instant opportunity finder',
        'jina_money_finder.py': 'Advanced money keyword research'
    }
    
    for filename, description in files.items():
        if os.path.exists(filename):
            print(f"✅ {filename}")
            print(f"   {description}")
        else:
            print(f"❌ {filename} - Not found")
    
    # Summary
    print("\n\n📊 SUMMARY")
    print("=" * 60)
    
    status = []
    if jina_key:
        status.append("Jina API ✅")
    else:
        status.append("Jina API ❌")
    
    if configured:
        status.append("BrightData ✅")
    else:
        status.append("BrightData ❌")
    
    print(f"Status: {' | '.join(status)}")
    
    if jina_key and configured:
        print("\n🎉 You're fully set up with automatic fallback!")
        print("Run: python find_money_now.py")
    elif jina_key:
        print("\n⚠️ You have Jina but no BrightData fallback")
        print("This is OK for most searches")
    elif configured:
        print("\n⚠️ You have BrightData but Jina would be faster/cheaper")
        print("Consider adding Jina for better performance")
    else:
        print("\n❌ Please configure at least one scraping service")


if __name__ == "__main__":
    check_setup()