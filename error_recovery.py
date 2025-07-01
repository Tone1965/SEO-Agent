# =====================================
# ERROR_RECOVERY.PY - ERROR RECOVERY & RESILIENCE
# =====================================
# This provides automatic retry mechanisms, fallback strategies, and self-healing capabilities
# Ensures the system can recover from failures and continue operating reliably
# Terry: Use this to make your system bulletproof and resilient to any failures

import asyncio
import logging
import time
import traceback
import functools
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import random
import threading
from collections import defaultdict, deque
import aiohttp
import sqlite3

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types of failures the system can encounter"""
    API_RATE_LIMIT = "api_rate_limit"
    API_TIMEOUT = "api_timeout"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    MEMORY_ERROR = "memory_error"
    VALIDATION_ERROR = "validation_error"
    AGENT_FAILURE = "agent_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN_ERROR = "unknown_error"

class RecoveryStrategy(Enum):
    """Recovery strategies for different failure types"""
    RETRY_EXPONENTIAL = "retry_exponential"
    RETRY_LINEAR = "retry_linear"
    FALLBACK_SIMPLE = "fallback_simple"
    FALLBACK_ALTERNATIVE_API = "fallback_alternative_api"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RESTART_COMPONENT = "restart_component"
    ESCALATE_TO_HUMAN = "escalate_to_human"

@dataclass
class FailureEvent:
    """Records a failure event for analysis"""
    failure_id: str
    component: str
    failure_type: FailureType
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    timestamp: datetime
    recovery_attempted: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_successful: bool = False
    recovery_time: Optional[float] = None

@dataclass
class CircuitBreakerState:
    """Circuit breaker state management"""
    component: str
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    success_count: int = 0
    next_attempt_time: Optional[datetime] = None

class RetryConfig:
    """Configuration for retry mechanisms"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60,
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold

