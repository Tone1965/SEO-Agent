# =====================================
# MAIN.PY - CORE SEO AGENT SYSTEM
# =====================================
# This is the main orchestration system with 10 specialized AI agents
# Use this to generate complete SEO-optimized websites for local service businesses
# Each agent handles a specific aspect: market analysis, content, design, SEO, etc.
# Terry: This is your primary engine - run this to create entire websites automatically

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import os
from flask import Flask, request, jsonify, send_from_directory, send_file
from celery import Celery
import uuid
from website_generator import WebsiteFileGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectConfig:
    """Configuration for website generation project"""
    business_type: str
    location: str
    target_keywords: List[str]
    competition_level: str
    budget_range: str
    timeline: str
    unique_seed: str = None
    
    def __post_init__(self):
        if not self.unique_seed:
            self.unique_seed = str(uuid.uuid4())

class AIClient:
    """Unified AI client for Claude Sonnet 4 and OpenAI GPT-4"""
    
    def __init__(self):
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def claude_request(self, prompt: str, max_tokens: int = 4000) -> str:
        """Send request to Claude Sonnet 4"""
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.claude_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': max_tokens,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        async with self.session.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data
        ) as response:
            result = await response.json()
            return result['content'][0]['text']
    
    async def openai_request(self, prompt: str, model: str = "gpt-4") -> str:
        """Send request to OpenAI GPT-4"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 4000
        }
        
        async with self.session.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data
        ) as response:
            result = await response.json()
            return result['choices'][0]['message']['content']

class MarketScannerAgent:
    """Agent 1: Scans local market and competition"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Market Scanner"
    
    async def analyze_market(self, config: ProjectConfig) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        logger.info(f"Market Scanner analyzing {config.business_type} in {config.location}")
        
        prompt = f"""
        You are a professional market research analyst. Analyze the local {config.business_type} market in {config.location}.
        
        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "market_overview": {{
                "market_size": "estimated annual revenue",
                "demand_level": "high/medium/low",
                "growth_trend": "growing/stable/declining",
                "seasonality": "seasonal patterns description"
            }},
            "competitors": [
                {{
                    "name": "competitor name",
                    "website": "website if known",
                    "strengths": ["strength1", "strength2"],
                    "weaknesses": ["weakness1", "weakness2"],
                    "market_share": "estimated percentage",
                    "pricing_strategy": "premium/competitive/budget"
                }}
            ],
            "opportunities": [
                "specific market gap or opportunity",
                "underserved customer segment",
                "service differentiation opportunity"
            ],
            "target_demographics": {{
                "primary_age_range": "age range",
                "income_level": "income bracket",
                "property_type": "residential/commercial/both",
                "pain_points": ["main customer problems"]
            }},
            "pricing_insights": {{
                "average_service_cost": "price range",
                "premium_pricing_opportunity": "yes/no with explanation",
                "competitive_pricing_required": "yes/no with explanation"
            }},
            "digital_landscape": {{
                "seo_difficulty": "high/medium/low",
                "top_ranking_sites": ["domain1.com", "domain2.com"],
                "social_media_presence": "strong/weak in market",
                "online_review_importance": "critical/important/moderate"
            }},
            "recommended_strategy": {{
                "positioning": "how to position in market",
                "key_differentiators": ["unique selling point 1", "unique selling point 2"],
                "marketing_channels": ["recommended channels"],
                "content_themes": ["content topic 1", "content topic 2"]
            }}
        }}
        
        Competition level: {config.competition_level}
        Target keywords: {', '.join(config.target_keywords)}
        Budget range: {config.budget_range}
        
        Be specific and actionable. Base insights on real market conditions for {config.location}.
        """
        
        try:
            analysis_json = await self.ai_client.claude_request(prompt, max_tokens=4000)
            
            # Parse JSON response
            import json
            try:
                analysis_data = json.loads(analysis_json)
            except json.JSONDecodeError:
                # Fallback if Claude returns non-JSON
                analysis_data = {
                    "raw_analysis": analysis_json,
                    "status": "parsed_as_text"
                }
            
            logger.info("Market analysis completed successfully")
            
            return {
                'agent': self.name,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'market_analysis': analysis_data,
                'config_seed': config.unique_seed,
                'location': config.location,
                'business_type': config.business_type
            }
            
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return {
                'agent': self.name,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e),
                'config_seed': config.unique_seed
            }

