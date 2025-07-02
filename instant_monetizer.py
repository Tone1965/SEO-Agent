"""
Instant Monetizer - Turn opportunities into money in 14 days
"""
import os
from datetime import datetime, timedelta
from jina_opportunity_finder import JinaOpportunityFinder

class InstantMonetizer:
    def __init__(self):
        self.finder = JinaOpportunityFinder()
        
    def build_action_plan(self, opportunity: dict) -> dict:
        """Create exact steps to monetize this opportunity"""
        
        if opportunity['action'] != 'BUILD NOW':
            return None
            
        # Generate the complete action plan
        plan = {
            'opportunity': opportunity,
            'timeline': self._create_timeline(opportunity),
            'content_plan': self._create_content_plan(opportunity),
            'monetization_strategy': self._create_monetization_plan(opportunity),
            'estimated_investment': self._calculate_investment(opportunity),
            'break_even_days': self._calculate_break_even(opportunity)
        }
        
        return plan
    
    def _create_timeline(self, opp: dict) -> list:
        """14-day sprint to profit"""
        
        timeline = [
            {
                'day': '1-2',
                'tasks': [
                    f"Register domain: {opp['domain_suggestion']}",
                    "Set up hosting (use existing)",
                    "Install WordPress/Static site",
                    "Add SSL certificate"
                ]
            },
            {
                'day': '3-5',
                'tasks': [
                    "Create 5 core pages:",
                    f"- Homepage: '{opp['keyword']} Available Now'",
                    f"- Service page: 'Weekend/Emergency {opp['keyword'].split()[1]}'",
                    "- Areas served page with all suburbs",
                    "- Pricing page (even if estimates)",
                    "- Contact with prominent phone number"
                ]
            },
            {
                'day': '6-7',
                'tasks': [
                    "Add Google My Business listing",
                    "Submit to local directories",
                    "Create 5 location-specific pages",
                    "Add schema markup for local business"
                ]
            },
            {
                'day': '8-10',
                'tasks': [
                    "Build 20 local citations",
                    "Create 3 blog posts about weekend service",
                    "Add customer review schema",
                    "Optimize page speed"
                ]
            },
            {
                'day': '11-14',
                'tasks': [
                    "Monitor rankings daily",
                    "Set up call tracking",
                    "Contact 5 local plumbers/contractors",
                    "Negotiate lead sale agreement"
                ]
            }
        ]
        
        return timeline
    
    def _create_content_plan(self, opp: dict) -> dict:
        """Content that ranks FAST"""
        
        keyword = opp['keyword']
        location = opp['location']
        
        return {
            'homepage': {
                'title': f"{keyword.title()} in {location} - Open Now!",
                'h1': f"24/7 {keyword.title()} Services in {location}",
                'content_blocks': [
                    "Emergency availability statement",
                    "Service area list (all suburbs)",
                    "Why choose us (weekend availability)",
                    "Pricing transparency",
                    "Call to action every 200 words"
                ]
            },
            'service_pages': [
                f"Weekend {keyword} Services",
                f"Emergency {keyword} {location}",
                f"After Hours {keyword} Near Me",
                f"Sunday {keyword} Available",
                f"Same Day {keyword} Service"
            ],
            'blog_posts': [
                f"Why You Need a {keyword} Available on Weekends",
                f"Emergency {keyword} Costs in {location} - What to Expect",
                f"Finding a Reliable Weekend {keyword} in {location}"
            ]
        }
    
    def _create_monetization_plan(self, opp: dict) -> dict:
        """How to turn traffic into money"""
        
        lead_value = opp['lead_value']
        monthly_revenue = opp['monthly_revenue_potential']
        
        return {
            'option_1': {
                'model': 'Pay Per Lead',
                'pricing': f"${lead_value} per qualified call",
                'pitch': f"I have customers calling for {opp['keyword']}. Want them?",
                'expected_buyers': 3,
                'close_rate': '60%'
            },
            'option_2': {
                'model': 'Monthly Rental',
                'pricing': f"${int(monthly_revenue * 0.6)}/month",
                'pitch': "Exclusive weekend leads for your area",
                'contract_length': '6 months',
                'guaranteed_leads': int(monthly_revenue / lead_value * 0.7)
            },
            'option_3': {
                'model': 'Quick Flip',
                'pricing': f"${int(monthly_revenue * 12)}",
                'pitch': "Proven site with ranking and traffic",
                'time_to_sell': '60-90 days',
                'platforms': ['Flippa', 'Empire Flippers', 'Direct sale']
            }
        }
    
    def _calculate_investment(self, opp: dict) -> dict:
        """Real costs to build"""
        
        return {
            'domain': 12,
            'hosting': 0,  # Use existing
            'content': 0,  # AI generated
            'citations': 50,  # Paid service
            'time_hours': 10,
            'total_cash': 62,
            'break_even_leads': 1  # One lead pays it all back!
        }
    
    def _calculate_break_even(self, opp: dict) -> int:
        """Days until profitable"""
        
        investment = 62
        daily_revenue = opp['monthly_revenue_potential'] / 30
        
        return int(investment / daily_revenue) + opp['days_to_rank']
    
    def find_instant_opportunities(self, location: str) -> list:
        """Find ALL instant money opportunities in a location"""
        
        services = ['plumber', 'electrician', 'ac repair', 'locksmith', 'garage door']
        modifiers = ['weekend', 'emergency', 'after hours', '24 hour', 'sunday']
        
        all_opportunities = []
        
        for service in services:
            for modifier in modifiers:
                keyword = f"{modifier} {service}"
                opp = self.finder.search_and_analyze(keyword, location)
                
                if opp and opp['action'] == 'BUILD NOW':
                    plan = self.build_action_plan(opp)
                    all_opportunities.append(plan)
        
        # Sort by quickest to profit
        all_opportunities.sort(key=lambda x: x['break_even_days'])
        
        return all_opportunities


# Example output
if __name__ == "__main__":
    monetizer = InstantMonetizer()
    
    print("💰 INSTANT MONEY OPPORTUNITIES IN BIRMINGHAM")
    print("=" * 60)
    
    # Find one opportunity
    opp = monetizer.finder.search_and_analyze("weekend plumber", "Pelham AL")
    
    if opp['action'] == 'BUILD NOW':
        plan = monetizer.build_action_plan(opp)
        
        print(f"\n🎯 TARGET: {opp['keyword']} - {opp['location']}")
        print(f"💵 Monthly Revenue: ${opp['monthly_revenue_potential']:,}")
        print(f"⏱️ Days to Profit: {plan['break_even_days']}")
        print(f"💸 Total Investment: ${plan['estimated_investment']['total_cash']}")
        
        print("\n📅 14-DAY ACTION PLAN:")
        for phase in plan['timeline']:
            print(f"\nDay {phase['day']}:")
            for task in phase['tasks']:
                print(f"  ✓ {task}")
        
        print("\n💰 MONETIZATION OPTIONS:")
        for option, details in plan['monetization_strategy'].items():
            print(f"\n{option}: {details['model']}")
            print(f"  Price: {details['pricing']}")
            print(f"  Pitch: '{details['pitch']}'")
    
    print("\n🚀 START BUILDING NOW!")