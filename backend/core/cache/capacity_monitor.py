#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存容量监控系统
================

监控L1和L2缓存容量使用情况, 提供告警和自动扩容功能. 

核心功能:
- L1容量监控（85%警告, 95%严重）
- L2 Redis容量监控（80%警告, 90%严重）
- L1自动扩容（95%时扩容50%）
- 容量趋势预测（线性回归）
- Prometheus指标导出

版本: 1.0.0
日期: 2026-02-24
"""

import logging
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CapacityTrendPredictor:
    """容量趋势预测器(线性回归)"""

    def __init__(self, window_size: int = 1440):
        """
        初始化预测器

        Args:
            window_size: 历史数据窗口大小（默认1440 = 24小时 × 60分钟）
        """
        self.window_size = window_size
        self.l1_history: deque = deque(maxlen=window_size)
        self.l2_history: deque = deque(maxlen=window_size)

    def add_sample(self, l1_usage: float, l2_usage: float, timestamp: Optional[float] = None):
        """
        添加容量样本

        Args:
            l1_usage: L1使用率（0.0-1.0）
            l2_usage: L2使用率（0.0-1.0）
            timestamp: 时间戳（默认当前时间）
        """
        if timestamp is None:
            timestamp = time.time()

        self.l1_history.append((timestamp, l1_usage))
        self.l2_history.append((timestamp, l2_usage))

    def predict_exhaustion(self, history: deque, threshold: float = 0.95) -> Optional[float]:
        """
        预测何时达到容量上限

        使用线性回归预测容量使用趋势

        Args:
            history: 历史数据 [(timestamp, usage), ...]
            threshold: 容量上限阈值（默认95%）

        Returns:
            预测的耗尽时间戳, 如果无法预测则返回None
        """
        if len(history) < 10:
            # 数据不足, 无法预测
            return None

        try:
            # 提取时间和使用率
            # 使用相对时间(秒)而不是绝对时间戳, 避免数值不稳定
            base_timestamp = history[0][0]
            timestamps = [(t - base_timestamp) / 3600 for t, _ in history]  # 转换为小时
            usages = [u for _, u in history]

            # 线性回归: y = ax + b
            # x = 相对时间(小时), y = usage
            n = len(timestamps)

            sum_x = sum(timestamps)
            sum_y = sum(usages)
            sum_xy = sum(t * u for t, u in zip(timestamps, usages))
            sum_x2 = sum(t**2 for t in timestamps)

            # 计算斜率和截距
            denominator = n * sum_x2 - sum_x**2
            if denominator == 0:
                return None

            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n

            # 如果斜率<=0, 表示容量不会增长
            if slope <= 1e-10:  # 使用小的正数阈值而不是0
                return None

            # 计算何时达到threshold
            # threshold = slope * x + intercept
            # x = (threshold - intercept) / slope
            hours_until_exhaustion = (threshold - intercept) / slope

            if hours_until_exhaustion > 0:
                # 转换回绝对时间戳(从base_timestamp开始计算)
                exhaustion_time: float = base_timestamp + hours_until_exhaustion * 3600
                return exhaustion_time

        except Exception as e:
            logger.warning(f"容量预测失败: {e}")

        return None

    def predict_l1_exhaustion(self, threshold: float = 0.95) -> Optional[datetime]:
        """
        预测L1缓存何时耗尽

        Args:
            threshold: 容量上限阈值（默认95%）

        Returns:
            预测的耗尽时间, 如果无法预测则返回None
        """
        exhaustion_ts = self.predict_exhaustion(self.l1_history, threshold)
        if exhaustion_ts:
            return datetime.fromtimestamp(exhaustion_ts)
        return None

    def predict_l2_exhaustion(self, threshold: float = 0.90) -> Optional[datetime]:
        """
        预测L2缓存何时耗尽

        Args:
            threshold: 容量上限阈值（默认90%）

        Returns:
            预测的耗尽时间, 如果无法预测则返回None
        """
        exhaustion_ts = self.predict_exhaustion(self.l2_history, threshold)
        if exhaustion_ts:
            return datetime.fromtimestamp(exhaustion_ts)
        return None

    def get_trend_stats(self) -> Dict[str, Any]:
        """
        获取趋势统计信息

        Returns:
            趋势统计字典
        """
        stats: Dict[str, Any] = {
            "l1_samples": len(self.l1_history),
            "l2_samples": len(self.l2_history),
            "l1_exhaustion_prediction": None,
            "l2_exhaustion_prediction": None,
            "days_until_exhaustion_l1": None,
            "days_until_exhaustion_l2": None,
        }

        # L1预测
        l1_exhaustion = self.predict_l1_exhaustion(0.95)
        if l1_exhaustion:
            stats["l1_exhaustion_prediction"] = l1_exhaustion.isoformat()
            l1_days_remaining: float = (l1_exhaustion - datetime.now()).total_seconds() / 86400
            stats["days_until_exhaustion_l1"] = round(l1_days_remaining, 2)

        # L2预测
        l2_exhaustion = self.predict_l2_exhaustion(0.90)
        if l2_exhaustion:
            stats["l2_exhaustion_prediction"] = l2_exhaustion.isoformat()
            l2_days_remaining: float = (l2_exhaustion - datetime.now()).total_seconds() / 86400
            stats["days_until_exhaustion_l2"] = round(l2_days_remaining, 2)

        return stats


class CacheCapacityMonitor:
    """缓存容量监控器"""

    def __init__(
        self,
        hierarchical_cache,
        l1_warning_threshold: float = 0.85,
        l1_critical_threshold: float = 0.95,
        l2_warning_threshold: float = 0.80,
        l2_critical_threshold: float = 0.90,
        monitoring_interval: int = 60,
        alert_days_advance: int = 7,
    ):
        """
        初始化容量监控器

        Args:
            hierarchical_cache: 分层缓存实例
            l1_warning_threshold: L1警告阈值（默认85%）
            l1_critical_threshold: L1严重阈值（默认95%）
            l2_warning_threshold: L2警告阈值（默认80%）
            l2_critical_threshold: L2严重阈值（默认90%）
            monitoring_interval: 监控间隔（秒, 默认60）
            alert_days_advance: 提前告警天数（默认7天）
        """
        self.cache = hierarchical_cache
        self.l1_warning_threshold = l1_warning_threshold
        self.l1_critical_threshold = l1_critical_threshold
        self.l2_warning_threshold = l2_warning_threshold
        self.l2_critical_threshold = l2_critical_threshold
        self.monitoring_interval = monitoring_interval
        self.alert_days_advance = alert_days_advance

        # 趋势预测器
        self.predictor = CapacityTrendPredictor()

        # Prometheus指标
        self.prometheus_metrics: Dict[str, Dict[str, Any]] = {
            "cache_capacity_bytes": {},  # {level: capacity}
            "cache_usage_bytes": {},  # {level: usage}
            "cache_usage_ratio": {},  # {level: ratio}
            "cache_capacity_prediction_days": {},  # {level: days}
        }

        # 监控线程
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # 告警状态(防止重复告警)
        self._alert_state = {
            "l1_warning_sent": False,
            "l1_critical_sent": False,
            "l2_warning_sent": False,
            "l2_critical_sent": False,
            "prediction_alert_sent": False,
        }

        logger.info(
            f"✅ 容量监控器初始化: "
            f"L1阈值={l1_warning_threshold:.0%}/{l1_critical_threshold:.0%}, "
            f"L2阈值={l2_warning_threshold:.0%}/{l2_critical_threshold:.0%}, "
            f"监控间隔={monitoring_interval}s"
        )

    def get_l1_usage(self) -> float:
        """
        获取L1缓存使用率

        Returns:
            使用率（0.0-1.0）
        """
        with self.cache._lock:
            if self.cache.l1_size == 0:
                return 0.0
            l1_size: int = self.cache.l1_size
            return float(len(self.cache.l1_cache)) / float(l1_size)

    def get_l2_usage(self) -> float:
        """
        获取L2 Redis缓存使用率

        Returns:
            使用率（0.0-1.0）
        """
        try:
            redis_client = self.cache._get_redis_client()
            if redis_client is None:
                return 0.0

            # 获取Redis内存信息
            info = redis_client.info("memory")
            maxmemory = info.get("maxmemory", 0)
            used_memory = info.get("used_memory", 0)

            if maxmemory == 0:
                # Redis未设置maxmemory, 检查used_memory_rss
                used_memory_rss = info.get("used_memory_rss", 0)
                # 假设系统内存限制为2GB
                maxmemory = 2 * 1024 * 1024 * 1024  # 2GB

            used_memory_float: float = float(used_memory)
            maxmemory_float: float = float(maxmemory)
            return used_memory_float / maxmemory_float if maxmemory_float > 0 else 0.0

        except Exception as e:
            logger.warning(f"获取L2容量失败: {e}")
            return 0.0

    def get_redis_memory_stats(self) -> Dict:
        """
        获取Redis内存统计信息

        Returns:
            内存统计字典
        """
        try:
            redis_client = self.cache._get_redis_client()
            if redis_client is None:
                return {}

            info = redis_client.info("memory")

            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_rss": info.get("used_memory_rss", 0),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "maxmemory": info.get("maxmemory", 0),
                "maxmemory_policy": info.get("maxmemory_policy", "noeviction"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0.0),
                "used_memory_percentage": self._calculate_memory_percentage(info),
            }

        except Exception as e:
            logger.warning(f"获取Redis内存统计失败: {e}")
            return {}

    def _calculate_memory_percentage(self, info: Dict) -> float:
        """
        计算内存使用百分比

        Args:
            info: Redis INFO memory输出

        Returns:
            内存使用百分比
        """
        maxmemory: int = int(info.get("maxmemory", 0))
        used_memory: int = int(info.get("used_memory", 0))

        if maxmemory == 0:
            # Redis未设置maxmemory
            return 0.0

        return (float(used_memory) / float(maxmemory) * 100) if maxmemory > 0 else 0.0

    def monitor_l1_capacity(self) -> Optional[str]:
        """
        监控L1缓存容量

        Returns:
            告警级别（"WARNING", "CRITICAL" 或 None）
        """
        usage = self.get_l1_usage()

        # 更新Prometheus指标
        self.prometheus_metrics["cache_capacity_bytes"]["l1"] = self.cache.l1_size
        self.prometheus_metrics["cache_usage_bytes"]["l1"] = len(self.cache.l1_cache)
        self.prometheus_metrics["cache_usage_ratio"]["l1"] = usage

        # 检查严重阈值
        if usage >= self.l1_critical_threshold:
            if not self._alert_state["l1_critical_sent"]:
                logger.critical(
                    f"🚨 L1容量严重告警: {usage:.1%} >= {self.l1_critical_threshold:.1%}"
                )
                self._alert_state["l1_critical_sent"] = True

                # 自动扩容L1
                self._auto_expand_l1()

            return "CRITICAL"

        # 检查警告阈值
        elif usage >= self.l1_warning_threshold:
            if not self._alert_state["l1_warning_sent"]:
                logger.warning(f"⚠️ L1容量警告: {usage:.1%} >= {self.l1_warning_threshold:.1%}")
                self._alert_state["l1_warning_sent"] = True
            return "WARNING"

        # 重置告警状态
        else:
            self._alert_state["l1_warning_sent"] = False
            self._alert_state["l1_critical_sent"] = False
            return None

    def monitor_l2_capacity(self) -> Optional[str]:
        """
        监控L2 Redis缓存容量

        Returns:
            告警级别（"WARNING", "CRITICAL" 或 None）
        """
        usage = self.get_l2_usage()

        # 更新Prometheus指标
        redis_stats = self.get_redis_memory_stats()
        if redis_stats:
            self.prometheus_metrics["cache_capacity_bytes"]["l2"] = redis_stats.get("maxmemory", 0)
            self.prometheus_metrics["cache_usage_bytes"]["l2"] = redis_stats.get("used_memory", 0)
            self.prometheus_metrics["cache_usage_ratio"]["l2"] = usage

        # 检查严重阈值
        if usage >= self.l2_critical_threshold:
            if not self._alert_state["l2_critical_sent"]:
                logger.critical(
                    f"🚨 L2容量严重告警: {usage:.1%} >= {self.l2_critical_threshold:.1%}"
                )
                self._alert_state["l2_critical_sent"] = True
            return "CRITICAL"

        # 检查警告阈值
        elif usage >= self.l2_warning_threshold:
            if not self._alert_state["l2_warning_sent"]:
                logger.warning(f"⚠️ L2容量警告: {usage:.1%} >= {self.l2_warning_threshold:.1%}")
                self._alert_state["l2_warning_sent"] = True
            return "WARNING"

        # 重置告警状态
        else:
            self._alert_state["l2_warning_sent"] = False
            self._alert_state["l2_critical_sent"] = False
            return None

    def _auto_expand_l1(self):
        """
        自动扩容L1缓存

        扩容策略: 增加50%容量
        """
        with self.cache._lock:
            old_size = self.cache.l1_size
            new_size = int(old_size * 1.5)

            self.cache.l1_size = new_size

            logger.info(
                f"📈 L1缓存自动扩容: {old_size} → {new_size} (+{new_size - old_size}, +50%)"
            )

    def check_capacity_predictions(self) -> List[Dict]:
        """
        检查容量预测告警

        Returns:
            告警列表
        """
        alerts = []

        # 检查L1预测
        l1_exhaustion = self.predictor.predict_l1_exhaustion(0.95)
        if l1_exhaustion:
            days_until = (l1_exhaustion - datetime.now()).total_seconds() / 86400

            # 更新Prometheus指标
            self.prometheus_metrics["cache_capacity_prediction_days"]["l1"] = days_until

            if days_until <= self.alert_days_advance:
                alert = {
                    "level": "l1",
                    "predicted_exhaustion": l1_exhaustion.isoformat(),
                    "days_until": round(days_until, 2),
                    "message": f"L1缓存预计在{days_until:.1f}天后耗尽",
                }
                alerts.append(alert)

                if not self._alert_state["prediction_alert_sent"]:
                    logger.warning(f"🔮 容量预测告警: {alert['message']}")
                    self._alert_state["prediction_alert_sent"] = True

        # 检查L2预测
        l2_exhaustion = self.predictor.predict_l2_exhaustion(0.90)
        if l2_exhaustion:
            days_until = (l2_exhaustion - datetime.now()).total_seconds() / 86400

            # 更新Prometheus指标
            self.prometheus_metrics["cache_capacity_prediction_days"]["l2"] = days_until

            if days_until <= self.alert_days_advance:
                alert = {
                    "level": "l2",
                    "predicted_exhaustion": l2_exhaustion.isoformat(),
                    "days_until": round(days_until, 2),
                    "message": f"L2缓存预计在{days_until:.1f}天后耗尽",
                }
                alerts.append(alert)

        return alerts

    def _monitoring_loop(self):
        """监控线程主循环"""
        logger.info("🔄 容量监控线程已启动")

        while not self._stop_event.is_set():
            try:
                # 监控L1容量
                l1_alert = self.monitor_l1_capacity()

                # 监控L2容量
                l2_alert = self.monitor_l2_capacity()

                # 添加样本到预测器
                l1_usage = self.get_l1_usage()
                l2_usage = self.get_l2_usage()
                self.predictor.add_sample(l1_usage, l2_usage)

                # 检查容量预测
                prediction_alerts = self.check_capacity_predictions()

                # 记录监控状态
                if l1_alert or l2_alert or prediction_alerts:
                    logger.debug(
                        f"📊 监控状态: L1={l1_usage:.1%}({l1_alert}), "
                        f"L2={l2_usage:.1%}({l2_alert}), "
                        f"预测告警={len(prediction_alerts)}"
                    )

            except Exception as e:
                logger.error(f"❌ 监控循环错误: {e}")

            # 等待下一次监控
            self._stop_event.wait(self.monitoring_interval)

        logger.info("⏹️ 容量监控线程已停止")

    def start(self):
        """启动监控线程"""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._stop_event.clear()
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="CacheCapacityMonitor",
            )
            self._monitoring_thread.start()
            logger.info("✅ 容量监控已启动")

    def stop(self):
        """停止监控线程"""
        self._stop_event.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
            logger.info("⏹️ 容量监控已停止")

    def get_capacity_report(self) -> Dict:
        """
        获取容量报告

        Returns:
            容量报告字典
        """
        l1_usage = self.get_l1_usage()
        l2_usage = self.get_l2_usage()

        report = {
            "timestamp": datetime.now().isoformat(),
            "l1": {
                "usage_ratio": f"{l1_usage:.2%}",
                "used": len(self.cache.l1_cache),
                "capacity": self.cache.l1_size,
                "alert_level": self.monitor_l1_capacity(),
            },
            "l2": {
                "usage_ratio": f"{l2_usage:.2%}",
                "redis_stats": self.get_redis_memory_stats(),
                "alert_level": self.monitor_l2_capacity(),
            },
            "predictions": self.predictor.get_trend_stats(),
            "prometheus_metrics": self.prometheus_metrics,
        }

        return report

    def get_prometheus_metrics(self) -> str:
        """
        导出Prometheus指标

        Returns:
            Prometheus格式的指标字符串
        """
        lines = []

        # L1容量指标
        l1_usage = self.get_l1_usage()
        lines.append(f'cache_capacity_bytes{{level="l1"}} {self.cache.l1_size} {int(time.time())}')
        lines.append(
            f'cache_usage_bytes{{level="l1"}} {len(self.cache.l1_cache)} {int(time.time())}'
        )
        lines.append(f'cache_usage_ratio{{level="l1"}} {l1_usage:.4f} {int(time.time())}')

        # L2容量指标
        redis_stats = self.get_redis_memory_stats()
        if redis_stats:
            maxmemory = redis_stats.get("maxmemory", 0)
            used_memory = redis_stats.get("used_memory", 0)
            l2_usage = self.get_l2_usage()

            lines.append(f'cache_capacity_bytes{{level="l2"}} {maxmemory} {int(time.time())}')
            lines.append(f'cache_usage_bytes{{level="l2"}} {used_memory} {int(time.time())}')
            lines.append(f'cache_usage_ratio{{level="l2"}} {l2_usage:.4f} {int(time.time())}')

        # 预测指标
        trend_stats = self.predictor.get_trend_stats()
        if trend_stats.get("days_until_exhaustion_l1"):
            lines.append(
                f'cache_capacity_prediction_days{{level="l1"}} {trend_stats["days_until_exhaustion_l1"]} {int(time.time())}'
            )
        if trend_stats.get("days_until_exhaustion_l2"):
            lines.append(
                f'cache_capacity_prediction_days{{level="l2"}} {trend_stats["days_until_exhaustion_l2"]} {int(time.time())}'
            )

        return "\n".join(lines)


# 全局容量监控器实例(延迟初始化)
_capacity_monitor: Optional[CacheCapacityMonitor] = None


def get_capacity_monitor() -> Optional[CacheCapacityMonitor]:
    """
    获取全局容量监控器实例

    Returns:
        CacheCapacityMonitor实例或None
    """
    return _capacity_monitor


def init_capacity_monitor(
    hierarchical_cache,
    l1_warning_threshold: float = 0.85,
    l1_critical_threshold: float = 0.95,
    l2_warning_threshold: float = 0.80,
    l2_critical_threshold: float = 0.90,
    monitoring_interval: int = 60,
    alert_days_advance: int = 7,
    auto_start: bool = True,
) -> CacheCapacityMonitor:
    """
    初始化全局容量监控器

    Args:
        hierarchical_cache: 分层缓存实例
        l1_warning_threshold: L1警告阈值（默认85%）
        l1_critical_threshold: L1严重阈值（默认95%）
        l2_warning_threshold: L2警告阈值（默认80%）
        l2_critical_threshold: L2严重阈值（默认90%）
        monitoring_interval: 监控间隔（秒, 默认60）
        alert_days_advance: 提前告警天数（默认7天）
        auto_start: 是否自动启动监控（默认True）

    Returns:
        CacheCapacityMonitor实例
    """
    global _capacity_monitor

    if _capacity_monitor is None:
        _capacity_monitor = CacheCapacityMonitor(
            hierarchical_cache=hierarchical_cache,
            l1_warning_threshold=l1_warning_threshold,
            l1_critical_threshold=l1_critical_threshold,
            l2_warning_threshold=l2_warning_threshold,
            l2_critical_threshold=l2_critical_threshold,
            monitoring_interval=monitoring_interval,
            alert_days_advance=alert_days_advance,
        )

        if auto_start:
            _capacity_monitor.start()

        logger.info("✅ 全局容量监控器已初始化")

    return _capacity_monitor


# 公开别名, 用于模块导入
cache_capacity_monitor = _capacity_monitor


logger.info("✅ 缓存容量监控系统已加载 (1.0.0)")
