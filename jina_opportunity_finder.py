"""
Jina-Powered Opportunity Finder
Find and validate money-making keywords in real-time
"""
import os
import requests
import json
from datetime import datetime
from typing import Dict, List

class JinaOpportunityFinder:
    def __init__(self):
        self.api_key = os.getenv('JINA_API_KEY')
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
    def search_and_analyze(self, keyword: str, location: str) -> Dict:
        """Search for keyword opportunities and analyze competition"""
        
        # Search Google via Jina
        search_query = f"{keyword} {location}"
        search_url = f"https://s.jina.ai/{search_query}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            search_results = response.json()
            
            # Analyze competition
            competition_analysis = self._analyze_competition(search_results)
            
            # Calculate opportunity score
            opportunity = self._calculate_opportunity(
                keyword=keyword,
                location=location,
                competition=competition_analysis
            )
            
            return opportunity
            
        except Exception as e:
            print(f"Error searching {keyword}: {e}")
            return None
    
    def _analyze_competition(self, search_results: Dict) -> Dict:
        """Analyze how weak the competition is"""
        
        weak_signals = 0
        strong_competitors = 0
        
        # Look for weak signals in top 10
        for result in search_results.get('results', [])[:10]:
            content = result.get('content', '').lower()
            title = result.get('title', '').lower()
            url = result.get('url', '').lower()
            
            # Weak signals (easy to beat)
            if any(weak in url for weak in ['yelp.', 'yellowpages.', 'facebook.', 'nextdoor.']):
                weak_signals += 1
            if len(content) < 500:  # Thin content
                weak_signals += 1
            if 'wordpress.com' in url or 'blogspot.' in url:  # Free blogs
                weak_signals += 1
                
            # Strong signals (harder to beat)
            if any(strong in url for strong in ['plumber', 'hvac', 'roofing', 'contractor']):
                if len(content) > 2000:  # Established sites
                    strong_competitors += 1
        
        return {
            'weak_signals': weak_signals,
            'strong_competitors': strong_competitors,
            'difficulty': 'easy' if weak_signals > 5 else 'medium' if weak_signals > 2 else 'hard'
        }
    
    def _calculate_opportunity(self, keyword: str, location: str, competition: Dict) -> Dict:
        """Calculate if this is worth building NOW"""
        
        # Estimate search volume (you'd use real data in production)
        search_volume = self._estimate_volume(keyword)
        
        # Lead value by service type
        lead_values = {
            'emergency': 200,
            'weekend': 150,
            'after hours': 175,
            '24 hour': 160,
            'sunday': 140,
            'saturday': 130,
            'default': 100
        }
        
        # Calculate lead value
        lead_value = lead_values['default']
        for key, value in lead_values.items():
            if key in keyword.lower():
                lead_value = value
                break
        
        # Time to rank based on competition
        if competition['difficulty'] == 'easy':
            days_to_rank = 14
        elif competition['difficulty'] == 'medium':
            days_to_rank = 30
        else:
            days_to_rank = 60
            
        # Calculate monthly revenue
        clicks_per_month = search_volume * 0.1  # 10% CTR
        monthly_revenue = clicks_per_month * lead_value
        
        # Build decision
        should_build = (
            search_volume > 50 and
            competition['difficulty'] in ['easy', 'medium'] and
            monthly_revenue > 1000 and
            days_to_rank <= 30
        )
        
        return {
            'keyword': keyword,
            'location': location,
            'search_volume': search_volume,
            'competition_difficulty': competition['difficulty'],
            'weak_competitors': competition['weak_signals'],
            'lead_value': lead_value,
            'days_to_rank': days_to_rank,
            'monthly_revenue_potential': monthly_revenue,
            'action': 'BUILD NOW' if should_build else 'SKIP',
            'domain_suggestion': self._generate_domain(keyword, location),
            'build_priority': 'HIGH' if monthly_revenue > 3000 else 'MEDIUM'
        }
    
    def _estimate_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword type"""
        # In production, use real search volume data
        # This is a rough estimate based on keyword patterns
        
        estimates = {
            'emergency': 200,
            '24 hour': 150,
            'weekend': 100,
            'sunday': 80,
            'saturday': 90,
            'after hours': 120,
            'near me': 300,
            'spanish': 150,  # Underserved market!
        }
        
        volume = 50  # Base volume
        for term, add_volume in estimates.items():
            if term in keyword.lower():
                volume += add_volume
                
        return volume
    
    def _generate_domain(self, keyword: str, location: str) -> str:
        """Generate domain name suggestion"""
        # Clean up for domain
        keyword_clean = keyword.lower().replace(' ', '-')
        location_clean = location.lower().split(',')[0].replace(' ', '-')
        
        return f"{keyword_clean}-{location_clean}.com"
    
    def find_weekend_opportunities(self, service: str, cities: List[str]) -> List[Dict]:
        """Find all weekend/after-hours opportunities for a service"""
        
        opportunities = []
        weekend_keywords = [
            f"weekend {service}",
            f"saturday {service}",
            f"sunday {service}",
            f"after hours {service}",
            f"24 hour {service}",
            f"emergency {service} open now",
            f"{service} open late",
            f"{service} available weekends"
        ]
        
        for city in cities:
            for keyword in weekend_keywords:
                opportunity = self.search_and_analyze(keyword, city)
                if opportunity and opportunity['action'] == 'BUILD NOW':
                    opportunities.append(opportunity)
                    
        # Sort by revenue potential
        opportunities.sort(key=lambda x: x['monthly_revenue_potential'], reverse=True)
        return opportunities
    
    def validate_with_real_data(self, url: str) -> Dict:
        """Scrape actual competitor to validate opportunity"""
        
        scrape_url = f"https://r.jina.ai/{url}"
        
        try:
            response = requests.get(scrape_url, headers=self.headers)
            content = response.text
            
            # Analyze what we got
            validation = {
                'content_length': len(content),
                'mentions_weekend': 'weekend' in content.lower() or 'saturday' in content.lower(),
                'mentions_emergency': 'emergency' in content.lower(),
                'has_pricing': '$' in content or 'price' in content.lower(),
                'has_phone': any(char.isdigit() for char in content),
                'weakness_score': 0
            }
            
            # Calculate weakness score
            if validation['content_length'] < 1000:
                validation['weakness_score'] += 3
            if not validation['mentions_weekend']:
                validation['weakness_score'] += 2
            if not validation['has_pricing']:
                validation['weakness_score'] += 1
                
            validation['verdict'] = 'WEAK - ATTACK' if validation['weakness_score'] > 3 else 'STRONG - AVOID'
            
            return validation
            
        except Exception as e:
            return {'error': str(e)}


# Example usage
if __name__ == "__main__":
    finder = JinaOpportunityFinder()
    
    # Find weekend plumber opportunities
    print("🔍 Searching for Weekend Plumber Opportunities...")
    print("=" * 50)
    
    opportunities = finder.find_weekend_opportunities(
        service="plumber",
        cities=["Birmingham AL", "Hoover AL", "Pelham AL", "Vestavia Hills AL"]
    )
    
    for opp in opportunities[:5]:  # Top 5
        print(f"\n💰 OPPORTUNITY: {opp['keyword']} - {opp['location']}")
        print(f"📊 Search Volume: {opp['search_volume']}/month")
        print(f"🎯 Competition: {opp['competition_difficulty']} ({opp['weak_competitors']} weak sites)")
        print(f"💵 Lead Value: ${opp['lead_value']}")
        print(f"⏱️ Rank Time: {opp['days_to_rank']} days")
        print(f"💰 Monthly Revenue: ${opp['monthly_revenue_potential']:,}")
        print(f"🌐 Domain: {opp['domain_suggestion']}")
        print(f"🚀 Action: {opp['action']}")
        print("-" * 40)