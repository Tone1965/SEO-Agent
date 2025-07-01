#!/usr/bin/env python3
"""
GitWait MCP Server
A Model Context Protocol server for managing git operations with timing controls,
CI/CD pipeline waiting, and multi-agent coordination.

Based on GitHub MCP server patterns from:
https://docs.github.com/en/copilot/how-tos/context/model-context-protocol/using-the-github-mcp-server
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import requests
from pathlib import Path

# MCP imports
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gitwait-mcp")

class WaitType(Enum):
    """Types of wait operations supported"""
    CI_PIPELINE = "ci_pipeline"
    PR_MERGE = "pr_merge"
    BRANCH_PROTECTION = "branch_protection"
    RATE_LIMIT = "rate_limit"
    CUSTOM_DELAY = "custom_delay"
    QUEUE_OPERATION = "queue_operation"

class OperationStatus(Enum):
    """Status of git operations"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"

@dataclass
class GitOperation:
    """Represents a git operation in the queue"""
    id: str
    command: str
    args: List[str]
    wait_type: WaitType
    wait_duration: int
    created_at: datetime
    status: OperationStatus
    priority: int = 1
    max_retries: int = 3
    current_retries: int = 0
    repository: Optional[str] = None
    branch: Optional[str] = None
    pr_number: Optional[int] = None

@dataclass
class WaitConfig:
    """Configuration for wait operations"""
    default_ci_wait: int = 300  # 5 minutes
    default_pr_wait: int = 600  # 10 minutes
    max_wait_time: int = 3600   # 1 hour
    rate_limit_delay: int = 60  # 1 minute
    github_token: Optional[str] = None
    webhook_url: Optional[str] = None

