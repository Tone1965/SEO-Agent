# =====================================
# AGENT_MONITOR.PY - PERFORMANCE MONITORING
# =====================================
# This provides real-time agent performance tracking, success/failure rates, and quality scores
# Monitors resource usage, processing times, and system health
# Terry: Use this to track and optimize your agents' performance in real-time

import asyncio
import logging
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import sqlite3
import statistics
import redis
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Performance metrics for an individual agent"""
    agent_id: str
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    total_cost: float = 0.0
    avg_cost_per_execution: float = 0.0
    quality_scores: List[float] = None
    avg_quality_score: float = 0.0
    last_execution: Optional[datetime] = None
    status: str = "idle"  # idle, running, error, disabled
    
    def __post_init__(self):
        if self.quality_scores is None:
            self.quality_scores = []

@dataclass
class ExecutionRecord:
    """Record of a single agent execution"""
    execution_id: str
    agent_id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    quality_score: Optional[float] = None
    cost: Optional[float] = None
    resource_usage: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}
        if self.resource_usage is None:
            self.resource_usage = {}

@dataclass
class SystemMetrics:
    """Overall system performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_agents: int
    total_executions_per_minute: int
    avg_response_time: float
    error_rate: float
    system_health_score: float

class ResourceMonitor:
    """Monitors system resource usage"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.monitoring_active = False
        self.resource_history = deque(maxlen=3600)  # Keep 1 hour of data
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.resource_history.append(metrics)
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {str(e)}")
                time.sleep(5)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=None)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            active_agents=0,  # Will be updated by agent monitor
            total_executions_per_minute=0,  # Will be calculated
            avg_response_time=0.0,  # Will be calculated
            error_rate=0.0,  # Will be calculated
            system_health_score=0.0  # Will be calculated
        )
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get most recent system metrics"""
        return self.resource_history[-1] if self.resource_history else None
    
    def get_average_metrics(self, minutes: int = 5) -> Dict[str, float]:
        """Get average metrics over specified time period"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.resource_history 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            'avg_cpu_usage': statistics.mean(m.cpu_usage for m in recent_metrics),
            'avg_memory_usage': statistics.mean(m.memory_usage for m in recent_metrics),
            'avg_disk_usage': statistics.mean(m.disk_usage for m in recent_metrics),
            'sample_count': len(recent_metrics)
        }

class AgentPerformanceMonitor:
    """Monitors individual agent performance"""
    
    def __init__(self, db_path: str = "agent_performance.db"):
        self.db_path = db_path
        self.agent_metrics = {}
        self.execution_history = deque(maxlen=10000)  # Keep recent executions
        self.active_executions = {}
        self.resource_monitor = ResourceMonitor()
        self.init_database()
        
        # Start resource monitoring
        self.resource_monitor.start_monitoring()
    
    def init_database(self):
        """Initialize SQLite database for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agent metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_metrics (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                total_execution_time REAL DEFAULT 0,
                min_execution_time REAL DEFAULT 0,
                max_execution_time REAL DEFAULT 0,
                avg_execution_time REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                avg_cost_per_execution REAL DEFAULT 0,
                avg_quality_score REAL DEFAULT 0,
                last_execution DATETIME,
                status TEXT DEFAULT 'idle',
                last_updated DATETIME NOT NULL
            )
        ''')
        
        # Execution records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_records (
                execution_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                execution_time REAL,
                success BOOLEAN,
                error_message TEXT,
                input_data TEXT,
                output_data TEXT,
                quality_score REAL,
                cost REAL,
                resource_usage TEXT
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                timestamp DATETIME PRIMARY KEY,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                disk_usage REAL NOT NULL,
                network_io TEXT,
                active_agents INTEGER DEFAULT 0,
                total_executions_per_minute INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                error_rate REAL DEFAULT 0,
                system_health_score REAL DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_agent ON execution_records(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_time ON execution_records(start_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_time ON system_metrics(timestamp)')
        
        conn.commit()
        conn.close()
    
    def start_execution(self, agent_id: str, agent_name: str, input_data: Dict[str, Any]) -> str:
        """Start tracking an agent execution"""
        
        execution_id = f"exec_{agent_id}_{int(time.time() * 1000000)}_{uuid.uuid4().hex[:8]}"
        
        execution_record = ExecutionRecord(
            execution_id=execution_id,
            agent_id=agent_id,
            agent_name=agent_name,
            start_time=datetime.now(),
            input_data=input_data
        )
        
        self.active_executions[execution_id] = execution_record
        
        # Update agent status
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_name=agent_name
            )
        
        self.agent_metrics[agent_id].status = "running"
        
        logger.debug(f"Started execution tracking: {execution_id}")
        return execution_id
    
    def end_execution(self, execution_id: str, success: bool, output_data: Dict[str, Any] = None,
                     error_message: str = None, quality_score: float = None, cost: float = None):
        """End tracking an agent execution"""
        
        if execution_id not in self.active_executions:
            logger.warning(f"Execution ID not found: {execution_id}")
            return
        
        execution_record = self.active_executions[execution_id]
        execution_record.end_time = datetime.now()
        execution_record.execution_time = (execution_record.end_time - execution_record.start_time).total_seconds()
        execution_record.success = success
        execution_record.output_data = output_data or {}
        execution_record.error_message = error_message
        execution_record.quality_score = quality_score
        execution_record.cost = cost or 0.0
        
        # Collect resource usage at end
        current_metrics = self.resource_monitor.get_current_metrics()
        if current_metrics:
            execution_record.resource_usage = {
                'cpu_usage': current_metrics.cpu_usage,
                'memory_usage': current_metrics.memory_usage,
                'timestamp': current_metrics.timestamp.isoformat()
            }
        
        # Update agent metrics
        self._update_agent_metrics(execution_record)
        
        # Store execution record
        self._store_execution_record(execution_record)
        
        # Move to history and remove from active
        self.execution_history.append(execution_record)
        del self.active_executions[execution_id]
        
        # Update agent status
        agent_metrics = self.agent_metrics[execution_record.agent_id]
        agent_metrics.status = "idle"
        agent_metrics.last_execution = execution_record.end_time
        
        logger.debug(f"Ended execution tracking: {execution_id} (success: {success})")
    
    def _update_agent_metrics(self, execution_record: ExecutionRecord):
        """Update agent metrics based on execution record"""
        
        agent_id = execution_record.agent_id
        if agent_id not in self.agent_metrics:
            return
        
        metrics = self.agent_metrics[agent_id]
        
        # Update execution counts
        metrics.total_executions += 1
        if execution_record.success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
        
        # Update timing metrics
        if execution_record.execution_time:
            metrics.total_execution_time += execution_record.execution_time
            metrics.min_execution_time = min(metrics.min_execution_time, execution_record.execution_time)
            metrics.max_execution_time = max(metrics.max_execution_time, execution_record.execution_time)
            metrics.avg_execution_time = metrics.total_execution_time / metrics.total_executions
        
        # Update cost metrics
        if execution_record.cost:
            metrics.total_cost += execution_record.cost
            metrics.avg_cost_per_execution = metrics.total_cost / metrics.total_executions
        
        # Update quality metrics
        if execution_record.quality_score is not None:
            metrics.quality_scores.append(execution_record.quality_score)
            # Keep only recent quality scores (last 100)
            if len(metrics.quality_scores) > 100:
                metrics.quality_scores = metrics.quality_scores[-100:]
            metrics.avg_quality_score = statistics.mean(metrics.quality_scores)
        
        # Store updated metrics
        self._store_agent_metrics(metrics)
    
    def _store_execution_record(self, record: ExecutionRecord):
        """Store execution record in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO execution_records 
                (execution_id, agent_id, agent_name, start_time, end_time, execution_time,
                 success, error_message, input_data, output_data, quality_score, cost, resource_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.execution_id, record.agent_id, record.agent_name,
                record.start_time, record.end_time, record.execution_time,
                record.success, record.error_message,
                json.dumps(record.input_data), json.dumps(record.output_data),
                record.quality_score, record.cost, json.dumps(record.resource_usage)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing execution record: {str(e)}")
    
    def _store_agent_metrics(self, metrics: AgentMetrics):
        """Store agent metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO agent_metrics 
                (agent_id, agent_name, total_executions, successful_executions, failed_executions,
                 total_execution_time, min_execution_time, max_execution_time, avg_execution_time,
                 total_cost, avg_cost_per_execution, avg_quality_score, last_execution, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.agent_id, metrics.agent_name, metrics.total_executions,
                metrics.successful_executions, metrics.failed_executions,
                metrics.total_execution_time, 
                metrics.min_execution_time if metrics.min_execution_time != float('inf') else None,
                metrics.max_execution_time, metrics.avg_execution_time,
                metrics.total_cost, metrics.avg_cost_per_execution, metrics.avg_quality_score,
                metrics.last_execution, metrics.status, datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing agent metrics: {str(e)}")
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent"""
        return self.agent_metrics.get(agent_id)
    
    def get_all_agent_metrics(self) -> Dict[str, AgentMetrics]:
        """Get metrics for all agents"""
        return self.agent_metrics.copy()
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Get overall system performance summary"""
        
        current_time = datetime.now()
        
        # Calculate totals across all agents
        total_executions = sum(m.total_executions for m in self.agent_metrics.values())
        total_successful = sum(m.successful_executions for m in self.agent_metrics.values())
        total_failed = sum(m.failed_executions for m in self.agent_metrics.values())
        
        success_rate = (total_successful / total_executions * 100) if total_executions > 0 else 0
        
        # Get recent execution rate
        recent_executions = [
            record for record in self.execution_history
            if record.start_time > current_time - timedelta(minutes=1)
        ]
        executions_per_minute = len(recent_executions)
        
        # Calculate average response time
        recent_execution_times = [
            record.execution_time for record in recent_executions
            if record.execution_time is not None
        ]
        avg_response_time = statistics.mean(recent_execution_times) if recent_execution_times else 0
        
        # Get resource metrics
        resource_metrics = self.resource_monitor.get_average_metrics(5)
        
        # Calculate system health score
        health_score = self._calculate_system_health_score(success_rate, resource_metrics, avg_response_time)
        
        return {
            'timestamp': current_time.isoformat(),
            'total_agents': len(self.agent_metrics),
            'active_agents': len([m for m in self.agent_metrics.values() if m.status == "running"]),
            'total_executions': total_executions,
            'successful_executions': total_successful,
            'failed_executions': total_failed,
            'success_rate_percent': success_rate,
            'executions_per_minute': executions_per_minute,
            'avg_response_time_seconds': avg_response_time,
            'resource_metrics': resource_metrics,
            'system_health_score': health_score,
            'active_executions': len(self.active_executions)
        }
    
    def _calculate_system_health_score(self, success_rate: float, resource_metrics: Dict, avg_response_time: float) -> float:
        """Calculate overall system health score (0-100)"""
        
        health_score = 100.0
        
        # Success rate impact (0-40 points)
        health_score -= (100 - success_rate) * 0.4
        
        # Resource usage impact (0-30 points)
        if resource_metrics:
            cpu_penalty = max(0, resource_metrics.get('avg_cpu_usage', 0) - 80) * 0.5
            memory_penalty = max(0, resource_metrics.get('avg_memory_usage', 0) - 85) * 0.5
            health_score -= cpu_penalty + memory_penalty
        
        # Response time impact (0-30 points)
        if avg_response_time > 10:  # More than 10 seconds is concerning
            response_penalty = min(30, (avg_response_time - 10) * 2)
            health_score -= response_penalty
        
        return max(0, min(100, health_score))
    
    def get_agent_performance_report(self, agent_id: str, days: int = 7) -> Dict[str, Any]:
        """Get detailed performance report for an agent"""
        
        if agent_id not in self.agent_metrics:
            return {"error": "Agent not found"}
        
        metrics = self.agent_metrics[agent_id]
        
        # Get recent execution history
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_executions = [
            record for record in self.execution_history
            if record.agent_id == agent_id and record.start_time > cutoff_time
        ]
        
        # Calculate performance trends
        daily_executions = defaultdict(int)
        daily_successes = defaultdict(int)
        daily_costs = defaultdict(float)
        
        for record in recent_executions:
            day_key = record.start_time.date().isoformat()
            daily_executions[day_key] += 1
            if record.success:
                daily_successes[day_key] += 1
            if record.cost:
                daily_costs[day_key] += record.cost
        
        # Performance insights
        insights = []
        
        if metrics.avg_execution_time > 30:
            insights.append("Agent execution time is above optimal threshold")
        
        if metrics.total_executions > 0:
            recent_success_rate = (metrics.successful_executions / metrics.total_executions) * 100
            if recent_success_rate < 90:
                insights.append(f"Success rate ({recent_success_rate:.1f}%) below target")
        
        if metrics.avg_quality_score > 0 and metrics.avg_quality_score < 0.8:
            insights.append("Quality score below target threshold")
        
        return {
            'agent_id': agent_id,
            'agent_name': metrics.agent_name,
            'report_period_days': days,
            'current_metrics': asdict(metrics),
            'recent_executions_count': len(recent_executions),
            'daily_performance': {
                'executions': dict(daily_executions),
                'successes': dict(daily_successes),
                'costs': dict(daily_costs)
            },
            'performance_insights': insights,
            'generated_at': datetime.now().isoformat()
        }

def monitor_agent_execution(monitor: AgentPerformanceMonitor, agent_id: str, agent_name: str):
    """Decorator for monitoring agent execution"""
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Prepare input data for monitoring
            input_data = {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            
            execution_id = monitor.start_execution(agent_id, agent_name, input_data)
            
            try:
                # Execute the function
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Calculate quality score (simplified)
                quality_score = 0.8 if isinstance(result, dict) and result.get('success') else 0.5
                
                # Calculate cost (simplified)
                estimated_cost = execution_time * 0.01  # $0.01 per second
                
                # End monitoring with success
                monitor.end_execution(
                    execution_id,
                    success=True,
                    output_data={'result_type': type(result).__name__},
                    quality_score=quality_score,
                    cost=estimated_cost
                )
                
                return result
                
            except Exception as e:
                # End monitoring with failure
                monitor.end_execution(
                    execution_id,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for sync functions
            input_data = {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            
            execution_id = monitor.start_execution(agent_id, agent_name, input_data)
            
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                quality_score = 0.8 if isinstance(result, dict) and result.get('success') else 0.5
                estimated_cost = execution_time * 0.01
                
                monitor.end_execution(
                    execution_id,
                    success=True,
                    output_data={'result_type': type(result).__name__},
                    quality_score=quality_score,
                    cost=estimated_cost
                )
                
                return result
                
            except Exception as e:
                monitor.end_execution(
                    execution_id,
                    success=False,
                    error_message=str(e)
                )
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Example usage
class MonitoredMarketScanner:
    """Market Scanner with performance monitoring"""
    
    def __init__(self):
        self.monitor = AgentPerformanceMonitor()
    
    @monitor_agent_execution(monitor, "market_scanner_001", "Market Scanner Agent")
    async def analyze_market(self, business_type: str, location: str):
        """Market analysis with performance monitoring"""
        
        # Simulate processing
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'business_type': business_type,
            'location': location,
            'analysis': 'Market analysis complete'
        }
    
    def get_performance_summary(self):
        """Get performance summary"""
        return self.monitor.get_system_performance_summary()
    
    def get_agent_report(self):
        """Get detailed agent report"""
        return self.monitor.get_agent_performance_report("market_scanner_001")

if __name__ == "__main__":
    import functools
    
    async def test_monitoring():
        """Test the monitoring system"""
        
        scanner = MonitoredMarketScanner()
        
        # Run several executions
        for i in range(5):
            try:
                result = await scanner.analyze_market("HVAC", f"Location {i+1}")
                print(f"Execution {i+1}: Success")
            except Exception as e:
                print(f"Execution {i+1}: Failed - {str(e)}")
            
            await asyncio.sleep(1)
        
        # Get performance summary
        summary = scanner.get_performance_summary()
        print(f"\nPerformance Summary:")
        print(json.dumps(summary, indent=2, default=str))
        
        # Get detailed report
        report = scanner.get_agent_report()
        print(f"\nDetailed Agent Report:")
        print(json.dumps(report, indent=2, default=str))
    
    asyncio.run(test_monitoring())