"""
GitWait Integration for SEO Agent System
Integrates GitWait MCP server with the advanced agentic architecture.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import subprocess
import os

# Import the existing agentic components
try:
    from agent_memory import AgentMemoryManager
    from error_recovery import with_retry, RetryConfig, CircuitBreakerConfig
    from agent_monitor import monitor_agent_execution, AgentPerformanceMonitor
    from agent_coordinator import AgentCoordinator, Task, AgentPriority, ResourceRequirement, ResourceType
except ImportError:
    # Fallback if modules not available
    logging.warning("Advanced agentic components not available")

logger = logging.getLogger(__name__)

@dataclass
class GitWaitConfig:
    """Configuration for GitWait integration"""
    mcp_server_path: str = "mcp_servers/gitwait_server.py"
    github_token: Optional[str] = None
    default_timeout: int = 300
    max_retries: int = 3
    enable_memory: bool = True
    enable_monitoring: bool = True

class GitWaitAgent:
    """GitWait agent integrated with the SEO Agent System"""
    
    def __init__(self, config: GitWaitConfig = None):
        self.config = config or GitWaitConfig()
        self.agent_id = "gitwait_agent_001"
        self.agent_name = "GitWait Agent"
        
        # Initialize agentic components if available
        try:
            self.memory_manager = AgentMemoryManager() if self.config.enable_memory else None
            self.monitor = AgentPerformanceMonitor() if self.config.enable_monitoring else None
            self.memory = self.memory_manager.get_agent_memory(self.agent_id) if self.memory_manager else None
        except:
            self.memory_manager = None
            self.monitor = None
            self.memory = None
            logger.warning("Advanced agentic features not available")
        
        # GitWait server process
        self.server_process = None
        self.is_running = False
        
        logger.info(f"GitWait Agent initialized: {self.agent_id}")
    
    async def start_server(self):
        """Start the GitWait MCP server"""
        if self.is_running:
            return True
        
        try:
            env = os.environ.copy()
            if self.config.github_token:
                env["GITHUB_TOKEN"] = self.config.github_token
            
            self.server_process = subprocess.Popen(
                ["python", self.config.mcp_server_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give server time to start
            await asyncio.sleep(2)
            
            if self.server_process.poll() is None:
                self.is_running = True
                logger.info("GitWait MCP server started successfully")
                
                # Store in memory
                if self.memory:
                    self.memory.add("server_started", {
                        "timestamp": datetime.now().isoformat(),
                        "pid": self.server_process.pid
                    })
                
                return True
            else:
                logger.error("GitWait MCP server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting GitWait server: {str(e)}")
            return False
    
    async def stop_server(self):
        """Stop the GitWait MCP server"""
        if self.server_process and self.is_running:
            self.server_process.terminate()
            await asyncio.sleep(1)
            
            if self.server_process.poll() is None:
                self.server_process.kill()
            
            self.is_running = False
            logger.info("GitWait MCP server stopped")
    
    @with_retry(
        retry_config=RetryConfig(max_attempts=3, base_delay=2.0),
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5),
        fallback_function=None
    )
    async def wait_for_ci_completion(self, repository: str, commit_sha: str, 
                                   timeout: int = None) -> Dict[str, Any]:
        """Wait for CI/CD pipeline completion with error recovery"""
        timeout = timeout or self.config.default_timeout
        
        if self.memory:
            self.memory.add(f"ci_wait_{commit_sha}", {
                "repository": repository,
                "commit_sha": commit_sha,
                "started_at": datetime.now().isoformat(),
                "timeout": timeout
            })
        
        try:
            # Use MCP server via subprocess for now
            # In production, this would use proper MCP client
            result = await self._call_mcp_tool("wait_for_ci", {
                "repository": repository,
                "commit_sha": commit_sha,
                "timeout": timeout
            })
            
            # Record outcome for learning
            if self.memory_manager:
                success_score = 1.0 if result.get("success") else 0.0
                self.memory_manager.record_agent_outcome(
                    self.agent_id,
                    "ci_wait",
                    {"repository": repository, "commit_sha": commit_sha},
                    result,
                    success_score,
                    result.get("duration", timeout),
                    0.01  # Minimal cost for waiting
                )
            
            return result
            
        except Exception as e:
            logger.error(f"CI wait failed: {str(e)}")
            raise
    
    async def safe_git_push(self, repository: str, branch: str = "main", 
                           wait_for_ci: bool = True, files_changed: list = None) -> Dict[str, Any]:
        """Safely push to git with CI waiting and protection for documentation files"""
        
        # Check if protected files are being modified
        protected_files = ["README.md", "CLAUDE.md"]
        if files_changed and any(f in protected_files for f in files_changed):
            logger.warning("Protected documentation files detected in changes")
            
            # Record this in memory for future reference
            if self.memory:
                self.memory.add("protected_file_push_attempt", {
                    "files": files_changed,
                    "timestamp": datetime.now().isoformat(),
                    "repository": repository,
                    "branch": branch
                })
            
            return {
                "success": False,
                "error": "Protected files require explicit permission before push",
                "protected_files": [f for f in files_changed if f in protected_files],
                "suggestion": "Request permission before modifying README.md or CLAUDE.md"
            }
        
        try:
            # Queue the git push operation
            operation_id = await self._call_mcp_tool("queue_git_operation", {
                "command": "git",
                "args": ["push", "origin", branch],
                "wait_type": "custom_delay",
                "wait_duration": 5,  # Small delay to prevent rapid-fire pushes
                "priority": 2,
                "repository": repository
            })
            
            # Wait for push to complete
            push_result = await self._wait_for_operation(operation_id["operation_id"])
            
            if not push_result.get("success"):
                return push_result
            
            # If CI waiting is enabled, wait for CI
            if wait_for_ci:
                # Get the latest commit SHA
                commit_sha = await self._get_latest_commit_sha(repository)
                
                if commit_sha:
                    ci_result = await self.wait_for_ci_completion(
                        repository.replace(os.getcwd() + "/", ""),  # Convert to owner/repo format
                        commit_sha
                    )
                    
                    return {
                        "push_success": True,
                        "ci_result": ci_result,
                        "overall_success": ci_result.get("success", False),
                        "operation_id": operation_id["operation_id"]
                    }
            
            return {
                "push_success": True,
                "overall_success": True,
                "operation_id": operation_id["operation_id"]
            }
            
        except Exception as e:
            logger.error(f"Safe git push failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def coordinate_multi_agent_commits(self, agents: list, repository: str) -> Dict[str, Any]:
        """Coordinate commits from multiple agents to prevent conflicts"""
        
        coordination_results = []
        
        for i, agent_info in enumerate(agents):
            agent_id = agent_info.get("agent_id", f"agent_{i}")
            files_to_commit = agent_info.get("files", [])
            commit_message = agent_info.get("commit_message", f"Agent {agent_id} update")
            
            try:
                # Queue git operations with priority based on agent importance
                priority = agent_info.get("priority", 1)
                
                # Add files
                add_operation = await self._call_mcp_tool("queue_git_operation", {
                    "command": "git",
                    "args": ["add"] + files_to_commit,
                    "wait_type": "custom_delay",
                    "wait_duration": 2,  # Small delay between operations
                    "priority": priority,
                    "repository": repository
                })
                
                # Commit
                commit_operation = await self._call_mcp_tool("queue_git_operation", {
                    "command": "git", 
                    "args": ["commit", "-m", commit_message],
                    "wait_type": "custom_delay",
                    "wait_duration": 1,
                    "priority": priority,
                    "repository": repository
                })
                
                coordination_results.append({
                    "agent_id": agent_id,
                    "add_operation_id": add_operation["operation_id"],
                    "commit_operation_id": commit_operation["operation_id"],
                    "status": "queued"
                })
                
            except Exception as e:
                coordination_results.append({
                    "agent_id": agent_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "coordination_id": f"multi_agent_{int(datetime.now().timestamp())}",
            "agents_coordinated": len(agents),
            "operations": coordination_results
        }
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call GitWait MCP tool (simplified for demo)"""
        # In production, this would use proper MCP client library
        # For now, simulate the responses
        
        if tool_name == "wait_for_ci":
            # Simulate CI waiting
            await asyncio.sleep(min(arguments.get("timeout", 30), 10))  # Simulate shorter wait
            return {
                "success": True,
                "status": "completed",
                "state": "success",
                "duration": 10,
                "checks": []
            }
        
        elif tool_name == "queue_git_operation":
            operation_id = f"op_{int(datetime.now().timestamp() * 1000)}"
            return {"operation_id": operation_id}
        
        else:
            return {"success": True}
    
    async def _wait_for_operation(self, operation_id: str) -> Dict[str, Any]:
        """Wait for a queued operation to complete"""
        # Simulate operation completion
        await asyncio.sleep(2)
        return {"success": True, "operation_id": operation_id}
    
    async def _get_latest_commit_sha(self, repository: str) -> str:
        """Get the latest commit SHA"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repository,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception as e:
            logger.error(f"Error getting commit SHA: {str(e)}")
        
        return None

# Integration with existing orchestrator
class GitWaitOrchestrator:
    """Orchestrator that integrates GitWait with the SEO Agent System"""
    
    def __init__(self):
        self.gitwait_agent = GitWaitAgent()
        
        # Initialize with existing coordinator if available
        try:
            self.coordinator = AgentCoordinator()
            self.register_gitwait_agent()
        except:
            self.coordinator = None
            logger.warning("Agent coordinator not available")
    
    def register_gitwait_agent(self):
        """Register GitWait agent with the coordinator"""
        if not self.coordinator:
            return
        
        from agent_coordinator import Agent, ResourceType
        
        gitwait_agent_def = Agent(
            agent_id=self.gitwait_agent.agent_id,
            agent_name=self.gitwait_agent.agent_name,
            agent_type="coordination",
            capabilities=["git_wait", "ci_wait", "pr_wait", "queue_operations"],
            max_concurrent_tasks=3,
            resource_limits={
                ResourceType.CPU_CORES: 1.0,
                ResourceType.MEMORY_MB: 512.0,
                ResourceType.API_CALLS: 100.0
            }
        )
        
        self.coordinator.register_agent(gitwait_agent_def)
        logger.info("GitWait agent registered with coordinator")
    
    async def create_coordinated_git_task(self, task_type: str, **kwargs) -> str:
        """Create a coordinated git task"""
        if not self.coordinator:
            return await getattr(self.gitwait_agent, task_type)(**kwargs)
        
        from agent_coordinator import Task, AgentPriority
        
        task = Task(
            task_id=f"gitwait_{task_type}_{int(datetime.now().timestamp())}",
            agent_id=self.gitwait_agent.agent_id,
            function_name=task_type,
            parameters=kwargs,
            priority=AgentPriority.HIGH,
            resource_requirements=[
                ResourceRequirement(ResourceType.CPU_CORES, 0.5),
                ResourceRequirement(ResourceType.MEMORY_MB, 256.0)
            ]
        )
        
        return self.coordinator.submit_task(task)

# Example usage and integration
async def integrate_gitwait_with_seo_system():
    """Example of integrating GitWait with the SEO Agent System"""
    
    orchestrator = GitWaitOrchestrator()
    
    # Start GitWait server
    await orchestrator.gitwait_agent.start_server()
    
    # Example: Safe push with CI waiting
    repository = "/path/to/repo"
    files_changed = ["main.py", "requirements.txt"]
    
    result = await orchestrator.gitwait_agent.safe_git_push(
        repository=repository,
        branch="main",
        wait_for_ci=True,
        files_changed=files_changed
    )
    
    print("Git Push Result:", json.dumps(result, indent=2))
    
    # Example: Multi-agent coordination
    agents = [
        {
            "agent_id": "content_optimizer",
            "files": ["optimized_content.html"],
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
    
    coordination_result = await orchestrator.gitwait_agent.coordinate_multi_agent_commits(
        agents=agents,
        repository=repository
    )
    
    print("Multi-Agent Coordination:", json.dumps(coordination_result, indent=2))
    
    # Clean up
    await orchestrator.gitwait_agent.stop_server()

if __name__ == "__main__":
    asyncio.run(integrate_gitwait_with_seo_system())