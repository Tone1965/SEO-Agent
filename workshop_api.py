"""
Workshop API endpoints for individual agent control
"""
from flask import Blueprint, request, jsonify
import json
import time
from typing import Dict, Any, List

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

# Initialize AI client
ai_client = AIClient()

@workshop_bp.route('/api/run-agent', methods=['POST'])
def run_agent():
    """Run a single agent with provided configuration"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        agent_name = data.get('agent_name')
        project = data.get('project', {})
        dependencies = data.get('dependencies', [])
        config = data.get('config', {})
        
        # Validate agent ID
        if agent_id not in AGENT_REGISTRY:
            return jsonify({
                'success': False,
                'error': f'Invalid agent ID: {agent_id}'
            }), 400
        
        # Get agent class
        AgentClass = AGENT_REGISTRY[agent_id]
        
        # Initialize agent
        agent = AgentClass(ai_client)
        
        # Prepare context from dependencies
        context = {
            'business_type': project.get('businessType', ''),
            'location': project.get('location', ''),
            'keywords': project.get('keywords', '').split(','),
            'project_config': project
        }
        
        # Add dependency outputs to context
        for dep in dependencies:
            dep_id = dep.get('id')
            dep_output = dep.get('output')
            if dep_id and dep_output:
                context[f'agent_{dep_id}_output'] = dep_output
        
        # Run the agent
        result = agent.run(context)
        
        # Format output based on agent type
        if isinstance(result, dict):
            output = json.dumps(result, indent=2)
        elif isinstance(result, list):
            output = '\n'.join([str(item) for item in result])
        else:
            output = str(result)
        
        return jsonify({
            'success': True,
            'output': output,
            'agent_id': agent_id,
            'agent_name': agent_name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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