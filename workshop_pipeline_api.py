"""
Workshop Pipeline API - Connects live data to agent pipeline with user control
"""

from flask import Blueprint, request, jsonify
import asyncio
import json
from typing import Dict, Any
import logging
from datetime import datetime

# Import the data coordinator
from data_coordinator import DataCoordinator, LiveMarketData

# Import AI client from main
from main import AIClient

logger = logging.getLogger(__name__)

workshop_pipeline_bp = Blueprint('workshop_pipeline', __name__)

# Initialize components
data_coordinator = DataCoordinator()
ai_client = AIClient()

# Agent registry with their specific prompts
AGENT_REGISTRY = {
    'data_gatherer': {
        'name': 'Data Gatherer',
        'model': 'claude',
        'prompt_template': """You are gathering live market data for {service_type} in {location}.
        
Analyze the following search results and competitor data:
{live_data}

Extract and summarize:
1. Top 10 competitors with their strengths/weaknesses
2. Market gaps and opportunities
3. Common pricing strategies
4. Service offerings that are missing
5. Local optimization opportunities

Format as a clear, actionable report."""
    },
    
    'market_scanner': {
        'name': 'Market Scanner',
        'model': 'claude',
        'prompt_template': """You are the Market Scanner analyzing {service_type} in {location}.

Based on this live data:
{live_data}

Previous data gathering showed:
{previous_outputs}

Provide:
1. Competition difficulty score (1-10)
2. Weak competitors we can outrank quickly
3. Strong competitors and why they rank well
4. Specific opportunities for quick wins
5. Recommended approach to dominate this market

Be specific with URLs and examples."""
    },
    
    'seo_strategist': {
        'name': 'SEO Strategist',
        'model': 'claude',
        'prompt_template': """You are the SEO Strategist for {service_type} in {location}.

Live market data:
{live_data}

Market analysis:
{previous_outputs}

Create an SEO strategy including:
1. Primary keyword target: {service_type} {location}
2. 10 long-tail keywords with search intent
3. Content topics that competitors miss
4. Technical SEO priorities
5. Link building opportunities
6. Local SEO tactics

Focus on actionable tactics that will work within 14 days."""
    },
    
    'content_generator': {
        'name': 'Content Generator',
        'model': 'openai',
        'prompt_template': """You are creating content for {service_type} in {location}.

Market data and SEO strategy:
{previous_outputs}

Generate:
1. Homepage H1 and title tag
2. Homepage opening paragraph (150 words)
3. 5 service page titles
4. 3 blog post titles addressing customer questions
5. Meta descriptions for each

Make content compelling, local-focused, and conversion-optimized.
Include urgency and trust signals."""
    },
    
    'website_architect': {
        'name': 'Website Architect',
        'model': 'claude',
        'prompt_template': """You are the Website Architect for {service_type} in {location}.

Based on all previous analysis:
{previous_outputs}

Design:
1. Site structure (pages and hierarchy)
2. URL structure
3. Internal linking strategy
4. Call-to-action placement
5. Mobile-first considerations
6. Page speed optimization priorities

Output a clear sitemap and technical implementation plan."""
    }
}

@workshop_pipeline_bp.route('/api/workshop/run-agent', methods=['POST'])
def run_agent():
    """Run a specific agent in the pipeline with live data"""
    try:
        data = request.json
        agent_id = data.get('agentId')
        service_type = data.get('serviceType')
        location = data.get('location')
        previous_outputs = data.get('previousOutputs', {})
        
        if agent_id not in AGENT_REGISTRY:
            return jsonify({'success': False, 'error': 'Invalid agent ID'}), 400
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            run_agent_async(agent_id, service_type, location, previous_outputs)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

async def run_agent_async(agent_id: str, service_type: str, location: str, previous_outputs: Dict) -> Dict:
    """Async agent execution with live data"""
    
    agent_config = AGENT_REGISTRY[agent_id]
    
    # Step 1: Get live data for data gatherer, or use previous data
    if agent_id == 'data_gatherer':
        # Gather fresh live data
        live_data = await data_coordinator.gather_live_data(
            keyword=service_type,
            location=location
        )
        live_data_formatted = data_coordinator.format_for_agent('DataGatherer', live_data)
    else:
        # Use data from previous agents
        if 'data_gatherer' in previous_outputs:
            live_data_formatted = previous_outputs['data_gatherer'].get('liveData', {})
        else:
            # Fallback: gather fresh data
            live_data = await data_coordinator.gather_live_data(service_type, location)
            live_data_formatted = data_coordinator.format_for_agent(agent_config['name'], live_data)
    
    # Step 2: Prepare the prompt
    prompt = agent_config['prompt_template'].format(
        service_type=service_type,
        location=location,
        live_data=json.dumps(live_data_formatted, indent=2),
        previous_outputs=json.dumps(previous_outputs, indent=2) if previous_outputs else "None"
    )
    
    # Step 3: Call the appropriate AI model
    async with ai_client as client:
        if agent_config['model'] == 'claude':
            output = await client.claude_request(prompt)
        else:
            output = await client.openai_request(prompt)
    
    return {
        'success': True,
        'output': output,
        'liveData': live_data_formatted,
        'agentId': agent_id,
        'agentName': agent_config['name']
    }

@workshop_pipeline_bp.route('/api/workshop/validate-opportunity', methods=['POST'])
def validate_opportunity():
    """Quick validation of an opportunity before running full pipeline"""
    try:
        data = request.json
        service_type = data.get('serviceType')
        location = data.get('location')
        
        # Run async validation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get live data
        live_data = loop.run_until_complete(
            data_coordinator.gather_live_data(service_type, location)
        )
        loop.close()
        
        # Return validation results
        return jsonify({
            'success': True,
            'validation': {
                'opportunityScore': live_data.opportunity_score,
                'difficulty': live_data.difficulty_level,
                'monthlyRevenue': live_data.monthly_revenue_potential,
                'competitorCount': len(live_data.competitor_data),
                'weakCompetitors': len(live_data.weak_competitors),
                'marketGaps': live_data.market_gaps
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating opportunity: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workshop_pipeline_bp.route('/api/workshop/save-project', methods=['POST'])
def save_project():
    """Save the complete project with all agent outputs"""
    try:
        data = request.json
        project_name = data.get('projectName')
        agent_outputs = data.get('agentOutputs')
        
        # Save to file or database
        project_data = {
            'name': project_name,
            'serviceType': data.get('serviceType'),
            'location': data.get('location'),
            'timestamp': str(datetime.now()),
            'agentOutputs': agent_outputs
        }
        
        # Create projects directory if it doesn't exist
        import os
        os.makedirs('projects', exist_ok=True)
        
        # Save to JSON file
        filename = f"projects/{project_name.replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Project saved as {filename}'
        })
        
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500