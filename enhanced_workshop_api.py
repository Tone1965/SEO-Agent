"""
Enhanced Workshop API - Find underserved opportunities across ALL services
Uses live data from Jina/BrightData to find easy wins
"""
from flask import Blueprint, request, jsonify
import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Import scraping and opportunity finding tools
from jina_complete import JinaComplete
from scraping_manager import ScrapingManager
from integrated_opportunity_finder import IntegratedOpportunityFinder

# Import existing agents
from workshop_api import AGENT_REGISTRY, ai_client

enhanced_workshop_bp = Blueprint('enhanced_workshop', __name__)

# Initialize tools
jina = JinaComplete()
scraper = ScrapingManager()
opportunity_finder = IntegratedOpportunityFinder()

# Expanded service categories for comprehensive search
SERVICE_CATEGORIES = {
    'emergency_services': [
        'plumber', 'electrician', 'hvac', 'locksmith', 'roofer',
        'water damage', 'gas leak repair', 'sewer repair', 'garage door'
    ],
    'medical_services': [
        'dentist', 'chiropractor', 'physical therapy', 'urgent care',
        'pediatrician', 'dermatologist', 'eye doctor', 'psychologist'
    ],
    'legal_services': [
        'divorce lawyer', 'criminal defense', 'personal injury',
        'bankruptcy attorney', 'immigration lawyer', 'family law'
    ],
    'home_services': [
        'house cleaning', 'lawn care', 'pest control', 'handyman',
        'painting contractor', 'flooring', 'kitchen remodeling', 'bathroom renovation'
    ],
    'automotive': [
        'auto repair', 'oil change', 'tire shop', 'auto body',
        'transmission repair', 'brake service', 'car detailing', 'windshield repair'
    ],
    'personal_services': [
        'hair salon', 'barber shop', 'nail salon', 'massage therapy',
        'tattoo shop', 'dog grooming', 'dry cleaning', 'tailor'
    ],
    'educational': [
        'tutoring', 'driving school', 'music lessons', 'art classes',
        'language school', 'test prep', 'coding bootcamp', 'dance studio'
    ],
    'fitness_wellness': [
        'gym', 'yoga studio', 'personal trainer', 'nutritionist',
        'crossfit', 'martial arts', 'pilates', 'wellness coach'
    ],
    'specialized_trades': [
        'welding', 'concrete contractor', 'fence installation', 'solar panels',
        'pool service', 'landscaping', 'tree service', 'septic service'
    ],
    'business_services': [
        'accountant', 'bookkeeping', 'it support', 'web design',
        'marketing agency', 'commercial cleaning', 'security services', 'courier'
    ]
}

# High-value modifiers that indicate urgent need
MONEY_MODIFIERS = [
    'emergency', '24 hour', 'same day', 'urgent', 'weekend',
    'sunday', 'after hours', 'open now', 'tonight', 'asap',
    'spanish speaking', 'mobile', 'on site', 'certified', 'licensed'
]

