"""
Response Strategy Selector
Intelligently selects the best response method based on context, resources, and system state
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResponseStrategy(Enum):
    """Available response strategies"""
    ENHANCED_TEMPLATE = "enhanced_template"  # Primary: Smart template with full personalization
    BASIC_TEMPLATE = "basic_template"        # Secondary: Simple template with minimal context
    LLM_ASSISTED = "llm_assisted"           # Tertiary: LLM for complex cases (rare)
    EMERGENCY_FALLBACK = "emergency_fallback" # Last resort: Hardcoded responses

class SystemLoadLevel(Enum):
    """System load levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """Current system performance metrics"""
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    response_time_ms: float = 0.0
    database_query_count: int = 0
    cache_hit_rate: float = 0.0
    active_users: int = 0
    error_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SelectionCriteria:
    """Criteria for strategy selection"""
    message_complexity: float = 0.5  # 0.0 = simple, 1.0 = complex
    emotion_intensity: float = 0.5   # 0.0 = neutral, 1.0 = very intense
    context_availability: float = 0.5 # 0.0 = no context, 1.0 = rich context
    user_engagement_level: float = 0.5 # 0.0 = low, 1.0 = high
    conversation_length: int = 0
    requires_empathy: bool = False
    requires_memory: bool = False
    is_crisis_situation: bool = False

@dataclass
class StrategyDecision:
    """Result of strategy selection"""
    selected_strategy: ResponseStrategy
    confidence: float
    reasoning: List[str] = field(default_factory=list)
    fallback_strategies: List[ResponseStrategy] = field(default_factory=list)
    estimated_cost: float = 0.0  # Relative cost (0.0 = free, 1.0 = expensive)
    estimated_quality: float = 0.0  # Expected quality (0.0 = poor, 1.0 = excellent)
    system_constraints: List[str] = field(default_factory=list)

