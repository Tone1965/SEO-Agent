"""
Integrated Opportunity Finder
Combines Jina semantic search with BrightData competitor analysis
"""
import os
from brightdata_simple import BrightDataSimple
from jina_opportunity_finder import JinaOpportunityFinder
from instant_monetizer import InstantMonetizer
from typing import Dict, List
import json

class IntegratedOpportunityFinder:
    def __init__(self):
        self.jina = JinaOpportunityFinder()
        self.brightdata = BrightDataSimple()
        self.monetizer = InstantMonetizer()
        
    def find_golden_opportunities(self, location: str, min_profit: int = 1000) -> List[Dict]:
        """Find the best money-making opportunities in a location"""
        
        print(f"🔍 Searching for opportunities in {location}")
        print(f"💰 Minimum profit target: ${min_profit}/month")
        print("=" * 60)
        
        # High-value service keywords
        services = [
            'emergency plumber',
            'weekend electrician', 
            'after hours hvac',
            '24 hour locksmith',
            'sunday garage door repair',
            'emergency water heater',
            'weekend ac repair',
            'emergency roof repair'
        ]
        
        all_opportunities = []
        
        for service in services:
            print(f"\n📍 Analyzing: {service}")
            
            # Step 1: Use Jina to analyze search opportunity
            jina_analysis = self.jina.search_and_analyze(service, location)
            
            if not jina_analysis or jina_analysis['action'] != 'BUILD NOW':
                print(f"  ❌ Not profitable enough")
                continue
            
            # Step 2: Use BrightData to analyze competition
            competitors = self.brightdata.find_weak_competitors(service, location)
            
            # Count weak competitors
            weak_count = sum(1 for c in competitors[:5] if c.get('weakness_score', 0) >= 3)
            
            # Step 3: Create opportunity report
            opportunity = {
                'keyword': service,
                'location': location,
                'jina_data': jina_analysis,
                'weak_competitors': weak_count,
                'top_competitor_weaknesses': self._get_top_weaknesses(competitors),
                'monthly_revenue': jina_analysis['monthly_revenue_potential'],
                'days_to_profit': jina_analysis['days_to_rank'],
                'domain_suggestion': jina_analysis['domain_suggestion'],
                'build_priority': self._calculate_priority(jina_analysis, weak_count),
                'action_plan': None  # Will be filled if selected
            }
            
            if opportunity['monthly_revenue'] >= min_profit:
                all_opportunities.append(opportunity)
                print(f"  ✅ Found opportunity: ${opportunity['monthly_revenue']}/month")
            
        # Sort by best opportunities first
        all_opportunities.sort(key=lambda x: (
            x['build_priority'] == 'URGENT',
            x['monthly_revenue'],
            -x['days_to_profit']
        ), reverse=True)
        
        # Generate action plans for top 3
        for i, opp in enumerate(all_opportunities[:3]):
            print(f"\n🎯 Creating action plan for: {opp['keyword']}")
            opp['action_plan'] = self.monetizer.build_action_plan(opp['jina_data'])
        
        return all_opportunities
    
    def _get_top_weaknesses(self, competitors: List[Dict]) -> List[str]:
        """Get most common weaknesses from competitors"""
        weakness_count = {}
        
        for comp in competitors[:5]:
            if comp.get('success'):
                for weakness in comp.get('weaknesses', []):
                    weakness_count[weakness] = weakness_count.get(weakness, 0) + 1
        
        # Sort by frequency
        sorted_weaknesses = sorted(weakness_count.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_weaknesses[:3]]
    
    def _calculate_priority(self, jina_data: Dict, weak_competitors: int) -> str:
        """Calculate build priority based on opportunity and competition"""
        
        revenue = jina_data['monthly_revenue_potential']
        days = jina_data['days_to_rank']
        
        if revenue > 3000 and weak_competitors >= 3 and days <= 14:
            return 'URGENT'
        elif revenue > 2000 and weak_competitors >= 2:
            return 'HIGH'
        elif revenue > 1000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_opportunity_report(self, opportunities: List[Dict]) -> str:
        """Generate a formatted report of opportunities"""
        
        report = []
        report.append("🏆 TOP MONEY-MAKING OPPORTUNITIES")
        report.append("=" * 60)
        
        for i, opp in enumerate(opportunities[:5], 1):
            report.append(f"\n#{i} {opp['keyword'].upper()} - {opp['location']}")
            report.append(f"💰 Revenue: ${opp['monthly_revenue']:,}/month")
            report.append(f"⏱️ Time to Profit: {opp['days_to_profit']} days")
            report.append(f"🎯 Priority: {opp['build_priority']}")
            report.append(f"🌐 Domain: {opp['domain_suggestion']}")
            report.append(f"⚔️ Weak Competitors: {opp['weak_competitors']}/5")
            
            if opp['top_competitor_weaknesses']:
                report.append("📊 Competitor Weaknesses:")
                for weakness in opp['top_competitor_weaknesses']:
                    report.append(f"   • {weakness}")
            
            if opp.get('action_plan'):
                report.append("\n📅 QUICK ACTION PLAN:")
                plan = opp['action_plan']
                report.append(f"   Investment: ${plan['estimated_investment']['total_cash']}")
                report.append(f"   Break-even: {plan['break_even_days']} days")
                report.append("   First 3 Days:")
                for task in plan['timeline'][0]['tasks'][:3]:
                    report.append(f"   ✓ {task}")
            
            report.append("-" * 60)
        
        return "\n".join(report)
    
    def export_opportunities(self, opportunities: List[Dict], filename: str = "opportunities.json"):
        """Export opportunities to JSON file"""
        
        # Clean data for export
        export_data = []
        for opp in opportunities:
            clean_opp = {
                'keyword': opp['keyword'],
                'location': opp['location'],
                'monthly_revenue': opp['monthly_revenue'],
                'days_to_profit': opp['days_to_profit'],
                'domain': opp['domain_suggestion'],
                'priority': opp['build_priority'],
                'weak_competitors': opp['weak_competitors'],
                'competitor_weaknesses': opp['top_competitor_weaknesses']
            }
            
            if opp.get('action_plan'):
                clean_opp['investment_required'] = opp['action_plan']['estimated_investment']['total_cash']
                clean_opp['break_even_days'] = opp['action_plan']['break_even_days']
            
            export_data.append(clean_opp)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✅ Exported {len(export_data)} opportunities to {filename}")


# Main execution
if __name__ == "__main__":
    finder = IntegratedOpportunityFinder()
    
    # Find opportunities in Birmingham
    opportunities = finder.find_golden_opportunities(
        location="Birmingham AL",
        min_profit=1500
    )
    
    # Generate and print report
    report = finder.generate_opportunity_report(opportunities)
    print("\n" + report)
    
    # Export to file
    finder.export_opportunities(opportunities)
    
    # Show summary
    print(f"\n📊 SUMMARY:")
    print(f"Total Opportunities Found: {len(opportunities)}")
    urgent = sum(1 for o in opportunities if o['build_priority'] == 'URGENT')
    print(f"Urgent Opportunities: {urgent}")
    total_revenue = sum(o['monthly_revenue'] for o in opportunities)
    print(f"Total Monthly Revenue Potential: ${total_revenue:,}")
    
    if opportunities:
        print(f"\n🚀 RECOMMENDED ACTION:")
        best = opportunities[0]
        print(f"Start with: {best['keyword']} in {best['location']}")
        print(f"Register domain: {best['domain_suggestion']}")
        print(f"Expected profit in 30 days: ${best['monthly_revenue']:,}")