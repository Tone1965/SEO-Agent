"""
Workshop API - Connects live data to agent pipeline with user control
"""
from flask import Blueprint, request, jsonify
import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import logging

# Import the data coordinator
from data_coordinator import DataCoordinator, LiveMarketData

# Import existing agent classes from main.py
from main import (
    MarketScannerAgent,
    OpportunityAnalyzerAgent,
    BlueprintGeneratorAgent,
    ContentArchitectAgent,
    ContentGeneratorAgent,
    SEOOptimizerAgent,
    DesignSystemAgent,
    CodeGeneratorAgent,
    QualityAssuranceAgent,
    DeploymentAgent,
    AIClient
)

logger = logging.getLogger(__name__)

workshop_bp = Blueprint('workshop', __name__)

# Agent registry mapping IDs to classes
AGENT_REGISTRY = {
    1: MarketScannerAgent,
    2: OpportunityAnalyzerAgent,
    3: BlueprintGeneratorAgent,
    4: ContentArchitectAgent,
    5: ContentGeneratorAgent,
    6: SEOOptimizerAgent,
    7: DesignSystemAgent,
    8: CodeGeneratorAgent,
    9: QualityAssuranceAgent,
    10: DeploymentAgent
}

# Initialize components
data_coordinator = DataCoordinator()
ai_client = AIClient()

@workshop_bp.route('/api/workshop/run-agent', methods=['POST'])
def run_agent():
    """Run a specific agent in the pipeline with live data"""
    try:
        data = request.json
        agent_id = data.get('agentId')
        service_type = data.get('serviceType')
        location = data.get('location')
        previous_outputs = data.get('previousOutputs', {})
        
        # Map string agent IDs to numeric IDs for legacy agents
        agent_id_map = {
            'data_gatherer': 1,
            'market_scanner': 1,
            'seo_strategist': 6,
            'content_generator': 5,
            'website_architect': 3
        }
        
        numeric_id = agent_id_map.get(agent_id)
        
        if not numeric_id or numeric_id not in AGENT_REGISTRY:
            return jsonify({'success': False, 'error': 'Invalid agent ID'}), 400
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            run_agent_async(agent_id, numeric_id, service_type, location, previous_outputs)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

async def run_agent_async(agent_id: str, numeric_id: int, service_type: str, location: str, previous_outputs: Dict) -> Dict:
    """Async agent execution with live data"""
    
    # Step 1: Get live data
    if agent_id == 'data_gatherer':
        # Gather fresh live data
        live_data = await data_coordinator.gather_live_data(
            keyword=service_type,
            location=location
        )
        live_data_formatted = {
            'keyword': live_data.keyword,
            'location': live_data.location,
            'competitors': live_data.competitor_data,
            'market_gaps': live_data.market_gaps,
            'opportunity_score': live_data.opportunity_score,
            'weak_competitors': len(live_data.weak_competitors),
            'difficulty': live_data.difficulty_level
        }
    else:
        # Use data from previous agents
        if 'data_gatherer' in previous_outputs:
            live_data_formatted = previous_outputs['data_gatherer'].get('liveData', {})
        else:
            # Fallback: gather fresh data
            live_data = await data_coordinator.gather_live_data(service_type, location)
            agent_names = {1: 'MarketScanner', 6: 'SEOStrategist', 5: 'ContentGenerator', 3: 'WebsiteArchitect'}
            live_data_formatted = data_coordinator.format_for_agent(agent_names.get(numeric_id, 'MarketScanner'), live_data)
    
    # Step 2: Get agent class and run with live data
    AgentClass = AGENT_REGISTRY[numeric_id]
    agent = AgentClass(ai_client)
    
    # Prepare context with live data
    context = {
        'business_type': service_type,
        'location': location,
        'keywords': [service_type],
        'live_data': live_data_formatted,
        'previous_outputs': previous_outputs
    }
    
    # Run the agent
    try:
        result = await agent.run_async(context) if hasattr(agent, 'run_async') else agent.run(context)
        
        # Format output
        if isinstance(result, dict):
            output = json.dumps(result, indent=2)
        elif isinstance(result, list):
            output = '\n'.join([str(item) for item in result])
        else:
            output = str(result)
            
        return {
            'success': True,
            'output': output,
            'liveData': live_data_formatted,
            'agentId': agent_id,
            'agentName': agent_id.replace('_', ' ').title()
        }
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        return {
            'success': False,
            'error': str(e),
            'agentId': agent_id
        }

@workshop_bp.route('/api/save-workflow', methods=['POST'])
def save_workflow():
    """Save the current workflow state"""
    try:
        data = request.json
        workflow_id = f"workflow_{int(time.time())}"
        
        # In production, save to database
        # For now, return success
        return jsonify({
            'success': True,
            'workflow_id': workflow_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workshop_bp.route('/api/load-workflow/<workflow_id>', methods=['GET'])
def load_workflow(workflow_id):
    """Load a saved workflow"""
    try:
        # In production, load from database
        # For now, return example data
        return jsonify({
            'success': True,
            'workflow': {
                'project': {},
                'agents': [],
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workshop_bp.route('/api/agent-config/<int:agent_id>', methods=['GET'])
def get_agent_config(agent_id):
    """Get configuration options for a specific agent"""
    try:
        # Define config options per agent
        configs = {
            1: {  # Market Scanner
                'depth': {
                    'type': 'select',
                    'options': ['surface', 'medium', 'deep'],
                    'default': 'medium',
                    'description': 'How deep to analyze competitors'
                },
                'includeIndirect': {
                    'type': 'boolean',
                    'default': True,
                    'description': 'Include indirect competitors'
                }
            },
            2: {  # Opportunity Analyzer
                'focusAreas': {
                    'type': 'multiselect',
                    'options': ['keywords', 'content', 'technical', 'local'],
                    'default': ['keywords', 'content'],
                    'description': 'Areas to focus on'
                }
            },
            5: {  # Content Generator
                'tone': {
                    'type': 'select',
                    'options': ['professional', 'friendly', 'technical', 'casual'],
                    'default': 'professional',
                    'description': 'Writing tone'
                },
                'length': {
                    'type': 'select',
                    'options': ['concise', 'standard', 'comprehensive'],
                    'default': 'standard',
                    'description': 'Content length preference'
                }
            }
        }
        
        config = configs.get(agent_id, {})
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500