# GitWait MCP Server

**A Model Context Protocol server for managing git operations with timing controls, CI/CD pipeline waiting, and multi-agent coordination.**

## 🚀 Overview

GitWait provides sophisticated git operation management for the SEO Agent System, enabling:

- **CI/CD Pipeline Waiting** - Wait for builds/tests before proceeding
- **Queue Management** - Serialize git operations to prevent conflicts  
- **Rate Limiting** - Respect GitHub API limits
- **Multi-Agent Coordination** - Coordinate commits from multiple AI agents
- **Error Recovery** - Built-in retry and circuit breaker patterns
- **Documentation Protection** - Special handling for README.md/CLAUDE.md

## 🛠️ Installation

### 1. Install Dependencies
```bash
cd mcp_servers/
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export GITHUB_TOKEN="your_github_token"
export GITWAIT_WEBHOOK_URL="your_webhook_url"
export GITWAIT_CI_WAIT="300"      # Default CI wait time (seconds)
export GITWAIT_PR_WAIT="600"      # Default PR wait time (seconds) 
export GITWAIT_MAX_WAIT="3600"    # Maximum wait time (seconds)
export GITWAIT_RATE_LIMIT="60"    # Rate limit delay (seconds)
```

### 3. Configure MCP Client
Add to your MCP configuration:
```json
{
  "mcpServers": {
    "gitwait": {
      "command": "python",
      "args": ["mcp_servers/gitwait_server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITWAIT_CI_WAIT": "300"
      }
    }
  }
}
```

## 🔧 Available Tools

### 1. `wait_for_ci`
Wait for CI/CD pipeline to complete for a specific commit.

```json
{
  "repository": "owner/repo",
  "commit_sha": "abc123...",
  "timeout": 300
}
```

### 2. `wait_for_pr_merge`
Wait for a pull request to be merged.

```json
{
  "repository": "owner/repo", 
  "pr_number": 42,
  "timeout": 600
}
```

### 3. `queue_git_operation`
Queue a git operation with timing controls.

```json
{
  "command": "git",
  "args": ["push", "origin", "main"],
  "wait_type": "custom_delay",
  "wait_duration": 30,
  "priority": 2,
  "repository": "/path/to/repo"
}
```

### 4. `get_operation_status`
Get status of a queued or active operation.

```json
{
  "operation_id": "gitwait_1234567890"
}
```

### 5. `cancel_operation`
Cancel a queued or active operation.

```json
{
  "operation_id": "gitwait_1234567890"
}
```

### 6. `check_rate_limits`
Check GitHub API rate limits.

```json
{
  "repository": "owner/repo"
}
```

### 7. `get_queue_status`
Get current queue status and active operations.

```json
{}
```

## 🎯 Use Cases

### 1. **SEO Agent System Integration**
```python
from gitwait_integration import GitWaitAgent

agent = GitWaitAgent()
await agent.start_server()

# Safe push with CI waiting
result = await agent.safe_git_push(
    repository="/path/to/seo-agent",
    branch="main", 
    wait_for_ci=True,
    files_changed=["generated_site.html"]
)
```

### 2. **Multi-Agent Coordination**
```python
# Coordinate commits from multiple AI agents
agents = [
    {
        "agent_id": "content_optimizer",
        "files": ["content.html"],
        "commit_message": "Update optimized content",
        "priority": 2
    },
    {
        "agent_id": "design_generator",
        "files": ["styles.css"], 
        "commit_message": "Update design system",
        "priority": 1
    }
]

result = await agent.coordinate_multi_agent_commits(
    agents=agents,
    repository="/path/to/repo"
)
```

### 3. **Documentation Protection**
```python
# Automatically prevents unauthorized changes to protected files
result = await agent.safe_git_push(
    repository="/path/to/repo",
    files_changed=["README.md", "other_file.py"]  # Will block this push
)

# Result: {"success": false, "error": "Protected files require permission"}
```

### 4. **CI/CD Integration**
```python
# Wait for CI before deploying
ci_result = await agent.wait_for_ci_completion(
    repository="owner/repo",
    commit_sha="abc123...",
    timeout=600
)

if ci_result["success"]:
    # Proceed with deployment
    pass
```

## 🔄 Wait Types

| Wait Type | Description | Use Case |
|-----------|-------------|----------|
| `ci_pipeline` | Wait for CI/CD to complete | Before deployment |
| `pr_merge` | Wait for PR to be merged | Before next operation |
| `custom_delay` | Fixed delay in seconds | Rate limiting |
| `rate_limit` | Respect API rate limits | GitHub API calls |
| `queue_operation` | Queue with priority | Multi-agent coordination |

