#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控增强模块
================

提供缓存命中率监控, 性能指标收集和实时监控功能

版本: 1.0.0
日期: 2026-03-10
"""

import logging
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CacheMetrics:
    """
    缓存性能指标收集器
    """

    def __init__(self, max_history: int = 1000):
        """
        初始化指标收集器

        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self._lock = threading.RLock()

        # 实时指标
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'avg_response_time_ms': 0.0,
            'last_request_time': None,
        }

        # 历史指标(用于趋势分析)
        self.history = deque(maxlen=max_history)

        # 响应时间记录
        self.response_times = deque(maxlen=100)

    def record_hit(self, response_time_ms: float = 0.0):
        """
        记录缓存命中

        Args:
            response_time_ms: 响应时间（毫秒）
        """
        with self._lock:
            self.metrics['hits'] += 1
            self.metrics['total_requests'] += 1
            self.metrics['last_request_time'] = datetime.now().isoformat()

            if response_time_ms > 0:
                self.response_times.append(response_time_ms)
                self._update_avg_response_time()

    def record_miss(self, response_time_ms: float = 0.0):
        """
        记录缓存未命中

        Args:
            response_time_ms: 响应时间（毫秒）
        """
        with self._lock:
            self.metrics['misses'] += 1
            self.metrics['total_requests'] += 1
            self.metrics['last_request_time'] = datetime.now().isoformat()

            if response_time_ms > 0:
                self.response_times.append(response_time_ms)
                self._update_avg_response_time()

    def _update_avg_response_time(self):
        """更新平均响应时间"""
        if self.response_times:
            self.metrics['avg_response_time_ms'] = sum(self.response_times) / len(
                self.response_times
            )

    def get_hit_rate(self) -> float:
        """
        获取命中率

        Returns:
            命中率（百分比）
        """
        with self._lock:
            total = self.metrics['total_requests']
            if total == 0:
                return 0.0
            return (self.metrics['hits'] / total) * 100

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取当前指标

        Returns:
            指标字典
        """
        with self._lock:
            return {
                **self.metrics,
                'hit_rate': f"{self.get_hit_rate():.2f}%",
            }

    def snapshot(self):
        """创建指标快照(用于历史记录)"""
        with self._lock:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'hits': self.metrics['hits'],
                'misses': self.metrics['misses'],
                'total_requests': self.metrics['total_requests'],
                'hit_rate': self.get_hit_rate(),
                'avg_response_time_ms': self.metrics['avg_response_time_ms'],
            }
            self.history.append(snapshot)

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取历史指标

        Args:
            limit: 返回的记录数限制

        Returns:
            历史指标列表
        """
        with self._lock:
            return list(self.history)[-limit:]

    def reset(self):
        """重置指标"""
        with self._lock:
            self.metrics = {
                'hits': 0,
                'misses': 0,
                'total_requests': 0,
                'avg_response_time_ms': 0.0,
                'last_request_time': None,
            }
            self.response_times.clear()