class OpportunityAnalyzerAgent:
    """Agent 2: Identifies specific opportunities and niches"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Opportunity Analyzer"
    
    async def find_opportunities(self, market_data: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Find specific business opportunities"""
        prompt = f"""
        Based on this market analysis: {market_data['market_analysis']}
        
        For {config.business_type} in {config.location}, identify:
        
        1. Top 5 underserved niches
        2. Content gap opportunities 
        3. Keyword opportunities competitors are missing
        4. Local SEO opportunities
        5. Service differentiation opportunities
        6. Partnership opportunities
        7. Seasonal opportunities
        8. Technology advantages possible
        
        Budget range: {config.budget_range}
        Timeline: {config.timeline}
        
        Provide specific, actionable recommendations with implementation priority.
        """
        
        opportunities = await self.ai_client.claude_request(prompt)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'opportunities': opportunities,
            'market_context': market_data,
            'config_seed': config.unique_seed
        }

class BlueprintGeneratorAgent:
    """Agent 3: Creates comprehensive website blueprint"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Blueprint Generator"
    
    async def create_blueprint(self, opportunities: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Generate detailed website blueprint"""
        prompt = f"""
        Create a comprehensive website blueprint for {config.business_type} in {config.location}.
        
        Based on opportunities: {opportunities['opportunities']}
        
        Generate detailed blueprint including:
        
        1. SITE ARCHITECTURE:
           - Page hierarchy and navigation
           - URL structure for SEO
           - Internal linking strategy
           
        2. CONTENT STRATEGY:
           - Content pillars and themes
           - Blog content calendar (12 months)
           - Service page structure
           - FAQ and resource sections
           
        3. CONVERSION FUNNELS:
           - Lead generation funnels
           - Service inquiry funnels
           - Newsletter signup strategies
           
        4. TECHNICAL REQUIREMENTS:
           - Performance optimization
           - Mobile responsiveness
           - Local SEO technical setup
           - Schema markup requirements
           
        5. COMPETITIVE ADVANTAGES:
           - Unique value propositions
           - Differentiation strategies
           - Brand positioning
        
        Unique seed: {config.unique_seed}
        Make this completely unique and different from standard templates.
        """
        
        blueprint = await self.ai_client.claude_request(prompt)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'blueprint': blueprint,
            'opportunities_context': opportunities,
            'config_seed': config.unique_seed
        }

class ContentArchitectAgent:
    """Agent 4: Designs content architecture and semantic structure"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Content Architect"
    
    async def design_content_architecture(self, blueprint: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Design semantic content architecture"""
        prompt = f"""
        Design advanced content architecture for {config.business_type} website.
        
        Blueprint: {blueprint['blueprint']}
        
        Create:
        
        1. SEMANTIC CONTENT STRUCTURE:
           - Topic clusters and pillar pages
           - Entity relationships and connections
           - Keyword semantic mapping
           - Content depth requirements
           
        2. SEO CONTENT STRATEGY:
           - Primary/secondary keyword mapping
           - Long-tail keyword opportunities
           - Featured snippet optimization
           - Local search optimization
           
        3. CONTENT TYPES PLANNING:
           - Service pages with unique angles
           - Educational content series
           - Case studies and testimonials
           - Interactive content opportunities
           
        4. CONTENT CALENDAR:
           - Publishing schedule optimization
           - Seasonal content planning
           - Trending topic integration
           - Update and refresh schedule
           
        5. ADVANCED SEO ARCHITECTURE:
           - Schema markup implementation
           - Technical SEO content requirements
           - Link building content assets
           - Authority building content
        
        Target keywords: {config.target_keywords}
        Unique approach seed: {config.unique_seed}
        """
        
        architecture = await self.ai_client.openai_request(prompt)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'content_architecture': architecture,
            'blueprint_context': blueprint,
            'config_seed': config.unique_seed
        }

