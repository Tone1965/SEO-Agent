"""
BrightData Simple Web Scraper
No Playwright/Selenium needed - uses direct API
"""
import os
import requests
from typing import Dict, List
import json
from urllib.parse import quote

class BrightDataSimple:
    def __init__(self):
        self.customer_id = os.getenv('BRIGHTDATA_CUSTOMER_ID')
        self.username = os.getenv('BRIGHTDATA_USERNAME')
        self.password = os.getenv('BRIGHTDATA_PASSWORD')
        self.host = os.getenv('BRIGHTDATA_HOST')
        
    def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL using BrightData proxy"""
        
        # BrightData proxy configuration
        proxy = {
            'http': f'http://{self.username}:{self.password}@{self.host}:22225',
            'https': f'http://{self.username}:{self.password}@{self.host}:22225'
        }
        
        try:
            # Make request through BrightData proxy
            response = requests.get(url, proxies=proxy, timeout=30)
            
            # Extract basic SEO data from HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title = soup.find('title')
            title_text = title.text if title else ''
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # H1 tags
            h1_tags = soup.find_all('h1')
            h1_texts = [h1.text.strip() for h1 in h1_tags]
            
            # Word count
            text = soup.get_text()
            word_count = len(text.split())
            
            # Phone numbers (simple pattern)
            import re
            phone_pattern = r'[\d\s\(\)\-\+\.]{10,20}'
            phones = re.findall(phone_pattern, text)[:3]
            
            # Schema markup
            schema_scripts = soup.find_all('script', type='application/ld+json')
            has_schema = len(schema_scripts) > 0
            
            # Identify weaknesses
            weaknesses = []
            if len(title_text) < 30:
                weaknesses.append("Short or missing title")
            if len(description) < 120:
                weaknesses.append("Weak meta description")
            if word_count < 500:
                weaknesses.append("Thin content")
            if not h1_tags:
                weaknesses.append("No H1 tags")
            if not has_schema:
                weaknesses.append("No schema markup")
            
            return {
                'url': url,
                'success': True,
                'title': title_text,
                'meta_description': description,
                'h1_tags': h1_texts,
                'word_count': word_count,
                'phone_numbers': phones,
                'has_schema': has_schema,
                'weaknesses': weaknesses,
                'weakness_score': len(weaknesses),
                'opportunity': '🟢 HIGH' if len(weaknesses) >= 3 else '🟡 MEDIUM' if len(weaknesses) >= 2 else '🔴 LOW'
            }
            
        except Exception as e:
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }
    
    def find_weak_competitors(self, keyword: str, location: str) -> List[Dict]:
        """Find competitors with weak SEO"""
        
        # First get search results from Jina
        jina_key = os.getenv('JINA_API_KEY')
        if not jina_key:
            print("❌ Jina API key not set!")
            return []
        
        search_query = f"{keyword} {location}"
        search_url = f"https://s.jina.ai/{quote(search_query)}"
        
        headers = {"Authorization": f"Bearer {jina_key}"}
        
        try:
            # Get search results
            response = requests.get(search_url, headers=headers, timeout=30)
            data = response.json()
            
            competitors = []
            
            # Analyze top 10 results
            for result in data.get('results', [])[:10]:
                url = result.get('url', '')
                if url:
                    print(f"Analyzing: {url}")
                    competitor_data = self.scrape_url(url)
                    competitors.append(competitor_data)
            
            # Sort by weakness (most weak first)
            competitors.sort(key=lambda x: x.get('weakness_score', 0), reverse=True)
            
            return competitors
            
        except Exception as e:
            print(f"Error: {e}")
            return []


# Simplified tester that doesn't need async
def test_brightdata():
    """Test BrightData scraping"""
    scraper = BrightDataSimple()
    
    print("🔍 Testing BrightData Scraper")
    print("=" * 60)
    
    # Test single URL scrape
    test_url = "https://example.com"
    result = scraper.scrape_url(test_url)
    
    if result['success']:
        print(f"✅ Successfully scraped {test_url}")
        print(f"Title: {result['title']}")
        print(f"Word Count: {result['word_count']}")
        print(f"Weaknesses: {len(result['weaknesses'])}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("🎯 Finding Weak Competitors")
    print("=" * 60)
    
    # Find weak competitors
    competitors = scraper.find_weak_competitors(
        keyword="emergency plumber",
        location="Birmingham AL"
    )
    
    for i, comp in enumerate(competitors[:5], 1):
        if comp['success']:
            print(f"\n#{i} {comp['url']}")
            print(f"Opportunity: {comp['opportunity']}")
            print(f"Weaknesses ({comp['weakness_score']}):")
            for weakness in comp['weaknesses']:
                print(f"  • {weakness}")
        else:
            print(f"\n#{i} Failed: {comp['url']}")


if __name__ == "__main__":
    test_brightdata()