#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控和告警系统
==================
监控缓存性能指标，并在异常时触发告警

核心功能:
- 实时指标采集 (命中率、响应时间、QPS)
- 告警规则引擎 (阈值+持续时间验证)
- 告警去重机制 (防止重复告警)
- 性能指标历史追踪
- 自动化响应 (预热、扩容)

版本: 1.0.0
日期: 2026-02-24
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from backend.core.cache.filters import SensitiveDataFilter

logger = logging.getLogger(__name__)

# Add sensitive data filter to prevent information leakage
logger.addFilter(SensitiveDataFilter())


class AlertLevel(Enum):
    """告警级别"""
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    INFO = "INFO"


@dataclass
class AlertRule:
    """告警规则定义

    Args:
        name: 规则名称
        metric: 监控指标名称
        threshold: 阈值
        duration: 持续时间（秒），指标持续异常多久才触发告警
        level: 告警级别
        action: 触发动作（可选的回调函数）
        description: 规则描述
    """
    name: str
    metric: str
    threshold: float
    duration: int
    level: AlertLevel
    action: Optional[Callable[[], None]] = None
    description: str = ""

    def __str__(self) -> str:
        return (
            f"AlertRule(name={self.name}, "
            f"metric={self.metric}, "
            f"threshold={self.threshold:.2%}, "
            f"duration={self.duration}s, "
            f"level={self.level.value})"
        )


@dataclass
class AlertEvent:
    """告警事件"""
    rule_name: str
    metric: str
    current_value: float
    threshold: float
    level: AlertLevel
    timestamp: float = field(default_factory=time.time)
    duration: int = 0
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_name": self.rule_name,
            "metric": self.metric,
            "current_value": f"{self.current_value:.2%}" if self.metric.endswith("_rate") else f"{self.current_value:.2f}",
            "threshold": f"{self.threshold:.2%}" if self.metric.endswith("_rate") else f"{self.threshold:.2f}",
            "level": self.level.value,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "resolved": self.resolved
        }


@dataclass
class MetricSnapshot:
    """指标快照"""
    timestamp: float
    l1_hit_rate: float
    l2_hit_rate: float
    overall_hit_rate: float
    l1_usage: float
    l2_memory_usage: float
    qps: float
    avg_response_time_ms: float


class MetricsHistory:
    """指标历史记录（使用循环缓冲区）"""

    def __init__(self, max_size: int = 3600):
        """
        初始化指标历史

        Args:
            max_size: 最大保存的快照数量，默认3600（1分钟1个，保存1小时）
        """
        self.max_size = max_size
        self.history: deque[MetricSnapshot] = deque(maxlen=max_size)
        self._lock = Lock()

    def add(self, snapshot: MetricSnapshot):
        """添加快照"""
        with self._lock:
            self.history.append(snapshot)

    def get_recent(self, duration_seconds: int) -> List[MetricSnapshot]:
        """
        获取最近的快照

        Args:
            duration_seconds: 时间范围（秒）

        Returns:
            在时间范围内的所有快照
        """
        cutoff_time = time.time() - duration_seconds

        with self._lock:
            return [s for s in self.history if s.timestamp >= cutoff_time]

    def get_latest(self) -> Optional[MetricSnapshot]:
        """获取最新快照"""
        with self._lock:
            return self.history[-1] if self.history else None

    def get_trend(self, metric: str, duration_seconds: int = 300) -> Optional[Dict[str, float]]:
        """
        计算指标趋势

        Args:
            metric: 指标名称 (l1_hit_rate, l2_hit_rate, overall_hit_rate)
            duration_seconds: 时间范围（秒），默认300秒（5分钟）

        Returns:
            趋势数据 {min, max, avg, trend} 或 None
        """
        snapshots = self.get_recent(duration_seconds)
        if not snapshots:
            return None

        values = [getattr(s, metric) for s in snapshots]

        if not values:
            return None

        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
            "trend": values[-1] - values[0] if len(values) > 1 else 0
        }