class ContentGeneratorAgent:
    """Agent 5: Generates all website content using advanced copywriting"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Content Generator"
    
    async def generate_content(self, architecture: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Generate all website content with advanced copywriting"""
        
        # Split content generation into chunks to avoid token limits
        content_sections = await self._generate_content_sections(architecture, config)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'generated_content': content_sections,
            'architecture_context': architecture,
            'config_seed': config.unique_seed
        }
    
    async def _generate_content_sections(self, architecture: Dict, config: ProjectConfig) -> Dict[str, str]:
        """Generate content in manageable sections"""
        
        sections = {}
        
        # Homepage content
        homepage_prompt = f"""
        Create compelling homepage content for {config.business_type} in {config.location}.
        
        Architecture guide: {architecture['content_architecture'][:1000]}...
        
        Include:
        1. Powerful headline with emotional hook
        2. Compelling value proposition
        3. Service overview with benefits
        4. Social proof section
        5. Clear call-to-action
        6. Local credibility indicators
        
        Use advanced copywriting principles:
        - Schwartz/Halbert emotional triggers
        - Problem-agitation-solution structure
        - Social proof integration
        - Urgency and scarcity elements
        
        Unique seed: {config.unique_seed}
        Make this completely different from competitors.
        """
        
        sections['homepage'] = await self.ai_client.claude_request(homepage_prompt)
        
        # Service pages content
        services_prompt = f"""
        Create detailed service pages content for {config.business_type}.
        
        For each main service, create:
        1. Service-specific headlines
        2. Detailed benefit explanations
        3. Process/methodology descriptions
        4. FAQ sections
        5. Pricing information approaches
        6. Local relevance connections
        
        Target keywords: {config.target_keywords}
        Location: {config.location}
        Unique approach: {config.unique_seed}
        """
        
        sections['services'] = await self.ai_client.claude_request(services_prompt)
        
        # About page content
        about_prompt = f"""
        Create compelling About page content that builds trust and authority.
        
        Include:
        1. Origin story with emotional connection
        2. Team expertise and credentials
        3. Local community involvement
        4. Mission and values alignment
        5. Unique methodology or approach
        6. Awards, certifications, recognition
        
        Business type: {config.business_type}
        Location: {config.location}
        Unique angle: {config.unique_seed}
        """
        
        sections['about'] = await self.ai_client.openai_request(about_prompt)
        
        return sections

class SEOOptimizerAgent:
    """Agent 6: Handles all SEO optimization and technical implementation"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "SEO Optimizer"
    
    async def optimize_seo(self, content: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Complete SEO optimization"""
        prompt = f"""
        Perform comprehensive SEO optimization for {config.business_type} website.
        
        Content to optimize: {str(content['generated_content'])[:2000]}...
        
        Provide:
        
        1. TECHNICAL SEO:
           - Complete meta tags for all pages
           - Schema markup (JSON-LD) for local business
           - XML sitemap structure
           - Robots.txt configuration
           - .htaccess optimization rules
           
        2. ON-PAGE SEO:
           - Title tag optimization (unique for each page)
           - Meta descriptions (compelling and keyword-rich)
           - Header tag hierarchy (H1-H6)
           - Image alt text suggestions
           - Internal linking strategy
           
        3. LOCAL SEO:
           - Google My Business optimization
           - Local schema markup
           - NAP consistency guidelines
           - Local citation opportunities
           - Local keyword optimization
           
        4. CONTENT SEO:
           - Keyword density optimization
           - LSI keyword integration
           - Featured snippet optimization
           - Long-tail keyword targeting
           - Content gap filling
           
        5. PERFORMANCE SEO:
           - Page speed optimization
           - Core Web Vitals improvements
           - Mobile optimization
           - Image optimization guidelines
        
        Location: {config.location}
        Keywords: {config.target_keywords}
        Unique implementation: {config.unique_seed}
        """
        
        seo_optimization = await self.ai_client.claude_request(prompt, max_tokens=4000)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'seo_optimization': seo_optimization,
            'content_context': content,
            'config_seed': config.unique_seed
        }

class DesignSystemAgent:
    """Agent 7: Creates modern, conversion-focused design system"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Design System"
    
    async def create_design_system(self, content: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Generate complete design system for 2025"""
        prompt = f"""
        Create a cutting-edge design system for {config.business_type} website in 2025.
        
        Business context: {config.business_type} in {config.location}
        
        Design requirements:
        
        1. VISUAL IDENTITY:
           - Modern color palette (primary, secondary, accent)
           - Typography system (headings, body, UI)
           - Logo concept and branding direction
           - Photography style guidelines
           
        2. UI/UX DESIGN:
           - Layout grid system
           - Component library (buttons, forms, cards)
           - Navigation design
           - Mobile-first responsive approach
           
        3. CONVERSION OPTIMIZATION:
           - CTA button designs and placement
           - Form design for maximum conversion
           - Trust signal placement
           - Social proof display methods
           
        4. 2025 DESIGN TRENDS:
           - Advanced CSS animations
           - Micro-interactions
           - Glassmorphism/Neumorphism elements
           - Advanced typography
           - Modern spacing and layout
           
        5. ACCESSIBILITY:
           - WCAG 2.1 AA compliance
           - Color contrast optimization
           - Screen reader optimization
           - Keyboard navigation
           
        6. TECHNICAL IMPLEMENTATION:
           - CSS custom properties
           - Component structure
           - Animation specifications
           - Responsive breakpoints
        
        Unique design seed: {config.unique_seed}
        Create something completely different and modern.
        """
        
        design_system = await self.ai_client.openai_request(prompt, model="gpt-4")
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'design_system': design_system,
            'content_context': content,
            'config_seed': config.unique_seed
        }

