"""
Test Jina's new semantic and long-tail keyword features
"""
from jina_complete import JinaComplete

def test_keyword_discovery():
    jina = JinaComplete()
    
    # Test semantic keyword discovery
    print("\n🧠 TESTING SEMANTIC KEYWORD DISCOVERY")
    print("="*60)
    
    seed_keyword = "plumber"
    location = "Birmingham AL"
    
    semantic_keywords = jina.find_semantic_keywords(seed_keyword, location)
    
    print(f"\nSemantic keywords for '{seed_keyword}':")
    for kw in semantic_keywords[:10]:
        print(f"- {kw['keyword']} | Vol: {kw['search_volume']} | Diff: {kw['difficulty']} | Score: {kw['opportunity_score']}")
    
    # Test long-tail keyword discovery
    print("\n\n🎯 TESTING LONG-TAIL KEYWORD DISCOVERY")
    print("="*60)
    
    longtail_keywords = jina.find_longtail_keywords(seed_keyword, location)
    
    print(f"\nLong-tail keywords for '{seed_keyword}':")
    for kw in longtail_keywords[:15]:
        print(f"- {kw['keyword']} | Vol: {kw['search_volume']} | Intent: {kw['intent']} | CPC: ${kw['cpc_estimate']}")
    
    # Find golden opportunities (high volume, low competition)
    print("\n\n💎 GOLDEN OPPORTUNITIES (High Volume + Low Competition)")
    print("="*60)
    
    all_keywords = semantic_keywords + longtail_keywords
    golden = [kw for kw in all_keywords if kw['opportunity_score'] > 70]
    golden.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    for kw in golden[:10]:
        print(f"⭐ {kw['keyword']}")
        print(f"   Volume: {kw['search_volume']} | Competition: {kw['competition']:.2f}")
        print(f"   Opportunity Score: {kw['opportunity_score']} | Est. CPC: ${kw['cpc_estimate']}")
        print()

if __name__ == "__main__":
    test_keyword_discovery()