"""
BrightData Web Scraper Integration
Fast, reliable web scraping for SEO analysis
"""
import os
import asyncio
from playwright.async_api import async_playwright
import requests
from typing import Dict, List, Optional
import json
import re

class BrightDataScraper:
    def __init__(self):
        # Load BrightData credentials from environment
        self.puppeteer_url = os.getenv('BRIGHTDATA_PUPPETEER_URL')
        self.selenium_url = os.getenv('BRIGHTDATA_SELENIUM_URL')
        self.customer_id = os.getenv('BRIGHTDATA_CUSTOMER_ID')
        
    async def scrape_competitor_data(self, urls: List[str]) -> List[Dict]:
        """Scrape competitor websites for SEO analysis"""
        results = []
        
        async with async_playwright() as p:
            # Connect to BrightData browser
            browser = await p.chromium.connect_over_cdp(self.puppeteer_url)
            
            for url in urls:
                try:
                    page = await browser.new_page()
                    await page.goto(url, wait_until='networkidle')
                    
                    # Extract SEO data
                    data = await self._extract_seo_data(page)
                    data['url'] = url
                    results.append(data)
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    results.append({
                        'url': url,
                        'error': str(e)
                    })
            
            await browser.close()
            
        return results
    
    async def _extract_seo_data(self, page) -> Dict:
        """Extract comprehensive SEO data from a page"""
        
        # Title and meta tags
        title = await page.title()
        meta_description = await page.locator('meta[name="description"]').get_attribute('content') or ''
        h1_text = await page.locator('h1').first.text_content() if await page.locator('h1').count() > 0 else ''
        
        # Content analysis
        content = await page.content()
        text_content = await page.locator('body').text_content()
        word_count = len(text_content.split()) if text_content else 0
        
        # Schema markup
        schema_scripts = await page.locator('script[type="application/ld+json"]').all()
        schema_data = []
        for script in schema_scripts:
            try:
                content = await script.text_content()
                schema_data.append(json.loads(content))
            except:
                pass
        
        # Local SEO signals
        has_google_maps = await page.locator('iframe[src*="google.com/maps"]').count() > 0
        phone_numbers = await self._extract_phone_numbers(page)
        has_nap = await self._check_nap_consistency(page)
        
        # Technical SEO
        page_speed = await self._measure_page_speed(page)
        
        return {
            'title': title,
            'meta_description': meta_description,
            'h1': h1_text,
            'word_count': word_count,
            'schema_markup': schema_data,
            'has_google_maps': has_google_maps,
            'phone_numbers': phone_numbers,
            'has_nap': has_nap,
            'page_speed_score': page_speed,
            'weaknesses': self._identify_weaknesses({
                'title': title,
                'meta_description': meta_description,
                'word_count': word_count,
                'schema_markup': schema_data,
                'has_google_maps': has_google_maps
            })
        }
    
    async def _extract_phone_numbers(self, page) -> List[str]:
        """Extract phone numbers from page"""
        import re
        
        text = await page.locator('body').text_content()
        if not text:
            return []
            
        # Common phone number patterns
        phone_pattern = r'[\d\s\(\)\-\+\.]{10,20}'
        phones = re.findall(phone_pattern, text)
        
        # Clean and validate
        valid_phones = []
        for phone in phones[:5]:  # Limit to 5 numbers
            cleaned = re.sub(r'[^\d]', '', phone)
            if 10 <= len(cleaned) <= 15:
                valid_phones.append(phone.strip())
                
        return valid_phones
    
    async def _check_nap_consistency(self, page) -> bool:
        """Check for Name, Address, Phone consistency"""
        # Look for common NAP containers
        nap_selectors = [
            'address', 
            '[itemtype*="LocalBusiness"]',
            '.contact-info',
            '#contact',
            'footer'
        ]
        
        for selector in nap_selectors:
            if await page.locator(selector).count() > 0:
                return True
                
        return False
    
    async def _measure_page_speed(self, page) -> int:
        """Simple page speed estimation"""
        # This is a simplified version - in production use Lighthouse
        metrics = await page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart
                }
            }
        """)
        
        # Simple scoring (0-100)
        if metrics['loadComplete'] < 1000:
            return 90
        elif metrics['loadComplete'] < 2000:
            return 70
        elif metrics['loadComplete'] < 3000:
            return 50
        else:
            return 30
    
    def _identify_weaknesses(self, data: Dict) -> List[str]:
        """Identify SEO weaknesses we can exploit"""
        weaknesses = []
        
        # Title issues
        if not data['title'] or len(data['title']) < 30:
            weaknesses.append("Weak or missing title tag")
        
        # Meta description
        if not data['meta_description'] or len(data['meta_description']) < 120:
            weaknesses.append("Poor meta description")
        
        # Content
        if data['word_count'] < 500:
            weaknesses.append("Thin content (under 500 words)")
        
        # Schema
        if not data['schema_markup']:
            weaknesses.append("No schema markup")
        
        # Local SEO
        if not data['has_google_maps']:
            weaknesses.append("No Google Maps embed")
            
        return weaknesses
    
    async def find_easy_targets(self, keyword: str, location: str, num_results: int = 10) -> List[Dict]:
        """Find weak competitors for a keyword"""
        
        # First, use Jina to get search results
        search_query = f"{keyword} {location}"
        search_url = f"https://s.jina.ai/{search_query}"
        
        headers = {"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"}
        
        try:
            response = requests.get(search_url, headers=headers)
            search_results = response.json()
            
            # Extract URLs from top results
            urls = []
            for result in search_results.get('results', [])[:num_results]:
                urls.append(result['url'])
            
            # Scrape and analyze each URL
            competitor_data = await self.scrape_competitor_data(urls)
            
            # Score and rank by weakness
            for competitor in competitor_data:
                if 'error' not in competitor:
                    weakness_score = len(competitor.get('weaknesses', []))
                    competitor['weakness_score'] = weakness_score
                    competitor['opportunity_level'] = self._calculate_opportunity(weakness_score)
            
            # Sort by opportunity (highest weakness first)
            competitor_data.sort(key=lambda x: x.get('weakness_score', 0), reverse=True)
            
            return competitor_data
            
        except Exception as e:
            print(f"Error finding targets: {e}")
            return []
    
    def _calculate_opportunity(self, weakness_score: int) -> str:
        """Calculate opportunity level based on weaknesses"""
        if weakness_score >= 4:
            return "🟢 HIGH - Easy to outrank"
        elif weakness_score >= 2:
            return "🟡 MEDIUM - Possible to outrank"
        else:
            return "🔴 LOW - Difficult to outrank"


# Example usage
if __name__ == "__main__":
    scraper = BrightDataScraper()
    
    async def test_scraper():
        print("🔍 Finding Easy SEO Targets...")
        print("=" * 60)
        
        targets = await scraper.find_easy_targets(
            keyword="emergency plumber",
            location="Birmingham AL"
        )
        
        for i, target in enumerate(targets[:5], 1):
            print(f"\n#{i} {target['url']}")
            print(f"Opportunity: {target.get('opportunity_level', 'Unknown')}")
            print(f"Weaknesses Found: {target.get('weakness_score', 0)}")
            
            if 'weaknesses' in target:
                print("Issues to Exploit:")
                for weakness in target['weaknesses']:
                    print(f"  • {weakness}")
            
            print("-" * 40)
    
    # Run the test
    asyncio.run(test_scraper())