class ErrorRecoveryEngine:
    """Main engine for error recovery and resilience"""
    
    def __init__(self, db_path: str = "error_recovery.db"):
        self.db_path = db_path
        self.circuit_breakers = {}
        self.failure_history = deque(maxlen=1000)
        self.recovery_strategies = self._init_recovery_strategies()
        self.component_health = defaultdict(lambda: {"healthy": True, "last_check": datetime.now()})
        self.init_database()
        
        # Start background monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()
    
    def init_database(self):
        """Initialize SQLite database for failure tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failure_events (
                failure_id TEXT PRIMARY KEY,
                component TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                timestamp DATETIME NOT NULL,
                recovery_attempted BOOLEAN DEFAULT 0,
                recovery_strategy TEXT,
                recovery_successful BOOLEAN DEFAULT 0,
                recovery_time REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_health (
                component TEXT PRIMARY KEY,
                healthy BOOLEAN NOT NULL,
                failure_count INTEGER DEFAULT 0,
                last_failure DATETIME,
                last_success DATETIME,
                uptime_percentage REAL DEFAULT 100.0,
                last_updated DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_recovery_strategies(self) -> Dict[FailureType, List[RecoveryStrategy]]:
        """Initialize recovery strategies for different failure types"""
        return {
            FailureType.API_RATE_LIMIT: [
                RecoveryStrategy.RETRY_EXPONENTIAL,
                RecoveryStrategy.FALLBACK_ALTERNATIVE_API
            ],
            FailureType.API_TIMEOUT: [
                RecoveryStrategy.RETRY_LINEAR,
                RecoveryStrategy.CIRCUIT_BREAKER
            ],
            FailureType.API_ERROR: [
                RecoveryStrategy.RETRY_EXPONENTIAL,
                RecoveryStrategy.FALLBACK_SIMPLE
            ],
            FailureType.NETWORK_ERROR: [
                RecoveryStrategy.RETRY_EXPONENTIAL,
                RecoveryStrategy.CIRCUIT_BREAKER
            ],
            FailureType.MEMORY_ERROR: [
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.RESTART_COMPONENT
            ],
            FailureType.VALIDATION_ERROR: [
                RecoveryStrategy.FALLBACK_SIMPLE,
                RecoveryStrategy.ESCALATE_TO_HUMAN
            ],
            FailureType.AGENT_FAILURE: [
                RecoveryStrategy.RESTART_COMPONENT,
                RecoveryStrategy.FALLBACK_ALTERNATIVE_API
            ],
            FailureType.DEPENDENCY_FAILURE: [
                RecoveryStrategy.CIRCUIT_BREAKER,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            FailureType.RESOURCE_EXHAUSTION: [
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.ESCALATE_TO_HUMAN
            ],
            FailureType.UNKNOWN_ERROR: [
                RecoveryStrategy.RETRY_LINEAR,
                RecoveryStrategy.ESCALATE_TO_HUMAN
            ]
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any]) -> FailureType:
        """Classify error type for appropriate recovery strategy"""
        
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # API Rate Limits
        if "rate limit" in error_str or "429" in error_str or "quota" in error_str:
            return FailureType.API_RATE_LIMIT
        
        # API Timeouts
        if "timeout" in error_str or "timed out" in error_str:
            return FailureType.API_TIMEOUT
        
        # Network Errors
        if "connection" in error_str or "network" in error_str or "dns" in error_str:
            return FailureType.NETWORK_ERROR
        
        # Memory Errors
        if "memory" in error_str or "outofmemory" in error_type:
            return FailureType.MEMORY_ERROR
        
        # Validation Errors
        if "validation" in error_str or "invalid" in error_str or "schema" in error_str:
            return FailureType.VALIDATION_ERROR
        
        # API Errors
        if "api" in error_str or "401" in error_str or "403" in error_str or "500" in error_str:
            return FailureType.API_ERROR
        
        return FailureType.UNKNOWN_ERROR
    
    def record_failure(self, component: str, error: Exception, context: Dict[str, Any]) -> str:
        """Record a failure event"""
        
        failure_type = self.classify_error(error, context)
        
        failure_event = FailureEvent(
            failure_id=f"failure_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}",
            component=component,
            failure_type=failure_type,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context=context,
            timestamp=datetime.now()
        )
        
        # Store in memory
        self.failure_history.append(failure_event)
        
        # Store in database
        self._store_failure_event(failure_event)
        
        # Update component health
        self._update_component_health(component, success=False)
        
        logger.error(f"Failure recorded for {component}: {failure_type.value} - {str(error)}")
        
        return failure_event.failure_id
    
    def _store_failure_event(self, event: FailureEvent):
        """Store failure event in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO failure_events 
                (failure_id, component, failure_type, error_message, stack_trace,
                 context, timestamp, recovery_attempted, recovery_strategy,
                 recovery_successful, recovery_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.failure_id, event.component, event.failure_type.value,
                event.error_message, event.stack_trace, json.dumps(event.context),
                event.timestamp, event.recovery_attempted,
                event.recovery_strategy.value if event.recovery_strategy else None,
                event.recovery_successful, event.recovery_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing failure event: {str(e)}")
    
    def _update_component_health(self, component: str, success: bool):
        """Update component health status"""
        
        self.component_health[component]["last_check"] = datetime.now()
        
        if success:
            self.component_health[component]["healthy"] = True
            self.component_health[component]["last_success"] = datetime.now()
        else:
            # Check if component should be marked unhealthy
            recent_failures = self._get_recent_failures(component, minutes=10)
            if len(recent_failures) >= 3:
                self.component_health[component]["healthy"] = False
        
        # Update database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO component_health 
                (component, healthy, last_updated)
                VALUES (?, ?, ?)
            ''', (component, self.component_health[component]["healthy"], datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating component health: {str(e)}")
    
    def _get_recent_failures(self, component: str, minutes: int = 10) -> List[FailureEvent]:
        """Get recent failures for a component"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            event for event in self.failure_history 
            if event.component == component and event.timestamp > cutoff_time
        ]

def with_retry(retry_config: RetryConfig = None, 
               circuit_breaker_config: CircuitBreakerConfig = None,
               fallback_function: Callable = None):
    """Decorator for adding retry and circuit breaker functionality"""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            component_name = f"{func.__module__}.{func.__name__}"
            
            # Get or create error recovery engine
            if not hasattr(async_wrapper, '_recovery_engine'):
                async_wrapper._recovery_engine = ErrorRecoveryEngine()
            
            recovery_engine = async_wrapper._recovery_engine
            
            # Check circuit breaker if configured
            if circuit_breaker_config:
                if not recovery_engine._check_circuit_breaker(component_name, circuit_breaker_config):
                    logger.warning(f"Circuit breaker OPEN for {component_name}")
                    if fallback_function:
                        return await fallback_function(*args, **kwargs)
                    else:
                        raise Exception(f"Circuit breaker open for {component_name}")
            
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    
                    # Record success
                    execution_time = time.time() - start_time
                    recovery_engine._update_component_health(component_name, success=True)
                    
                    # Update circuit breaker on success
                    if circuit_breaker_config:
                        recovery_engine._record_circuit_breaker_success(component_name)
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Record failure
                    context = {
                        'function': component_name,
                        'attempt': attempt + 1,
                        'max_attempts': retry_config.max_attempts,
                        'args': str(args)[:200],  # Truncate for storage
                        'kwargs': str(kwargs)[:200]
                    }
                    
                    failure_id = recovery_engine.record_failure(component_name, e, context)
                    
                    # Update circuit breaker on failure
                    if circuit_breaker_config:
                        recovery_engine._record_circuit_breaker_failure(component_name, circuit_breaker_config)
                    
                    # Don't retry on last attempt
                    if attempt == retry_config.max_attempts - 1:
                        break
                    
                    # Calculate delay
                    delay = recovery_engine._calculate_retry_delay(
                        attempt, retry_config, recovery_engine.classify_error(e, context)
                    )
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {component_name}: {str(e)}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            # All retries failed
            if fallback_function:
                logger.info(f"All retries failed for {component_name}, trying fallback")
                try:
                    return await fallback_function(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed for {component_name}: {str(fallback_error)}")
                    raise last_exception
            else:
                raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for synchronous functions
            component_name = f"{func.__module__}.{func.__name__}"
            
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        break
                    
                    # Simple retry delay for sync functions
                    delay = min(retry_config.base_delay * (retry_config.exponential_base ** attempt), 
                               retry_config.max_delay)
                    
                    if retry_config.jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {component_name}: {str(e)}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ErrorRecoveryEngine:
    """Extended ErrorRecoveryEngine with circuit breaker and advanced recovery"""
    
    def _check_circuit_breaker(self, component: str, config: CircuitBreakerConfig) -> bool:
        """Check if circuit breaker allows the call"""
        
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = CircuitBreakerState(component=component)
        
        breaker = self.circuit_breakers[component]
        now = datetime.now()
        
        if breaker.state == "OPEN":
            if breaker.next_attempt_time and now >= breaker.next_attempt_time:
                # Try to move to HALF_OPEN
                breaker.state = "HALF_OPEN"
                breaker.success_count = 0
                logger.info(f"Circuit breaker for {component} moved to HALF_OPEN")
                return True
            else:
                return False  # Still open
        
        elif breaker.state == "HALF_OPEN":
            # Allow limited calls to test if service is back
            return True
        
        else:  # CLOSED
            return True
    
    def _record_circuit_breaker_failure(self, component: str, config: CircuitBreakerConfig):
        """Record a failure for circuit breaker"""
        
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = CircuitBreakerState(component=component)
        
        breaker = self.circuit_breakers[component]
        breaker.failure_count += 1
        breaker.last_failure_time = datetime.now()
        
        if breaker.state == "HALF_OPEN":
            # Go back to OPEN
            breaker.state = "OPEN"
            breaker.next_attempt_time = datetime.now() + timedelta(seconds=config.timeout_seconds)
            logger.warning(f"Circuit breaker for {component} moved to OPEN (from HALF_OPEN)")
        
        elif breaker.state == "CLOSED" and breaker.failure_count >= config.failure_threshold:
            # Open the circuit
            breaker.state = "OPEN"
            breaker.next_attempt_time = datetime.now() + timedelta(seconds=config.timeout_seconds)
            logger.warning(f"Circuit breaker for {component} moved to OPEN (threshold reached)")
    
    def _record_circuit_breaker_success(self, component: str):
        """Record a success for circuit breaker"""
        
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = CircuitBreakerState(component=component)
        
        breaker = self.circuit_breakers[component]
        
        if breaker.state == "HALF_OPEN":
            breaker.success_count += 1
            if breaker.success_count >= 3:  # Configurable success threshold
                breaker.state = "CLOSED"
                breaker.failure_count = 0
                logger.info(f"Circuit breaker for {component} moved to CLOSED (recovered)")
        
        elif breaker.state == "CLOSED":
            # Reset failure count on success
            breaker.failure_count = max(0, breaker.failure_count - 1)
    
    def _calculate_retry_delay(self, attempt: int, config: RetryConfig, failure_type: FailureType) -> float:
        """Calculate retry delay based on failure type and attempt"""
        
        # Base delay calculation
        if failure_type == FailureType.API_RATE_LIMIT:
            # Longer delays for rate limits
            delay = config.base_delay * (config.exponential_base ** (attempt + 2))
        else:
            delay = config.base_delay * (config.exponential_base ** attempt)
        
        # Apply maximum delay
        delay = min(delay, config.max_delay)
        
        # Add jitter if enabled
        if config.jitter:
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _background_monitor(self):
        """Background monitoring for system health"""
        
        while self.monitoring_active:
            try:
                # Check component health
                self._check_all_component_health()
                
                # Clean up old circuit breaker states
                self._cleanup_circuit_breakers()
                
                # Generate health report
                self._generate_health_report()
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in background monitor: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _check_all_component_health(self):
        """Check health of all components"""
        
        for component, health_info in self.component_health.items():
            # Check if component hasn't been used recently
            time_since_check = datetime.now() - health_info["last_check"]
            
            if time_since_check > timedelta(hours=1):
                # Mark as potentially stale
                health_info["stale"] = True
    
    def _cleanup_circuit_breakers(self):
        """Clean up old circuit breaker states"""
        
        now = datetime.now()
        to_remove = []
        
        for component, breaker in self.circuit_breakers.items():
            # Remove old, unused circuit breakers
            if (breaker.last_failure_time and 
                now - breaker.last_failure_time > timedelta(hours=24) and
                breaker.state == "CLOSED"):
                to_remove.append(component)
        
        for component in to_remove:
            del self.circuit_breakers[component]
    
    def _generate_health_report(self):
        """Generate system health report"""
        
        healthy_components = sum(1 for health in self.component_health.values() if health["healthy"])
        total_components = len(self.component_health)
        
        open_circuit_breakers = sum(1 for breaker in self.circuit_breakers.values() if breaker.state == "OPEN")
        
        recent_failures = len([
            event for event in self.failure_history 
            if event.timestamp > datetime.now() - timedelta(hours=1)
        ])
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "healthy_components": healthy_components,
            "total_components": total_components,
            "health_percentage": (healthy_components / total_components * 100) if total_components > 0 else 100,
            "open_circuit_breakers": open_circuit_breakers,
            "recent_failures": recent_failures,
            "system_status": "healthy" if healthy_components == total_components and open_circuit_breakers == 0 else "degraded"
        }
        
        # Log health report periodically
        if int(time.time()) % 300 == 0:  # Every 5 minutes
            logger.info(f"System Health: {health_report['health_percentage']:.1f}% healthy, {recent_failures} recent failures")

# Fallback functions for common scenarios
async def claude_api_fallback(*args, **kwargs):
    """Fallback for Claude API failures"""
    logger.info("Using Claude API fallback - returning cached or simplified response")
    return {
        "success": False,
        "fallback": True,
        "message": "Service temporarily unavailable, using cached response",
        "data": {}
    }

async def openai_api_fallback(*args, **kwargs):
    """Fallback for OpenAI API failures"""
    logger.info("Using OpenAI API fallback - returning template response")
    return {
        "success": False,
        "fallback": True,
        "message": "Content generation service temporarily unavailable",
        "content": "This content is temporarily unavailable. Please try again later."
    }

async def database_fallback(*args, **kwargs):
    """Fallback for database failures"""
    logger.info("Using database fallback - in-memory storage")
    return {
        "success": False,
        "fallback": True,
        "message": "Database temporarily unavailable, using in-memory storage"
    }

# Example usage with existing agents
class ResilientMarketScanner:
    """Market Scanner with error recovery capabilities"""
    
    def __init__(self):
        self.recovery_engine = ErrorRecoveryEngine()
    
    @with_retry(
        retry_config=RetryConfig(max_attempts=3, base_delay=2.0, max_delay=30.0),
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60),
        fallback_function=claude_api_fallback
    )
    async def analyze_market(self, business_type: str, location: str):
        """Market analysis with error recovery"""
        
        # Simulate potential failures for demonstration
        if random.random() < 0.1:  # 10% chance of failure
            raise Exception("Simulated API failure")
        
        # Actual market analysis logic would go here
        await asyncio.sleep(1)  # Simulate processing
        
        return {
            "business_type": business_type,
            "location": location,
            "competitors": ["Competitor 1", "Competitor 2"],
            "market_analysis": "Detailed analysis here"
        }
    
    def get_health_status(self):
        """Get health status of the scanner"""
        return self.recovery_engine.component_health.get(
            f"{self.__class__.__module__}.{self.__class__.__name__}.analyze_market",
            {"healthy": True, "last_check": datetime.now()}
        )

# Integration example
async def test_resilient_system():
    """Test the resilient system"""
    
    scanner = ResilientMarketScanner()
    
    # Test multiple calls to see error recovery in action
    for i in range(10):
        try:
            result = await scanner.analyze_market("HVAC", "Birmingham, AL")
            print(f"Call {i+1}: Success - {result.get('fallback', False) and 'FALLBACK' or 'NORMAL'}")
        except Exception as e:
            print(f"Call {i+1}: Failed - {str(e)}")
        
        await asyncio.sleep(0.5)
    
    # Check health status
    health = scanner.get_health_status()
    print(f"\nHealth Status: {health}")

if __name__ == "__main__":
    # Test the error recovery system
    asyncio.run(test_resilient_system())