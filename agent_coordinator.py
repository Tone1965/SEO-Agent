# =====================================
# AGENT_COORDINATOR.PY - COORDINATION PROTOCOL
# =====================================
# This provides agent coordination, priority systems, resource allocation, and conflict resolution
# Enables true multi-agent collaboration with deadlock prevention
# Terry: Use this to orchestrate multiple agents working together efficiently

import asyncio
import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import sqlite3
import redis
from concurrent.futures import ThreadPoolExecutor
import heapq

logger = logging.getLogger(__name__)

class AgentPriority(Enum):
    """Agent priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class ResourceType(Enum):
    """Types of resources that can be allocated"""
    CPU_CORES = "cpu_cores"
    MEMORY_MB = "memory_mb"
    API_CALLS = "api_calls"
    NETWORK_BANDWIDTH = "network_bandwidth"
    STORAGE_GB = "storage_gb"
    GPU_UNITS = "gpu_units"

@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    resource_type: ResourceType
    amount: float
    max_amount: Optional[float] = None
    duration_seconds: Optional[float] = None
    priority: AgentPriority = AgentPriority.NORMAL

@dataclass
class Task:
    """Task definition for agent execution"""
    task_id: str
    agent_id: str
    function_name: str
    parameters: Dict[str, Any]
    priority: AgentPriority
    resource_requirements: List[ResourceRequirement]
    dependencies: List[str] = field(default_factory=list)  # Task IDs this task depends on
    created_at: datetime = field(default_factory=datetime.now)
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    estimated_duration: Optional[float] = None

@dataclass
class Agent:
    """Agent definition and status"""
    agent_id: str
    agent_name: str
    agent_type: str
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: Set[str] = field(default_factory=set)
    status: str = "idle"  # idle, busy, error, offline
    last_heartbeat: datetime = field(default_factory=datetime.now)
    total_completed_tasks: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 1.0
    resource_limits: Dict[ResourceType, float] = field(default_factory=dict)
    current_resource_usage: Dict[ResourceType, float] = field(default_factory=dict)

@dataclass
class ResourcePool:
    """System resource pool management"""
    total_resources: Dict[ResourceType, float]
    allocated_resources: Dict[ResourceType, float] = field(default_factory=dict)
    reserved_resources: Dict[ResourceType, float] = field(default_factory=dict)
    
    def __post_init__(self):
        for resource_type in self.total_resources:
            if resource_type not in self.allocated_resources:
                self.allocated_resources[resource_type] = 0.0
            if resource_type not in self.reserved_resources:
                self.reserved_resources[resource_type] = 0.0
    
    def available_resources(self) -> Dict[ResourceType, float]:
        """Get currently available resources"""
        return {
            resource_type: self.total_resources[resource_type] - 
                          self.allocated_resources[resource_type] - 
                          self.reserved_resources[resource_type]
            for resource_type in self.total_resources
        }
    
    def can_allocate(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if resource requirements can be satisfied"""
        available = self.available_resources()
        
        for req in requirements:
            if req.resource_type not in available:
                continue
            
            if available[req.resource_type] < req.amount:
                return False
        
        return True
    
    def allocate(self, requirements: List[ResourceRequirement]) -> bool:
        """Allocate resources if available"""
        if not self.can_allocate(requirements):
            return False
        
        for req in requirements:
            if req.resource_type in self.allocated_resources:
                self.allocated_resources[req.resource_type] += req.amount
        
        return True
    
    def deallocate(self, requirements: List[ResourceRequirement]):
        """Deallocate resources"""
        for req in requirements:
            if req.resource_type in self.allocated_resources:
                self.allocated_resources[req.resource_type] = max(
                    0, self.allocated_resources[req.resource_type] - req.amount
                )

