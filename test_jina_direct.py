#!/usr/bin/env python3
"""
Debug existing Jina integration
"""
import os
import requests

# Test direct Jina call
jina_key = os.getenv('JINA_API_KEY', '')
print(f"JINA_API_KEY: {'SET' if jina_key else 'NOT SET'}")

if jina_key:
    headers = {"Authorization": f"Bearer {jina_key}"}
else:
    headers = {}
    print("WARNING: No API key, trying without auth")

# Test search
print("\n1. Testing Jina Search (s.jina.ai)...")
try:
    response = requests.get("https://s.jina.ai/plumber Birmingham", headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results: {len(data.get('results', []))}")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Failed: {e}")

# Test scrape
print("\n2. Testing Jina Scrape (r.jina.ai)...")
try:
    response = requests.get("https://r.jina.ai/https://example.com", headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Content length: {len(response.text)}")
        print(f"First 100 chars: {response.text[:100]}")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Failed: {e}")