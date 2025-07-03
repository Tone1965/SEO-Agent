"""
Data Coordinator - Manages live data flow from Jina/BrightData to all agents
Ensures every agent gets real market data, not templates
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Import data sources
from jina_complete import JinaComplete
from scraping_manager import ScrapingManager

logger = logging.getLogger(__name__)

@dataclass
class LiveMarketData:
    """Structured market data for agent consumption"""
    keyword: str
    location: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Search Results
    serp_results: List[Dict] = field(default_factory=list)
    competitor_urls: List[str] = field(default_factory=list)
    
    # Competitor Analysis
    competitor_data: List[Dict] = field(default_factory=list)
    weak_competitors: List[Dict] = field(default_factory=list)
    strong_competitors: List[Dict] = field(default_factory=list)
    
    # Market Insights
    market_gaps: List[str] = field(default_factory=list)
    opportunity_score: float = 0.0
    difficulty_level: str = "MEDIUM"
    
    # Keywords & SEO
    related_keywords: List[str] = field(default_factory=list)
    search_volume_estimate: int = 0
    commercial_intent: bool = True
    
    # Content Opportunities
    content_gaps: List[str] = field(default_factory=list)
    missing_topics: List[str] = field(default_factory=list)
    questions_to_answer: List[str] = field(default_factory=list)
    
    # Technical Data
    avg_page_speed: float = 0.0
    mobile_friendly_ratio: float = 0.0
    schema_usage: Dict[str, int] = field(default_factory=dict)
    
    # Revenue Potential
    estimated_cpc: float = 0.0
    lead_value: float = 0.0
    monthly_revenue_potential: float = 0.0

class DataCoordinator:
    """Coordinates data flow from scrapers to all agents"""
    
    def __init__(self):
        self.jina = JinaComplete()
        self.scraper = ScrapingManager()
        self._cache = {}
        
    async def gather_live_data(self, keyword: str, location: str) -> LiveMarketData:
        """Gather comprehensive live data for all agents"""
        logger.info(f"Gathering live data for: {keyword} in {location}")
        
        # Initialize data structure
        market_data = LiveMarketData(keyword=keyword, location=location)
        
        # 1. Get SERP results
        search_query = f"{keyword} {location}"
        serp_data = await self._get_serp_data(search_query)
        
        if serp_data:
            market_data.serp_results = serp_data.get('results', [])
            market_data.competitor_urls = [r.get('url') for r in market_data.serp_results[:10]]
            
        # 2. Analyze competitors
        await self._analyze_competitors(market_data)
        
        # 3. Find market gaps
        self._identify_market_gaps(market_data)
        
        # 4. Calculate opportunity metrics
        self._calculate_opportunity_metrics(market_data)
        
        # 5. Get related keywords
        await self._get_related_keywords(market_data)
        
        # 6. Identify content opportunities
        self._find_content_opportunities(market_data)
        
        # 7. Analyze technical aspects
        await self._analyze_technical_factors(market_data)
        
        # 8. Calculate revenue potential
        self._calculate_revenue_potential(market_data)
        
        logger.info(f"Data gathering complete. Opportunity score: {market_data.opportunity_score}")
        return market_data
    
    async def _get_serp_data(self, query: str) -> Optional[Dict]:
        """Get search engine results"""
        try:
            # Try Jina first
            results = self.jina.search(query)
            if results and 'error' not in results:
                return results
            
            # Fallback to scraper
            results = self.scraper.search(query)
            return results if results and 'error' not in results else None
            
        except Exception as e:
            logger.error(f"Error getting SERP data: {e}")
            return None
    
    async def _analyze_competitors(self, market_data: LiveMarketData):
        """Analyze competitor strengths and weaknesses"""
        weak_indicators = [
            'yelp.com', 'yellowpages.com', 'facebook.com', 'nextdoor.com',
            'angi.com', 'thumbtack.com', 'manta.com', 'citysearch.com'
        ]
        
        for i, result in enumerate(market_data.serp_results[:10]):
            url = result.get('url', '').lower()
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            competitor_info = {
                'rank': i + 1,
                'url': url,
                'title': title,
                'snippet': snippet,
                'weaknesses': [],
                'strengths': []
            }
            
            # Check for weak signals
            if any(domain in url for domain in weak_indicators):
                competitor_info['weaknesses'].append('Directory listing, not dedicated site')
                market_data.weak_competitors.append(competitor_info)
            else:
                # Analyze dedicated sites
                if len(title) < 35:
                    competitor_info['weaknesses'].append('Poor title optimization')
                if market_data.keyword.lower() not in snippet.lower():
                    competitor_info['weaknesses'].append('Weak keyword relevance')
                    
                if competitor_info['weaknesses']:
                    market_data.weak_competitors.append(competitor_info)
                else:
                    market_data.strong_competitors.append(competitor_info)
            
            market_data.competitor_data.append(competitor_info)
    
    def _identify_market_gaps(self, market_data: LiveMarketData):
        """Find gaps in the market"""
        gaps = []
        
        # Check for missing service modifiers
        urgent_modifiers = ['emergency', '24 hour', 'same day', 'urgent', 'weekend']
        for modifier in urgent_modifiers:
            if not any(modifier in r.get('title', '').lower() 
                      for r in market_data.serp_results[:5]):
                gaps.append(f"No dedicated {modifier} service pages in top 5")
        
        # Check for local optimization
        if not any(market_data.location.lower() in r.get('title', '').lower() 
                  for r in market_data.serp_results[:5]):
            gaps.append(f"Weak local optimization for {market_data.location}")
        
        # Check for trust signals
        trust_terms = ['licensed', 'insured', 'certified', 'guarantee']
        if not any(any(term in r.get('snippet', '').lower() for term in trust_terms)
                  for r in market_data.serp_results[:5]):
            gaps.append("Missing trust signals in top results")
        
        market_data.market_gaps = gaps
    
    def _calculate_opportunity_metrics(self, market_data: LiveMarketData):
        """Calculate opportunity score and difficulty"""
        score = 0
        
        # Weak competition bonus
        weak_ratio = len(market_data.weak_competitors) / 10
        score += weak_ratio * 40
        
        # Market gaps bonus
        score += len(market_data.market_gaps) * 10
        
        # Local opportunity
        if market_data.location.lower() not in ' '.join(
            r.get('title', '') for r in market_data.serp_results[:5]).lower():
            score += 20
        
        # Set difficulty
        if weak_ratio > 0.5:
            market_data.difficulty_level = "EASY"
        elif weak_ratio > 0.3:
            market_data.difficulty_level = "MEDIUM"
        else:
            market_data.difficulty_level = "HARD"
        
        market_data.opportunity_score = min(score, 100)
    
    async def _get_related_keywords(self, market_data: LiveMarketData):
        """Get related keywords for content"""
        # Extract from SERP titles and snippets
        all_text = ' '.join(
            f"{r.get('title', '')} {r.get('snippet', '')}"
            for r in market_data.serp_results
        )
        
        # Common service-related terms
        service_terms = ['repair', 'service', 'installation', 'maintenance', 
                        'emergency', 'licensed', 'professional', 'local']
        
        related = []
        for term in service_terms:
            if term in all_text.lower() and term not in market_data.keyword.lower():
                related.append(f"{market_data.keyword} {term}")
        
        market_data.related_keywords = related[:10]
    
    def _find_content_opportunities(self, market_data: LiveMarketData):
        """Identify content gaps and opportunities"""
        # Analyze what competitors are missing
        common_questions = [
            f"How much does {market_data.keyword} cost",
            f"How long does {market_data.keyword} take",
            f"Do I need {market_data.keyword}",
            f"{market_data.keyword} vs alternatives",
            f"DIY {market_data.keyword}"
        ]
        
        # Check which questions aren't answered
        snippets_text = ' '.join(r.get('snippet', '').lower() 
                                for r in market_data.serp_results)
        
        for question in common_questions:
            if question.lower() not in snippets_text:
                market_data.questions_to_answer.append(question)
        
        # Content gaps
        if 'emergency' in market_data.keyword and 'emergency' not in snippets_text:
            market_data.content_gaps.append("No emergency service content")
        if 'price' not in snippets_text and 'cost' not in snippets_text:
            market_data.content_gaps.append("No pricing information")
        if 'guarantee' not in snippets_text:
            market_data.content_gaps.append("No service guarantees mentioned")
    
    async def _analyze_technical_factors(self, market_data: LiveMarketData):
        """Analyze technical SEO factors"""
        # Simple analysis based on SERP results
        mobile_count = sum(1 for r in market_data.serp_results 
                          if 'mobile' in r.get('snippet', '').lower())
        
        market_data.mobile_friendly_ratio = mobile_count / len(market_data.serp_results)
        
        # Schema detection (simplified)
        schema_count = sum(1 for r in market_data.serp_results 
                          if any(term in str(r) for term in ['rating', 'reviews', 'price']))
        
        market_data.schema_usage['LocalBusiness'] = schema_count
    
    def _calculate_revenue_potential(self, market_data: LiveMarketData):
        """Calculate potential revenue"""
        # Base CPC estimates by service type
        if 'emergency' in market_data.keyword.lower():
            market_data.estimated_cpc = 25.0
            market_data.lead_value = 200.0
        elif 'lawyer' in market_data.keyword.lower() or 'attorney' in market_data.keyword.lower():
            market_data.estimated_cpc = 50.0
            market_data.lead_value = 500.0
        elif 'plumber' in market_data.keyword.lower():
            market_data.estimated_cpc = 15.0
            market_data.lead_value = 150.0
        else:
            market_data.estimated_cpc = 10.0
            market_data.lead_value = 100.0
        
        # Estimate based on competition
        if market_data.difficulty_level == "EASY":
            monthly_leads = 50
        elif market_data.difficulty_level == "MEDIUM":
            monthly_leads = 30
        else:
            monthly_leads = 15
        
        market_data.monthly_revenue_potential = monthly_leads * market_data.lead_value
    
    def format_for_agent(self, agent_name: str, market_data: LiveMarketData) -> Dict[str, Any]:
        """Format data specifically for each agent's needs"""
        
        if agent_name == "MarketScanner":
            return {
                'keyword': market_data.keyword,
                'location': market_data.location,
                'competitors': market_data.competitor_data,
                'opportunity_score': market_data.opportunity_score,
                'market_gaps': market_data.market_gaps
            }
        
        elif agent_name == "SEOStrategist":
            return {
                'keyword': market_data.keyword,
                'related_keywords': market_data.related_keywords,
                'competitor_weaknesses': [c['weaknesses'] for c in market_data.weak_competitors],
                'content_gaps': market_data.content_gaps,
                'difficulty': market_data.difficulty_level
            }
        
        elif agent_name == "ContentGenerator":
            return {
                'keyword': market_data.keyword,
                'questions_to_answer': market_data.questions_to_answer,
                'content_gaps': market_data.content_gaps,
                'competitor_snippets': [r['snippet'] for r in market_data.serp_results[:5]]
            }
        
        elif agent_name == "WebsiteArchitect":
            return {
                'keyword': market_data.keyword,
                'location': market_data.location,
                'competitor_urls': market_data.competitor_urls[:5],
                'mobile_priority': market_data.mobile_friendly_ratio < 0.5,
                'schema_needed': market_data.schema_usage.get('LocalBusiness', 0) < 3
            }
        
        # Return full data for other agents
        return {
            'keyword': market_data.keyword,
            'location': market_data.location,
            'opportunity_score': market_data.opportunity_score,
            'market_data': market_data.__dict__
        }