# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the SEO Agent System repository.

## CRITICAL BEHAVIOR RULES - NEVER VIOLATE
- NEVER say "absolutely right" or similar definitive statements
- NEVER simplify complex problems - do deep technical analysis
- NEVER use fake data or shortcuts - always use real data and proper implementation
- NEVER repeat the same failed approaches in loops
- ALWAYS examine ALL files and configurations end-to-end before suggesting fixes
- ALWAYS approach problems like a senior developer with comprehensive research
- WHEN troubleshooting: analyze the ENTIRE system, not just surface symptoms

## Project Overview

This is the **SEO Agent System** - a complete AI-powered website generation platform that uses 10 specialized AI agents to create unique, SEO-optimized websites for local service businesses.

### Core Technology Stack
- **Backend**: Python with Flask and Celery
- **AI Models**: Claude Sonnet 4 + OpenAI GPT-4
- **Frontend**: HTML5/CSS3/JavaScript with Alpine.js
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Docker + Digital Ocean/Netlify/Vercel
- **Version Control**: Git + GitHub integration

### System Architecture

The system operates as a multi-agent orchestration platform:

```
User Input → Python Orchestrator → 10 AI Agents → Complete Website
```

## File Structure and Responsibilities

### Core System Files

#### `main.py` - **CORE ORCHESTRATION SYSTEM**
- **Purpose**: Main engine that coordinates all 10 AI agents
- **Key Classes**: 
  - `SEOAgentOrchestrator` - Main coordinator
  - Individual agent classes (MarketScannerAgent, ContentGeneratorAgent, etc.)
  - `AIClient` - Unified API client for Claude/OpenAI
- **Usage**: Run this file to start the Flask server and begin website generation
- **Dependencies**: Flask, Celery, Anthropic, OpenAI APIs

#### `funnel_system.py` - **MARKETING FUNNEL GENERATOR**
- **Purpose**: Creates marketing content using Schwartz/Halbert copywriting principles
- **Key Classes**:
  - `SchwartzHalbertCopywriter` - Advanced copywriting engine
  - `FunnelGenerator` - Complete funnel creation
  - `FunnelSystemOrchestrator` - Main coordinator
- **Generates**: Email sequences, landing pages, blog content, case studies, sales scripts
- **Unique Features**: Emotional triggers, objection handling, conversion optimization

#### `premium_design.py` - **MODERN DESIGN SYSTEM**
- **Purpose**: Creates cutting-edge design systems for 2025
- **Key Classes**:
  - `ColorPaletteGenerator` - Brand-appropriate color schemes
  - `TypographySystem` - Modern font combinations and scaling
  - `ComponentLibrary` - Reusable UI components
  - `AnimationSystem` - Modern interactions and animations
- **Output**: Complete design tokens, CSS variables, component specifications

#### `unique_generator.py` - **UNIQUENESS ENGINE**
- **Purpose**: Ensures every generated website is completely different
- **Key Classes**:
  - `ContentVariationEngine` - Content structure variations
  - `DesignVariationEngine` - Visual design variations
  - `KeywordVariationEngine` - SEO approach variations
  - `UniquenessValidator` - Prevents duplication
- **Critical Function**: Prevents Google penalties for duplicate content

#### `mcp_integration.py` - **ADVANCED INTEGRATIONS (OPTIONAL)**
- **Purpose**: Provides GitHub, Docker, and deployment integrations
- **Key Classes**:
  - `GitHubIntegration` - Repository management
  - `DockerIntegration` - Containerization
  - `DeploymentIntegration` - Multi-platform deployment
- **Advanced Features**: Auto-deployment, asset optimization, CI/CD pipeline

#### `frontend/index.html` - **WEB DASHBOARD**
- **Purpose**: User interface for website generation
- **Technology**: Alpine.js, Tailwind CSS, Font Awesome
- **Features**: Real-time progress tracking, agent status monitoring, results display
- **API Integration**: Communicates with Flask backend via REST API

## AI Model Usage Strategy

### Claude Sonnet 4 (Strategic Analysis)
**Used for complex reasoning and technical decisions:**
- Market analysis and competitor research
- SEO strategy and technical optimization
- Website architecture and blueprints
- Code generation and quality assurance
- Deployment planning

### OpenAI GPT-4 (Creative Content)
**Used for creative writing and marketing:**
- Blog posts and marketing copy
- Social media content
- Creative design variations
- Email sequences and sales copy

### Division of Labor
```
Complex Analysis → Claude Sonnet 4
Creative Writing → OpenAI GPT-4
Orchestration → Python
```

## Environment Variables Required

```bash
# AI API Keys
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Background Tasks
REDIS_URL=redis://localhost:6379/0

# Optional: Advanced Features
GITHUB_TOKEN=your_github_token
DOCKER_HOST=unix:///var/run/docker.sock
```

## Development Commands