@enhanced_workshop_bp.route('/api/find-opportunities', methods=['POST'])
def find_opportunities():
    """Find underserved opportunities using live data"""
    try:
        data = request.json
        location = data.get('location', 'Birmingham AL')
        categories = data.get('categories', ['emergency_services'])
        min_revenue = data.get('min_revenue', 2000)
        
        all_opportunities = []
        
        # Search each category
        for category in categories:
            services = SERVICE_CATEGORIES.get(category, [])
            
            for service in services[:3]:  # Top 3 per category to start
                for modifier in MONEY_MODIFIERS[:5]:  # Top 5 modifiers
                    keyword = f"{modifier} {service} {location}"
                    
                    # Use Jina to search
                    results = jina.search(keyword)
                    
                    if results:
                        # Analyze opportunity
                        opp = analyze_opportunity(keyword, results, location, service, modifier)
                        
                        if opp['monthly_revenue'] >= min_revenue and opp['worth_building']:
                            all_opportunities.append(opp)
        
        # Sort by best opportunities
        all_opportunities.sort(key=lambda x: (x['monthly_revenue'], -x['days_to_rank']), reverse=True)
        
        return jsonify({
            'success': True,
            'opportunities': all_opportunities[:10],  # Top 10
            'total_found': len(all_opportunities),
            'search_details': {
                'location': location,
                'categories': categories,
                'min_revenue': min_revenue
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_workshop_bp.route('/api/analyze-competitors', methods=['POST'])
def analyze_competitors():
    """Deep dive into specific opportunity competitors"""
    try:
        data = request.json
        keyword = data.get('keyword')
        location = data.get('location')
        
        # Search for competitors
        results = scraper.search(f"{keyword} {location}")
        
        competitor_analysis = []
        
        # Analyze top 5 competitors
        for i, result in enumerate(results.get('results', [])[:5]):
            url = result.get('url', '')
            
            # Scrape competitor
            content = scraper.scrape(url)
            
            if content:
                analysis = jina.analyze_competitor(url)
                analysis['rank'] = i + 1
                competitor_analysis.append(analysis)
        
        # Generate attack plan
        if competitor_analysis:
            attack_plan = generate_attack_plan(keyword, competitor_analysis)
        else:
            attack_plan = None
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'location': location,
            'competitors': competitor_analysis,
            'attack_plan': attack_plan
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_workshop_bp.route('/api/validate-opportunity', methods=['POST'])
def validate_opportunity():
    """Validate opportunity with real data before building"""
    try:
        data = request.json
        keyword = data.get('keyword')
        location = data.get('location')
        
        # Multi-source validation
        validation = {
            'keyword': keyword,
            'location': location,
            'checks': {}
        }
        
        # 1. Check search volume trends
        search_data = jina.search(keyword)
        validation['checks']['search_presence'] = len(search_data.get('results', [])) > 0
        
        # 2. Check competition weakness
        weak_count = 0
        for result in search_data.get('results', [])[:10]:
            url = result.get('url', '').lower()
            if any(weak in url for weak in ['yelp.com', 'yellowpages.com', 'facebook.com']):
                weak_count += 1
        
        validation['checks']['weak_competition'] = weak_count >= 3
        validation['weak_competitor_count'] = weak_count
        
        # 3. Check for dedicated sites
        has_dedicated = False
        for result in search_data.get('results', [])[:10]:
            url = result.get('url', '').lower()
            if any(term in url for term in keyword.lower().split()[:2]):
                has_dedicated = True
                break
        
        validation['checks']['no_dedicated_sites'] = not has_dedicated
        
        # 4. Calculate opportunity score
        score = 0
        if validation['checks']['search_presence']: score += 30
        if validation['checks']['weak_competition']: score += 40
        if validation['checks']['no_dedicated_sites']: score += 30
        
        validation['opportunity_score'] = score
        validation['recommendation'] = get_recommendation(score)
        
        # 5. Suggested domain
        validation['suggested_domain'] = generate_domain(keyword, location)
        
        return jsonify({
            'success': True,
            'validation': validation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_workshop_bp.route('/api/generate-action-plan', methods=['POST'])
def generate_action_plan():
    """Generate detailed 14-day action plan for opportunity"""
    try:
        data = request.json
        opportunity = data.get('opportunity', {})
        
        plan = {
            'keyword': opportunity.get('keyword'),
            'location': opportunity.get('location'),
            'timeline': generate_timeline(opportunity),
            'content_plan': generate_content_plan(opportunity),
            'technical_checklist': generate_technical_checklist(opportunity),
            'monetization_strategy': generate_monetization_strategy(opportunity),
            'estimated_costs': calculate_costs(opportunity),
            'revenue_projection': calculate_revenue_projection(opportunity)
        }
        
        return jsonify({
            'success': True,
            'action_plan': plan
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions
def analyze_opportunity(keyword: str, results: Dict, location: str, service: str, modifier: str) -> Dict:
    """Analyze if keyword is worth targeting"""
    
    weak_sites = 0
    strong_sites = 0
    
    for result in results.get('results', [])[:10]:
        url = result.get('url', '').lower()
        
        # Weak signals
        weak_domains = ['yelp.com', 'yellowpages.com', 'facebook.com', 
                       'nextdoor.com', 'angi.com', 'thumbtack.com',
                       'manta.com', 'superpages.com', 'citysearch.com']
        
        if any(domain in url for domain in weak_domains):
            weak_sites += 1
        elif service.lower() in url or modifier.lower() in url:
            strong_sites += 1
    
    # Estimate metrics
    competition_score = (weak_sites / 10) * 100
    difficulty = 'EASY' if competition_score > 50 else 'MEDIUM' if competition_score > 30 else 'HARD'
    
    # Revenue calculation
    lead_values = {
        'emergency': 200, '24 hour': 175, 'same day': 150,
        'urgent': 140, 'weekend': 130, 'sunday': 120,
        'after hours': 110, 'spanish speaking': 100
    }
    
    lead_value = lead_values.get(modifier.split()[0], 80)
    estimated_searches = 50 + (weak_sites * 20)  # More weak sites = more searches
    monthly_revenue = int(estimated_searches * 0.1 * lead_value)
    
    # Days to rank
    if difficulty == 'EASY':
        days_to_rank = 14
    elif difficulty == 'MEDIUM':
        days_to_rank = 30
    else:
        days_to_rank = 60
    
    return {
        'keyword': keyword,
        'service': service,
        'modifier': modifier,
        'location': location,
        'weak_sites': weak_sites,
        'strong_sites': strong_sites,
        'competition_score': competition_score,
        'difficulty': difficulty,
        'lead_value': lead_value,
        'estimated_searches': estimated_searches,
        'monthly_revenue': monthly_revenue,
        'days_to_rank': days_to_rank,
        'worth_building': monthly_revenue > 2000 and days_to_rank <= 30,
        'domain_suggestion': generate_domain(keyword, location)
    }

def generate_domain(keyword: str, location: str) -> str:
    """Generate domain suggestion"""
    parts = keyword.lower().split()
    city = location.lower().split(',')[0].strip().replace(' ', '')
    
    # Remove common words
    parts = [p for p in parts if p not in ['the', 'in', 'at', 'near', 'by']]
    
    # Build domain
    if len(parts) >= 3:
        domain = f"{parts[0]}-{parts[1]}-{city}.com"
    else:
        domain = f"{'-'.join(parts)}-{city}.com"
    
    return domain.replace('--', '-')

def get_recommendation(score: int) -> str:
    """Get recommendation based on score"""
    if score >= 80:
        return "🟢 EXCELLENT - Build immediately! Very high success probability."
    elif score >= 60:
        return "🟡 GOOD - Worth building, moderate competition."
    elif score >= 40:
        return "🟠 FAIR - Possible but requires more effort."
    else:
        return "🔴 POOR - High competition, consider different keyword."

def generate_timeline(opportunity: Dict) -> List[Dict]:
    """Generate 14-day timeline"""
    return [
        {
            'days': '1-2',
            'tasks': [
                f"Register domain: {opportunity.get('domain_suggestion', 'your-domain.com')}",
                "Set up hosting (use existing if available)",
                "Install SSL certificate",
                "Set up basic WordPress or static site"
            ]
        },
        {
            'days': '3-5',
            'tasks': [
                "Create 5 core pages (Home, Services, Areas, About, Contact)",
                f"Focus all content on '{opportunity.get('modifier', 'emergency')}' availability",
                "Add phone number prominently on every page",
                "Install call tracking"
            ]
        },
        {
            'days': '6-8',
            'tasks': [
                "Add Google My Business listing",
                "Build 20+ local citations",
                "Create service area pages for nearby cities",
                "Add schema markup for local business"
            ]
        },
        {
            'days': '9-12',
            'tasks': [
                "Create 3 blog posts about emergency/urgent services",
                "Add customer testimonials section",
                "Optimize page speed (aim for < 3 seconds)",
                "Submit sitemap to Google"
            ]
        },
        {
            'days': '13-14',
            'tasks': [
                "Contact local service providers",
                "Set up lead forwarding system",
                "Monitor initial rankings",
                "Fine-tune based on early data"
            ]
        }
    ]

def generate_content_plan(opportunity: Dict) -> Dict:
    """Generate content strategy"""
    keyword = opportunity.get('keyword', '')
    service = opportunity.get('service', 'service')
    modifier = opportunity.get('modifier', 'emergency')
    
    return {
        'homepage': {
            'title': f"{modifier.title()} {service.title()} - Available Now",
            'h1': f"24/7 {modifier.title()} {service.title()} Services",
            'key_sections': [
                f"Why we're the #1 {modifier} {service}",
                "Service areas and response times",
                "Transparent pricing",
                "Call now button every 300 words"
            ]
        },
        'service_pages': [
            f"{modifier} {service} Services",
            f"Weekend {service} Availability",
            f"After Hours {service}",
            f"Same Day {service} Service",
            f"Emergency {service} Near Me"
        ],
        'blog_topics': [
            f"What to do when you need {modifier} {service} help",
            f"How much does {modifier} {service} cost?",
            f"Finding reliable {modifier} {service} in {opportunity.get('location', 'your area')}"
        ]
    }

def generate_technical_checklist(opportunity: Dict) -> List[str]:
    """Technical SEO checklist"""
    return [
        "Mobile-responsive design (critical for emergency searches)",
        "Click-to-call buttons on mobile",
        "Page speed under 3 seconds",
        "SSL certificate installed",
        "Schema markup for LocalBusiness",
        "Schema markup for Service",
        "XML sitemap created and submitted",
        "Robots.txt configured",
        "Google Analytics installed",
        "Google Search Console verified",
        "Local business citations consistent (NAP)",
        "Service area pages for nearby cities"
    ]

def generate_monetization_strategy(opportunity: Dict) -> Dict:
    """How to make money from the site"""
    lead_value = opportunity.get('lead_value', 100)
    monthly_revenue = opportunity.get('monthly_revenue', 3000)
    
    return {
        'pay_per_lead': {
            'model': 'Charge per qualified call',
            'pricing': f"${lead_value} per lead",
            'pitch': f"I have customers calling for {opportunity.get('service', 'your service')}. Interested?",
            'target_buyers': 3
        },
        'monthly_rental': {
            'model': 'Rent exclusive access',
            'pricing': f"${int(monthly_revenue * 0.6)}/month",
            'contract': '6-month minimum',
            'benefits': 'All leads exclusively yours'
        },
        'website_flip': {
            'model': 'Build and sell',
            'timing': 'After 3-6 months',
            'price': f"${monthly_revenue * 8}-${monthly_revenue * 12}",
            'platforms': ['Flippa', 'Empire Flippers', 'Direct sale']
        }
    }

def calculate_costs(opportunity: Dict) -> Dict:
    """Calculate investment needed"""
    return {
        'domain': 12,
        'hosting': 10,  # Monthly
        'citations': 50,  # One-time
        'content': 0,  # AI generated
        'time_hours': 15,
        'total_cash': 72,
        'break_even': '1-2 leads'
    }

def calculate_revenue_projection(opportunity: Dict) -> Dict:
    """Project revenue over time"""
    monthly = opportunity.get('monthly_revenue', 3000)
    
    return {
        'month_1': int(monthly * 0.3),  # Ramp up
        'month_2': int(monthly * 0.7),
        'month_3': monthly,
        'month_6': int(monthly * 1.2),  # Growth
        'year_1_total': monthly * 10  # Conservative
    }

def generate_attack_plan(keyword: str, competitors: List[Dict]) -> Dict:
    """Generate plan to outrank competitors"""
    
    # Aggregate weaknesses
    all_weaknesses = []
    for comp in competitors:
        all_weaknesses.extend(comp.get('weaknesses', []))
    
    # Count weakness frequency
    weakness_counts = {}
    for w in all_weaknesses:
        weakness_counts[w] = weakness_counts.get(w, 0) + 1
    
    # Top weaknesses to exploit
    top_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'keyword': keyword,
        'competitors_analyzed': len(competitors),
        'common_weaknesses': [w[0] for w in top_weaknesses],
        'quick_wins': [
            "Create dedicated page for exact keyword match",
            "Add content addressing all weaknesses found",
            "Include elements competitors are missing",
            "Focus on local + urgency signals",
            "Better mobile experience than all competitors"
        ],
        'content_advantages': [
            "More comprehensive content (2000+ words)",
            "Clear pricing information",
            "Prominent phone numbers",
            "Trust signals (licenses, insurance)",
            "Real customer testimonials"
        ]
    }