"""
DeepSearch API Endpoint - Add this to main.py
"""

@app.route('/api/deepsearch', methods=['POST'])
def deep_search():
    """Advanced AI-powered research using Jina DeepSearch"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        research_type = data.get('type', 'seo_analysis')
        
        if not query:
            return jsonify({'error': 'Query required'}), 400
            
        import redis
        from jina_deepsearch import JinaDeepSearch
        
        # Connect to Redis
        redis_client = redis.Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )
        
        # Check Redis cache
        cache_key = f"deepsearch:{research_type}:{query.lower().replace(' ', '_')}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            logger.info(f"Found cached DeepSearch data")
            cached_result = json.loads(cached_data)
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        # Perform DeepSearch
        deep_search = JinaDeepSearch()
        logger.info(f"Starting DeepSearch: {query}")
        
        if research_type == 'competitor':
            result = deep_search.multi_platform_seo_analysis(query, "")
        elif research_type == 'keywords':
            result = deep_search.keyword_difficulty_analysis([query], "")
        elif research_type == 'gaps':
            # Extract business type and location
            parts = query.split(' in ')
            business_type = parts[0] if parts else query
            location = parts[1] if len(parts) > 1 else ""
            result = deep_search.find_content_gaps(business_type, location)
        else:
            result = deep_search.deep_research(query, research_type)
        
        if result.get('success'):
            # Store in Redis with 2 hour TTL for expensive DeepSearch
            redis_client.setex(
                cache_key,
                7200,  # 2 hours
                json.dumps(result)
            )
            logger.info(f"DeepSearch completed, used {result.get('tokens_used', 0)} tokens")
            
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error in deep_search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-simple', methods=['POST'])
def search_simple():
    """Simple fast search using basic Jina search API"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query required'}), 400
            
        from jina_complete import JinaComplete
        jina = JinaComplete()
        
        # Single fast search
        results = jina.search(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results.get('results', [])[:10],
            'count': len(results.get('results', []))
        })
            
    except Exception as e:
        logger.error(f"Error in search_simple: {str(e)}")
        return jsonify({'error': str(e)}), 500