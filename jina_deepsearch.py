"""
Jina DeepSearch Integration - Advanced AI-powered research
Uses Jina's ChatGPT-like API for comprehensive SEO analysis
"""
import os
import json
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class JinaDeepSearch:
    def __init__(self):
        self.api_key = os.getenv('JINA_API_KEY')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.base_url = "https://deepsearch.jina.ai/v1"
        
    def deep_research(self, query: str, research_type: str = "seo_analysis") -> Dict:
        """
        Perform deep research using Jina's AI agents
        
        Args:
            query: Research query (e.g., "plumber Birmingham AL competitive analysis")
            research_type: Type of research to perform
        """
        
        # Build research prompt based on type
        prompts = {
            "seo_analysis": f"""
                Perform a comprehensive SEO competitive analysis for: {query}
                
                Research tasks:
                1. Find top competitors across Google, Bing, Facebook, Reddit, Yelp
                2. Analyze their content strategies and keywords
                3. Identify content gaps and opportunities
                4. Check their domain authority and backlinks
                5. Find low-competition long-tail keywords
                6. Analyze local SEO factors if applicable
                
                Provide actionable insights with specific URLs and data.
            """,
            
            "keyword_research": f"""
                Deep keyword research for: {query}
                
                Find:
                1. Search volume estimates across platforms
                2. Competition difficulty scores
                3. Related semantic keywords
                4. Long-tail variations with commercial intent
                5. Question-based keywords
                6. Platform-specific trending keywords
                
                Include exact data and sources.
            """,
            
            "competitor_intel": f"""
                Competitor intelligence gathering for: {query}
                
                Analyze:
                1. Top 10 competitors' online presence
                2. Their content publishing frequency
                3. Social media engagement rates
                4. Customer reviews and complaints
                5. Pricing strategies if visible
                6. Unique selling propositions
                
                Provide specific examples and URLs.
            """
        }
        
        data = {
            "model": "jina-deepsearch-v1",
            "messages": [
                {
                    "role": "user",
                    "content": prompts.get(research_type, prompts["seo_analysis"])
                }
            ],
            "stream": False,
            "reasoning_effort": "high",
            "budget_tokens": 50000,  # Enough for thorough research
            "max_returned_urls": "20",
            "max_attempts": 32,
            "team_size": 3,  # Multiple agents working in parallel
            "search_provider": "google"  # Can also use "arxiv", "bing", etc.
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=120  # Give it time to research
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract key information
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'visited_urls': result.get('visitedURLs', []),
                    'read_urls': result.get('readURLs', []),
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                    'citations': self._extract_citations(result)
                }
            else:
                logger.error(f"DeepSearch API error: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"DeepSearch request failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_citations(self, result: Dict) -> List[Dict]:
        """Extract citations from the response"""
        citations = []
        
        # Check for annotations in the response
        choices = result.get('choices', [])
        if choices and 'message' in choices[0]:
            message = choices[0]['message']
            if 'annotations' in message:
                for annotation in message['annotations']:
                    if annotation['type'] == 'url_citation':
                        citations.append(annotation['url_citation'])
        
        return citations
    
    def multi_platform_seo_analysis(self, keyword: str, location: str = "") -> Dict:
        """
        Use DeepSearch to analyze SEO across all platforms at once
        """
        
        query = f"{keyword} {location} competitive analysis across Google, Bing, Yahoo, Facebook, Reddit, Twitter, LinkedIn, YouTube, TikTok, Instagram, Yelp"
        
        # Let Jina's AI do all the heavy lifting
        research = self.deep_research(query, "seo_analysis")
        
        if research['success']:
            # Parse the AI's findings
            return {
                'success': True,
                'analysis': research['content'],
                'sources': research['visited_urls'],
                'tokens_used': research['tokens_used']
            }
        else:
            return research
    
    def find_content_gaps(self, business_type: str, location: str) -> Dict:
        """
        Discover content gaps and opportunities
        """
        
        query = f"{business_type} in {location} content gaps opportunities competitor weaknesses"
        
        research = self.deep_research(query, "competitor_intel")
        
        if research['success']:
            return {
                'success': True,
                'gaps': research['content'],
                'competitor_urls': research['read_urls'],
                'opportunities': self._parse_opportunities(research['content'])
            }
        else:
            return research
    
    def _parse_opportunities(self, content: str) -> List[Dict]:
        """Extract actionable opportunities from research content"""
        
        opportunities = []
        
        # Look for patterns indicating opportunities
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['opportunity', 'gap', 'missing', 'lacks', 'doesn\'t have']):
                opportunities.append({
                    'description': line.strip(),
                    'context': ' '.join(lines[max(0, i-1):min(len(lines), i+2)])
                })
        
        return opportunities[:10]  # Top 10 opportunities

    def keyword_difficulty_analysis(self, keywords: List[str], location: str = "") -> Dict:
        """
        Analyze keyword difficulty across multiple platforms
        """
        
        query = f"keyword difficulty analysis for: {', '.join(keywords)} in {location}"
        
        research = self.deep_research(query, "keyword_research")
        
        if research['success']:
            return {
                'success': True,
                'analysis': research['content'],
                'data_sources': research['visited_urls']
            }
        else:
            return research


# Embeddings for semantic search
class JinaEmbeddings:
    def __init__(self):
        self.api_key = os.getenv('JINA_API_KEY')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def get_embeddings(self, texts: List[str], images: List[str] = None) -> Dict:
        """
        Get multi-modal embeddings for texts and images
        """
        
        inputs = []
        
        # Add texts
        for text in texts:
            inputs.append({"text": text})
            
        # Add images if provided
        if images:
            for image in images:
                inputs.append({"image": image})
        
        data = {
            "model": "jina-embeddings-v4",
            "task": "text-matching",
            "late_chunking": True,
            "truncate": True,
            "input": inputs
        }
        
        try:
            response = requests.post(
                "https://api.jina.ai/v1/embeddings",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Embeddings API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Embeddings request failed: {e}")
            return None
    
    def semantic_keyword_matching(self, seed_keyword: str, candidate_keywords: List[str]) -> List[Dict]:
        """
        Find semantically related keywords using embeddings
        """
        
        # Get embeddings for all keywords
        all_keywords = [seed_keyword] + candidate_keywords
        embeddings_response = self.get_embeddings(all_keywords)
        
        if not embeddings_response:
            return []
            
        embeddings = embeddings_response.get('data', [])
        if len(embeddings) < 2:
            return []
            
        # Calculate similarity scores
        seed_embedding = embeddings[0]['embedding']
        results = []
        
        for i, candidate in enumerate(candidate_keywords):
            candidate_embedding = embeddings[i + 1]['embedding']
            
            # Cosine similarity
            similarity = self._cosine_similarity(seed_embedding, candidate_embedding)
            
            results.append({
                'keyword': candidate,
                'similarity': similarity,
                'relevance': 'HIGH' if similarity > 0.8 else 'MEDIUM' if similarity > 0.6 else 'LOW'
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
            
        return dot_product / (magnitude1 * magnitude2)