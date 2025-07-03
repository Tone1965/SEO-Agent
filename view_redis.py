#!/usr/bin/env python3
"""
View Redis Data - See what Jina.ai cached
"""
import redis
import json
import os
from datetime import datetime

def view_redis_data():
    # Connect to Redis
    redis_client = redis.Redis.from_url(
        os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        decode_responses=True
    )
    
    print("🔍 REDIS DATA VIEWER")
    print("=" * 60)
    
    # Get all keys
    all_keys = redis_client.keys('*')
    jina_keys = [k for k in all_keys if k.startswith('jina:')]
    
    print(f"\n📊 Total Redis Keys: {len(all_keys)}")
    print(f"🔎 Jina Cache Keys: {len(jina_keys)}")
    
    if jina_keys:
        print("\n📦 JINA CACHED DATA:")
        print("-" * 60)
        
        for key in jina_keys:
            ttl = redis_client.ttl(key)
            value = redis_client.get(key)
            
            print(f"\n🔑 Key: {key}")
            print(f"⏱️  TTL: {ttl} seconds ({ttl // 60} minutes)")
            
            try:
                data = json.loads(value)
                print(f"📝 Business: {data.get('business_name', 'Unknown')}")
                print(f"📅 Cached: {data.get('timestamp', 'Unknown')}")
                print(f"🌐 Platforms: {len(data.get('presence', []))}")
                
                # Show platform results
                for platform in data.get('presence', []):
                    print(f"   • {platform['query']}: {len(platform.get('results', []))} results")
                    
            except Exception as e:
                print(f"❌ Error parsing: {e}")
                print(f"📄 Raw: {value[:200]}...")
    else:
        print("\n❌ No Jina data cached in Redis")
    
    # Also check Celery tasks
    print("\n\n📋 CELERY TASK KEYS:")
    print("-" * 60)
    celery_keys = [k for k in all_keys if 'celery' in k.lower()]
    for key in celery_keys[:10]:  # Show first 10
        print(f"• {key}")

if __name__ == "__main__":
    view_redis_data()