class CacheMonitor:
    """
    缓存监控器

    提供实时监控, 性能指标收集和告警功能
    """

    def __init__(self, cache_instance, alert_thresholds: Optional[Dict] = None):
        """
        初始化监控器

        Args:
            cache_instance: 缓存实例
            alert_thresholds: 告警阈值配置
                {
                    'low_hit_rate': 50.0,  # 命中率低于50%告警
                    'high_miss_rate': 50.0,  # 未命中率高于50%告警
                    'slow_response': 100.0,  # 响应时间高于100ms告警
                }
        """
        self.cache = cache_instance
        self.metrics = CacheMetrics()
        self.alert_thresholds = alert_thresholds or {
            'low_hit_rate': 50.0,
            'high_miss_rate': 50.0,
            'slow_response': 100.0,
        }
        self._lock = threading.RLock()

        # 告警记录
        self.alerts = deque(maxlen=100)

    def record_cache_operation(self, cache_key: str, hit: bool, response_time_ms: float = 0.0):
        """
        记录缓存操作

        Args:
            cache_key: 缓存键
            hit: 是否命中
            response_time_ms: 响应时间（毫秒）
        """
        if hit:
            self.metrics.record_hit(response_time_ms)
        else:
            self.metrics.record_miss(response_time_ms)

        # 检查告警
        self._check_alerts()

    def _check_alerts(self):
        """检查是否需要告警"""
        hit_rate = self.metrics.get_hit_rate()
        avg_response = self.metrics.metrics['avg_response_time_ms']

        # 检查命中率
        if hit_rate < self.alert_thresholds['low_hit_rate']:
            alert = {
                'type': 'low_hit_rate',
                'severity': 'warning',
                'message': f'缓存命中率过低: {hit_rate:.2f}%',
                'threshold': self.alert_thresholds['low_hit_rate'],
                'current_value': hit_rate,
                'timestamp': datetime.now().isoformat(),
            }
            self.alerts.append(alert)

        # 检查响应时间
        if avg_response > self.alert_thresholds['slow_response']:
            alert = {
                'type': 'slow_response',
                'severity': 'warning',
                'message': f'平均响应时间过慢: {avg_response:.2f}ms',
                'threshold': self.alert_thresholds['slow_response'],
                'current_value': avg_response,
                'timestamp': datetime.now().isoformat(),
            }
            self.alerts.append(alert)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取监控统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            # 获取缓存统计
            cache_stats = self.cache.get_stats()

            # 获取指标统计
            metrics_stats = self.metrics.get_metrics()

            # 获取最近告警
            recent_alerts = list(self.alerts)[-10:]

            return {
                'cache_stats': cache_stats,
                'performance_metrics': metrics_stats,
                'recent_alerts': recent_alerts,
                'alert_count': len(self.alerts),
            }

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能摘要

        Args:
            hours: 查询的小时数

        Returns:
            性能摘要字典
        """
        history = self.metrics.get_history(limit=hours * 60)  # 假设每分钟一个快照

        if not history:
            return {'period_hours': hours, 'message': '暂无历史数据'}

        # 计算统计数据
        hit_rates = [h['hit_rate'] for h in history]
        response_times = [
            h['avg_response_time_ms'] for h in history if h['avg_response_time_ms'] > 0
        ]

        return {
            'period_hours': hours,
            'avg_hit_rate': sum(hit_rates) / len(hit_rates) if hit_rates else 0,
            'min_hit_rate': min(hit_rates) if hit_rates else 0,
            'max_hit_rate': max(hit_rates) if hit_rates else 0,
            'avg_response_time_ms': (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            'total_snapshots': len(history),
        }

    def create_snapshot(self):
        """创建指标快照"""
        self.metrics.snapshot()

    def reset_metrics(self):
        """重置指标"""
        self.metrics.reset()


# 全局监控器实例
_cache_monitor: Optional[CacheMonitor] = None


def get_cache_monitor(cache_instance=None) -> CacheMonitor:
    """
    获取缓存监控器实例

    Args:
        cache_instance: 缓存实例（首次调用时需要提供）

    Returns:
        CacheMonitor实例
    """
    global _cache_monitor

    if _cache_monitor is None:
        if cache_instance is None:
            raise ValueError("首次调用需要提供cache_instance参数")
        _cache_monitor = CacheMonitor(cache_instance)

    return _cache_monitor


def record_cache_operation(cache_key: str, hit: bool, response_time_ms: float = 0.0):
    """
    记录缓存操作的便捷函数

    Args:
        cache_key: 缓存键
        hit: 是否命中
        response_time_ms: 响应时间（毫秒）
    """
    if _cache_monitor is not None:
        _cache_monitor.record_cache_operation(cache_key, hit, response_time_ms)


logger.info("✅ 缓存监控增强模块已加载 (1.0.0)")