class CodeGeneratorAgent:
    """Agent 8: Generates clean, production-ready code"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Code Generator"
    
    async def generate_code(self, design: Dict, seo: Dict, content: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Generate complete website code"""
        
        # Generate code in sections to manage token limits
        code_sections = await self._generate_code_sections(design, seo, content, config)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'generated_code': code_sections,
            'design_context': design,
            'seo_context': seo,
            'config_seed': config.unique_seed
        }
    
    async def _generate_code_sections(self, design: Dict, seo: Dict, content: Dict, config: ProjectConfig) -> Dict[str, str]:
        """Generate code in manageable sections"""
        
        sections = {}
        
        # HTML structure
        html_prompt = f"""
        Generate semantic HTML5 structure for {config.business_type} website.
        
        Design system: {design['design_system'][:1000]}...
        SEO requirements: {seo['seo_optimization'][:1000]}...
        
        Include:
        1. Semantic HTML5 structure
        2. SEO-optimized meta tags
        3. Schema markup integration
        4. Accessibility attributes
        5. Performance optimization
        6. Mobile-first responsive structure
        
        Generate complete HTML for homepage with proper structure.
        Unique implementation: {config.unique_seed}
        """
        
        sections['html'] = await self.ai_client.claude_request(html_prompt)
        
        # CSS styles
        css_prompt = f"""
        Generate modern CSS for the website design system.
        
        Design specifications: {design['design_system'][:1500]}...
        
        Include:
        1. CSS custom properties for theming
        2. Modern layout with CSS Grid/Flexbox
        3. Responsive design breakpoints
        4. Advanced animations and transitions
        5. Component-based styling
        6. Performance-optimized CSS
        
        Generate production-ready CSS following BEM methodology.
        Unique styling approach: {config.unique_seed}
        """
        
        sections['css'] = await self.ai_client.openai_request(css_prompt)
        
        # JavaScript functionality
        js_prompt = f"""
        Generate modern JavaScript for website functionality.
        
        Requirements:
        1. Modern ES6+ JavaScript
        2. Performance optimization
        3. Accessibility enhancements
        4. Form validation and submission
        5. Smooth scrolling and animations
        6. Mobile touch optimizations
        7. SEO-friendly interactions
        
        Business type: {config.business_type}
        Unique functionality: {config.unique_seed}
        """
        
        sections['javascript'] = await self.ai_client.openai_request(js_prompt)
        
        return sections

class QualityAssuranceAgent:
    """Agent 9: Comprehensive testing and quality assurance"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Quality Assurance"
    
    async def perform_qa(self, code: Dict, seo: Dict, design: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Comprehensive quality assurance testing"""
        prompt = f"""
        Perform comprehensive QA testing for {config.business_type} website.
        
        Code to test: {str(code['generated_code'])[:1500]}...
        SEO optimization: {seo['seo_optimization'][:1000]}...
        
        Perform these QA checks:
        
        1. CODE QUALITY:
           - HTML validation and semantics
           - CSS performance and optimization
           - JavaScript best practices
           - Cross-browser compatibility
           - Mobile responsiveness testing
           
        2. SEO AUDIT:
           - Technical SEO compliance
           - Content optimization verification
           - Meta tag completeness
           - Schema markup validation
           - Performance impact assessment
           
        3. ACCESSIBILITY AUDIT:
           - WCAG 2.1 AA compliance
           - Screen reader compatibility
           - Keyboard navigation
           - Color contrast ratios
           - Alternative text completeness
           
        4. PERFORMANCE AUDIT:
           - Page load speed analysis
           - Core Web Vitals optimization
           - Image optimization verification
           - Code minification opportunities
           - Caching strategy verification
           
        5. CONVERSION OPTIMIZATION:
           - CTA placement and effectiveness
           - Form usability testing
           - Trust signal verification
           - User experience flow
           
        6. SECURITY AUDIT:
           - Form security validation
           - Content security policy
           - HTTPS implementation
           - Data protection compliance
        
        Provide detailed report with specific fixes and improvements.
        QA seed: {config.unique_seed}
        """
        
        qa_report = await self.ai_client.claude_request(prompt, max_tokens=4000)
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'qa_report': qa_report,
            'code_context': code,
            'seo_context': seo,
            'design_context': design,
            'config_seed': config.unique_seed
        }

