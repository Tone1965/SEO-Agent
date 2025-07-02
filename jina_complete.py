"""
Jina Complete Integration - Search, Scrape, Analyze, Monetize
Uses ALL of Jina's capabilities for finding and validating opportunities
"""
import os
import requests
from typing import Dict, List, Optional
import json
import re
from datetime import datetime

class JinaComplete:
    def __init__(self):
        self.api_key = os.getenv('JINA_API_KEY')
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
    def search(self, query: str) -> Dict:
        """Search Google and get actual content from results"""
        
        url = f"https://s.jina.ai/{query}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            return response.json()
        except Exception as e:
            print(f"Search error: {e}")
            return {}
    
    def scrape(self, url: str) -> str:
        """Scrape any URL and get clean content"""
        
        scrape_url = f"https://r.jina.ai/{url}"
        
        try:
            response = requests.get(scrape_url, headers=self.headers, timeout=30)
            return response.text
        except Exception as e:
            print(f"Scrape error: {e}")
            return ""
    
    def find_money_keywords(self, location: str) -> List[Dict]:
        """Find ALL money-making keywords in a location"""
        
        print(f"🔍 JINA KEYWORD RESEARCH FOR {location.upper()}")
        print("=" * 60)
        
        # Services people NEED urgently
        urgent_services = [
            'plumber', 'electrician', 'ac repair', 'heating repair',
            'locksmith', 'garage door repair', 'water heater',
            'sewer repair', 'gas leak', 'appliance repair'
        ]
        
        # When they NEED it NOW
        urgent_modifiers = [
            'emergency', 'open now', 'today', 'tonight',
            'weekend', 'sunday', 'saturday', 'after hours',
            '24 hour', 'same day', 'urgent', 'asap'
        ]
        
        # Language variations (underserved markets!)
        languages = ['', 'spanish', 'se habla español']
        
        opportunities = []
        
        for service in urgent_services:
            for modifier in urgent_modifiers[:5]:  # Top 5 modifiers
                for lang in languages:
                    # Build search query
                    if lang:
                        keyword = f"{modifier} {service} {location} {lang}"
                    else:
                        keyword = f"{modifier} {service} {location}"
                    
                    # Search with Jina
                    results = self.search(keyword)
                    
                    # Analyze opportunity
                    opportunity = self._analyze_opportunity(keyword, results, location)
                    
                    if opportunity['worth_building']:
                        opportunities.append(opportunity)
                        print(f"✅ {keyword}: ${opportunity['monthly_revenue']}/mo")
        
        return opportunities
    
    def _analyze_opportunity(self, keyword: str, search_results: Dict, location: str) -> Dict:
        """Analyze if keyword is worth targeting"""
        
        # Count weak competitors
        weak_sites = 0
        strong_sites = 0
        total_results = 0
        
        for result in search_results.get('results', [])[:10]:
            total_results += 1
            url = result.get('url', '').lower()
            content = result.get('content', '')
            
            # Weak sites we can beat
            if any(site in url for site in ['yelp.com', 'yellowpages.com', 
                                             'facebook.com', 'nextdoor.com',
                                             'angi.com', 'thumbtack.com']):
                weak_sites += 1
            
            # Thin content
            elif len(content) < 500:
                weak_sites += 1
            
            # Strong competitors
            elif any(indicator in url for indicator in ['plumber', 'electric', 'hvac', 'contractor']):
                if len(content) > 1500:
                    strong_sites += 1
        
        # Extract service and modifier
        parts = keyword.lower().split()
        modifier = parts[0] if parts[0] in ['emergency', 'weekend', 'sunday', 'saturday', 
                                            '24', 'after', 'same', 'urgent'] else 'standard'
        
        # Calculate metrics
        competition_score = (weak_sites / max(total_results, 1)) * 100
        difficulty = 'EASY' if competition_score > 50 else 'MEDIUM' if competition_score > 30 else 'HARD'
        
        # Estimate search volume (would use real data in production)
        searches = self._estimate_searches(keyword)
        
        # Lead values by urgency
        lead_values = {
            'emergency': 200,
            '24': 175,
            'sunday': 160,
            'weekend': 150,
            'saturday': 140,
            'after': 130,
            'same': 120,
            'urgent': 110,
            'standard': 80
        }
        
        lead_value = lead_values.get(modifier, 100)
        
        # Calculate revenue
        clicks = searches * 0.1  # 10% CTR
        monthly_revenue = int(clicks * lead_value)
        
        # Ranking time based on competition
        if difficulty == 'EASY':
            days_to_rank = 14
        elif difficulty == 'MEDIUM':
            days_to_rank = 30
        else:
            days_to_rank = 60
        
        # Decision
        worth_building = (
            monthly_revenue > 1500 and
            days_to_rank <= 30 and
            weak_sites >= 3
        )
        
        return {
            'keyword': keyword,
            'location': location,
            'monthly_searches': searches,
            'competition_score': competition_score,
            'difficulty': difficulty,
            'weak_sites': weak_sites,
            'strong_sites': strong_sites,
            'lead_value': lead_value,
            'monthly_revenue': monthly_revenue,
            'days_to_rank': days_to_rank,
            'worth_building': worth_building,
            'domain': self._suggest_domain(keyword, location)
        }
    
    def _estimate_searches(self, keyword: str) -> int:
        """Estimate search volume based on keyword type"""
        
        # Base estimates for service + modifier combos
        keyword_lower = keyword.lower()
        
        base = 50  # minimum
        
        # Service multipliers
        if 'plumber' in keyword_lower: base += 200
        elif 'electrician' in keyword_lower: base += 150
        elif 'ac' in keyword_lower or 'hvac' in keyword_lower: base += 250
        elif 'locksmith' in keyword_lower: base += 100
        elif 'water heater' in keyword_lower: base += 80
        
        # Urgency multipliers
        if 'emergency' in keyword_lower: base *= 1.5
        elif 'weekend' in keyword_lower: base *= 1.3
        elif '24 hour' in keyword_lower: base *= 1.4
        elif 'today' in keyword_lower: base *= 1.2
        
        # Spanish market bonus
        if 'spanish' in keyword_lower or 'español' in keyword_lower:
            base *= 0.7  # Less volume but ZERO competition usually
        
        return int(base)
    
    def _suggest_domain(self, keyword: str, location: str) -> str:
        """Suggest money-making domain"""
        
        # Clean location
        city = location.lower().split(',')[0].strip().replace(' ', '-')
        
        # Extract key parts
        parts = keyword.lower().split()
        
        # Build domain
        if 'emergency' in parts:
            service = [p for p in parts if p in ['plumber', 'electrician', 'ac', 'hvac', 'locksmith']][0]
            return f"{city}-emergency-{service}.com"
        elif 'weekend' in parts:
            service = [p for p in parts if p in ['plumber', 'electrician', 'ac', 'hvac', 'locksmith']][0]
            return f"weekend-{service}-{city}.com"
        else:
            # Generic format
            clean_keyword = '-'.join(parts[:3])
            return f"{clean_keyword}-{city}.com"
    
    def analyze_competitor(self, url: str) -> Dict:
        """Deep competitor analysis using Jina scraping"""
        
        print(f"\n🔍 Analyzing competitor: {url}")
        
        # Scrape the site
        content = self.scrape(url)
        
        if not content:
            return {'error': 'Could not scrape site'}
        
        # Extract intelligence
        analysis = {
            'url': url,
            'content_length': len(content),
            'word_count': len(content.split()),
            
            # Business info
            'phone_numbers': self._extract_phones(content),
            'email_addresses': self._extract_emails(content),
            'business_hours': self._extract_hours(content),
            'service_areas': self._extract_locations(content),
            
            # SEO elements
            'has_emergency_keywords': any(kw in content.lower() for kw in 
                                         ['emergency', '24 hour', 'urgent', 'same day']),
            'has_weekend_keywords': any(kw in content.lower() for kw in 
                                       ['weekend', 'saturday', 'sunday']),
            'mentions_pricing': '$' in content or 'price' in content.lower(),
            'has_testimonials': any(kw in content.lower() for kw in 
                                   ['review', 'testimonial', 'customer said', 'client said']),
            
            # Weaknesses to exploit
            'weaknesses': self._identify_weaknesses(content),
            
            # Opportunities
            'missing_keywords': self._find_missing_keywords(content),
            'content_gaps': self._find_content_gaps(content)
        }
        
        return analysis
    
    def _extract_phones(self, content: str) -> List[str]:
        """Extract all phone numbers"""
        
        patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
            r'1[-.\s]?\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            phones.extend(matches)
        
        return list(set(phones))[:3]
    
    def _extract_emails(self, content: str) -> List[str]:
        """Extract email addresses"""
        
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, content)
        return list(set(emails))[:3]
    
    def _extract_hours(self, content: str) -> Dict:
        """Extract business hours"""
        
        hours = {
            'mentions_24_7': '24/7' in content or '24 hour' in content.lower(),
            'mentions_weekend': 'weekend' in content.lower() or 'saturday' in content.lower(),
            'mentions_emergency': 'emergency' in content.lower()
        }
        
        # Look for hour patterns
        time_pattern = r'\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)'
        times = re.findall(time_pattern, content)
        
        if times:
            hours['has_specific_hours'] = True
            hours['hours_found'] = times[:4]
        else:
            hours['has_specific_hours'] = False
        
        return hours
    
    def _extract_locations(self, content: str) -> List[str]:
        """Extract service areas mentioned"""
        
        # Look for location patterns
        locations = []
        
        # Common patterns
        patterns = [
            r'serving\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'service\s+area[s]?:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'we\s+serve\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            locations.extend(matches)
        
        # Also look for city names (simplified)
        words = content.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                # Check if followed by state abbreviation
                if i < len(words) - 1 and len(words[i+1]) == 2 and words[i+1].isupper():
                    locations.append(f"{word} {words[i+1]}")
        
        return list(set(locations))[:10]
    
    def _identify_weaknesses(self, content: str) -> List[str]:
        """Identify specific weaknesses to exploit"""
        
        weaknesses = []
        
        # Content weaknesses
        if len(content) < 500:
            weaknesses.append("Very thin content - easy to outrank")
        elif len(content) < 1000:
            weaknesses.append("Thin content - can be beaten with comprehensive page")
        
        # Missing urgency keywords
        if 'emergency' not in content.lower():
            weaknesses.append("No emergency service mentioned")
        
        if not any(day in content.lower() for day in ['saturday', 'sunday', 'weekend']):
            weaknesses.append("No weekend availability mentioned")
        
        # Missing trust signals
        if not any(word in content.lower() for word in ['license', 'insured', 'certified']):
            weaknesses.append("No licensing/insurance mentioned")
        
        if '$' not in content and 'price' not in content.lower():
            weaknesses.append("No pricing transparency")
        
        # Missing local SEO
        if 'near me' not in content.lower():
            weaknesses.append("Not optimized for 'near me' searches")
        
        # No reviews/testimonials
        if not any(word in content.lower() for word in ['review', 'testimonial', 'customer']):
            weaknesses.append("No social proof/reviews")
        
        return weaknesses
    
    def _find_missing_keywords(self, content: str) -> List[str]:
        """Find profitable keywords they're missing"""
        
        content_lower = content.lower()
        missing = []
        
        # High-value keywords they should have
        valuable_keywords = [
            'emergency plumber open now',
            'same day service',
            '24 hour emergency',
            'weekend plumber near me',
            'sunday plumber',
            'after hours plumber',
            'plumber open late',
            'spanish speaking plumber',
            'plomero cerca de mi'
        ]
        
        for keyword in valuable_keywords:
            if keyword not in content_lower:
                missing.append(keyword)
        
        return missing[:5]
    
    def _find_content_gaps(self, content: str) -> List[str]:
        """Find content they should have but don't"""
        
        gaps = []
        content_lower = content.lower()
        
        # Essential pages/content
        if 'emergency' not in content_lower:
            gaps.append("No emergency service page")
        
        if 'pricing' not in content_lower and 'cost' not in content_lower:
            gaps.append("No pricing/cost information")
        
        if 'service area' not in content_lower:
            gaps.append("No clear service area page")
        
        if not re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', content):
            gaps.append("No phone number prominently displayed")
        
        if 'faq' not in content_lower and 'question' not in content_lower:
            gaps.append("No FAQ section")
        
        return gaps
    
    def generate_attack_plan(self, competitor_analysis: Dict, keyword: str) -> Dict:
        """Generate plan to outrank competitor"""
        
        weaknesses = competitor_analysis.get('weaknesses', [])
        missing_keywords = competitor_analysis.get('missing_keywords', [])
        
        plan = {
            'target_url': competitor_analysis['url'],
            'our_advantages': [],
            'content_strategy': [],
            'quick_wins': []
        }
        
        # Build advantages based on their weaknesses
        if 'Very thin content' in str(weaknesses):
            plan['our_advantages'].append("Create 2000+ word comprehensive guide")
            plan['content_strategy'].append("Write detailed service pages with FAQs")
        
        if 'No emergency service mentioned' in weaknesses:
            plan['our_advantages'].append("Focus entire site on emergency availability")
            plan['quick_wins'].append("Domain: emergency-[service]-[city].com")
        
        if 'No weekend availability mentioned' in weaknesses:
            plan['our_advantages'].append("Highlight weekend/Sunday availability")
            plan['quick_wins'].append("Title tags: 'Open Weekends & Sundays'")
        
        if 'No pricing transparency' in weaknesses:
            plan['our_advantages'].append("Add clear pricing table")
            plan['content_strategy'].append("Create pricing calculator")
        
        # Use their missing keywords
        if missing_keywords:
            plan['content_strategy'].append(f"Target keywords: {', '.join(missing_keywords[:3])}")
        
        # Quick action items
        plan['14_day_plan'] = [
            f"Day 1: Register domain targeting '{keyword}'",
            "Day 2-3: Create 5 pages addressing their weaknesses",
            "Day 4-5: Add all missing keywords to content",
            "Day 6-7: Build better local citations",
            "Day 8-10: Create content they don't have",
            "Day 11-14: Monitor rankings and adjust"
        ]
        
        return plan


# Example usage
if __name__ == "__main__":
    jina = JinaComplete()
    
    print("💰 JINA COMPLETE MONEY FINDER")
    print("=" * 60)
    
    # 1. Find money keywords
    opportunities = jina.find_money_keywords("Birmingham AL")
    
    print(f"\n📊 Found {len(opportunities)} opportunities")
    
    # 2. Analyze top opportunity
    if opportunities:
        best = opportunities[0]
        print(f"\n🎯 BEST OPPORTUNITY: {best['keyword']}")
        print(f"Revenue: ${best['monthly_revenue']}/month")
        print(f"Domain: {best['domain']}")
        
        # 3. Analyze a competitor
        print("\n🔍 Analyzing top competitor...")
        
        # Search for the keyword to get competitor
        results = jina.search(best['keyword'])
        if results.get('results'):
            competitor_url = results['results'][0]['url']
            
            # Deep analysis
            analysis = jina.analyze_competitor(competitor_url)
            
            print(f"\n📊 COMPETITOR ANALYSIS: {competitor_url}")
            print(f"Weaknesses found: {len(analysis['weaknesses'])}")
            for weakness in analysis['weaknesses'][:3]:
                print(f"  • {weakness}")
            
            # 4. Generate attack plan
            attack_plan = jina.generate_attack_plan(analysis, best['keyword'])
            
            print(f"\n⚔️ ATTACK PLAN:")
            for advantage in attack_plan['our_advantages']:
                print(f"  ✓ {advantage}")
            
            print(f"\n📅 14-DAY EXECUTION:")
            for day_task in attack_plan['14_day_plan'][:3]:
                print(f"  {day_task}")
    
    # Save everything
    report = {
        'opportunities': opportunities[:10],
        'generated': datetime.now().isoformat()
    }
    
    with open('jina_opportunities.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Full report saved to jina_opportunities.json")