class GitWaitServer:
    """Main GitWait MCP server implementation"""
    
    def __init__(self):
        self.config = WaitConfig()
        self.operation_queue: List[GitOperation] = []
        self.active_operations: Dict[str, GitOperation] = {}
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.webhook_url = os.getenv("GITWAIT_WEBHOOK_URL")
        
        # Load config from environment
        self.config.github_token = self.github_token
        self.config.webhook_url = self.webhook_url
        self.config.default_ci_wait = int(os.getenv("GITWAIT_CI_WAIT", "300"))
        self.config.default_pr_wait = int(os.getenv("GITWAIT_PR_WAIT", "600"))
        self.config.max_wait_time = int(os.getenv("GITWAIT_MAX_WAIT", "3600"))
        self.config.rate_limit_delay = int(os.getenv("GITWAIT_RATE_LIMIT", "60"))
        
        logger.info("GitWait MCP Server initialized")
    
    async def wait_for_ci_pipeline(self, repository: str, commit_sha: str, 
                                  timeout: int = None) -> Dict[str, Any]:
        """Wait for CI/CD pipeline to complete"""
        timeout = timeout or self.config.default_ci_wait
        start_time = time.time()
        
        logger.info(f"Waiting for CI pipeline: {repository}@{commit_sha}")
        
        while time.time() - start_time < timeout:
            try:
                status = await self._check_ci_status(repository, commit_sha)
                
                if status["state"] == "success":
                    return {
                        "success": True,
                        "status": "completed",
                        "state": status["state"],
                        "duration": time.time() - start_time,
                        "checks": status.get("checks", [])
                    }
                elif status["state"] == "failure":
                    return {
                        "success": False,
                        "status": "failed",
                        "state": status["state"],
                        "duration": time.time() - start_time,
                        "error": status.get("error", "CI pipeline failed"),
                        "checks": status.get("checks", [])
                    }
                elif status["state"] in ["pending", "running"]:
                    logger.info(f"CI still running, waiting... ({status['state']})")
                    await asyncio.sleep(30)  # Check every 30 seconds
                    continue
                
            except Exception as e:
                logger.error(f"Error checking CI status: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
        
        return {
            "success": False,
            "status": "timeout",
            "duration": timeout,
            "error": f"CI pipeline did not complete within {timeout} seconds"
        }
    
    async def _check_ci_status(self, repository: str, commit_sha: str) -> Dict[str, Any]:
        """Check GitHub CI status for a commit"""
        if not self.github_token:
            # Fallback to local git status check
            return await self._check_local_status(repository, commit_sha)
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check commit status
        url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}/status"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Also check check runs
            check_runs_url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}/check-runs"
            check_response = requests.get(check_runs_url, headers=headers, timeout=30)
            check_data = check_response.json() if check_response.status_code == 200 else {"check_runs": []}
            
            return {
                "state": data.get("state", "pending"),
                "statuses": data.get("statuses", []),
                "checks": check_data.get("check_runs", []),
                "total_count": data.get("total_count", 0)
            }
            
        except requests.RequestException as e:
            logger.error(f"GitHub API error: {str(e)}")
            return {"state": "error", "error": str(e)}
    
    async def _check_local_status(self, repository: str, commit_sha: str) -> Dict[str, Any]:
        """Fallback to check local git status when no GitHub token"""
        try:
            # Simple check if commit exists and is reachable
            result = subprocess.run(
                ["git", "cat-file", "-e", commit_sha],
                cwd=repository,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {"state": "success", "checks": [], "local_check": True}
            else:
                return {"state": "pending", "checks": [], "local_check": True}
                
        except subprocess.TimeoutExpired:
            return {"state": "error", "error": "Git command timeout"}
        except Exception as e:
            return {"state": "error", "error": str(e)}
    
    async def wait_for_pr_merge(self, repository: str, pr_number: int, 
                               timeout: int = None) -> Dict[str, Any]:
        """Wait for pull request to be merged"""
        timeout = timeout or self.config.default_pr_wait
        start_time = time.time()
        
        logger.info(f"Waiting for PR merge: {repository}#{pr_number}")
        
        while time.time() - start_time < timeout:
            try:
                status = await self._check_pr_status(repository, pr_number)
                
                if status["state"] == "merged":
                    return {
                        "success": True,
                        "status": "merged",
                        "duration": time.time() - start_time,
                        "merge_commit_sha": status.get("merge_commit_sha")
                    }
                elif status["state"] == "closed":
                    return {
                        "success": False,
                        "status": "closed",
                        "duration": time.time() - start_time,
                        "error": "Pull request was closed without merging"
                    }
                elif status["state"] == "open":
                    logger.info(f"PR still open, waiting... (mergeable: {status.get('mergeable')})")
                    await asyncio.sleep(60)  # Check every minute
                    continue
                    
            except Exception as e:
                logger.error(f"Error checking PR status: {str(e)}")
                await asyncio.sleep(60)
        
        return {
            "success": False,
            "status": "timeout",
            "duration": timeout,
            "error": f"Pull request did not merge within {timeout} seconds"
        }
    
    async def _check_pr_status(self, repository: str, pr_number: int) -> Dict[str, Any]:
        """Check GitHub PR status"""
        if not self.github_token:
            return {"state": "unknown", "error": "No GitHub token available"}
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "state": data.get("state"),
                "merged": data.get("merged", False),
                "mergeable": data.get("mergeable"),
                "merge_commit_sha": data.get("merge_commit_sha"),
                "head_sha": data.get("head", {}).get("sha"),
                "base_ref": data.get("base", {}).get("ref")
            }
            
        except requests.RequestException as e:
            logger.error(f"GitHub API error: {str(e)}")
            return {"state": "error", "error": str(e)}
    
    async def queue_git_operation(self, command: str, args: List[str], 
                                 wait_type: WaitType, wait_duration: int = 0,
                                 priority: int = 1, repository: str = None) -> str:
        """Queue a git operation with specified wait conditions"""
        
        operation_id = f"gitwait_{int(time.time() * 1000000)}"
        
        operation = GitOperation(
            id=operation_id,
            command=command,
            args=args,
            wait_type=wait_type,
            wait_duration=wait_duration,
            created_at=datetime.now(),
            status=OperationStatus.PENDING,
            priority=priority,
            repository=repository
        )
        
        # Insert in priority order
        inserted = False
        for i, existing_op in enumerate(self.operation_queue):
            if priority > existing_op.priority:
                self.operation_queue.insert(i, operation)
                inserted = True
                break
        
        if not inserted:
            self.operation_queue.append(operation)
        
        logger.info(f"Queued git operation: {operation_id} ({command} {' '.join(args)})")
        
        # Start processing queue if not already running
        asyncio.create_task(self._process_queue())
        
        return operation_id
    
    async def _process_queue(self):
        """Process the git operation queue"""
        while self.operation_queue:
            operation = self.operation_queue.pop(0)
            self.active_operations[operation.id] = operation
            
            try:
                operation.status = OperationStatus.RUNNING
                logger.info(f"Processing operation: {operation.id}")
                
                # Apply wait conditions
                if operation.wait_type == WaitType.CUSTOM_DELAY and operation.wait_duration > 0:
                    logger.info(f"Waiting {operation.wait_duration} seconds before executing")
                    await asyncio.sleep(operation.wait_duration)
                
                # Execute the git command
                result = await self._execute_git_command(operation)
                
                if result["success"]:
                    operation.status = OperationStatus.SUCCESS
                    logger.info(f"Operation completed successfully: {operation.id}")
                else:
                    operation.status = OperationStatus.FAILED
                    logger.error(f"Operation failed: {operation.id} - {result.get('error')}")
                    
                    # Retry if configured
                    if operation.current_retries < operation.max_retries:
                        operation.current_retries += 1
                        operation.status = OperationStatus.PENDING
                        self.operation_queue.insert(0, operation)  # Retry at front of queue
                        logger.info(f"Retrying operation: {operation.id} (attempt {operation.current_retries + 1})")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing operation {operation.id}: {str(e)}")
                operation.status = OperationStatus.FAILED
            
            finally:
                if operation.status != OperationStatus.PENDING:  # Don't remove if retrying
                    self.active_operations.pop(operation.id, None)
    
    async def _execute_git_command(self, operation: GitOperation) -> Dict[str, Any]:
        """Execute a git command"""
        try:
            cmd = [operation.command] + operation.args
            
            cwd = operation.repository if operation.repository else os.getcwd()
            
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            else:
                return {
                    "success": False,
                    "error": f"Command failed with code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a queued or active operation"""
        # Check active operations
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            return {
                "id": operation.id,
                "status": operation.status.value,
                "command": operation.command,
                "args": operation.args,
                "created_at": operation.created_at.isoformat(),
                "retries": operation.current_retries,
                "wait_type": operation.wait_type.value
            }
        
        # Check queued operations
        for operation in self.operation_queue:
            if operation.id == operation_id:
                return {
                    "id": operation.id,
                    "status": operation.status.value,
                    "command": operation.command,
                    "args": operation.args,
                    "created_at": operation.created_at.isoformat(),
                    "position_in_queue": self.operation_queue.index(operation),
                    "wait_type": operation.wait_type.value
                }
        
        return None
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a queued or active operation"""
        # Remove from queue
        for i, operation in enumerate(self.operation_queue):
            if operation.id == operation_id:
                operation.status = OperationStatus.CANCELLED
                self.operation_queue.pop(i)
                logger.info(f"Cancelled queued operation: {operation_id}")
                return True
        
        # Cancel active operation
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.status = OperationStatus.CANCELLED
            logger.info(f"Cancelled active operation: {operation_id}")
            return True
        
        return False
    
    async def rate_limit_check(self, repository: str) -> Dict[str, Any]:
        """Check GitHub API rate limits"""
        if not self.github_token:
            return {
                "rate_limit_remaining": "unknown",
                "reset_time": "unknown",
                "should_wait": False
            }
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            core_rate = data.get("rate", {})
            remaining = core_rate.get("remaining", 0)
            reset_time = core_rate.get("reset", 0)
            
            should_wait = remaining < 100  # Wait if less than 100 requests remaining
            
            return {
                "rate_limit_remaining": remaining,
                "rate_limit_total": core_rate.get("limit", 0),
                "reset_time": datetime.fromtimestamp(reset_time).isoformat(),
                "should_wait": should_wait,
                "recommended_wait": self.config.rate_limit_delay if should_wait else 0
            }
            
        except requests.RequestException as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return {
                "error": str(e),
                "should_wait": True,
                "recommended_wait": self.config.rate_limit_delay
            }

# Initialize the MCP server
server = Server("gitwait")
gitwait = GitWaitServer()

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available GitWait tools"""
    return [
        types.Tool(
            name="wait_for_ci",
            description="Wait for CI/CD pipeline to complete for a specific commit",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "commit_sha": {
                        "type": "string",
                        "description": "Commit SHA to wait for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum wait time in seconds (default: 300)",
                        "default": 300
                    }
                },
                "required": ["repository", "commit_sha"]
            }
        ),
        types.Tool(
            name="wait_for_pr_merge",
            description="Wait for a pull request to be merged",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum wait time in seconds (default: 600)",
                        "default": 600
                    }
                },
                "required": ["repository", "pr_number"]
            }
        ),
        types.Tool(
            name="queue_git_operation",
            description="Queue a git operation with timing controls",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Git command to execute (e.g., 'git')"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command arguments (e.g., ['push', 'origin', 'main'])"
                    },
                    "wait_type": {
                        "type": "string",
                        "enum": ["ci_pipeline", "pr_merge", "custom_delay", "rate_limit"],
                        "description": "Type of wait condition"
                    },
                    "wait_duration": {
                        "type": "integer",
                        "description": "Wait duration in seconds (for custom_delay)",
                        "default": 0
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Operation priority (higher = executed first)",
                        "default": 1
                    },
                    "repository": {
                        "type": "string",
                        "description": "Repository path (optional)"
                    }
                },
                "required": ["command", "args", "wait_type"]
            }
        ),
        types.Tool(
            name="get_operation_status",
            description="Get status of a queued or active git operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation_id": {
                        "type": "string",
                        "description": "Operation ID returned from queue_git_operation"
                    }
                },
                "required": ["operation_id"]
            }
        ),
        types.Tool(
            name="cancel_operation",
            description="Cancel a queued or active git operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation_id": {
                        "type": "string",
                        "description": "Operation ID to cancel"
                    }
                },
                "required": ["operation_id"]
            }
        ),
        types.Tool(
            name="check_rate_limits",
            description="Check GitHub API rate limits",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository to check (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_queue_status",
            description="Get current queue status and active operations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "wait_for_ci":
            result = await gitwait.wait_for_ci_pipeline(
                repository=arguments["repository"],
                commit_sha=arguments["commit_sha"],
                timeout=arguments.get("timeout")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "wait_for_pr_merge":
            result = await gitwait.wait_for_pr_merge(
                repository=arguments["repository"],
                pr_number=arguments["pr_number"],
                timeout=arguments.get("timeout")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "queue_git_operation":
            operation_id = await gitwait.queue_git_operation(
                command=arguments["command"],
                args=arguments["args"],
                wait_type=WaitType(arguments["wait_type"]),
                wait_duration=arguments.get("wait_duration", 0),
                priority=arguments.get("priority", 1),
                repository=arguments.get("repository")
            )
            result = {"operation_id": operation_id, "status": "queued"}
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_operation_status":
            result = await gitwait.get_operation_status(arguments["operation_id"])
            if result is None:
                result = {"error": "Operation not found"}
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "cancel_operation":
            success = await gitwait.cancel_operation(arguments["operation_id"])
            result = {"cancelled": success}
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "check_rate_limits":
            result = await gitwait.rate_limit_check(
                repository=arguments.get("repository", "")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_queue_status":
            result = {
                "queued_operations": len(gitwait.operation_queue),
                "active_operations": len(gitwait.active_operations),
                "queue": [
                    {
                        "id": op.id,
                        "command": op.command,
                        "status": op.status.value,
                        "priority": op.priority,
                        "wait_type": op.wait_type.value
                    }
                    for op in gitwait.operation_queue[:10]  # Show first 10
                ],
                "active": [
                    {
                        "id": op.id,
                        "command": op.command,
                        "status": op.status.value
                    }
                    for op in gitwait.active_operations.values()
                ]
            }
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the GitWait MCP server"""
    # Server capabilities
    options = InitializationOptions(
        server_name="gitwait",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())