class DeploymentAgent:
    """Agent 10: Handles deployment and launch optimization"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.name = "Deployment Specialist"
    
    async def prepare_deployment(self, qa_report: Dict, code: Dict, config: ProjectConfig) -> Dict[str, Any]:
        """Prepare comprehensive deployment strategy"""
        prompt = f"""
        Create deployment strategy for {config.business_type} website.
        
        QA Report: {qa_report['qa_report'][:1500]}...
        Code base: {str(code['generated_code'])[:1000]}...
        
        Provide complete deployment package:
        
        1. HOSTING SETUP:
           - Recommended hosting providers
           - Server configuration requirements
           - Domain setup and DNS configuration
           - SSL certificate implementation
           - CDN setup for performance
           
        2. DEPLOYMENT CHECKLIST:
           - Pre-launch testing checklist
           - File organization and structure
           - Database setup (if needed)
           - Environment configuration
           - Backup strategy implementation
           
        3. LAUNCH STRATEGY:
           - Soft launch testing plan
           - SEO launch checklist
           - Google Search Console setup
           - Analytics implementation
           - Social media integration
           
        4. POST-LAUNCH OPTIMIZATION:
           - Performance monitoring setup
           - SEO tracking implementation
           - Conversion tracking setup
           - A/B testing recommendations
           - Maintenance schedule
           
        5. MARKETING LAUNCH:
           - Local SEO activation
           - Social media announcement
           - Email marketing integration
           - PPC campaign setup
           - Content marketing launch
           
        6. MONITORING & MAINTENANCE:
           - Uptime monitoring
           - Security monitoring
           - Performance tracking
           - Content update schedule
           - SEO ranking monitoring
        
        Budget: {config.budget_range}
        Timeline: {config.timeline}
        Deployment seed: {config.unique_seed}
        """
        
        deployment_plan = await self.ai_client.openai_request(prompt, model="gpt-4")
        
        return {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'deployment_plan': deployment_plan,
            'qa_context': qa_report,
            'code_context': code,
            'config_seed': config.unique_seed
        }

class SEOAgentOrchestrator:
    """Main orchestrator that coordinates all 10 agents"""
    
    def __init__(self):
        self.ai_client = None
        self.agents = {}
        self.results = {}
    
    async def initialize(self):
        """Initialize AI client and all agents"""
        self.ai_client = AIClient()
        await self.ai_client.__aenter__()
        
        # Initialize all 10 agents
        self.agents = {
            'market_scanner': MarketScannerAgent(self.ai_client),
            'opportunity_analyzer': OpportunityAnalyzerAgent(self.ai_client),
            'blueprint_generator': BlueprintGeneratorAgent(self.ai_client),
            'content_architect': ContentArchitectAgent(self.ai_client),
            'content_generator': ContentGeneratorAgent(self.ai_client),
            'seo_optimizer': SEOOptimizerAgent(self.ai_client),
            'design_system': DesignSystemAgent(self.ai_client),
            'code_generator': CodeGeneratorAgent(self.ai_client),
            'quality_assurance': QualityAssuranceAgent(self.ai_client),
            'deployment': DeploymentAgent(self.ai_client)
        }
        
        logger.info("All 10 SEO agents initialized successfully")
    
    async def generate_complete_website(self, config: ProjectConfig) -> Dict[str, Any]:
        """Run all agents in sequence to generate complete website"""
        
        try:
            logger.info(f"Starting website generation for {config.business_type} in {config.location}")
            
            # Agent 1: Market Analysis
            logger.info("Running Market Scanner Agent...")
            market_data = await self.agents['market_scanner'].analyze_market(config)
            self.results['market_data'] = market_data
            
            # Agent 2: Opportunity Analysis
            logger.info("Running Opportunity Analyzer Agent...")
            opportunities = await self.agents['opportunity_analyzer'].find_opportunities(market_data, config)
            self.results['opportunities'] = opportunities
            
            # Agent 3: Blueprint Generation
            logger.info("Running Blueprint Generator Agent...")
            blueprint = await self.agents['blueprint_generator'].create_blueprint(opportunities, config)
            self.results['blueprint'] = blueprint
            
            # Agent 4: Content Architecture
            logger.info("Running Content Architect Agent...")
            architecture = await self.agents['content_architect'].design_content_architecture(blueprint, config)
            self.results['architecture'] = architecture
            
            # Agent 5: Content Generation
            logger.info("Running Content Generator Agent...")
            content = await self.agents['content_generator'].generate_content(architecture, config)
            self.results['content'] = content
            
            # Agent 6: SEO Optimization
            logger.info("Running SEO Optimizer Agent...")
            seo = await self.agents['seo_optimizer'].optimize_seo(content, config)
            self.results['seo'] = seo
            
            # Agent 7: Design System
            logger.info("Running Design System Agent...")
            design = await self.agents['design_system'].create_design_system(content, config)
            self.results['design'] = design
            
            # Agent 8: Code Generation
            logger.info("Running Code Generator Agent...")
            code = await self.agents['code_generator'].generate_code(design, seo, content, config)
            self.results['code'] = code
            
            # Agent 9: Quality Assurance
            logger.info("Running Quality Assurance Agent...")
            qa = await self.agents['quality_assurance'].perform_qa(code, seo, design, config)
            self.results['qa'] = qa
            
            # Agent 10: Deployment
            logger.info("Running Deployment Agent...")
            deployment = await self.agents['deployment'].prepare_deployment(qa, code, config)
            self.results['deployment'] = deployment
            
            # GENERATE ACTUAL WEBSITE FILES
            logger.info("Generating actual website files...")
            website_generator = WebsiteFileGenerator()
            
            # Prepare agent results for file generation
            agent_results = {
                'market_scanner': market_data,
                'content_generator': content,
                'design_system': design,
                'seo_optimizer': seo,
                'deployment': deployment
            }
            
            # Generate complete website
            website_files = website_generator.generate_complete_website(
                agent_results, 
                asdict(config)
            )
            
            # Calculate real quality score based on QA results
            quality_score = 0
            if self.results.get('qa'):
                qa_data = self.results['qa']
                if isinstance(qa_data, dict):
                    # Calculate score from QA metrics
                    if qa_data.get('seo_score'):
                        quality_score += int(qa_data['seo_score'])
                    if qa_data.get('content_quality'):
                        quality_score += int(qa_data['content_quality'])
                    if qa_data.get('technical_score'):
                        quality_score += int(qa_data['technical_score'])
                    quality_score = min(quality_score // 3, 100)  # Average capped at 100
                else:
                    quality_score = 75  # Default if QA didn't provide structured data
            
            # Compile final results
            final_result = {
                'project_config': asdict(config),
                'generation_timestamp': datetime.now().isoformat(),
                'agent_results': self.results,
                'website_files': website_files,
                'success': website_files.get('success', False),
                'message': 'Complete website generated successfully by all 10 agents',
                'download_ready': website_files.get('success', False),
                'zip_path': website_files.get('zip_path'),
                'project_dir': website_files.get('project_dir'),
                'quality_score': quality_score
            }
            
            if website_files.get('success'):
                logger.info(f"Website files generated successfully at: {website_files.get('project_dir')}")
            else:
                logger.error(f"Website file generation failed: {website_files.get('error')}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error during website generation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': self.results
            }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.ai_client:
            await self.ai_client.__aexit__(None, None, None)

# Flask API for web interface
app = Flask(__name__)

# Workshop blueprints removed - using only main system

# Celery configuration for background tasks
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def generate_website_task(config_dict):
    """Celery task for background website generation"""
    async def run_generation():
        config = ProjectConfig(**config_dict)
        orchestrator = SEOAgentOrchestrator()
        
        try:
            await orchestrator.initialize()
            result = await orchestrator.generate_complete_website(config)
            return result
        finally:
            await orchestrator.cleanup()
    
    # Run async task in new event loop
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_generation())
    finally:
        loop.close()

@app.route('/')
def index():
    """Serve the frontend interface"""
    return send_from_directory('frontend', 'index.html')

# Workshop routes removed - using only main system at /

@app.route('/api/generate', methods=['POST'])
def generate_website():
    """API endpoint to start website generation"""
    try:
        data = request.json
        
        # Create project configuration
        config = ProjectConfig(
            business_type=data['business_type'],
            location=data['location'],
            target_keywords=data['target_keywords'],
            competition_level=data['competition_level'],
            budget_range=data['budget_range'],
            timeline=data['timeline']
        )
        
        # Start background task
        task = generate_website_task.delay(asdict(config))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Website generation started',
            'config': asdict(config)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/status/<task_id>')
def get_task_status(task_id):
    """Get status of website generation task"""
    task = generate_website_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be processed'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1)
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return jsonify(response)

@app.route('/api/download/<task_id>')
def download_website(task_id):
    """Download generated website files as ZIP"""
    task = generate_website_task.AsyncResult(task_id)
    
    if task.state == 'SUCCESS':
        result = task.result
        
        # Check if website files were generated successfully
        if result.get('download_ready') and result.get('zip_path'):
            zip_path = result['zip_path']
            
            # Verify file exists
            if os.path.exists(zip_path):
                try:
                    project_name = result.get('website_files', {}).get('project_name', 'website')
                    return send_file(
                        zip_path,
                        as_attachment=True,
                        download_name=f"{project_name}.zip",
                        mimetype='application/zip'
                    )
                except Exception as e:
                    logger.error(f"Error sending file: {str(e)}")
                    return jsonify({'error': 'Error downloading file'}), 500
            else:
                return jsonify({'error': 'Website files not found'}), 404
        else:
            return jsonify({
                'error': 'Website generation completed but files not ready for download',
                'details': result.get('website_files', {})
            }), 400
    else:
        return jsonify({
            'error': 'Website generation not completed yet',
            'state': task.state
        }), 400

@app.route('/api/preview/<task_id>')
def preview_website(task_id):
    """Get preview of generated website"""
    task = generate_website_task.AsyncResult(task_id)
    
    if task.state == 'SUCCESS':
        result = task.result
        if result.get('success') and result.get('agent_results'):
            # Return content for preview
            content_data = result['agent_results'].get('content', {})
            return jsonify({
                'success': True,
                'content_preview': content_data.get('content_sections', {}),
                'project_config': result.get('project_config', {}),
                'generation_timestamp': result.get('generation_timestamp')
            })
        else:
            return jsonify({'error': 'Website generation failed'}), 400
    else:
        return jsonify({
            'error': 'Website not ready for preview',
            'state': task.state
        }), 400

@app.route('/api/scrape', methods=['POST'])
def scrape_competitor():
    """Search for competitor across multiple platforms using Jina API"""
    try:
        data = request.json
        competitor_input = data.get('url', '').strip()
        
        if not competitor_input:
            return jsonify({'error': 'Competitor name or URL required'}), 400
            
        import requests
        import redis
        from urllib.parse import urlparse
        jina_api_key = os.getenv('JINA_API_KEY', '')
        headers = {"Authorization": f"Bearer {jina_api_key}"} if jina_api_key else {}
        
        # Connect to Redis
        redis_client = redis.Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )
        
        # Extract business name from URL or use as-is
        if competitor_input.startswith('http'):
            parsed = urlparse(competitor_input)
            domain = parsed.netloc.replace('www.', '')
            business_name = domain.split('.')[0]
        else:
            business_name = competitor_input
            
        # Check Redis cache first
        cache_key = f"jina:competitor:{business_name.lower().replace(' ', '_')}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            logger.info(f"Found cached data for {business_name}")
            return jsonify(json.loads(cached_data))
            
        # Search across multiple platforms with async parallel processing
        search_queries = [
            f"{business_name} reviews",
            f"{business_name} Facebook",
            f"{business_name} Reddit",
            f"{business_name} complaints BBB",
            f"{business_name} Yelp"
        ]
        
        all_results = []
        
        # If no API key, skip search and just scrape the main site
        if not jina_api_key:
            logger.warning("No Jina API key - skipping multi-platform search")
        else:
            import concurrent.futures
            import re
            
            def search_single_query(query):
                """Search a single query with timeout management"""
                try:
                    search_url = f"https://s.jina.ai/{query}"
                    response = requests.get(search_url, headers=headers, timeout=10)  # Reduced timeout per query
                    if response.status_code == 200:
                        # Parse text results from Jina
                        content = response.text
                        results = []
                        # Extract result blocks using regex
                        # Find all result entries [1], [2], etc.
                        entries = re.findall(r'\[(\d+)\] Title: (.+?)\n\[(?:\d+)\] URL Source: (.+?)\n(?:\[(?:\d+)\] Description: (.+?)\n)?', content, re.DOTALL)
                        
                        for entry in entries[:3]:  # Top 3 results
                            num, title, url, desc = entry
                            results.append({
                                'title': title.strip(),
                                'url': url.strip(),
                                'description': desc.strip() if desc else ''
                            })
                        return {
                            'query': query,
                            'results': results
                        }
                    elif response.status_code == 401:
                        logger.error("Jina authentication failed - check API key")
                        return None
                except requests.exceptions.Timeout:
                    logger.warning(f"Search timed out for query: {query}")
                    return {'query': query, 'results': [], 'error': 'timeout'}
                except Exception as e:
                    logger.error(f"Jina search error for {query}: {e}")
                    return {'query': query, 'results': [], 'error': str(e)}
            
            # Execute searches in parallel with ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all queries at once
                future_to_query = {executor.submit(search_single_query, query): query for query in search_queries}
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_query, timeout=15):
                    result = future.result()
                    if result and result is not None:
                        all_results.append(result)
                
        # Also scrape their main site if URL provided
        main_site_content = ""
        if competitor_input.startswith('http'):
            try:
                scrape_url = f"https://r.jina.ai/{competitor_input}"
                response = requests.get(scrape_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    main_site_content = response.text[:1000]
            except:
                pass
        
        result_data = {
            'success': True,
            'business_name': business_name,
            'main_site': main_site_content,
            'presence': all_results,
            'summary': f"Found {len(all_results)} platform results for {business_name}",
            'cached': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in Redis with 1 hour TTL
        redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(result_data)
        )
        logger.info(f"Cached data for {business_name} in Redis")
        
        return jsonify(result_data)
            
    except Exception as e:
        logger.error(f"Error in scrape_competitor: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/keywords', methods=['POST'])
def discover_keywords():
    """Discover semantic and long-tail keywords using Jina"""
    try:
        data = request.json
        seed_keyword = data.get('keyword', '').strip()
        location = data.get('location', '').strip()
        
        if not seed_keyword:
            return jsonify({'error': 'Keyword required'}), 400
            
        # Import and use jina_complete
        from jina_complete import JinaComplete
        jina = JinaComplete()
        
        # Get semantic keywords
        semantic_keywords = jina.find_semantic_keywords(seed_keyword, location)[:10]
        
        # Get long-tail keywords
        longtail_keywords = jina.find_longtail_keywords(seed_keyword, location)[:15]
        
        # Find golden opportunities
        all_keywords = semantic_keywords + longtail_keywords
        golden = [kw for kw in all_keywords if kw.get('opportunity_score', 0) > 70]
        golden.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'seed_keyword': seed_keyword,
            'location': location,
            'semantic_keywords': semantic_keywords,
            'longtail_keywords': longtail_keywords,
            'golden_opportunities': golden[:10],
            'total_found': len(all_keywords)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis-data')
def view_redis_data():
    """View all Jina data stored in Redis"""
    try:
        import redis
        redis_client = redis.Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )
        
        # Get all keys matching our pattern
        keys = redis_client.keys('jina:*')
        
        data = {}
        for key in keys:
            ttl = redis_client.ttl(key)
            value = redis_client.get(key)
            
            try:
                data[key] = {
                    'data': json.loads(value) if value else None,
                    'ttl_seconds': ttl,
                    'expires_in': f"{ttl // 60} minutes" if ttl > 0 else 'expired'
                }
            except:
                data[key] = {
                    'raw': value,
                    'ttl_seconds': ttl
                }
        
        return jsonify({
            'total_keys': len(keys),
            'redis_data': data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-platforms', methods=['POST'])
def analyze_platforms():
    """Analyze keyword across multiple platforms"""
    try:
        data = request.json
        keyword = data.get('keyword', '').strip()
        location = data.get('location', '').strip()
        
        if not keyword:
            return jsonify({'error': 'Keyword required'}), 400
            
        from jina_complete import JinaComplete
        jina = JinaComplete()
        
        # Multi-platform content gap analysis
        gaps = jina.analyze_content_gaps_multi_platform(keyword, location)
        
        # Calculate difficulty across platforms
        difficulty = jina.calculate_multi_platform_difficulty(keyword, location)
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'location': location,
            'content_gaps': gaps,
            'platform_difficulty': difficulty,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Platform analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/monitor-brand', methods=['POST'])
def monitor_brand():
    """Monitor brand mentions across platforms"""
    try:
        data = request.json
        brand_names = data.get('brands', [])
        
        if not brand_names:
            return jsonify({'error': 'Brand names required'}), 400
            
        from jina_complete import JinaComplete
        jina = JinaComplete()
        
        # Monitor brand mentions (converted from async)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        mentions = loop.run_until_complete(jina.monitor_brand_mentions(brand_names))
        loop.close()
        
        return jsonify({
            'success': True,
            'brand_mentions': mentions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Brand monitoring error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'SEO Agent System'
    })

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=5000)