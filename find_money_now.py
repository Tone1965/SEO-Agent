#!/usr/bin/env python3
"""
FIND MONEY NOW - Instant opportunity finder using Jina
Run this to find keywords you can monetize in 14 days
"""
import os
from jina_complete import JinaComplete
from datetime import datetime
import json

def find_instant_money(city="Birmingham AL"):
    """Find opportunities you can build and monetize TODAY"""
    
    print("💰 INSTANT MONEY FINDER - POWERED BY JINA")
    print("=" * 60)
    print(f"🎯 Target Location: {city}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('JINA_API_KEY'):
        print("\n❌ ERROR: No Jina API key found!")
        print("\n📝 Quick Setup:")
        print("1. Go to https://jina.ai")
        print("2. Sign up (it's free)")
        print("3. Get your API key")
        print("4. Add to .env: JINA_API_KEY=your_key_here")
        return
    
    jina = JinaComplete()
    
    # Find money keywords
    print("\n🔍 Searching for instant money keywords...")
    print("Looking for: emergency services, weekend availability, urgent needs")
    print("-" * 60)
    
    opportunities = jina.find_money_keywords(city)
    
    if not opportunities:
        print("❌ No opportunities found. Try a different city.")
        return
    
    # Filter to ONLY the best
    instant_money = [o for o in opportunities if o['monthly_revenue'] > 2000 and o['days_to_rank'] <= 21]
    
    print(f"\n✅ Found {len(instant_money)} INSTANT MONEY opportunities!")
    
    # Show top 3
    print("\n🏆 TOP 3 OPPORTUNITIES (BUILD THESE NOW):")
    print("=" * 60)
    
    for i, opp in enumerate(instant_money[:3], 1):
        print(f"\n#{i} KEYWORD: {opp['keyword']}")
        print(f"💰 Monthly Revenue: ${opp['monthly_revenue']:,}")
        print(f"📊 Searches/Month: ~{opp['monthly_searches']}")
        print(f"⏱️ Days to Profit: {opp['days_to_rank']}")
        print(f"🎯 Competition: {opp['difficulty']} ({opp['weak_sites']}/10 weak sites)")
        print(f"🌐 Domain to Register: {opp['domain']}")
        print(f"💵 Lead Value: ${opp['lead_value']} per call")
        
        # Quick action plan
        print(f"\n📋 QUICK ACTION PLAN:")
        print(f"   Day 1: Register {opp['domain']}")
        print(f"   Day 2: Build 5-page site focused on '{opp['keyword'].split()[0]}'")
        print(f"   Day 3-7: Get 20 citations + Google My Business")
        print(f"   Day 14: Start getting calls (${opp['lead_value']} each)")
        
        # ROI calculation
        investment = 62  # Domain + citations
        first_month_profit = opp['monthly_revenue'] - investment
        print(f"\n💸 ROI: Invest $62 → Make ${first_month_profit:,} profit first month")
        print("-" * 60)
    
    # Analyze top competitor for first opportunity
    if instant_money:
        print(f"\n🔍 COMPETITOR ANALYSIS FOR: {instant_money[0]['keyword']}")
        print("=" * 60)
        
        # Get top competitor
        results = jina.search(instant_money[0]['keyword'])
        if results.get('results'):
            competitor_url = results['results'][0]['url']
            
            print(f"Analyzing: {competitor_url}")
            analysis = jina.analyze_competitor(competitor_url)
            
            print(f"\n⚔️ WEAKNESSES TO EXPLOIT:")
            for weakness in analysis['weaknesses'][:5]:
                print(f"  • {weakness}")
            
            print(f"\n🎯 KEYWORDS THEY'RE MISSING:")
            for keyword in analysis['missing_keywords'][:3]:
                print(f"  • {keyword}")
            
            print(f"\n✅ YOUR ADVANTAGES:")
            print(f"  • Target their missing keywords")
            print(f"  • Fix all their weaknesses")
            print(f"  • Focus on {instant_money[0]['keyword'].split()[0]} availability")
    
    # Save opportunities
    report = {
        'city': city,
        'date': datetime.now().isoformat(),
        'opportunities_found': len(opportunities),
        'instant_money': instant_money[:5],
        'total_monthly_revenue': sum(o['monthly_revenue'] for o in instant_money[:5])
    }
    
    filename = f"money_report_{city.replace(' ', '_').replace(',', '')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Full report saved to: {filename}")
    
    # Final summary
    if instant_money:
        print("\n" + "=" * 60)
        print("🚀 NEXT STEPS TO MAKE MONEY:")
        print("=" * 60)
        print(f"1. Pick ONE keyword (recommend: {instant_money[0]['keyword']})")
        print(f"2. Register domain: {instant_money[0]['domain']}")
        print("3. Build simple 5-page site today")
        print("4. Focus ALL content on availability/urgency")
        print(f"5. Start selling leads in 14 days at ${instant_money[0]['lead_value']} each")
        print(f"\n💰 Potential: ${instant_money[0]['monthly_revenue']:,}/month")
        print(f"📍 Investment: $62 (domain + citations)")
        print(f"⏱️ Time to profit: {instant_money[0]['days_to_rank']} days")


if __name__ == "__main__":
    # You can change the city here
    city = "Birmingham AL"
    
    # Find money!
    find_instant_money(city)
    
    print("\n✨ Ready to build? Pick a keyword and START NOW!")