"""
Alerting System Module

Comprehensive alerting system for monitoring GraphQL API performance,
errors, and system health. Provides real-time alerts and notifications.
"""

import logging
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Alert types"""
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    RESPONSE_TIME = "response_time"
    SYSTEM_HEALTH = "system_health"
    GRAPHQL_COMPLEXITY = "graphql_complexity"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None


class AlertingSystem:
    """
    Alerting System
    
    Monitors system metrics and triggers alerts when thresholds are exceeded.
    Supports multiple alert channels and customizable rules.
    """
    
    def __init__(self):
        self._alerts: Dict[str, Alert] = {}
        self._alert_rules: Dict[str, Dict] = {}
        self._alert_handlers: List[Callable] = []
        self._lock = threading.Lock()
        self._alert_counters = defaultdict(int)
        
        # Initialize default alert rules
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialize default alert rules"""
        self._alert_rules = {
            'high_error_rate': {
                'type': AlertType.ERROR_RATE,
                'threshold': 5.0,  # 5% error rate
                'severity': AlertSeverity.WARNING,
                'message': 'Error rate is above threshold',
            },
            'critical_error_rate': {
                'type': AlertType.ERROR_RATE,
                'threshold': 10.0,  # 10% error rate
                'severity': AlertSeverity.CRITICAL,
                'message': 'Critical error rate detected',
            },
            'low_cache_hit_rate': {
                'type': AlertType.CACHE_HIT_RATE,
                'threshold': 40.0,  # Below 40%
                'severity': AlertSeverity.WARNING,
                'message': 'Cache hit rate is below threshold',
                'comparison': 'below',
            },
            'slow_response_time': {
                'type': AlertType.RESPONSE_TIME,
                'threshold': 1000.0,  # 1 second
                'severity': AlertSeverity.WARNING,
                'message': 'Response time is slow',
            },
            'very_slow_response_time': {
                'type': AlertType.RESPONSE_TIME,
                'threshold': 3000.0,  # 3 seconds
                'severity': AlertSeverity.ERROR,
                'message': 'Response time is very slow',
            },
            'high_graphql_complexity': {
                'type': AlertType.GRAPHQL_COMPLEXITY,
                'threshold': 800.0,  # Complexity score
                'severity': AlertSeverity.WARNING,
                'message': 'GraphQL query complexity is high',
            },
        }
    
    def check_metric(self, metric_type: AlertType, value: float, context: Dict = None):
        """
        Check a metric against alert rules.
        
        Args:
            metric_type: Type of metric being checked
            value: Current metric value
            context: Additional context information
        """
        with self._lock:
            for rule_name, rule in self._alert_rules.items():
                if rule['type'] != metric_type:
                    continue
                
                threshold = rule['threshold']
                comparison = rule.get('comparison', 'above')
                
                # Check if threshold is exceeded
                is_exceeded = (
                    (comparison == 'above' and value > threshold) or
                    (comparison == 'below' and value < threshold)
                )
                
                if is_exceeded:
                    self._trigger_alert(rule_name, rule, value, context)
                else:
                    self._resolve_alert(rule_name)
    
    def _trigger_alert(self, rule_name: str, rule: Dict, value: float, context: Dict):
        """Trigger an alert"""
        alert_id = f"{rule_name}_{int(time.time())}"
        
        # Check if similar alert already exists
        existing_alert = self._alerts.get(rule_name)
        if existing_alert and not existing_alert.resolved:
            # Update existing alert
            existing_alert.metric_value = value
            existing_alert.timestamp = time.time()
            return
        
        # Create new alert
        alert = Alert(
            id=alert_id,
            type=rule['type'],
            severity=rule['severity'],
            message=rule['message'],
            metric_value=value,
            threshold=rule['threshold'],
            timestamp=time.time(),
        )
        
        self._alerts[rule_name] = alert
        self._alert_counters[rule_name] += 1
        
        # Log alert
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }[alert.severity]
        
        logger.log(
            log_level,
            f"ALERT [{alert.severity.value.upper()}]: {alert.message} "
            f"(value: {value}, threshold: {alert.threshold})",
            extra={'alert_id': alert.id, 'context': context}
        )
        
        # Notify handlers
        for handler in self._alert_handlers:
            try:
                handler(alert, context)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def _resolve_alert(self, rule_name: str):
        """Resolve an alert"""
        alert = self._alerts.get(rule_name)
        if alert and not alert.resolved:
            alert.resolved = True
            alert.resolved_at = time.time()
            
            logger.info(
                f"ALERT RESOLVED: {alert.message}",
                extra={'alert_id': alert.id}
            )
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler"""
        self._alert_handlers.append(handler)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        with self._lock:
            return [
                alert for alert in self._alerts.values()
                if not alert.resolved
            ]
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for the last N hours"""
        cutoff = time.time() - (hours * 3600)
        with self._lock:
            return [
                alert for alert in self._alerts.values()
                if alert.timestamp >= cutoff
            ]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        with self._lock:
            total_alerts = len(self._alerts)
            active_alerts = len([a for a in self._alerts.values() if not a.resolved])
            resolved_alerts = total_alerts - active_alerts
            
            severity_counts = defaultdict(int)
            for alert in self._alerts.values():
                severity_counts[alert.severity.value] += 1
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'by_severity': dict(severity_counts),
                'by_type': dict(self._alert_counters),
            }
    
    def clear_resolved_alerts(self):
        """Clear all resolved alerts"""
        with self._lock:
            self._alerts = {
                k: v for k, v in self._alerts.items()
                if not v.resolved
            }


# Global alerting system instance
_alerting_system = None


def get_alerting_system() -> AlertingSystem:
    """Get or create alerting system instance"""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = AlertingSystem()
    return _alerting_system