class ResponseStrategySelector:
    """
    Intelligently selects response strategies based on multiple factors
    """
    
    def __init__(self):
        self.strategy_weights = self._load_strategy_weights()
        self.system_thresholds = self._load_system_thresholds()
        self.performance_history = []
        self.max_history_size = 100
        
        # Strategy performance tracking
        self.strategy_stats = {
            'total_selections': 0,
            'strategy_usage': {},
            'strategy_success_rates': {},
            'average_response_times': {},
            'cost_tracking': {}
        }
        
        # Circuit breaker for expensive operations
        self.circuit_breaker = {
            'llm_failures': 0,
            'llm_last_failure': None,
            'llm_circuit_open': False,
            'database_failures': 0,
            'database_last_failure': None,
            'database_circuit_open': False
        }
        
        logger.info("ResponseStrategySelector initialized with intelligent selection")
    
    def _load_strategy_weights(self) -> Dict[str, Dict[str, float]]:
        """Load weights for different selection factors"""
        return {
            'message_complexity': {
                ResponseStrategy.ENHANCED_TEMPLATE.value: 0.8,
                ResponseStrategy.BASIC_TEMPLATE.value: 0.6,
                ResponseStrategy.LLM_ASSISTED.value: 1.0,
                ResponseStrategy.EMERGENCY_FALLBACK.value: 0.2
            },
            'emotion_intensity': {
                ResponseStrategy.ENHANCED_TEMPLATE.value: 0.9,
                ResponseStrategy.BASIC_TEMPLATE.value: 0.7,
                ResponseStrategy.LLM_ASSISTED.value: 0.8,
                ResponseStrategy.EMERGENCY_FALLBACK.value: 0.4
            },
            'context_availability': {
                ResponseStrategy.ENHANCED_TEMPLATE.value: 1.0,
                ResponseStrategy.BASIC_TEMPLATE.value: 0.5,
                ResponseStrategy.LLM_ASSISTED.value: 0.7,
                ResponseStrategy.EMERGENCY_FALLBACK.value: 0.1
            },
            'system_load': {
                ResponseStrategy.ENHANCED_TEMPLATE.value: 0.7,  # Medium resource usage
                ResponseStrategy.BASIC_TEMPLATE.value: 0.9,    # Low resource usage
                ResponseStrategy.LLM_ASSISTED.value: 0.3,     # High resource usage
                ResponseStrategy.EMERGENCY_FALLBACK.value: 1.0 # Minimal resources
            }
        }
    
    def _load_system_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load system performance thresholds"""
        return {
            'memory_usage_mb': {
                'low': 200,
                'medium': 350,
                'high': 450,
                'critical': 500
            },
            'cpu_usage_percent': {
                'low': 30,
                'medium': 60,
                'high': 80,
                'critical': 95
            },
            'response_time_ms': {
                'low': 100,
                'medium': 300,
                'high': 500,
                'critical': 1000
            },
            'error_rate': {
                'low': 0.01,
                'medium': 0.05,
                'high': 0.10,
                'critical': 0.20
            }
        }
    
    def select_strategy(self, criteria: SelectionCriteria, 
                       system_metrics: SystemMetrics) -> StrategyDecision:
        """
        Select the best response strategy based on criteria and system state
        """
        try:
            self.strategy_stats['total_selections'] += 1
            
            # Assess system load
            system_load = self._assess_system_load(system_metrics)
            
            # Check circuit breakers
            circuit_constraints = self._check_circuit_breakers()
            
            # Calculate strategy scores
            strategy_scores = self._calculate_strategy_scores(criteria, system_load)
            
            # Apply constraints
            strategy_scores = self._apply_constraints(strategy_scores, circuit_constraints, system_load)
            
            # Select best strategy
            selected_strategy = max(strategy_scores, key=strategy_scores.get)
            confidence = strategy_scores[selected_strategy]
            
            # Build reasoning
            reasoning = self._build_reasoning(selected_strategy, criteria, system_load, circuit_constraints)
            
            # Determine fallback strategies
            fallback_strategies = self._determine_fallbacks(selected_strategy, strategy_scores)
            
            # Estimate cost and quality
            estimated_cost = self._estimate_cost(selected_strategy)
            estimated_quality = self._estimate_quality(selected_strategy, criteria)
            
            # Create decision
            decision = StrategyDecision(
                selected_strategy=selected_strategy,
                confidence=confidence,
                reasoning=reasoning,
                fallback_strategies=fallback_strategies,
                estimated_cost=estimated_cost,
                estimated_quality=estimated_quality,
                system_constraints=circuit_constraints
            )
            
            # Update statistics
            self._update_statistics(decision)
            
            logger.debug(f"Selected strategy: {selected_strategy.value} "
                        f"(confidence: {confidence:.2f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error selecting strategy: {e}")
            return self._create_emergency_decision()
    
    def _assess_system_load(self, metrics: SystemMetrics) -> SystemLoadLevel:
        """Assess current system load level"""
        load_indicators = []
        
        # Memory usage assessment
        memory_thresholds = self.system_thresholds['memory_usage_mb']
        if metrics.memory_usage_mb >= memory_thresholds['critical']:
            load_indicators.append('critical')
        elif metrics.memory_usage_mb >= memory_thresholds['high']:
            load_indicators.append('high')
        elif metrics.memory_usage_mb >= memory_thresholds['medium']:
            load_indicators.append('medium')
        else:
            load_indicators.append('low')
        
        # CPU usage assessment
        cpu_thresholds = self.system_thresholds['cpu_usage_percent']
        if metrics.cpu_usage_percent >= cpu_thresholds['critical']:
            load_indicators.append('critical')
        elif metrics.cpu_usage_percent >= cpu_thresholds['high']:
            load_indicators.append('high')
        elif metrics.cpu_usage_percent >= cpu_thresholds['medium']:
            load_indicators.append('medium')
        else:
            load_indicators.append('low')
        
        # Response time assessment
        response_thresholds = self.system_thresholds['response_time_ms']
        if metrics.response_time_ms >= response_thresholds['critical']:
            load_indicators.append('critical')
        elif metrics.response_time_ms >= response_thresholds['high']:
            load_indicators.append('high')
        elif metrics.response_time_ms >= response_thresholds['medium']:
            load_indicators.append('medium')
        else:
            load_indicators.append('low')
        
        # Error rate assessment
        error_thresholds = self.system_thresholds['error_rate']
        if metrics.error_rate >= error_thresholds['critical']:
            load_indicators.append('critical')
        elif metrics.error_rate >= error_thresholds['high']:
            load_indicators.append('high')
        elif metrics.error_rate >= error_thresholds['medium']:
            load_indicators.append('medium')
        else:
            load_indicators.append('low')
        
        # Determine overall load (worst case)
        if 'critical' in load_indicators:
            return SystemLoadLevel.CRITICAL
        elif 'high' in load_indicators:
            return SystemLoadLevel.HIGH
        elif 'medium' in load_indicators:
            return SystemLoadLevel.MEDIUM
        else:
            return SystemLoadLevel.LOW
    
    def _check_circuit_breakers(self) -> List[str]:
        """Check circuit breaker status"""
        constraints = []
        current_time = datetime.now()
        
        # LLM circuit breaker
        if self.circuit_breaker['llm_circuit_open']:
            # Check if we should close the circuit (after 5 minutes)
            if (self.circuit_breaker['llm_last_failure'] and 
                current_time - self.circuit_breaker['llm_last_failure'] > timedelta(minutes=5)):
                self.circuit_breaker['llm_circuit_open'] = False
                self.circuit_breaker['llm_failures'] = 0
                logger.info("LLM circuit breaker closed")
            else:
                constraints.append("llm_circuit_open")
        
        # Database circuit breaker
        if self.circuit_breaker['database_circuit_open']:
            # Check if we should close the circuit (after 2 minutes)
            if (self.circuit_breaker['database_last_failure'] and 
                current_time - self.circuit_breaker['database_last_failure'] > timedelta(minutes=2)):
                self.circuit_breaker['database_circuit_open'] = False
                self.circuit_breaker['database_failures'] = 0
                logger.info("Database circuit breaker closed")
            else:
                constraints.append("database_circuit_open")
        
        return constraints
    
    def _calculate_strategy_scores(self, criteria: SelectionCriteria, 
                                 system_load: SystemLoadLevel) -> Dict[ResponseStrategy, float]:
        """Calculate scores for each strategy"""
        scores = {}
        
        for strategy in ResponseStrategy:
            score = 0.0
            
            # Message complexity factor
            complexity_weight = self.strategy_weights['message_complexity'][strategy.value]
            score += criteria.message_complexity * complexity_weight * 0.25
            
            # Emotion intensity factor
            emotion_weight = self.strategy_weights['emotion_intensity'][strategy.value]
            score += criteria.emotion_intensity * emotion_weight * 0.25
            
            # Context availability factor
            context_weight = self.strategy_weights['context_availability'][strategy.value]
            score += criteria.context_availability * context_weight * 0.25
            
            # System load factor (inverted - lower load = higher score)
            load_factor = self._get_load_factor(system_load)
            system_weight = self.strategy_weights['system_load'][strategy.value]
            score += (1.0 - load_factor) * system_weight * 0.25
            
            # Special case bonuses
            if criteria.is_crisis_situation and strategy == ResponseStrategy.ENHANCED_TEMPLATE:
                score += 0.2  # Prioritize quality for crisis
            
            if criteria.requires_empathy and strategy in [ResponseStrategy.ENHANCED_TEMPLATE, ResponseStrategy.LLM_ASSISTED]:
                score += 0.1  # Boost empathetic strategies
            
            if criteria.requires_memory and strategy == ResponseStrategy.ENHANCED_TEMPLATE:
                score += 0.15  # Boost memory-aware strategy
            
            scores[strategy] = min(1.0, max(0.0, score))  # Clamp to [0, 1]
        
        return scores
    
    def _get_load_factor(self, system_load: SystemLoadLevel) -> float:
        """Convert system load to numeric factor"""
        load_factors = {
            SystemLoadLevel.LOW: 0.1,
            SystemLoadLevel.MEDIUM: 0.4,
            SystemLoadLevel.HIGH: 0.7,
            SystemLoadLevel.CRITICAL: 0.9
        }
        return load_factors[system_load]
    
    def _apply_constraints(self, scores: Dict[ResponseStrategy, float], 
                          constraints: List[str], 
                          system_load: SystemLoadLevel) -> Dict[ResponseStrategy, float]:
        """Apply system constraints to strategy scores"""
        constrained_scores = scores.copy()
        
        # LLM circuit breaker constraint
        if "llm_circuit_open" in constraints:
            constrained_scores[ResponseStrategy.LLM_ASSISTED] = 0.0
        
        # Database circuit breaker constraint
        if "database_circuit_open" in constraints:
            # Reduce scores for strategies that require database
            constrained_scores[ResponseStrategy.ENHANCED_TEMPLATE] *= 0.3
        
        # Critical system load constraints
        if system_load == SystemLoadLevel.CRITICAL:
            # Force emergency fallback
            constrained_scores[ResponseStrategy.EMERGENCY_FALLBACK] = 1.0
            constrained_scores[ResponseStrategy.LLM_ASSISTED] = 0.0
            constrained_scores[ResponseStrategy.ENHANCED_TEMPLATE] *= 0.2
        
        # High system load constraints
        elif system_load == SystemLoadLevel.HIGH:
            # Discourage expensive operations
            constrained_scores[ResponseStrategy.LLM_ASSISTED] *= 0.1
            constrained_scores[ResponseStrategy.ENHANCED_TEMPLATE] *= 0.7
        
        return constrained_scores
    
    def _build_reasoning(self, strategy: ResponseStrategy, criteria: SelectionCriteria,
                        system_load: SystemLoadLevel, constraints: List[str]) -> List[str]:
        """Build reasoning for strategy selection"""
        reasoning = []
        
        # Strategy-specific reasoning
        if strategy == ResponseStrategy.ENHANCED_TEMPLATE:
            reasoning.append("Selected enhanced template for rich personalization")
            if criteria.context_availability > 0.7:
                reasoning.append("High context availability supports enhanced response")
            if criteria.emotion_intensity > 0.6:
                reasoning.append("Emotional intensity requires empathetic response")
        
        elif strategy == ResponseStrategy.BASIC_TEMPLATE:
            reasoning.append("Selected basic template for efficiency")
            if system_load in [SystemLoadLevel.MEDIUM, SystemLoadLevel.HIGH]:
                reasoning.append(f"System load ({system_load.value}) favors lightweight approach")
            if criteria.context_availability < 0.5:
                reasoning.append("Limited context available")
        
        elif strategy == ResponseStrategy.LLM_ASSISTED:
            reasoning.append("Selected LLM assistance for complex response")
            if criteria.message_complexity > 0.8:
                reasoning.append("High message complexity requires advanced processing")
            if criteria.is_crisis_situation:
                reasoning.append("Crisis situation needs careful handling")
        
        elif strategy == ResponseStrategy.EMERGENCY_FALLBACK:
            reasoning.append("Selected emergency fallback for reliability")
            if system_load == SystemLoadLevel.CRITICAL:
                reasoning.append("Critical system load requires minimal processing")
            if constraints:
                reasoning.append(f"System constraints: {', '.join(constraints)}")
        
        # System state reasoning
        if system_load != SystemLoadLevel.LOW:
            reasoning.append(f"System load: {system_load.value}")
        
        if constraints:
            reasoning.append(f"Active constraints: {', '.join(constraints)}")
        
        return reasoning
    
    def _determine_fallbacks(self, primary_strategy: ResponseStrategy, 
                           scores: Dict[ResponseStrategy, float]) -> List[ResponseStrategy]:
        """Determine fallback strategies in order of preference"""
        # Sort strategies by score, excluding the primary
        fallback_candidates = [(strategy, score) for strategy, score in scores.items() 
                              if strategy != primary_strategy]
        fallback_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Always include emergency fallback as last resort
        fallbacks = [strategy for strategy, _ in fallback_candidates[:2]]
        if ResponseStrategy.EMERGENCY_FALLBACK not in fallbacks:
            fallbacks.append(ResponseStrategy.EMERGENCY_FALLBACK)
        
        return fallbacks
    
    def _estimate_cost(self, strategy: ResponseStrategy) -> float:
        """Estimate relative cost of strategy"""
        cost_estimates = {
            ResponseStrategy.ENHANCED_TEMPLATE: 0.6,  # Medium cost (database + processing)
            ResponseStrategy.BASIC_TEMPLATE: 0.2,     # Low cost
            ResponseStrategy.LLM_ASSISTED: 1.0,       # High cost (API calls)
            ResponseStrategy.EMERGENCY_FALLBACK: 0.0  # No cost
        }
        return cost_estimates[strategy]
    
    def _estimate_quality(self, strategy: ResponseStrategy, criteria: SelectionCriteria) -> float:
        """Estimate expected response quality"""
        base_quality = {
            ResponseStrategy.ENHANCED_TEMPLATE: 0.9,
            ResponseStrategy.BASIC_TEMPLATE: 0.6,
            ResponseStrategy.LLM_ASSISTED: 0.8,
            ResponseStrategy.EMERGENCY_FALLBACK: 0.3
        }
        
        quality = base_quality[strategy]
        
        # Adjust based on criteria
        if strategy == ResponseStrategy.ENHANCED_TEMPLATE:
            # Quality depends on context availability
            quality *= (0.5 + 0.5 * criteria.context_availability)
        
        elif strategy == ResponseStrategy.LLM_ASSISTED:
            # Quality depends on message complexity match
            if criteria.message_complexity > 0.7:
                quality *= 1.1  # LLM excels at complex messages
            else:
                quality *= 0.9  # Overkill for simple messages
        
        return min(1.0, quality)
    
    def _create_emergency_decision(self) -> StrategyDecision:
        """Create emergency fallback decision"""
        return StrategyDecision(
            selected_strategy=ResponseStrategy.EMERGENCY_FALLBACK,
            confidence=1.0,
            reasoning=["Emergency fallback due to system error"],
            fallback_strategies=[],
            estimated_cost=0.0,
            estimated_quality=0.3,
            system_constraints=["system_error"]
        )
    
    def _update_statistics(self, decision: StrategyDecision):
        """Update strategy selection statistics"""
        strategy = decision.selected_strategy.value
        
        # Update usage counts
        self.strategy_stats['strategy_usage'][strategy] = \
            self.strategy_stats['strategy_usage'].get(strategy, 0) + 1
        
        # Track costs
        self.strategy_stats['cost_tracking'][strategy] = \
            self.strategy_stats['cost_tracking'].get(strategy, [])
        self.strategy_stats['cost_tracking'][strategy].append(decision.estimated_cost)
    
    def record_strategy_outcome(self, strategy: ResponseStrategy, success: bool, 
                              response_time_ms: float):
        """Record the outcome of a strategy execution"""
        strategy_name = strategy.value
        
        # Update success rates
        if strategy_name not in self.strategy_stats['strategy_success_rates']:
            self.strategy_stats['strategy_success_rates'][strategy_name] = []
        
        self.strategy_stats['strategy_success_rates'][strategy_name].append(success)
        
        # Keep only recent results (last 50)
        if len(self.strategy_stats['strategy_success_rates'][strategy_name]) > 50:
            self.strategy_stats['strategy_success_rates'][strategy_name] = \
                self.strategy_stats['strategy_success_rates'][strategy_name][-50:]
        
        # Update response times
        if strategy_name not in self.strategy_stats['average_response_times']:
            self.strategy_stats['average_response_times'][strategy_name] = []
        
        self.strategy_stats['average_response_times'][strategy_name].append(response_time_ms)
        
        # Keep only recent times (last 50)
        if len(self.strategy_stats['average_response_times'][strategy_name]) > 50:
            self.strategy_stats['average_response_times'][strategy_name] = \
                self.strategy_stats['average_response_times'][strategy_name][-50:]
        
        # Update circuit breakers based on failures
        if not success:
            if strategy == ResponseStrategy.LLM_ASSISTED:
                self.circuit_breaker['llm_failures'] += 1
                self.circuit_breaker['llm_last_failure'] = datetime.now()
                
                # Open circuit after 3 failures
                if self.circuit_breaker['llm_failures'] >= 3:
                    self.circuit_breaker['llm_circuit_open'] = True
                    logger.warning("LLM circuit breaker opened due to failures")
            
            elif strategy == ResponseStrategy.ENHANCED_TEMPLATE:
                self.circuit_breaker['database_failures'] += 1
                self.circuit_breaker['database_last_failure'] = datetime.now()
                
                # Open circuit after 5 failures
                if self.circuit_breaker['database_failures'] >= 5:
                    self.circuit_breaker['database_circuit_open'] = True
                    logger.warning("Database circuit breaker opened due to failures")
    
    def get_strategy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive strategy statistics"""
        stats = {
            'total_selections': self.strategy_stats['total_selections'],
            'strategy_usage': self.strategy_stats['strategy_usage'].copy(),
            'strategy_success_rates': {},
            'average_response_times': {},
            'average_costs': {},
            'circuit_breaker_status': {
                'llm_circuit_open': self.circuit_breaker['llm_circuit_open'],
                'database_circuit_open': self.circuit_breaker['database_circuit_open'],
                'llm_failures': self.circuit_breaker['llm_failures'],
                'database_failures': self.circuit_breaker['database_failures']
            }
        }
        
        # Calculate success rates
        for strategy, results in self.strategy_stats['strategy_success_rates'].items():
            if results:
                success_rate = sum(results) / len(results) * 100
                stats['strategy_success_rates'][strategy] = round(success_rate, 2)
        
        # Calculate average response times
        for strategy, times in self.strategy_stats['average_response_times'].items():
            if times:
                avg_time = sum(times) / len(times)
                stats['average_response_times'][strategy] = round(avg_time, 2)
        
        # Calculate average costs
        for strategy, costs in self.strategy_stats['cost_tracking'].items():
            if costs:
                avg_cost = sum(costs) / len(costs)
                stats['average_costs'][strategy] = round(avg_cost, 3)
        
        return stats
    
    def reset_circuit_breakers(self):
        """Manually reset circuit breakers"""
        self.circuit_breaker = {
            'llm_failures': 0,
            'llm_last_failure': None,
            'llm_circuit_open': False,
            'database_failures': 0,
            'database_last_failure': None,
            'database_circuit_open': False
        }
        logger.info("All circuit breakers reset")

# Global strategy selector instance
_strategy_selector = None

def get_strategy_selector() -> ResponseStrategySelector:
    """Get global strategy selector instance"""
    global _strategy_selector
    if _strategy_selector is None:
        _strategy_selector = ResponseStrategySelector()
    return _strategy_selector