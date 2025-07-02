"""
Scraping Manager - Intelligently uses Jina first, falls back to BrightData
Ensures you always get data, no matter what
"""
import os
import requests
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime
import time

class ScrapingManager:
    def __init__(self):
        # Jina config
        self.jina_api_key = os.getenv('JINA_API_KEY')
        self.jina_headers = {"Authorization": f"Bearer {self.jina_api_key}"}
        
        # BrightData config
        self.brightdata_url = os.getenv('BRIGHTDATA_PUPPETEER_URL')
        self.has_brightdata = bool(self.brightdata_url)
        
        # Stats tracking
        self.stats = {
            'jina_success': 0,
            'jina_failures': 0,
            'brightdata_used': 0,
            'total_requests': 0
        }
    
    def search(self, query: str) -> Dict:
        """Search with Jina first, fall back to BrightData if needed"""
        
        self.stats['total_requests'] += 1
        print(f"🔍 Searching: {query}")
        
        # Try Jina first
        try:
            result = self._jina_search(query)
            if result and result.get('results'):
                self.stats['jina_success'] += 1
                print("✅ Jina search successful")
                return result
        except Exception as e:
            print(f"⚠️ Jina search failed: {e}")
            self.stats['jina_failures'] += 1
        
        # Fall back to BrightData
        if self.has_brightdata:
            print("🔄 Falling back to BrightData...")
            return self._brightdata_search(query)
        else:
            print("❌ No fallback available - BrightData not configured")
            return {'error': 'Search failed and no fallback available'}
    
    def scrape(self, url: str) -> str:
        """Scrape with Jina first, fall back to BrightData if needed"""
        
        self.stats['total_requests'] += 1
        print(f"📄 Scraping: {url}")
        
        # Try Jina first
        try:
            content = self._jina_scrape(url)
            if content:
                self.stats['jina_success'] += 1
                print("✅ Jina scrape successful")
                return content
        except Exception as e:
            print(f"⚠️ Jina scrape failed: {e}")
            self.stats['jina_failures'] += 1
        
        # Fall back to BrightData
        if self.has_brightdata:
            print("🔄 Falling back to BrightData...")
            return asyncio.run(self._brightdata_scrape(url))
        else:
            print("❌ No fallback available - BrightData not configured")
            return ""
    
    def _jina_search(self, query: str) -> Dict:
        """Use Jina to search"""
        url = f"https://s.jina.ai/{query}"
        
        response = requests.get(url, headers=self.jina_headers, timeout=15)
        response.raise_for_status()  # Will raise exception on 4xx/5xx
        
        return response.json()
    
    def _jina_scrape(self, url: str) -> str:
        """Use Jina to scrape"""
        scrape_url = f"https://r.jina.ai/{url}"
        
        response = requests.get(scrape_url, headers=self.jina_headers, timeout=15)
        response.raise_for_status()
        
        return response.text
    
    def _brightdata_search(self, query: str) -> Dict:
        """Use BrightData to search Google"""
        # For search, we'll scrape Google directly
        google_url = f"https://www.google.com/search?q={query}"
        content = asyncio.run(self._brightdata_scrape(google_url))
        
        if content:
            self.stats['brightdata_used'] += 1
            # Parse Google results (simplified)
            return self._parse_google_results(content, query)
        
        return {'error': 'BrightData search failed'}
    
    async def _brightdata_scrape(self, url: str) -> str:
        """Use BrightData to scrape any URL"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self.brightdata_url)
                page = await browser.new_page()
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                content = await page.content()
                
                await browser.close()
                
                self.stats['brightdata_used'] += 1
                return content
                
        except Exception as e:
            print(f"❌ BrightData error: {e}")
            return ""
    
    def _parse_google_results(self, html: str, query: str) -> Dict:
        """Parse Google search results from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find search results (simplified)
        for item in soup.find_all('div', class_='g')[:10]:
            link_elem = item.find('a')
            if link_elem and link_elem.get('href'):
                url = link_elem['href']
                title = link_elem.text if link_elem.text else ''
                
                # Get snippet
                snippet_elem = item.find('span', class_='st')
                snippet = snippet_elem.text if snippet_elem else ''
                
                results.append({
                    'url': url,
                    'title': title,
                    'content': snippet
                })
        
        return {
            'query': query,
            'results': results,
            'source': 'brightdata'
        }
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total = self.stats['total_requests']
        if total == 0:
            return self.stats
        
        self.stats['jina_success_rate'] = f"{(self.stats['jina_success'] / total * 100):.1f}%"
        self.stats['brightdata_usage_rate'] = f"{(self.stats['brightdata_used'] / total * 100):.1f}%"
        
        return self.stats
    
    def test_both_services(self) -> Dict:
        """Test both Jina and BrightData"""
        print("🧪 Testing Scraping Services")
        print("=" * 60)
        
        test_results = {
            'jina': {'search': False, 'scrape': False},
            'brightdata': {'available': self.has_brightdata, 'working': False}
        }
        
        # Test Jina search
        print("\n1️⃣ Testing Jina Search...")
        try:
            result = self._jina_search("test")
            test_results['jina']['search'] = bool(result.get('results'))
            print("✅ Jina search working")
        except:
            print("❌ Jina search failed")
        
        # Test Jina scrape
        print("\n2️⃣ Testing Jina Scrape...")
        try:
            content = self._jina_scrape("https://example.com")
            test_results['jina']['scrape'] = len(content) > 100
            print("✅ Jina scrape working")
        except:
            print("❌ Jina scrape failed")
        
        # Test BrightData
        if self.has_brightdata:
            print("\n3️⃣ Testing BrightData...")
            try:
                content = asyncio.run(self._brightdata_scrape("https://example.com"))
                test_results['brightdata']['working'] = len(content) > 100
                print("✅ BrightData working")
            except Exception as e:
                print(f"❌ BrightData failed: {e}")
        else:
            print("\n3️⃣ BrightData not configured")
        
        return test_results


