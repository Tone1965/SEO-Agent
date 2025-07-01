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

This is the **SEO Agent System** - a complete AI-powered website generation platform that uses 10 specialized AI agents with advanced agentic capabilities including memory, error recovery, monitoring, and coordination to create unique, SEO-optimized websites for local service businesses.

### Core Technology Stack
- **Backend**: Python with Flask and Celery
- **AI Models**: Claude Sonnet 4 + OpenAI GPT-4
- **Frontend**: HTML5/CSS3/JavaScript with Alpine.js
- **Database**: Supabase (PostgreSQL) + SQLite for agent data
- **Coordination**: Redis for task queues and inter-agent communication
- **Monitoring**: Prometheus metrics + custom performance tracking
- **Deployment**: Docker + Digital Ocean/Netlify/Vercel
- **Version Control**: Git + GitHub integration

### System Architecture

The system operates as a multi-agent orchestration platform with advanced coordination:

```
User Input → Python Orchestrator → Agent Coordinator → 10 AI Agents → Complete Website
                    ↓                      ↓              ↓
              Task Queues            Memory System    Error Recovery
                    ↓                      ↓              ↓
             Performance Monitor    Learning Pipeline  Health Monitoring
```

## File Structure and Responsibilities

### Core System Files

#### **Advanced Agentic Components** ⭐ NEW

#### `agent_memory.py` - **MEMORY & LEARNING SYSTEM**
- **Purpose**: Provides persistent memory and learning capabilities for AI agents
- **Key Classes**:
  - `AgentMemoryStore` - Persistent SQLite storage for agent memories
  - `ShortTermMemory` - Working memory for current tasks (TTL-based)
  - `SharedMemory` - Inter-agent knowledge sharing via Redis
  - `LearningPipeline` - Continuous improvement from outcomes
  - `AgentMemoryManager` - Main coordinator for all memory systems
- **Usage**: Enables agents to remember successful patterns, learn from failures, and improve over time
- **Dependencies**: SQLite, Redis, threading for concurrent access

#### `error_recovery.py` - **ERROR RECOVERY & RESILIENCE**
- **Purpose**: Provides automatic retry mechanisms, fallback strategies, and self-healing capabilities
- **Key Classes**:
  - `ErrorRecoveryEngine` - Main engine for error handling and recovery
  - `CircuitBreakerState` - Prevents cascade failures with circuit breaker pattern
  - `RetryConfig` - Configuration for exponential backoff retry logic
  - `FailureEvent` - Records and analyzes failure patterns
- **Usage**: Ensures system can recover from API failures, network issues, and other errors
- **Decorators**: `@with_retry` for automatic retry with circuit breaker support

#### `agent_monitor.py` - **PERFORMANCE MONITORING**
- **Purpose**: Real-time agent performance tracking, success/failure rates, and quality scores
- **Key Classes**:
  - `AgentPerformanceMonitor` - Main monitoring coordinator
  - `ResourceMonitor` - System resource usage tracking (CPU, memory, network)
  - `ExecutionRecord` - Individual agent execution tracking
  - `AgentMetrics` - Performance metrics aggregation
- **Usage**: Monitor agent health, track costs, measure quality, optimize performance
- **Integration**: Prometheus metrics, custom dashboards, alerting

#### `agent_coordinator.py` - **COORDINATION PROTOCOL**
- **Purpose**: Agent coordination, priority systems, resource allocation, and conflict resolution
- **Key Classes**:
  - `AgentCoordinator` - Main coordination system
  - `Task` - Task definition with priorities and dependencies
  - `Agent` - Agent registration and status management
  - `ResourcePool` - System resource allocation and management
  - `DeadlockDetector` - Prevents and resolves circular dependencies
- **Usage**: Orchestrate multiple agents working together efficiently, prevent conflicts
- **Advanced Features**: Priority queues, resource limits, deadlock detection

### Original Core System Files

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

# Background Tasks & Coordination
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Advanced Agentic Features
UPSTASH_REDIS_URL=your_upstash_redis_url  # For shared memory
QSTASH_TOKEN=your_qstash_token           # For async messaging

# Monitoring & Observability
SENTRY_DSN=your_sentry_dsn               # Error tracking
PROMETHEUS_PORT=8000                     # Metrics export

# Optional: Advanced Features
GITHUB_TOKEN=your_github_token
DOCKER_HOST=unix:///var/run/docker.sock
FIRECRAWL_API_KEY=your_firecrawl_key     # Web scraping
```

## Development Commands

```bash
# Install dependencies (recommended)
pip install -r requirements.txt

