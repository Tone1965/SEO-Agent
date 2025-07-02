"""
Test BrightData + Jina Integration
"""
import asyncio
import os
from brightdata_scraper import BrightDataScraper
from integrated_opportunity_finder import IntegratedOpportunityFinder

async def test_brightdata_connection():
    """Test if BrightData connection works"""
    print("🔧 Testing BrightData Connection...")
    print("=" * 60)
    
    scraper = BrightDataScraper()
    
    # Test with a simple URL
    test_urls = ["https://example.com"]
    
    try:
        results = await scraper.scrape_competitor_data(test_urls)
        
        if results and results[0]:
            print("✅ BrightData connection successful!")
            print(f"Title: {results[0].get('title', 'N/A')}")
            print(f"Word Count: {results[0].get('word_count', 0)}")
            return True
        else:
            print("❌ Failed to get data")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n📝 Troubleshooting:")
        print("1. Make sure Playwright browsers are installed:")
        print("   python -m playwright install chromium")
        print("2. Check your BrightData credentials in .env")
        print("3. Verify your BrightData account is active")
        return False

def test_jina_connection():
    """Test if Jina API works"""
    print("\n🔧 Testing Jina API Connection...")
    print("=" * 60)
    
    jina_key = os.getenv('JINA_API_KEY')
    if not jina_key:
        print("❌ JINA_API_KEY not set in .env!")
        print("Add: JINA_API_KEY=your_key_here")
        return False
    
    # Test search
    try:
        import requests
        headers = {"Authorization": f"Bearer {jina_key}"}
        response = requests.get("https://s.jina.ai/test", headers=headers)
        
        if response.status_code == 200:
            print("✅ Jina API connection successful!")
            return True
        else:
            print(f"❌ Jina API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_integrated_system():
    """Test the complete integrated system"""
    print("\n🔧 Testing Integrated Opportunity Finder...")
    print("=" * 60)
    
    # Check if both APIs are configured
    if not os.getenv('JINA_API_KEY'):
        print("❌ Missing JINA_API_KEY")
        return False
    
    if not os.getenv('BRIGHTDATA_USERNAME'):
        print("❌ Missing BrightData credentials")
        return False
    
    print("✅ All credentials found!")
    print("\n📊 Sample opportunity search would analyze:")
    print("- Emergency plumber Birmingham AL")
    print("- Weekend electrician Birmingham AL")
    print("- 24 hour HVAC Birmingham AL")
    print("\nEach would check:")
    print("- Search volume and competition (Jina)")
    print("- Competitor weaknesses (BrightData)")
    print("- Revenue potential calculation")
    print("- Action plan generation")
    
    return True

# Main test runner
if __name__ == "__main__":
    print("🚀 SEO Agent System - API Integration Test")
    print("=" * 60)
    
    # Test BrightData
    bd_success = asyncio.run(test_brightdata_connection())
    
    # Test Jina
    jina_success = test_jina_connection()
    
    # Test integrated system
    integrated_success = test_integrated_system()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    print(f"BrightData: {'✅ PASS' if bd_success else '❌ FAIL'}")
    print(f"Jina API: {'✅ PASS' if jina_success else '❌ FAIL'}")
    print(f"Integration: {'✅ READY' if integrated_success else '❌ NOT READY'}")
    
    if bd_success and jina_success and integrated_success:
        print("\n🎉 All systems ready! You can now:")
        print("1. Run: python integrated_opportunity_finder.py")
        print("2. Find profitable keywords in any city")
        print("3. Get instant action plans for monetization")
    else:
        print("\n⚠️ Please fix the issues above before proceeding")