class MoneyFinderWithFallback:
    """Money finder that always works using fallback strategy"""
    
    def __init__(self):
        self.scraper = ScrapingManager()
        
    def find_opportunities(self, location: str) -> List[Dict]:
        """Find money opportunities with automatic fallback"""
        
        opportunities = []
        
        # High-value keywords
        keywords = [
            f"emergency plumber {location}",
            f"weekend electrician {location}",
            f"24 hour ac repair {location}",
            f"sunday locksmith {location}",
            f"after hours hvac {location}"
        ]
        
        for keyword in keywords:
            # Search with automatic fallback
            results = self.scraper.search(keyword)
            
            if 'error' not in results:
                # Analyze opportunity
                opportunity = self._analyze_results(keyword, results, location)
                if opportunity['worth_building']:
                    opportunities.append(opportunity)
                    
                    # Scrape top competitor for deeper analysis
                    if results.get('results'):
                        competitor_url = results['results'][0]['url']
                        content = self.scraper.scrape(competitor_url)
                        
                        if content:
                            opportunity['competitor_analysis'] = self._analyze_competitor(content)
        
        # Show stats
        print("\n📊 Scraping Statistics:")
        stats = self.scraper.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return opportunities
    
    def _analyze_results(self, keyword: str, results: Dict, location: str) -> Dict:
        """Analyze search results for opportunity"""
        
        weak_count = 0
        for result in results.get('results', [])[:10]:
            url = result.get('url', '').lower()
            
            # Count weak sites
            weak_domains = ['yelp.com', 'yellowpages.com', 'facebook.com', 
                           'nextdoor.com', 'angi.com', 'thumbtack.com']
            
            if any(domain in url for domain in weak_domains):
                weak_count += 1
        
        # Simple scoring
        worth_building = weak_count >= 3
        
        return {
            'keyword': keyword,
            'location': location,
            'weak_competitors': weak_count,
            'worth_building': worth_building,
            'estimated_revenue': weak_count * 500  # Rough estimate
        }
    
    def _analyze_competitor(self, content: str) -> Dict:
        """Analyze competitor content"""
        
        content_lower = content.lower()
        
        return {
            'word_count': len(content.split()),
            'has_emergency': 'emergency' in content_lower,
            'has_weekend': 'weekend' in content_lower or 'saturday' in content_lower,
            'has_pricing': '$' in content,
            'thin_content': len(content) < 1000
        }


# Test script
if __name__ == "__main__":
    print("🚀 SCRAPING MANAGER TEST")
    print("=" * 60)
    
    # Test services
    manager = ScrapingManager()
    test_results = manager.test_both_services()
    
    print("\n📋 TEST SUMMARY:")
    print(json.dumps(test_results, indent=2))
    
    # Test money finder
    print("\n💰 TESTING MONEY FINDER WITH FALLBACK")
    print("=" * 60)
    
    finder = MoneyFinderWithFallback()
    opportunities = finder.find_opportunities("Birmingham AL")
    
    print(f"\n✅ Found {len(opportunities)} opportunities")
    for opp in opportunities[:3]:
        print(f"\n🎯 {opp['keyword']}")
        print(f"   Weak competitors: {opp['weak_competitors']}/10")
        print(f"   Estimated revenue: ${opp['estimated_revenue']}/mo")