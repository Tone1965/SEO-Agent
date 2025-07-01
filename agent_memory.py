# =====================================
# AGENT_MEMORY.PY - MEMORY & STATE MANAGEMENT
# =====================================
# This provides persistent memory and learning capabilities for AI agents
# Enables agents to remember patterns, learn from outcomes, and improve over time
# Terry: Use this to make your agents truly intelligent and adaptive

import asyncio
import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import redis
from collections import defaultdict, deque
import threading
import uuid

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    id: str
    content: Any
    memory_type: str  # long_term, short_term, shared
    agent_id: str
    timestamp: datetime
    importance_score: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.tags:
            self.tags = []
        if not self.last_accessed:
            self.last_accessed = self.timestamp

@dataclass
class LearningOutcome:
    """Records learning outcomes for future improvement"""
    outcome_id: str
    agent_id: str
    task_type: str
    input_context: Dict
    output_result: Dict
    success_score: float  # 0.0 to 1.0
    execution_time: float
    cost_incurred: float
    feedback: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class AgentMemoryStore:
    """Persistent storage for agent memories"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Memory entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                content_data BLOB NOT NULL,
                importance_score REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                timestamp DATETIME NOT NULL,
                last_accessed DATETIME,
                tags TEXT
            )
        ''')
        
        # Learning outcomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_outcomes (
                outcome_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                input_context TEXT NOT NULL,
                output_result TEXT NOT NULL,
                success_score REAL NOT NULL,
                execution_time REAL NOT NULL,
                cost_incurred REAL NOT NULL,
                feedback TEXT,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        # Agent performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_metrics (
                agent_id TEXT PRIMARY KEY,
                total_tasks INTEGER DEFAULT 0,
                successful_tasks INTEGER DEFAULT 0,
                total_execution_time REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                average_success_rate REAL DEFAULT 0,
                last_updated DATETIME NOT NULL
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_agent ON memory_entries(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_importance ON memory_entries(importance_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcomes_agent ON learning_outcomes(agent_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcomes_task ON learning_outcomes(task_type)')
        
        conn.commit()
        conn.close()
    
    def store_memory(self, memory: MemoryEntry) -> bool:
        """Store a memory entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize content
            content_data = pickle.dumps(memory.content)
            content_hash = hashlib.md5(content_data).hexdigest()
            
            cursor.execute('''
                INSERT OR REPLACE INTO memory_entries 
                (id, agent_id, memory_type, content_hash, content_data, importance_score, 
                 access_count, timestamp, last_accessed, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.id, memory.agent_id, memory.memory_type, content_hash,
                content_data, memory.importance_score, memory.access_count,
                memory.timestamp, memory.last_accessed, json.dumps(memory.tags)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    def retrieve_memories(self, agent_id: str, memory_type: str = None, 
                         limit: int = 100, min_importance: float = 0.0) -> List[MemoryEntry]:
        """Retrieve memories for an agent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT id, agent_id, memory_type, content_data, importance_score,
                       access_count, timestamp, last_accessed, tags
                FROM memory_entries 
                WHERE agent_id = ? AND importance_score >= ?
            '''
            params = [agent_id, min_importance]
            
            if memory_type:
                query += ' AND memory_type = ?'
                params.append(memory_type)
            
            query += ' ORDER BY importance_score DESC, last_accessed DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                content = pickle.loads(row[3])
                memory = MemoryEntry(
                    id=row[0],
                    agent_id=row[1],
                    memory_type=row[2],
                    content=content,
                    importance_score=row[4],
                    access_count=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                    tags=json.loads(row[8]) if row[8] else []
                )
                memories.append(memory)
            
            conn.close()
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return []
    
    def store_learning_outcome(self, outcome: LearningOutcome) -> bool:
        """Store a learning outcome"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_outcomes 
                (outcome_id, agent_id, task_type, input_context, output_result,
                 success_score, execution_time, cost_incurred, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                outcome.outcome_id, outcome.agent_id, outcome.task_type,
                json.dumps(outcome.input_context), json.dumps(outcome.output_result),
                outcome.success_score, outcome.execution_time, outcome.cost_incurred,
                outcome.feedback, outcome.timestamp
            ))
            
            # Update agent metrics
            self._update_agent_metrics(cursor, outcome)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing learning outcome: {str(e)}")
            return False
    
    def _update_agent_metrics(self, cursor, outcome: LearningOutcome):
        """Update aggregate agent performance metrics"""
        
        # Get current metrics
        cursor.execute('SELECT * FROM agent_metrics WHERE agent_id = ?', (outcome.agent_id,))
        row = cursor.fetchone()
        
        if row:
            total_tasks = row[1] + 1
            successful_tasks = row[2] + (1 if outcome.success_score >= 0.7 else 0)
            total_execution_time = row[3] + outcome.execution_time
            total_cost = row[4] + outcome.cost_incurred
        else:
            total_tasks = 1
            successful_tasks = 1 if outcome.success_score >= 0.7 else 0
            total_execution_time = outcome.execution_time
            total_cost = outcome.cost_incurred
        
        average_success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        cursor.execute('''
            INSERT OR REPLACE INTO agent_metrics 
            (agent_id, total_tasks, successful_tasks, total_execution_time, 
             total_cost, average_success_rate, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            outcome.agent_id, total_tasks, successful_tasks, total_execution_time,
            total_cost, average_success_rate, datetime.now()
        ))

class ShortTermMemory:
    """Manages short-term working memory for agents"""
    
    def __init__(self, max_size: int = 50, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.memory = deque(maxlen=max_size)
        self.memory_dict = {}  # For fast lookup
        self.lock = threading.Lock()
    
    def add(self, key: str, value: Any, importance: float = 0.5):
        """Add item to short-term memory"""
        with self.lock:
            entry = {
                'key': key,
                'value': value,
                'importance': importance,
                'timestamp': datetime.now(),
                'access_count': 0
            }
            
            # Remove if already exists
            if key in self.memory_dict:
                old_entry = self.memory_dict[key]
                try:
                    self.memory.remove(old_entry)
                except ValueError:
                    pass
            
            self.memory.append(entry)
            self.memory_dict[key] = entry
            
            # Clean expired entries
            self._clean_expired()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve item from short-term memory"""
        with self.lock:
            if key in self.memory_dict:
                entry = self.memory_dict[key]
                
                # Check if expired
                if self._is_expired(entry):
                    self._remove_entry(key)
                    return None
                
                entry['access_count'] += 1
                entry['last_accessed'] = datetime.now()
                return entry['value']
            
            return None
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get most recent memories"""
        with self.lock:
            self._clean_expired()
            recent = list(self.memory)[-limit:]
            return [{'key': e['key'], 'value': e['value'], 
                    'timestamp': e['timestamp']} for e in recent]
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if memory entry is expired"""
        return (datetime.now() - entry['timestamp']).seconds > self.ttl_seconds
    
    def _clean_expired(self):
        """Remove expired entries"""
        current_time = datetime.now()
        to_remove = []
        
        for entry in self.memory:
            if (current_time - entry['timestamp']).seconds > self.ttl_seconds:
                to_remove.append(entry['key'])
        
        for key in to_remove:
            self._remove_entry(key)
    
    def _remove_entry(self, key: str):
        """Remove entry by key"""
        if key in self.memory_dict:
            entry = self.memory_dict[key]
            try:
                self.memory.remove(entry)
            except ValueError:
                pass
            del self.memory_dict[key]

class SharedMemory:
    """Manages shared memory between agents using Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_available = True
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available, using local storage: {str(e)}")
            self.redis_available = False
            self.local_storage = {}
            self.lock = threading.Lock()
    
    def set_shared_knowledge(self, key: str, value: Any, ttl: int = 3600):
        """Set shared knowledge accessible by all agents"""
        if self.redis_available:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        else:
            with self.lock:
                self.local_storage[key] = {
                    'value': value,
                    'timestamp': datetime.now(),
                    'ttl': ttl
                }
    
    def get_shared_knowledge(self, key: str) -> Optional[Any]:
        """Get shared knowledge"""
        if self.redis_available:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.error(f"Error getting shared knowledge: {str(e)}")
                return None
        else:
            with self.lock:
                if key in self.local_storage:
                    entry = self.local_storage[key]
                    # Check if expired
                    if (datetime.now() - entry['timestamp']).seconds > entry['ttl']:
                        del self.local_storage[key]
                        return None
                    return entry['value']
                return None
    
    def broadcast_message(self, channel: str, message: Dict):
        """Broadcast message to all agents"""
        if self.redis_available:
            self.redis_client.publish(channel, json.dumps(message))
        else:
            # For local storage, just log the message
            logger.info(f"Broadcast to {channel}: {message}")
    
    def subscribe_to_messages(self, channel: str):
        """Subscribe to broadcast messages"""
        if self.redis_available:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        else:
            return None

class LearningPipeline:
    """Handles learning from outcomes and strategy evolution"""
    
    def __init__(self, memory_store: AgentMemoryStore):
        self.memory_store = memory_store
        self.learning_patterns = defaultdict(list)
        self.strategy_cache = {}
    
    def record_outcome(self, agent_id: str, task_type: str, input_context: Dict,
                      output_result: Dict, success_score: float, execution_time: float,
                      cost_incurred: float, feedback: str = None) -> str:
        """Record a learning outcome"""
        
        outcome = LearningOutcome(
            outcome_id=str(uuid.uuid4()),
            agent_id=agent_id,
            task_type=task_type,
            input_context=input_context,
            output_result=output_result,
            success_score=success_score,
            execution_time=execution_time,
            cost_incurred=cost_incurred,
            feedback=feedback
        )
        
        success = self.memory_store.store_learning_outcome(outcome)
        
        if success:
            # Analyze for patterns
            self._analyze_learning_patterns(outcome)
            
            # Update strategy recommendations
            self._update_strategy_recommendations(agent_id, task_type, outcome)
        
        return outcome.outcome_id
    
    def get_strategy_recommendations(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """Get strategy recommendations based on learning"""
        
        cache_key = f"{agent_id}:{task_type}"
        
        if cache_key in self.strategy_cache:
            cached = self.strategy_cache[cache_key]
            # Check if cache is still fresh (1 hour)
            if (datetime.now() - cached['timestamp']).seconds < 3600:
                return cached['recommendations']
        
        # Generate fresh recommendations
        recommendations = self._generate_recommendations(agent_id, task_type)
        
        self.strategy_cache[cache_key] = {
            'recommendations': recommendations,
            'timestamp': datetime.now()
        }
        
        return recommendations
    
    def _analyze_learning_patterns(self, outcome: LearningOutcome):
        """Analyze patterns in learning outcomes"""
        
        pattern_key = f"{outcome.agent_id}:{outcome.task_type}"
        self.learning_patterns[pattern_key].append({
            'success_score': outcome.success_score,
            'execution_time': outcome.execution_time,
            'cost': outcome.cost_incurred,
            'timestamp': outcome.timestamp,
            'input_context': outcome.input_context
        })
        
        # Keep only recent patterns (last 100)
        if len(self.learning_patterns[pattern_key]) > 100:
            self.learning_patterns[pattern_key] = self.learning_patterns[pattern_key][-100:]
    
    def _update_strategy_recommendations(self, agent_id: str, task_type: str, outcome: LearningOutcome):
        """Update strategy recommendations based on new outcome"""
        
        # Identify what worked well
        if outcome.success_score >= 0.8:
            # Store successful strategies as memories
            success_memory = MemoryEntry(
                id=str(uuid.uuid4()),
                content={
                    'strategy': 'successful_approach',
                    'input_context': outcome.input_context,
                    'output_result': outcome.output_result,
                    'success_factors': self._extract_success_factors(outcome)
                },
                memory_type='long_term',
                agent_id=agent_id,
                timestamp=datetime.now(),
                importance_score=outcome.success_score,
                tags=[task_type, 'successful_strategy']
            )
            
            self.memory_store.store_memory(success_memory)
    
    def _extract_success_factors(self, outcome: LearningOutcome) -> List[str]:
        """Extract factors that contributed to success"""
        
        factors = []
        
        # Fast execution
        if outcome.execution_time < 30:  # seconds
            factors.append('fast_execution')
        
        # Cost effective
        if outcome.cost_incurred < 2.0:  # dollars
            factors.append('cost_effective')
        
        # High quality
        if outcome.success_score >= 0.9:
            factors.append('high_quality')
        
        return factors
    
    def _generate_recommendations(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """Generate strategy recommendations based on historical data"""
        
        # Get recent successful outcomes
        pattern_key = f"{agent_id}:{task_type}"
        patterns = self.learning_patterns.get(pattern_key, [])
        
        if not patterns:
            return {
                'status': 'no_data',
                'recommendations': ['Use default strategy', 'Focus on quality over speed']
            }
        
        # Analyze successful patterns
        successful_patterns = [p for p in patterns if p['success_score'] >= 0.7]
        
        if not successful_patterns:
            return {
                'status': 'no_success',
                'recommendations': ['Review failed attempts', 'Try alternative approaches']
            }
        
        # Generate recommendations
        recommendations = []
        
        # Execution time recommendations
        avg_successful_time = sum(p['execution_time'] for p in successful_patterns) / len(successful_patterns)
        recommendations.append(f"Target execution time: {avg_successful_time:.1f} seconds")
        
        # Cost recommendations
        avg_successful_cost = sum(p['cost'] for p in successful_patterns) / len(successful_patterns)
        recommendations.append(f"Target cost budget: ${avg_successful_cost:.2f}")
        
        # Success rate
        success_rate = len(successful_patterns) / len(patterns)
        if success_rate < 0.8:
            recommendations.append("Focus on improving consistency")
        else:
            recommendations.append("Maintain current successful approach")
        
        return {
            'status': 'success',
            'success_rate': success_rate,
            'recommendations': recommendations,
            'sample_size': len(patterns),
            'successful_samples': len(successful_patterns)
        }

class AgentMemoryManager:
    """Main memory manager that coordinates all memory systems"""
    
    def __init__(self, db_path: str = "agent_memory.db", redis_url: str = "redis://localhost:6379/1"):
        self.memory_store = AgentMemoryStore(db_path)
        self.short_term_memories = {}  # Per agent
        self.shared_memory = SharedMemory(redis_url)
        self.learning_pipeline = LearningPipeline(self.memory_store)
    
    def get_agent_memory(self, agent_id: str) -> ShortTermMemory:
        """Get or create short-term memory for an agent"""
        if agent_id not in self.short_term_memories:
            self.short_term_memories[agent_id] = ShortTermMemory()
        return self.short_term_memories[agent_id]
    
    def store_long_term_memory(self, agent_id: str, content: Any, 
                              importance: float, tags: List[str] = None) -> str:
        """Store long-term memory for an agent"""
        
        memory = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            memory_type='long_term',
            agent_id=agent_id,
            timestamp=datetime.now(),
            importance_score=importance,
            tags=tags or []
        )
        
        success = self.memory_store.store_memory(memory)
        return memory.id if success else None
    
    def retrieve_relevant_memories(self, agent_id: str, context: str, 
                                  limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to current context"""
        
        # Get all memories for agent
        memories = self.memory_store.retrieve_memories(agent_id, limit=100)
        
        # Simple relevance scoring (could be enhanced with embeddings)
        scored_memories = []
        context_lower = context.lower()
        
        for memory in memories:
            relevance_score = 0.0
            
            # Check tags
            for tag in memory.tags:
                if tag.lower() in context_lower:
                    relevance_score += 0.3
            
            # Check content (simplified)
            if isinstance(memory.content, dict):
                content_str = json.dumps(memory.content).lower()
                if any(word in content_str for word in context_lower.split()):
                    relevance_score += 0.2
            
            # Factor in importance and recency
            relevance_score += memory.importance_score * 0.3
            
            # Recency bonus
            days_old = (datetime.now() - memory.timestamp).days
            if days_old < 7:
                relevance_score += 0.2
            
            scored_memories.append((memory, relevance_score))
        
        # Sort by relevance and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in scored_memories[:limit]]
    
    def record_agent_outcome(self, agent_id: str, task_type: str, input_context: Dict,
                           output_result: Dict, success_score: float, execution_time: float,
                           cost_incurred: float, feedback: str = None) -> str:
        """Record outcome and learn from it"""
        
        return self.learning_pipeline.record_outcome(
            agent_id, task_type, input_context, output_result,
            success_score, execution_time, cost_incurred, feedback
        )
    
    def get_agent_insights(self, agent_id: str) -> Dict[str, Any]:
        """Get insights and recommendations for an agent"""
        
        # Get recent memories
        recent_memories = self.memory_store.retrieve_memories(agent_id, limit=20)
        
        # Get learning recommendations
        task_types = set()
        for memory in recent_memories:
            if 'task_type' in str(memory.content):
                # Extract task types from memory content
                if isinstance(memory.content, dict) and 'task_type' in memory.content:
                    task_types.add(memory.content['task_type'])
        
        recommendations = {}
        for task_type in task_types:
            recommendations[task_type] = self.learning_pipeline.get_strategy_recommendations(agent_id, task_type)
        
        return {
            'agent_id': agent_id,
            'memory_count': len(recent_memories),
            'task_types_handled': list(task_types),
            'strategy_recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup_old_memories(self, days_old: int = 30):
        """Clean up old, low-importance memories"""
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            conn = sqlite3.connect(self.memory_store.db_path)
            cursor = conn.cursor()
            
            # Delete old, low-importance memories
            cursor.execute('''
                DELETE FROM memory_entries 
                WHERE timestamp < ? AND importance_score < 0.3
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old memories")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up memories: {str(e)}")
            return 0

# Usage example and integration
async def integrate_memory_with_agents():
    """Example of how to integrate memory system with existing agents"""
    
    # Initialize memory manager
    memory_manager = AgentMemoryManager()
    
    # Example: Market Scanner Agent with memory
    class MemoryEnabledMarketScanner:
        def __init__(self, agent_id: str, memory_manager: AgentMemoryManager):
            self.agent_id = agent_id
            self.memory = memory_manager
            self.short_term = memory_manager.get_agent_memory(agent_id)
        
        async def analyze_market_with_memory(self, business_type: str, location: str):
            """Market analysis with memory capabilities"""
            
            start_time = datetime.now()
            
            # Check for relevant memories
            context = f"{business_type} {location}"
            relevant_memories = self.memory.retrieve_relevant_memories(
                self.agent_id, context
            )
            
            # Store current context in short-term memory
            self.short_term.add(
                f"current_analysis_{int(start_time.timestamp())}", 
                {'business_type': business_type, 'location': location},
                importance=0.7
            )
            
            # Simulate analysis (would be actual API call)
            await asyncio.sleep(2)  # Simulate processing time
            
            analysis_result = {
                'business_type': business_type,
                'location': location,
                'competitors_found': 5,
                'market_saturation': 'medium',
                'opportunities': ['local_seo', 'social_media'],
                'used_memories': len(relevant_memories)
            }
            
            # Calculate success score
            success_score = 0.85  # Would be calculated based on actual results
            execution_time = (datetime.now() - start_time).total_seconds()
            cost = 2.50  # Simulated API cost
            
            # Record outcome for learning
            outcome_id = self.memory.record_agent_outcome(
                self.agent_id,
                'market_analysis',
                {'business_type': business_type, 'location': location},
                analysis_result,
                success_score,
                execution_time,
                cost
            )
            
            # Store important findings as long-term memory
            if success_score >= 0.8:
                self.memory.store_long_term_memory(
                    self.agent_id,
                    {
                        'analysis_type': 'market_analysis',
                        'input': {'business_type': business_type, 'location': location},
                        'key_findings': analysis_result,
                        'outcome_id': outcome_id
                    },
                    importance=success_score,
                    tags=[business_type.lower(), location.lower(), 'market_analysis']
                )
            
            return {
                'analysis': analysis_result,
                'memory_context': {
                    'memories_used': len(relevant_memories),
                    'outcome_recorded': outcome_id,
                    'recommendations': self.memory.learning_pipeline.get_strategy_recommendations(
                        self.agent_id, 'market_analysis'
                    )
                }
            }
    
    # Test the memory-enabled agent
    scanner = MemoryEnabledMarketScanner("market_scanner_001", memory_manager)
    result = await scanner.analyze_market_with_memory("HVAC Services", "Birmingham, AL")
    
    print("Analysis with Memory Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Get agent insights
    insights = memory_manager.get_agent_insights("market_scanner_001")
    print("\nAgent Insights:")
    print(json.dumps(insights, indent=2, default=str))

if __name__ == "__main__":
    # Example usage
    asyncio.run(integrate_memory_with_agents())