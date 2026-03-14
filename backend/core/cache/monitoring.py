#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控和告警系统
==================
监控缓存性能指标, 并在异常时触发告警

核心功能:
- 实时指标采集 (命中率, 响应时间, QPS)
- 告警规则引擎 (阈值+持续时间验证)
- 告警去重机制 (防止重复告警)
- 性能指标历史追踪
- 自动化响应 (预热, 扩容)

版本: 1.0.0
日期: 2026-02-24
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

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
        duration: 持续时间（秒）, 指标持续异常多久才触发告警
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
            "current_value": (
                f"{self.current_value:.2%}"
                if self.metric.endswith("_rate")
                else f"{self.current_value:.2f}"
            ),
            "threshold": (
                f"{self.threshold:.2%}"
                if self.metric.endswith("_rate")
                else f"{self.threshold:.2f}"
            ),
            "level": self.level.value,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "resolved": self.resolved,
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
    """指标历史记录(使用循环缓冲区)"""

    def __init__(self, max_size: int = 3600):
        """
        初始化指标历史

        Args:
            max_size: 最大保存的快照数量, 默认3600（1分钟1个, 保存1小时）
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
            duration_seconds: 时间范围（秒）, 默认300秒（5分钟）

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
            "trend": values[-1] - values[0] if len(values) > 1 else 0,
        }


class CacheAlertManager:
    """缓存告警管理器

    监控缓存性能指标, 并在异常时触发告警

    告警规则:
    - L1命中率 <60% 持续5分钟 → WARNING
    - L2命中率 <70% 持续10分钟 → WARNING
    - 总体命中率 <50% 持续5分钟 → CRITICAL (自动预热)
    - L1命中率 <40% 持续3分钟 → CRITICAL (扩容L1)
    - L1使用率 >85% → WARNING
    - L1使用率 >95% → CRITICAL (自动扩容)
    """

    def __init__(self, hierarchical_cache, warmup_callback=None):
        """
        初始化告警管理器

        Args:
            hierarchical_cache: 三级缓存实例
            warmup_callback: 预热回调函数 (避免循环依赖)
        """
        self.cache = hierarchical_cache
        self.metrics_history = MetricsHistory(max_size=3600)
        self._warmup_callback = warmup_callback

        # 预热统计
        self._warmup_stats = {
            "triggered_count": 0,
            "last_triggered_time": 0,
            "last_trigger_result": None,
        }

        # 告警规则定义
        self.alert_rules: List[AlertRule] = [
            # L1命中率告警
            AlertRule(
                name="l1_hit_rate_low",
                metric="l1_hit_rate",
                threshold=0.6,
                duration=300,  # 5分钟
                level=AlertLevel.WARNING,
                description="L1缓存命中率低于60%持续5分钟",
            ),
            AlertRule(
                name="l1_hit_rate_critical",
                metric="l1_hit_rate",
                threshold=0.4,
                duration=180,  # 3分钟
                level=AlertLevel.CRITICAL,
                action=self._auto_expand_l1,
                description="L1缓存命中率低于40%持续3分钟, 触发自动扩容",
            ),
            # L2命中率告警
            AlertRule(
                name="l2_hit_rate_low",
                metric="l2_hit_rate",
                threshold=0.7,
                duration=600,  # 10分钟
                level=AlertLevel.WARNING,
                description="L2缓存命中率低于70%持续10分钟",
            ),
            # 总体命中率告警
            AlertRule(
                name="overall_hit_rate_critical",
                metric="overall_hit_rate",
                threshold=0.5,
                duration=300,  # 5分钟
                level=AlertLevel.CRITICAL,
                action=self._trigger_warm_up,
                description="总体缓存命中率低于50%持续5分钟, 触发自动预热",
            ),
            # L1容量告警
            AlertRule(
                name="l1_capacity_warning",
                metric="l1_usage",
                threshold=0.85,
                duration=60,  # 1分钟
                level=AlertLevel.WARNING,
                description="L1缓存使用率超过85%",
            ),
            AlertRule(
                name="l1_capacity_critical",
                metric="l1_usage",
                threshold=0.95,
                duration=30,  # 30秒
                level=AlertLevel.CRITICAL,
                action=self._auto_expand_l1,
                description="L1缓存使用率超过95%, 触发自动扩容",
            ),
        ]

        # 告警状态追踪
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.alert_history: List[AlertEvent] = []
        self._alert_lock = Lock()

        # 性能统计(用于计算QPS和响应时间)
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
        # 简化计算: L2命中 / (L1未命中次数)
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
                self._response_time_total / self._request_count if self._request_count > 0 else 0
            )
            # 重置计数器
            self._request_count = 0
            self._response_time_total = 0.0

        self._last_check_time = current_time

        # 获取Redis内存使用情况
        l2_memory_usage = self._get_redis_memory_usage()

        # 创建快照
        snapshot = MetricSnapshot(
            timestamp=current_time,
            l1_hit_rate=l1_hit_rate,
            l2_hit_rate=l2_hit_rate,
            overall_hit_rate=overall_hit_rate,
            l1_usage=l1_usage,
            l2_memory_usage=l2_memory_usage,
            qps=qps,
            avg_response_time_ms=avg_response_time,
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
            is_triggered = (
                current_value < rule.threshold
                if rule.metric.endswith("_rate")
                else current_value > rule.threshold
            )

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
                        duration=int(duration_seconds),
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
                # 指标正常, 标记告警为已解决
                if rule.name in self.active_alerts:
                    with self._alert_lock:
                        alert = self.active_alerts[rule.name]
                        alert.resolved = True
                        del self.active_alerts[rule.name]

                    logger.info(
                        f"✅ 告警已解除: {rule.name} " f"({rule.metric}: {current_value:.2%})"
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

        # 估算持续时间(假设快照间隔约1秒)
        oldest_anomaly_time = min(s.timestamp for s in snapshots if is_anomaly(s))

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

            # 如果告警级别相同, 且上次触发时间不超过1分钟, 则不重复触发
            if existing_alert.level == alert.level and time.time() - existing_alert.timestamp < 60:
                return False

        return True

    def _log_alert(self, alert: AlertEvent, rule: AlertRule):
        """记录告警日志"""
        log_func = logger.critical if alert.level == AlertLevel.CRITICAL else logger.warning

        value_str = (
            f"{alert.current_value:.2%}"
            if alert.metric.endswith("_rate")
            else f"{alert.current_value:.2%}"
        )
        threshold_str = (
            f"{alert.threshold:.2%}" if alert.metric.endswith("_rate") else f"{alert.threshold:.2%}"
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

            logger.warning(f"🔧 自动扩容L1缓存: {current_size} → {new_size}")

            self.cache.l1_size = new_size

            logger.info(f"✅ L1缓存扩容完成")
        except Exception as e:
            logger.error(f"❌ L1缓存扩容失败: {e}")

    def _trigger_warm_up(self):
        """
        触发缓存预热

        使用回调函数机制避免循环依赖:
        - monitoring.py (core层) 不直接依赖 services/cache
        - 由上层应用 (web_app.py) 注入预热回调
        - 支持同步和异步预热
        """
        try:
            logger.warning("🔥 检测到缓存命中率过低, 触发自动预热")

            # 记录触发时间
            self._warmup_stats["triggered_count"] += 1
            self._warmup_stats["last_triggered_time"] = time.time()

            # 调用预热回调
            if self._warmup_callback is not None:
                logger.info("✅ 执行预热回调函数")

                # 支持同步和异步回调
                import asyncio

                result = self._warmup_callback()

                # 检查是否是协程函数
                if asyncio.iscoroutine(result):
                    # 在新的事件循环中运行异步函数
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(result)
                        loop.close()
                    except Exception as e:
                        logger.error(f"❌ 异步预热执行失败: {e}")
                        result = {"error": str(e)}

                # 记录结果
                self._warmup_stats["last_trigger_result"] = result

                # 记录预热日志
                if isinstance(result, dict):
                    warmed = result.get("warmed", result.get("games_warmed", 0))
                    total = warmed + result.get("failed", 0) + result.get("skipped", 0)
                    logger.info(f"✅ 缓存预热完成: " f"预热 {warmed}/{total} 个键")

                    # 如果有详细的统计信息
                    if "games_warmed" in result:
                        logger.info(
                            f"  - 游戏: {result.get('games_warmed', 0)}, "
                            f"事件: {result.get('events_warmed', 0)}, "
                            f"参数: {result.get('params_warmed', 0)}"
                        )
                else:
                    logger.info(f"✅ 缓存预热完成: {result}")

            else:
                logger.warning(
                    "⚠️ 未配置预热回调函数, 跳过自动预热. "
                    "请在初始化时传入 warmup_callback 参数. "
                )
                logger.info(
                    "💡 提示: 在 web_app.py 中配置回调示例:\n"
                    "   from backend.services.cache.cache_warmup import CacheWarmer\n"
                    "   warmer = CacheWarmer()\n"
                    "   alert_manager = get_cache_alert_manager(\n"
                    "       hierarchical_cache,\n"
                    "       warmup_callback=warmer.warmup_all\n"
                    "   )"
                )

        except Exception as e:
            logger.error(f"❌ 缓存预热触发失败: {e}", exc_info=True)
            self._warmup_stats["last_trigger_result"] = {"error": str(e)}

    def _get_redis_memory_usage(self) -> float:
        """
        获取Redis内存使用情况

        使用Redis INFO命令获取memory信息, 返回内存使用率（百分比）

        Returns:
            内存使用率（0.0-1.0）, 如果获取失败则返回0.0

        Example:
            >>> usage = self._get_redis_memory_usage()
            >>> print(f"Redis内存使用率: {usage:.2%}")
            Redis内存使用率: 45.23%
        """
        try:
            # 获取Redis客户端
            redis_client = self.cache._get_redis_client()

            if redis_client is None:
                logger.debug("⚠️ Redis客户端不可用, 无法获取内存信息")
                return 0.0

            # 执行INFO memory命令
            memory_info = redis_client.info("memory")

            # 提取内存信息
            used_memory = memory_info.get("used_memory", 0)  # bytes
            max_memory = memory_info.get("maxmemory", 0)  # bytes

            # 如果没有设置maxmemory, 则使用系统内存作为参考
            if max_memory == 0:
                # 获取系统总内存(可选, 这里简化为0表示无限制)
                # 返回已使用内存(MB)而非百分比
                used_memory_mb = used_memory / (1024 * 1024)
                logger.debug(f"📊 Redis内存使用: {used_memory_mb:.2f}MB (无maxmemory限制)")
                # 返回0.0表示未设置限制(无法计算使用率)
                return 0.0

            # 计算内存使用率
            memory_usage_rate = used_memory / max_memory if max_memory > 0 else 0.0

            logger.debug(
                f"📊 Redis内存使用: {used_memory / (1024 * 1024):.2f}MB / "
                f"{max_memory / (1024 * 1024):.2f}MB ({memory_usage_rate:.2%})"
            )

            return memory_usage_rate

        except Exception as e:
            logger.warning(f"⚠️ 获取Redis内存信息失败: {e}")
            return 0.0

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
            return [alert.to_dict() for alert in self.alert_history[-limit:]]

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
            "l2_memory_usage": f"{latest.l2_memory_usage:.2%}",
            "qps": f"{latest.qps:.2f}",
            "avg_response_time_ms": f"{latest.avg_response_time_ms:.2f}",
            "trends": {
                "l1_hit_rate_5min": self.metrics_history.get_trend("l1_hit_rate", 300),
                "l2_hit_rate_5min": self.metrics_history.get_trend("l2_hit_rate", 300),
                "overall_hit_rate_5min": self.metrics_history.get_trend("overall_hit_rate", 300),
            },
            "warmup_stats": self._warmup_stats,
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
            "overall": summary.get("overall_hit_rate", "0%"),
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


def get_cache_alert_manager(hierarchical_cache=None, warmup_callback=None):
    """
    Get or create the global CacheAlertManager instance.

    Args:
        hierarchical_cache: 三级缓存实例（仅首次调用时需要）
        warmup_callback: 预热回调函数, 可选（用于自动预热触发）

    Returns:
        CacheAlertManager instance

    Example:
        >>> from backend.services.cache.cache_warmup import CacheWarmer
        >>> warmer = CacheWarmer()
        >>> alert_manager = get_cache_alert_manager(
        ...     hierarchical_cache,
        ...     warmup_callback=warmer.warmup_all
        ... )
    """
    global _global_alert_manager

    with _alert_manager_lock:
        if _global_alert_manager is None:
            if hierarchical_cache is None:
                raise ValueError(
                    "hierarchical_cache is required on first call to get_cache_alert_manager"
                )
            logger.info("Creating global CacheAlertManager instance")
            _global_alert_manager = CacheAlertManager(
                hierarchical_cache, warmup_callback=warmup_callback
            )
        elif warmup_callback is not None:
            # 更新已有实例的回调
            logger.info("Updating warmup callback for existing CacheAlertManager")
            _global_alert_manager._warmup_callback = warmup_callback

        return _global_alert_manager


# 公开别名, 用于模块导入
# Export the class for testing purposes (the instance requires hierarchical_cache parameter)
cache_alert_manager = CacheAlertManager


logger.info("✅ 缓存监控和告警系统已加载 (1.0.0)")