## 📊 Integration with Advanced Agentic Features

### Memory Integration
```python
# GitWait remembers successful patterns
from agent_memory import AgentMemoryManager

memory_manager = AgentMemoryManager()
agent = GitWaitAgent()
agent.memory_manager = memory_manager

# Automatically learns optimal wait times
await agent.wait_for_ci_completion(repo, commit)
# → Stores outcome for future optimization
```

### Error Recovery
```python
# Built-in retry and circuit breaker
@with_retry(
    retry_config=RetryConfig(max_attempts=3),
    circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5)
)
async def resilient_git_operation():
    return await agent.wait_for_ci_completion(repo, commit)
```

### Performance Monitoring
```python
# Automatic performance tracking
@monitor_agent_execution(monitor, "gitwait_001", "GitWait Agent")
async def monitored_operation():
    return await agent.safe_git_push(repo, branch)

# View metrics
summary = monitor.get_system_performance_summary()
```

### Agent Coordination
```python
# Register with agent coordinator
coordinator = AgentCoordinator()
coordinator.register_agent(gitwait_agent_definition)

# Submit coordinated tasks
task = Task(
    task_id="git_coordination_001",
    agent_id="gitwait_agent_001", 
    function_name="safe_git_push",
    priority=AgentPriority.HIGH
)
```

## 🛡️ Security Features

### 1. **Protected File Detection**
- Automatically detects changes to `README.md` and `CLAUDE.md`
- Blocks pushes containing protected files
- Requires explicit permission for documentation changes

### 2. **Rate Limit Protection**
- Monitors GitHub API rate limits
- Automatically delays operations when limits approached
- Prevents API quota exhaustion

### 3. **Operation Validation**
- Validates all git commands before execution
- Sanitizes input arguments
- Prevents execution of dangerous commands

## 📈 Performance Optimization

### 1. **Queue Prioritization**
- High-priority operations execute first
- Emergency operations can jump the queue
- Fair scheduling for multiple agents

### 2. **Smart Waiting**
- Adaptive wait times based on historical data
- Early completion detection
- Timeout protection

### 3. **Resource Management**
- Configurable concurrent operation limits
- Memory usage optimization
- CPU-efficient polling

## 🐛 Troubleshooting

### Common Issues

#### 1. **Server Won't Start**
```bash
# Check Python path and dependencies
python --version
pip list | grep mcp

# Check environment variables
echo $GITHUB_TOKEN
```

#### 2. **CI Waiting Timeouts**
```bash
# Increase timeout in environment
export GITWAIT_CI_WAIT="900"  # 15 minutes

# Check GitHub CI status manually
curl -H "Authorization: token $GITHUB_TOKEN" \
     "https://api.github.com/repos/owner/repo/commits/SHA/status"
```

#### 3. **Rate Limit Errors**
```bash
# Check current rate limits
curl -H "Authorization: token $GITHUB_TOKEN" \
     "https://api.github.com/rate_limit"

# Increase delay
export GITWAIT_RATE_LIMIT="120"  # 2 minutes
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for GitWait
logger = logging.getLogger("gitwait-mcp")
logger.setLevel(logging.DEBUG)
```

## 🔗 Integration Examples

### With Existing SEO Agent System
```python
# In main.py orchestrator
from gitwait_integration import GitWaitOrchestrator

class SEOAgentOrchestrator:
    def __init__(self):
        self.gitwait = GitWaitOrchestrator()
        
    async def deploy_generated_site(self, site_data):
        # Generate site files
        files = await self.generate_site_files(site_data)
        
        # Safe push with GitWait
        result = await self.gitwait.gitwait_agent.safe_git_push(
            repository=site_data["repository"],
            files_changed=files,
            wait_for_ci=True
        )
        
        return result
```

### With Error Recovery System
```python
# In error_recovery.py
from gitwait_integration import GitWaitAgent

class ErrorRecoveryEngine:
    def __init__(self):
        self.gitwait = GitWaitAgent()
        
    async def retry_failed_deployment(self, deployment_data):
        # Use GitWait for coordinated retry
        return await self.gitwait.safe_git_push(
            repository=deployment_data["repo"],
            wait_for_ci=True
        )
```

## 📄 License

This GitWait MCP server is part of the SEO Agent System and follows the same license terms.

## 🤝 Contributing

1. Follow the existing code patterns from GitHub MCP server
2. Add comprehensive error handling
3. Include proper type hints and documentation
4. Test with multiple repositories and CI systems
5. Ensure integration with advanced agentic features

---

**Built following GitHub MCP Server patterns for enterprise-grade reliability** 🚀