class CacheAlertManager:
    """缓存告警管理器

    监控缓存性能指标，并在异常时触发告警

    告警规则:
    - L1命中率 <60% 持续5分钟 → WARNING
    - L2命中率 <70% 持续10分钟 → WARNING
    - 总体命中率 <50% 持续5分钟 → CRITICAL (自动预热)
    - L1命中率 <40% 持续3分钟 → CRITICAL (扩容L1)
    - L1使用率 >85% → WARNING
    - L1使用率 >95% → CRITICAL (自动扩容)
    """

    def __init__(self, hierarchical_cache):
        """
        初始化告警管理器

        Args:
            hierarchical_cache: 三级缓存实例
        """
        self.cache = hierarchical_cache
        self.metrics_history = MetricsHistory(max_size=3600)

        # 告警规则定义
        self.alert_rules: List[AlertRule] = [
            # L1命中率告警
            AlertRule(
                name="l1_hit_rate_low",
                metric="l1_hit_rate",
                threshold=0.6,
                duration=300,  # 5分钟
                level=AlertLevel.WARNING,
                description="L1缓存命中率低于60%持续5分钟"
            ),
            AlertRule(
                name="l1_hit_rate_critical",
                metric="l1_hit_rate",
                threshold=0.4,
                duration=180,  # 3分钟
                level=AlertLevel.CRITICAL,
                action=self._auto_expand_l1,
                description="L1缓存命中率低于40%持续3分钟，触发自动扩容"
            ),

            # L2命中率告警
            AlertRule(
                name="l2_hit_rate_low",
                metric="l2_hit_rate",
                threshold=0.7,
                duration=600,  # 10分钟
                level=AlertLevel.WARNING,
                description="L2缓存命中率低于70%持续10分钟"
            ),

            # 总体命中率告警
            AlertRule(
                name="overall_hit_rate_critical",
                metric="overall_hit_rate",
                threshold=0.5,
                duration=300,  # 5分钟
                level=AlertLevel.CRITICAL,
                action=self._trigger_warm_up,
                description="总体缓存命中率低于50%持续5分钟，触发自动预热"
            ),

            # L1容量告警
            AlertRule(
                name="l1_capacity_warning",
                metric="l1_usage",
                threshold=0.85,
                duration=60,  # 1分钟
                level=AlertLevel.WARNING,
                description="L1缓存使用率超过85%"
            ),
            AlertRule(
                name="l1_capacity_critical",
                metric="l1_usage",
                threshold=0.95,
                duration=30,  # 30秒
                level=AlertLevel.CRITICAL,
                action=self._auto_expand_l1,
                description="L1缓存使用率超过95%，触发自动扩容"
            ),
        ]

        # 告警状态追踪
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.alert_history: List[AlertEvent] = []
        self._alert_lock = Lock()

        # 性能统计（用于计算QPS和响应时间）
        self._request_count = 0
        self._response_time_total = 0.0
        self._last_check_time = time.time()
        self._performance_lock = Lock()

        logger.info("✅ 缓存告警管理器初始化完成")

    def record_request(self, response_time_ms: float):
        """
        记录请求（用于计算QPS和响应时间）

        Args:
            response_time_ms: 响应时间（毫秒）
        """
        with self._performance_lock:
            self._request_count += 1
            self._response_time_total += response_time_ms

    def collect_metrics(self) -> MetricSnapshot:
        """
        采集当前指标快照

        Returns:
            指标快照
        """
        # 获取缓存统计信息
        stats = self.cache.get_stats()

        # 解析百分比字符串
        def parse_rate(rate_str: str) -> float:
            """解析百分比字符串"""
            if isinstance(rate_str, str):
                return float(rate_str.rstrip('%')) / 100
            return float(rate_str)

        # 计算各层命中率
        l1_hits = stats.get('l1_hits', 0)
        l2_hits = stats.get('l2_hits', 0)
        misses = stats.get('misses', 0)
        total_requests = stats.get('total_requests', 1)

        # L1命中率 = L1命中次数 / 总请求次数
        l1_hit_rate = l1_hits / total_requests if total_requests > 0 else 0

        # L2命中率 = L2命中次数 / (L2未命中但L2查询的次数)
        # 简化计算：L2命中 / (L1未命中次数)
        l1_misses = total_requests - l1_hits
        l2_hit_rate = l2_hits / l1_misses if l1_misses > 0 else 0

        # 总体命中率 = (L1命中 + L2命中) / 总请求次数
        overall_hit_rate = (l1_hits + l2_hits) / total_requests if total_requests > 0 else 0

        # 解析L1使用率
        l1_usage = parse_rate(stats.get('l1_usage', '0%'))

        # 计算QPS和平均响应时间
        current_time = time.time()
        time_elapsed = current_time - self._last_check_time

        with self._performance_lock:
            qps = self._request_count / time_elapsed if time_elapsed > 0 else 0
            avg_response_time = (
                self._response_time_total / self._request_count
                if self._request_count > 0 else 0
            )
            # 重置计数器
            self._request_count = 0
            self._response_time_total = 0.0

        self._last_check_time = current_time

        # 创建快照
        snapshot = MetricSnapshot(
            timestamp=current_time,
            l1_hit_rate=l1_hit_rate,
            l2_hit_rate=l2_hit_rate,
            overall_hit_rate=overall_hit_rate,
            l1_usage=l1_usage,
            l2_memory_usage=0.0,  # TODO: 从Redis获取
            qps=qps,
            avg_response_time_ms=avg_response_time
        )

        # 保存到历史记录
        self.metrics_history.add(snapshot)

        return snapshot

    def check_alerts(self) -> List[AlertEvent]:
        """
        检查所有告警规则

        Returns:
            新触发的告警事件列表
        """
        current_snapshot = self.collect_metrics()
        new_alerts: List[AlertEvent] = []

        for rule in self.alert_rules:
            # 获取当前指标值
            current_value = getattr(current_snapshot, rule.metric, 0.0)

            # 检查是否超过阈值
            is_triggered = current_value < rule.threshold if rule.metric.endswith("_rate") else current_value > rule.threshold

            if is_triggered:
                # 检查持续时间
                duration_seconds = self._check_duration(rule, current_value)

                if duration_seconds >= rule.duration:
                    # 触发告警
                    alert = AlertEvent(
                        rule_name=rule.name,
                        metric=rule.metric,
                        current_value=current_value,
                        threshold=rule.threshold,
                        level=rule.level,
                        duration=int(duration_seconds)
                    )

                    # 检查是否已经存在相同的告警
                    if self._should_trigger_alert(alert):
                        with self._alert_lock:
                            self.active_alerts[rule.name] = alert
                            self.alert_history.append(alert)

                        # 记录日志
                        self._log_alert(alert, rule)

                        # 执行告警动作
                        if rule.action:
                            try:
                                rule.action()
                            except Exception as e:
                                logger.error(f"❌ 告警动作执行失败: {e}")

                        new_alerts.append(alert)
            else:
                # 指标正常，标记告警为已解决
                if rule.name in self.active_alerts:
                    with self._alert_lock:
                        alert = self.active_alerts[rule.name]
                        alert.resolved = True
                        del self.active_alerts[rule.name]

                    logger.info(
                        f"✅ 告警已解除: {rule.name} "
                        f"({rule.metric}: {current_value:.2%})"
                    )

        return new_alerts

    def _check_duration(self, rule: AlertRule, current_value: float) -> float:
        """
        检查指标持续异常的时间

        Args:
            rule: 告警规则
            current_value: 当前指标值

        Returns:
            持续时间（秒）
        """
        snapshots = self.metrics_history.get_recent(rule.duration)

        # 统计异常快照数量
        is_anomaly = lambda s: (
            getattr(s, rule.metric, 0.0) < rule.threshold
            if rule.metric.endswith("_rate")
            else getattr(s, rule.metric, 0.0) > rule.threshold
        )

        anomaly_count = sum(1 for s in snapshots if is_anomaly(s))

        if anomaly_count == 0:
            return 0

        # 估算持续时间（假设快照间隔约1秒）
        oldest_anomaly_time = min(
            s.timestamp for s in snapshots if is_anomaly(s)
        )

        return time.time() - oldest_anomaly_time

    def _should_trigger_alert(self, alert: AlertEvent) -> bool:
        """
        判断是否应该触发告警（去重）

        Args:
            alert: 告警事件

        Returns:
            是否应该触发
        """
        # 检查是否已经存在相同的活跃告警
        if alert.rule_name in self.active_alerts:
            existing_alert = self.active_alerts[alert.rule_name]

            # 如果告警级别相同，且上次触发时间不超过1分钟，则不重复触发
            if (existing_alert.level == alert.level and
                time.time() - existing_alert.timestamp < 60):
                return False

        return True

    def _log_alert(self, alert: AlertEvent, rule: AlertRule):
        """记录告警日志"""
        log_func = (
            logger.critical if alert.level == AlertLevel.CRITICAL
            else logger.warning
        )

        value_str = (
            f"{alert.current_value:.2%}" if alert.metric.endswith("_rate")
            else f"{alert.current_value:.2%}"
        )
        threshold_str = (
            f"{alert.threshold:.2%}" if alert.metric.endswith("_rate")
            else f"{alert.threshold:.2%}"
        )

        log_func(
            f"🚨 缓存告警: {rule.description}\n"
            f"   指标: {alert.metric}\n"
            f"   当前值: {value_str}\n"
            f"   阈值: {threshold_str}\n"
            f"   持续时间: {alert.duration}秒\n"
            f"   级别: {alert.level.value}"
        )

    def _auto_expand_l1(self):
        """自动扩容L1缓存"""
        try:
            current_size = self.cache.l1_size
            new_size = int(current_size * 1.5)  # 扩容50%

            logger.warning(
                f"🔧 自动扩容L1缓存: {current_size} → {new_size}"
            )

            self.cache.l1_size = new_size

            logger.info(f"✅ L1缓存扩容完成")
        except Exception as e:
            logger.error(f"❌ L1缓存扩容失败: {e}")

    def _trigger_warm_up(self):
        """触发缓存预热"""
        logger.warning("🔥 触发缓存预热")
        # TODO: 调用智能预热系统
        # from .intelligent_warmer import cache_warmer
        # cache_warmer.warm_up_cache()

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        获取当前活跃的告警

        Returns:
            活跃告警列表
        """
        with self._alert_lock:
            return [alert.to_dict() for alert in self.active_alerts.values()]

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取告警历史

        Args:
            limit: 返回数量限制

        Returns:
            告警历史列表
        """
        with self._alert_lock:
            return [
                alert.to_dict()
                for alert in self.alert_history[-limit:]
            ]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要

        Returns:
            指标摘要字典
        """
        latest = self.metrics_history.get_latest()
        if not latest:
            return {}

        return {
            "timestamp": latest.timestamp,
            "l1_hit_rate": f"{latest.l1_hit_rate:.2%}",
            "l2_hit_rate": f"{latest.l2_hit_rate:.2%}",
            "overall_hit_rate": f"{latest.overall_hit_rate:.2%}",
            "l1_usage": f"{latest.l1_usage:.1f}%",
            "qps": f"{latest.qps:.2f}",
            "avg_response_time_ms": f"{latest.avg_response_time_ms:.2f}",
            "trends": {
                "l1_hit_rate_5min": self.metrics_history.get_trend("l1_hit_rate", 300),
                "l2_hit_rate_5min": self.metrics_history.get_trend("l2_hit_rate", 300),
                "overall_hit_rate_5min": self.metrics_history.get_trend("overall_hit_rate", 300),
            }
        }

    def reset(self):
        """重置告警管理器"""
        with self._alert_lock:
            self.active_alerts.clear()
            self.alert_history.clear()

        logger.info("🔄 告警管理器已重置")


# 导出Prometheus格式的指标
def export_prometheus_metrics(alert_manager: CacheAlertManager) -> str:
    """
    导出Prometheus格式的指标

    Args:
        alert_manager: 告警管理器实例

    Returns:
        Prometheus格式的指标字符串
    """
    lines = []

    # 缓存命中率
    summary = alert_manager.get_metrics_summary()
    if summary:
        hit_rates = {
            "l1": summary.get("l1_hit_rate", "0%"),
            "l2": summary.get("l2_hit_rate", "0%"),
            "overall": summary.get("overall_hit_rate", "0%")
        }

        for level, rate in hit_rates.items():
            rate_value = float(rate.rstrip('%')) / 100
            lines.append(f'cache_hit_rate{{level="{level}"}} {rate_value}')

    # 缓存容量
    stats = alert_manager.cache.get_stats()
    lines.append(f'cache_l1_usage {stats.get("l1_size", 0)}')
    lines.append(f'cache_l1_capacity {stats.get("l1_capacity", 0)}')

    # 活跃告警数量
    active_alerts = alert_manager.get_active_alerts()
    warning_count = sum(1 for a in active_alerts if a["level"] == "WARNING")
    critical_count = sum(1 for a in active_alerts if a["level"] == "CRITICAL")

    lines.append(f'cache_alerts{{level="warning"}} {warning_count}')
    lines.append(f'cache_alerts{{level="critical"}} {critical_count}')

    return "\n".join(lines)


# Global instance
_global_alert_manager: Optional[CacheAlertManager] = None
_alert_manager_lock = Lock()


def get_cache_alert_manager(hierarchical_cache=None):
    """
    Get or create the global CacheAlertManager instance.

    Args:
        hierarchical_cache: 三级缓存实例（仅首次调用时需要）

    Returns:
        CacheAlertManager instance
    """
    global _global_alert_manager

    with _alert_manager_lock:
        if _global_alert_manager is None:
            if hierarchical_cache is None:
                raise ValueError(
                    "hierarchical_cache is required on first call to get_cache_alert_manager"
                )
            logger.info("Creating global CacheAlertManager instance")
            _global_alert_manager = CacheAlertManager(hierarchical_cache)

        return _global_alert_manager


# 公开别名，用于模块导入
# Export the class for testing purposes (the instance requires hierarchical_cache parameter)
cache_alert_manager = CacheAlertManager


logger.info("✅ 缓存监控和告警系统已加载 (1.0.0)")