```bash
# Start development server
python main.py

# Start Celery worker (separate terminal)
celery -A main.celery worker --loglevel=info

# Start Redis (if not running)
redis-server

# Install dependencies
pip install flask celery anthropic openai playwright beautifulsoup4 supabase docker gitpython

# Run tests (when implemented)
python -m pytest tests/

# Type checking
mypy main.py
```

## API Endpoints

### Main Generation API
- `POST /api/generate` - Start website generation
- `GET /api/status/<task_id>` - Check generation progress
- `GET /api/download/<task_id>` - Download completed website

### Request Format
```json
{
  "business_type": "HVAC Services",
  "location": "Birmingham, AL",
  "target_keywords": ["hvac repair", "air conditioning"],
  "competition_level": "medium",
  "budget_range": "$3,000-$5,000",
  "timeline": "2-4 weeks"
}
```

## Troubleshooting Guidelines

### Common Issues and Solutions

#### 1. API Rate Limits
- **Problem**: Claude/OpenAI API rate limit errors
- **Solution**: Implement exponential backoff, request queuing
- **Files to Check**: `main.py` AIClient class

#### 2. Memory Issues
- **Problem**: Large content generation causing memory errors
- **Solution**: Process content in chunks, implement streaming
- **Files to Check**: All agent classes in `main.py`

#### 3. Uniqueness Validation Failures
- **Problem**: Generated content too similar to previous
- **Solution**: Increase variation parameters, regenerate with new seed
- **Files to Check**: `unique_generator.py`

#### 4. Deployment Failures
- **Problem**: Docker or platform deployment errors
- **Solution**: Check configuration files, validate credentials
- **Files to Check**: `mcp_integration.py`

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### API Call Optimization
- Batch similar requests where possible
- Implement caching for repeated content
- Use async/await for concurrent operations

### Content Generation Efficiency
- Stream large content generation
- Implement content chunking
- Cache frequently used templates

### Database Optimization
- Index frequently queried fields
- Implement connection pooling
- Use read replicas for heavy queries

## Security Considerations

### API Key Management
- Store in environment variables only
- Never commit to version control
- Rotate keys regularly

### Input Validation
- Sanitize all user inputs
- Validate business types and locations
- Implement rate limiting

### Output Security
- Scan generated content for malicious code
- Validate all generated files
- Implement content security policies

## Testing Strategy

### Unit Tests
- Test individual agent functions
- Mock API calls for consistent testing
- Validate output formats

### Integration Tests
- Test complete generation pipeline
- Validate API endpoint responses
- Test error handling scenarios

### Performance Tests
- Load test API endpoints
- Measure generation times
- Monitor memory usage

## Deployment Guidelines

### Production Environment
- Use Docker containers
- Implement load balancing
- Set up monitoring and alerting
- Configure auto-scaling

### Staging Environment
- Mirror production configuration
- Use test API keys
- Implement comprehensive logging

## Monitoring and Analytics

### Key Metrics
- Website generation success rate
- Average generation time
- API usage and costs
- User engagement metrics

### Logging
- Log all API calls and responses
- Track generation pipeline steps
- Monitor error rates and types

## Business Logic

### Website Generation Flow
1. **User Input** → Configuration validation
2. **Market Analysis** → Claude API for competitor research
3. **Content Strategy** → Claude API for SEO planning
4. **Content Creation** → OpenAI API for writing
5. **Design System** → Automated design generation
6. **Code Assembly** → Python file operations
7. **Quality Check** → Validation and testing
8. **Deployment Prep** → Docker/platform configuration

### Uniqueness Strategy
Every website must be completely unique:
- Different content structures
- Varied design approaches
- Unique keyword targeting
- Distinct user experience flows

### SEO Optimization
- Technical SEO implementation
- Local search optimization
- Schema markup generation
- Core Web Vitals optimization

## Cost Management

### API Usage Optimization
- Monitor token usage per generation
- Implement cost alerts
- Optimize prompt efficiency

### Expected Costs per Website
- Claude API: $2-3
- OpenAI API: $2-3
- Infrastructure: $0.50
- **Total: ~$5-7 per website**

## Future Enhancements

### Planned Features
- Multiple language support
- Industry-specific templates
- Advanced A/B testing
- Real-time SEO monitoring
- Automated content updates

### Scalability Improvements
- Microservices architecture
- Kubernetes deployment
- Multi-region support
- Edge computing integration

---

## Important Notes for Claude Code

When working with this system:

1. **Always understand the full context** - This is a complex multi-agent system
2. **Respect the AI model division** - Claude for analysis, OpenAI for creativity
3. **Maintain uniqueness** - Every generation must be different
4. **Focus on business value** - Generate websites that convert and rank
5. **Consider scalability** - Code for production deployment
6. **Preserve integrations** - Don't break the agent orchestration
7. **Test thoroughly** - Complex systems require comprehensive testing

The system is designed to generate complete, professional websites automatically. Any modifications should enhance this capability while maintaining the quality and uniqueness standards.