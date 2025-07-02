"""
Jina Money Finder - Find opportunities you can monetize TODAY
Uses Jina's search AND scraping to validate real opportunities
"""
import os
import requests
from typing import Dict, List, Tuple
from datetime import datetime
import json

class JinaMoneyFinder:
    def __init__(self):
        self.api_key = os.getenv('JINA_API_KEY')
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # High-value services that NEED weekend/emergency coverage
        self.money_services = [
            'plumber', 'electrician', 'hvac', 'ac repair', 'heating',
            'locksmith', 'garage door', 'water heater', 'sewer',
            'roofing', 'appliance repair', 'pest control'
        ]
        
        # Money modifiers - people NEED help NOW
        self.money_modifiers = [
            'emergency', 'weekend', 'sunday', 'saturday', 'after hours',
            '24 hour', 'same day', 'urgent', 'open now', 'today'
        ]
        
        # Lead values by urgency
        self.lead_values = {
            'emergency': 200,
            '24 hour': 175,
            'sunday': 160,
            'weekend': 150,
            'saturday': 140,
            'after hours': 130,
            'same day': 120,
            'today': 110,
            'urgent': 100,
            'open now': 90
        }
    
    def find_instant_money(self, location: str) -> List[Dict]:
        """Find opportunities you can monetize in 14 days"""
        
        print(f"💰 FINDING INSTANT MONEY OPPORTUNITIES IN {location.upper()}")
        print("=" * 60)
        
        opportunities = []
        
        for service in self.money_services[:5]:  # Top 5 services
            for modifier in self.money_modifiers[:3]:  # Top 3 modifiers
                keyword = f"{modifier} {service} {location}"
                
                # Step 1: Search to see what's ranking
                search_data = self._search_competitors(keyword)
                
                # Step 2: Analyze if it's worth building
                if self._is_money_opportunity(search_data):
                    
                    # Step 3: Validate with real numbers
                    opportunity = self._validate_opportunity(
                        keyword=keyword,
                        modifier=modifier,
                        service=service,
                        location=location,
                        search_data=search_data
                    )
                    
                    if opportunity['action'] == 'BUILD NOW':
                        opportunities.append(opportunity)
                        print(f"✅ FOUND: {keyword} - ${opportunity['monthly_revenue']}/mo")
        
        # Sort by fastest to profit
        opportunities.sort(key=lambda x: (x['days_to_profit'], -x['monthly_revenue']))
        
        return opportunities
    
    def _search_competitors(self, keyword: str) -> Dict:
        """Use Jina to search and analyze competition"""
        
        search_url = f"https://s.jina.ai/{keyword}"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=30)
            data = response.json()
            
            # Analyze top 10 results
            weak_count = 0
            has_dedicated_site = False
            
            for i, result in enumerate(data.get('results', [])[:10]):
                url = result.get('url', '').lower()
                content = result.get('content', '')
                
                # Check for weak sites
                if any(weak in url for weak in ['yelp.', 'yellowpages.', 'facebook.', 'nextdoor.']):
                    weak_count += 1
                
                # Check if anyone has a dedicated weekend/emergency site
                if any(mod in url for mod in ['weekend', 'emergency', 'sunday', '24hour']):
                    has_dedicated_site = True
                
                # Thin content = opportunity
                if len(content) < 500:
                    weak_count += 1
            
            return {
                'weak_competitors': weak_count,
                'has_dedicated_site': has_dedicated_site,
                'top_results': data.get('results', [])[:5]
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            return {'weak_competitors': 0, 'has_dedicated_site': True}
    
    def _is_money_opportunity(self, search_data: Dict) -> bool:
        """Quick check if worth pursuing"""
        
        return (
            search_data['weak_competitors'] >= 3 and
            not search_data['has_dedicated_site']
        )
    
    def _validate_opportunity(self, keyword: str, modifier: str, service: str, 
                            location: str, search_data: Dict) -> Dict:
        """Validate with real numbers and competitor analysis"""
        
        # Estimate search volume (in production, use real data)
        base_searches = {
            'plumber': 500,
            'electrician': 400,
            'hvac': 450,
            'ac repair': 600,
            'locksmith': 300,
            'garage door': 250,
            'water heater': 200,
            'roofing': 350
        }
        
        # Modifier multipliers
        modifier_multipliers = {
            'emergency': 0.3,
            'weekend': 0.25,
            'sunday': 0.15,
            'saturday': 0.15,
            '24 hour': 0.2,
            'after hours': 0.18
        }
        
        # Calculate searches
        base = base_searches.get(service, 200)
        multiplier = modifier_multipliers.get(modifier, 0.1)
        monthly_searches = int(base * multiplier)
        
        # Get lead value
        lead_value = self.lead_values.get(modifier, 100)
        
        # Calculate revenue
        clicks = monthly_searches * 0.1  # 10% CTR for low competition
        monthly_revenue = int(clicks * lead_value)
        
        # Days to profit based on competition
        if search_data['weak_competitors'] >= 5:
            days_to_profit = 14
            difficulty = 'EASY'
        elif search_data['weak_competitors'] >= 3:
            days_to_profit = 21
            difficulty = 'MEDIUM'
        else:
            days_to_profit = 30
            difficulty = 'HARD'
        
        # Decide action
        if monthly_revenue > 1500 and days_to_profit <= 21:
            action = 'BUILD NOW'
        elif monthly_revenue > 3000 and days_to_profit <= 30:
            action = 'BUILD NOW'
        else:
            action = 'SKIP'
        
        # Get competitor weaknesses
        weaknesses = self._analyze_competitor_weaknesses(search_data['top_results'])
        
        return {
            'keyword': keyword,
            'modifier': modifier,
            'service': service,
            'location': location,
            'monthly_searches': monthly_searches,
            'lead_value': lead_value,
            'monthly_revenue': monthly_revenue,
            'days_to_profit': days_to_profit,
            'difficulty': difficulty,
            'action': action,
            'weak_competitors': search_data['weak_competitors'],
            'competitor_weaknesses': weaknesses,
            'domain_suggestion': self._generate_domain(modifier, service, location),
            'action_plan': self._create_instant_action_plan(keyword, monthly_revenue, lead_value)
        }
    
    def _analyze_competitor_weaknesses(self, results: List[Dict]) -> List[str]:
        """Find specific weaknesses to exploit"""
        
        weaknesses = []
        
        for result in results[:3]:
            content = result.get('content', '').lower()
            
            # Check for missing elements
            if 'open saturday' not in content and 'open sunday' not in content:
                weaknesses.append("No weekend hours mentioned")
            
            if '$' not in content and 'price' not in content:
                weaknesses.append("No pricing transparency")
            
            if 'emergency' in result.get('url', '') and 'license' not in content:
                weaknesses.append("No licensing info")
            
            if len(content) < 800:
                weaknesses.append("Thin content - easy to outrank")
        
        # Remove duplicates
        return list(set(weaknesses))[:3]
    
    def _generate_domain(self, modifier: str, service: str, location: str) -> str:
        """Generate money-making domain"""
        
        # Clean location
        city = location.lower().split(',')[0].strip().replace(' ', '')
        
        # Money domains
        if modifier == 'emergency':
            return f"{city}{service}emergency.com"
        elif modifier in ['weekend', 'saturday', 'sunday']:
            return f"weekend{service}{city}.com"
        elif modifier == '24 hour':
            return f"24hour{service}{city}.com"
        else:
            return f"{modifier.replace(' ', '')}{service}{city}.com"
    
    def _create_instant_action_plan(self, keyword: str, revenue: int, lead_value: int) -> Dict:
        """14-day plan to profit"""
        
        return {
            'week_1': [
                f"Day 1: Register domain (targeting '{keyword}')",
                "Day 2: Create 5-page site focused on availability",
                "Day 3-4: Add local business schema + Google Maps",
                "Day 5-7: Build 20 local citations"
            ],
            'week_2': [
                "Day 8-10: Create 3 blog posts about emergency service",
                "Day 11-12: Contact 5 local contractors",
                f"Day 13: Set up call tracking (leads worth ${lead_value})",
                f"Day 14: First leads arriving! (${revenue}/month potential)"
            ],
            'monetization': {
                'option_1': f"Sell leads: ${lead_value} per call",
                'option_2': f"Rent site: ${int(revenue * 0.5)}/month",
                'option_3': f"Flip after 3 months: ${revenue * 6}"
            }
        }
    
    def scrape_competitor_intel(self, url: str) -> Dict:
        """Use Jina to scrape competitor intelligence"""
        
        scrape_url = f"https://r.jina.ai/{url}"
        
        try:
            response = requests.get(scrape_url, headers=self.headers, timeout=30)
            content = response.text
            
            # Extract intelligence
            intel = {
                'url': url,
                'content_length': len(content),
                'has_prices': '$' in content or 'price' in content.lower(),
                'mentions_emergency': 'emergency' in content.lower(),
                'mentions_weekend': any(day in content.lower() for day in ['weekend', 'saturday', 'sunday']),
                'has_phone': self._extract_phone(content),
                'service_areas': self._extract_areas(content),
                'services_offered': self._extract_services(content)
            }
            
            return intel
            
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_phone(self, content: str) -> str:
        """Extract phone number from content"""
        import re
        
        # Common phone patterns
        patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
            r'\d{10}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group()
        
        return None
    
    def _extract_areas(self, content: str) -> List[str]:
        """Extract service areas mentioned"""
        
        # Common area indicators
        area_keywords = ['serving', 'service area', 'we serve', 'areas:', 'locations:']
        areas = []
        
        content_lower = content.lower()
        for keyword in area_keywords:
            if keyword in content_lower:
                # Extract next 100 chars after keyword
                start = content_lower.find(keyword)
                snippet = content[start:start+200]
                
                # Look for city names (simplified)
                words = snippet.split()
                for word in words:
                    if word[0].isupper() and len(word) > 3:
                        areas.append(word)
        
        return list(set(areas))[:5]
    
    def _extract_services(self, content: str) -> List[str]:
        """Extract services offered"""
        
        services = []
        service_keywords = [
            'repair', 'installation', 'maintenance', 'emergency',
            'replacement', 'inspection', 'cleaning', 'service'
        ]
        
        for keyword in service_keywords:
            if keyword in content.lower():
                services.append(keyword)
        
        return services
    
    def generate_opportunity_report(self, opportunities: List[Dict]) -> str:
        """Generate actionable report"""
        
        report = []
        report.append("💰 INSTANT MONEY OPPORTUNITIES REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"Opportunities Found: {len(opportunities)}")
        
        total_revenue = sum(o['monthly_revenue'] for o in opportunities)
        report.append(f"Total Monthly Revenue Potential: ${total_revenue:,}")
        
        report.append("\n🎯 TOP 5 OPPORTUNITIES TO BUILD NOW:")
        report.append("-" * 60)
        
        for i, opp in enumerate(opportunities[:5], 1):
            report.append(f"\n#{i} {opp['keyword'].upper()}")
            report.append(f"📊 Searches: {opp['monthly_searches']}/month")
            report.append(f"💰 Revenue: ${opp['monthly_revenue']:,}/month")
            report.append(f"⏱️ Profit in: {opp['days_to_profit']} days")
            report.append(f"🎯 Difficulty: {opp['difficulty']}")
            report.append(f"🌐 Domain: {opp['domain_suggestion']}")
            
            report.append("\n🔧 Quick Action Plan:")
            for task in opp['action_plan']['week_1'][:2]:
                report.append(f"  • {task}")
            
            report.append("\n💵 Monetization:")
            for option, details in opp['action_plan']['monetization'].items():
                report.append(f"  • {details}")
            
            report.append("\n" + "-" * 40)
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    finder = JinaMoneyFinder()
    
    # Find instant money opportunities
    opportunities = finder.find_instant_money("Birmingham AL")
    
    # Generate report
    report = finder.generate_opportunity_report(opportunities)
    print(report)
    
    # Save opportunities
    with open('money_opportunities.json', 'w') as f:
        json.dump(opportunities, f, indent=2)
    
    print("\n✅ Saved detailed opportunities to money_opportunities.json")
    
    # Test competitor scraping
    print("\n🔍 Testing Competitor Intelligence:")
    intel = finder.scrape_competitor_intel("https://example-plumber.com")
    print(json.dumps(intel, indent=2))