# Start required services
redis-server                              # Start Redis server
celery -A main.celery worker --loglevel=info  # Start Celery worker (separate terminal)

# Start development server
python main.py

# Testing individual components
python agent_memory.py                   # Test memory system
python error_recovery.py                 # Test error recovery
python agent_monitor.py                  # Test monitoring
python agent_coordinator.py              # Test coordination

# Advanced testing
python -m pytest tests/                  # Run full test suite
python -c "from main import *; test_system()"  # Quick system test

# Monitoring and debugging
python -c "from agent_monitor import *; monitor = AgentPerformanceMonitor(); print(monitor.get_system_performance_summary())"

# Type checking
mypy main.py agent_memory.py error_recovery.py agent_monitor.py agent_coordinator.py
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
- **Solution**: Error recovery system automatically handles this with exponential backoff
- **Files to Check**: `error_recovery.py` ErrorRecoveryEngine, `main.py` AIClient class
- **Debug**: Check circuit breaker state, retry configurations

#### 2. Memory Issues
- **Problem**: Large content generation causing memory errors
- **Solution**: Process content in chunks, implement streaming
- **Files to Check**: All agent classes in `main.py`, `agent_memory.py` for memory cleanup
- **Debug**: Monitor memory usage with `agent_monitor.py`

#### 3. Agent Coordination Failures
- **Problem**: Tasks stuck in queue, deadlocks, resource conflicts
- **Solution**: Check agent coordination system and resource allocation
- **Files to Check**: `agent_coordinator.py` DeadlockDetector, ResourcePool
- **Debug**: `coordinator.get_coordination_status()` for system health

#### 4. Performance Degradation
- **Problem**: Slow agent execution, high failure rates
- **Solution**: Monitor system performance and adjust configurations
- **Files to Check**: `agent_monitor.py` performance metrics
- **Debug**: Check success rates, execution times, resource usage

#### 5. Memory System Issues
- **Problem**: Agents not learning, memory not persisting
- **Solution**: Check Redis connection, SQLite database integrity
- **Files to Check**: `agent_memory.py` AgentMemoryStore, SharedMemory
- **Debug**: Test Redis connectivity, check database files

#### 6. Uniqueness Validation Failures
- **Problem**: Generated content too similar to previous
- **Solution**: Increase variation parameters, regenerate with new seed
- **Files to Check**: `unique_generator.py`

#### 7. Deployment Failures
- **Problem**: Docker or platform deployment errors
- **Solution**: Check configuration files, validate credentials
- **Files to Check**: `mcp_integration.py`

### Advanced Debug Mode
Enable detailed logging and monitoring:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable advanced monitoring
from agent_monitor import AgentPerformanceMonitor
from agent_coordinator import AgentCoordinator
from error_recovery import ErrorRecoveryEngine

monitor = AgentPerformanceMonitor()
coordinator = AgentCoordinator()
recovery = ErrorRecoveryEngine()

# Check system health
print("System Status:", coordinator.get_coordination_status())
print("Performance:", monitor.get_system_performance_summary())
print("Recovery Engine:", recovery.component_health)
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

1. **Understand the advanced architecture** - This is a complex multi-agent system with memory, error recovery, monitoring, and coordination
2. **Respect the AI model division** - Claude for analysis, OpenAI for creativity
3. **Maintain uniqueness** - Every generation must be different
4. **Focus on business value** - Generate websites that convert and rank
5. **Consider scalability** - Code for production deployment with monitoring
6. **Preserve integrations** - Don't break the agent orchestration or agentic features
7. **Test thoroughly** - Complex systems require comprehensive testing
8. **Monitor performance** - Use the built-in monitoring system to track agent health
9. **Handle errors gracefully** - The error recovery system should handle most failures automatically
10. **Leverage memory** - Agents learn and improve over time through the memory system

### Advanced Agentic Features Integration

When modifying agents or adding new functionality:

- **Use memory decorators** to enable learning: `@with_memory(memory_manager)`
- **Add error recovery** to critical functions: `@with_retry(retry_config, circuit_breaker_config)`
- **Include monitoring** for new agents: `@monitor_agent_execution(monitor, agent_id, agent_name)`
- **Register with coordinator** for task management: `coordinator.register_agent(agent)`

The system is designed to generate complete, professional websites automatically with enterprise-grade reliability. Any modifications should enhance this capability while maintaining the quality, uniqueness, and reliability standards.