class DeadlockDetector:
    """Detects and resolves deadlocks in task dependencies"""
    
    def __init__(self):
        self.dependency_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
    
    def add_dependency(self, task_id: str, depends_on: str):
        """Add a dependency relationship"""
        self.dependency_graph[task_id].add(depends_on)
        self.reverse_graph[depends_on].add(task_id)
    
    def remove_dependency(self, task_id: str, depends_on: str):
        """Remove a dependency relationship"""
        self.dependency_graph[task_id].discard(depends_on)
        self.reverse_graph[depends_on].discard(task_id)
    
    def detect_deadlock(self) -> List[List[str]]:
        """Detect circular dependencies (deadlocks)"""
        
        def has_cycle_util(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph[node]:
                if neighbor not in visited:
                    cycle = has_cycle_util(neighbor, visited, rec_stack, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            path.pop()
            return None
        
        visited = set()
        cycles = []
        
        for node in self.dependency_graph:
            if node not in visited:
                cycle = has_cycle_util(node, visited, set(), [])
                if cycle:
                    cycles.append(cycle)
        
        return cycles
    
    def resolve_deadlock(self, cycle: List[str], tasks: Dict[str, Task]) -> List[str]:
        """Resolve deadlock by breaking the cycle"""
        
        # Strategy: Remove the dependency with the lowest priority task
        min_priority = min(tasks[task_id].priority.value for task_id in cycle)
        
        for i in range(len(cycle)):
            current_task = cycle[i]
            next_task = cycle[(i + 1) % len(cycle)]
            
            if tasks[current_task].priority.value == min_priority:
                # Remove this dependency
                self.remove_dependency(current_task, next_task)
                logger.warning(f"Deadlock resolved: Removed dependency {current_task} -> {next_task}")
                return [current_task, next_task]
        
        # Fallback: Remove first dependency in cycle
        if len(cycle) >= 2:
            self.remove_dependency(cycle[0], cycle[1])
            logger.warning(f"Deadlock resolved (fallback): Removed dependency {cycle[0]} -> {cycle[1]}")
            return [cycle[0], cycle[1]]
        
        return []

class AgentCoordinator:
    """Main coordination system for multi-agent orchestration"""
    
    def __init__(self, db_path: str = "agent_coordination.db", redis_url: str = "redis://localhost:6379/2"):
        self.db_path = db_path
        self.agents = {}
        self.tasks = {}
        self.task_queue = []  # Priority queue
        self.resource_pool = ResourcePool({
            ResourceType.CPU_CORES: 8.0,
            ResourceType.MEMORY_MB: 16384.0,
            ResourceType.API_CALLS: 1000.0,
            ResourceType.NETWORK_BANDWIDTH: 1000.0,  # Mbps
            ResourceType.STORAGE_GB: 100.0
        })
        self.deadlock_detector = DeadlockDetector()
        self.coordination_active = True
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Redis for inter-agent communication
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_available = True
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available for coordination: {str(e)}")
            self.redis_available = False
        
        self.init_database()
        
        # Start coordination loop
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
    
    def init_database(self):
        """Initialize SQLite database for coordination tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                capabilities TEXT NOT NULL,
                max_concurrent_tasks INTEGER DEFAULT 1,
                status TEXT DEFAULT 'idle',
                last_heartbeat DATETIME,
                total_completed_tasks INTEGER DEFAULT 0,
                avg_execution_time REAL DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                resource_limits TEXT,
                current_resource_usage TEXT
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                function_name TEXT NOT NULL,
                parameters TEXT NOT NULL,
                priority INTEGER NOT NULL,
                resource_requirements TEXT,
                dependencies TEXT,
                created_at DATETIME NOT NULL,
                assigned_at DATETIME,
                started_at DATETIME,
                completed_at DATETIME,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                retries INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3
            )
        ''')
        
        # Resource allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_allocations (
                allocation_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                amount REAL NOT NULL,
                allocated_at DATETIME NOT NULL,
                deallocated_at DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_agent(self, agent: Agent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
        
        # Store in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO agents 
                (agent_id, agent_name, agent_type, capabilities, max_concurrent_tasks,
                 status, last_heartbeat, total_completed_tasks, avg_execution_time,
                 success_rate, resource_limits, current_resource_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent.agent_id, agent.agent_name, agent.agent_type,
                json.dumps(agent.capabilities), agent.max_concurrent_tasks,
                agent.status, agent.last_heartbeat, agent.total_completed_tasks,
                agent.avg_execution_time, agent.success_rate,
                json.dumps({k.value: v for k, v in agent.resource_limits.items()}),
                json.dumps({k.value: v for k, v in agent.current_resource_usage.items()})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing agent registration: {str(e)}")
        
        logger.info(f"Agent registered: {agent.agent_id} ({agent.agent_name})")
    
    def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        
        # Add to internal storage
        self.tasks[task.task_id] = task
        
        # Add dependencies to deadlock detector
        for dep_task_id in task.dependencies:
            self.deadlock_detector.add_dependency(task.task_id, dep_task_id)
        
        # Add to priority queue
        heapq.heappush(self.task_queue, (task.priority.value, task.created_at.timestamp(), task.task_id))
        
        # Store in database
        self._store_task(task)
        
        logger.info(f"Task submitted: {task.task_id} (priority: {task.priority.name})")
        return task.task_id
    
    def _store_task(self, task: Task):
        """Store task in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (task_id, agent_id, function_name, parameters, priority, resource_requirements,
                 dependencies, created_at, assigned_at, started_at, completed_at, status,
                 result, error, retries, max_retries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id, task.agent_id, task.function_name,
                json.dumps(task.parameters), task.priority.value,
                json.dumps([asdict(req) for req in task.resource_requirements]),
                json.dumps(task.dependencies), task.created_at, task.assigned_at,
                task.started_at, task.completed_at, task.status.value,
                json.dumps(task.result) if task.result else None,
                task.error, task.retries, task.max_retries
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing task: {str(e)}")
    
    def _coordination_loop(self):
        """Main coordination loop"""
        
        while self.coordination_active:
            try:
                # Check for deadlocks
                cycles = self.deadlock_detector.detect_deadlock()
                for cycle in cycles:
                    self.deadlock_detector.resolve_deadlock(cycle, self.tasks)
                
                # Process task queue
                self._process_task_queue()
                
                # Update agent heartbeats
                self._check_agent_heartbeats()
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                # Sleep before next iteration
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in coordination loop: {str(e)}")
                time.sleep(5)
    
    def _process_task_queue(self):
        """Process tasks from the priority queue"""
        
        processed_tasks = []
        
        while self.task_queue:
            priority, created_time, task_id = heapq.heappop(self.task_queue)
            
            if task_id not in self.tasks:
                continue  # Task was removed
            
            task = self.tasks[task_id]
            
            # Check if task is ready (all dependencies completed)
            if not self._are_dependencies_satisfied(task):
                # Put back in queue
                heapq.heappush(self.task_queue, (priority, created_time, task_id))
                break
            
            # Find suitable agent
            suitable_agent = self._find_suitable_agent(task)
            if not suitable_agent:
                # Put back in queue
                heapq.heappush(self.task_queue, (priority, created_time, task_id))
                break
            
            # Check resource availability
            if not self.resource_pool.can_allocate(task.resource_requirements):
                # Put back in queue
                heapq.heappush(self.task_queue, (priority, created_time, task_id))
                break
            
            # Allocate resources and assign task
            if self.resource_pool.allocate(task.resource_requirements):
                self._assign_task_to_agent(task, suitable_agent)
                processed_tasks.append(task_id)
            
            # Limit processing per iteration
            if len(processed_tasks) >= 10:
                break
    
    def _are_dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied"""
        
        for dep_task_id in task.dependencies:
            if dep_task_id in self.tasks:
                dep_task = self.tasks[dep_task_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            else:
                # Dependency task not found - assume completed
                continue
        
        return True
    
    def _find_suitable_agent(self, task: Task) -> Optional[Agent]:
        """Find a suitable agent for the task"""
        
        # Filter agents by capability and availability
        suitable_agents = []
        
        for agent in self.agents.values():
            # Check if agent has required capabilities
            if task.function_name not in agent.capabilities:
                continue
            
            # Check if agent is available
            if agent.status != "idle":
                continue
            
            # Check if agent has capacity for more tasks
            if len(agent.current_tasks) >= agent.max_concurrent_tasks:
                continue
            
            # Check if agent has sufficient resource limits
            resource_ok = True
            for req in task.resource_requirements:
                if req.resource_type in agent.resource_limits:
                    current_usage = agent.current_resource_usage.get(req.resource_type, 0)
                    if current_usage + req.amount > agent.resource_limits[req.resource_type]:
                        resource_ok = False
                        break
            
            if resource_ok:
                suitable_agents.append(agent)
        
        if not suitable_agents:
            return None
        
        # Select best agent based on performance metrics
        best_agent = max(suitable_agents, key=lambda a: (
            a.success_rate,
            -a.avg_execution_time,  # Prefer faster agents
            -len(a.current_tasks)   # Prefer less busy agents
        ))
        
        return best_agent
    
    def _assign_task_to_agent(self, task: Task, agent: Agent):
        """Assign a task to an agent"""
        
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.now()
        agent.current_tasks.add(task.task_id)
        agent.status = "busy"
        
        # Update agent resource usage
        for req in task.resource_requirements:
            current = agent.current_resource_usage.get(req.resource_type, 0)
            agent.current_resource_usage[req.resource_type] = current + req.amount
        
        # Store updates
        self._store_task(task)
        
        # Send task to agent via Redis or direct call
        if self.redis_available:
            self._send_task_via_redis(task, agent)
        else:
            # For demonstration, we'll simulate task execution
            self.executor.submit(self._execute_task_simulation, task, agent)
        
        logger.info(f"Task {task.task_id} assigned to agent {agent.agent_id}")
    
    def _send_task_via_redis(self, task: Task, agent: Agent):
        """Send task to agent via Redis"""
        
        task_message = {
            'task_id': task.task_id,
            'function_name': task.function_name,
            'parameters': task.parameters,
            'assigned_at': task.assigned_at.isoformat()
        }
        
        channel = f"agent:{agent.agent_id}:tasks"
        self.redis_client.lpush(channel, json.dumps(task_message))
        
        # Also publish notification
        notification = {
            'type': 'task_assigned',
            'task_id': task.task_id,
            'agent_id': agent.agent_id
        }
        self.redis_client.publish('coordination:notifications', json.dumps(notification))
    
    def _execute_task_simulation(self, task: Task, agent: Agent):
        """Simulate task execution (for demonstration)"""
        
        try:
            # Mark task as running
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self._store_task(task)
            
            # Simulate execution time
            execution_time = task.estimated_duration or (2 + len(task.parameters) * 0.1)
            time.sleep(execution_time)
            
            # Simulate success/failure
            import random
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.result = {'simulated': True, 'execution_time': execution_time}
                
                # Update agent metrics
                agent.total_completed_tasks += 1
                agent.avg_execution_time = (
                    (agent.avg_execution_time * (agent.total_completed_tasks - 1) + execution_time) /
                    agent.total_completed_tasks
                )
            else:
                task.status = TaskStatus.FAILED
                task.error = "Simulated execution failure"
                task.retries += 1
            
            task.completed_at = datetime.now()
            
            # Clean up agent state
            agent.current_tasks.discard(task.task_id)
            if not agent.current_tasks:
                agent.status = "idle"
            
            # Release resources
            self.resource_pool.deallocate(task.resource_requirements)
            
            # Update agent resource usage
            for req in task.resource_requirements:
                current = agent.current_resource_usage.get(req.resource_type, 0)
                agent.current_resource_usage[req.resource_type] = max(0, current - req.amount)
            
            self._store_task(task)
            
            # Retry failed tasks if within retry limit
            if task.status == TaskStatus.FAILED and task.retries < task.max_retries:
                task.status = TaskStatus.PENDING
                task.assigned_at = None
                task.started_at = None
                task.completed_at = None
                heapq.heappush(self.task_queue, (
                    task.priority.value + task.retries,  # Lower priority for retries
                    datetime.now().timestamp(),
                    task.task_id
                ))
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._store_task(task)
    
    def _check_agent_heartbeats(self):
        """Check agent heartbeats and mark stale agents as offline"""
        
        current_time = datetime.now()
        heartbeat_timeout = timedelta(minutes=5)
        
        for agent in self.agents.values():
            if current_time - agent.last_heartbeat > heartbeat_timeout:
                if agent.status != "offline":
                    logger.warning(f"Agent {agent.agent_id} marked as offline (no heartbeat)")
                    agent.status = "offline"
    
    def _cleanup_completed_tasks(self):
        """Clean up old completed tasks"""
        
        cleanup_time = datetime.now() - timedelta(hours=24)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at < cleanup_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
    
    def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now()
            if self.agents[agent_id].status == "offline":
                self.agents[agent_id].status = "idle"
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get overall coordination status"""
        
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status in ["idle", "busy"]])
        
        task_counts = defaultdict(int)
        for task in self.tasks.values():
            task_counts[task.status.value] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_agents': total_agents,
            'active_agents': active_agents,
            'tasks_in_queue': len(self.task_queue),
            'task_counts': dict(task_counts),
            'resource_utilization': {
                resource_type.value: {
                    'total': self.resource_pool.total_resources[resource_type],
                    'allocated': self.resource_pool.allocated_resources[resource_type],
                    'available': self.resource_pool.available_resources()[resource_type]
                }
                for resource_type in self.resource_pool.total_resources
            }
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        current_tasks = [
            {
                'task_id': task_id,
                'status': self.tasks[task_id].status.value if task_id in self.tasks else 'unknown'
            }
            for task_id in agent.current_tasks
        ]
        
        return {
            'agent_id': agent.agent_id,
            'agent_name': agent.agent_name,
            'status': agent.status,
            'current_tasks': current_tasks,
            'total_completed': agent.total_completed_tasks,
            'success_rate': agent.success_rate,
            'avg_execution_time': agent.avg_execution_time,
            'last_heartbeat': agent.last_heartbeat.isoformat()
        }

# Example usage and integration
async def create_coordinated_agent_system():
    """Example of creating a coordinated multi-agent system"""
    
    # Initialize coordinator
    coordinator = AgentCoordinator()
    
    # Register agents
    market_scanner = Agent(
        agent_id="market_scanner_001",
        agent_name="Market Scanner",
        agent_type="analysis",
        capabilities=["analyze_market", "scan_competitors"],
        max_concurrent_tasks=2,
        resource_limits={
            ResourceType.CPU_CORES: 2.0,
            ResourceType.MEMORY_MB: 2048.0,
            ResourceType.API_CALLS: 100.0
        }
    )
    
    content_generator = Agent(
        agent_id="content_generator_001",
        agent_name="Content Generator",
        agent_type="content",
        capabilities=["generate_content", "write_blog_post"],
        max_concurrent_tasks=1,
        resource_limits={
            ResourceType.CPU_CORES: 1.0,
            ResourceType.MEMORY_MB: 1024.0,
            ResourceType.API_CALLS: 50.0
        }
    )
    
    coordinator.register_agent(market_scanner)
    coordinator.register_agent(content_generator)
    
    # Submit tasks with dependencies
    market_analysis_task = Task(
        task_id="task_market_001",
        agent_id="market_scanner_001",
        function_name="analyze_market",
        parameters={"business_type": "HVAC", "location": "Birmingham, AL"},
        priority=AgentPriority.HIGH,
        resource_requirements=[
            ResourceRequirement(ResourceType.CPU_CORES, 1.0),
            ResourceRequirement(ResourceType.MEMORY_MB, 512.0),
            ResourceRequirement(ResourceType.API_CALLS, 10.0)
        ],
        estimated_duration=30.0
    )
    
    content_task = Task(
        task_id="task_content_001",
        agent_id="content_generator_001",
        function_name="generate_content",
        parameters={"content_type": "blog_post", "topic": "HVAC services"},
        priority=AgentPriority.NORMAL,
        resource_requirements=[
            ResourceRequirement(ResourceType.CPU_CORES, 0.5),
            ResourceRequirement(ResourceType.MEMORY_MB, 256.0),
            ResourceRequirement(ResourceType.API_CALLS, 5.0)
        ],
        dependencies=["task_market_001"],  # Depends on market analysis
        estimated_duration=45.0
    )
    
    # Submit tasks
    coordinator.submit_task(market_analysis_task)
    coordinator.submit_task(content_task)
    
    # Monitor coordination for a while
    for i in range(10):
        await asyncio.sleep(5)
        status = coordinator.get_coordination_status()
        print(f"Coordination Status (iteration {i+1}):")
        print(json.dumps(status, indent=2, default=str))
        
        # Update heartbeats
        coordinator.update_agent_heartbeat("market_scanner_001")
        coordinator.update_agent_heartbeat("content_generator_001")
    
    return coordinator

if __name__ == "__main__":
    asyncio.run(create_coordinated_agent_system())