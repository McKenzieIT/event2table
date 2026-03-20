#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控系统测试
================

测试缓存监控增强模块的功能

版本: 1.0.0
日期: 2026-03-10
"""

import pytest
import time
from backend.core.cache.monitoring_enhanced import (
    CacheMetrics,
    CacheMonitor,
    get_cache_monitor,
    record_cache_operation,
)


class TestCacheMetrics:
    """测试缓存指标收集器"""

    def test_initial_state(self):
        """测试初始状态"""
        metrics = CacheMetrics()
        stats = metrics.get_metrics()

        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate'] == '0.00%'

    def test_record_hit(self):
        """测试记录命中"""
        metrics = CacheMetrics()
        metrics.record_hit(response_time_ms=1.5)

        stats = metrics.get_metrics()
        assert stats['hits'] == 1
        assert stats['total_requests'] == 1
        assert stats['hit_rate'] == '100.00%'
        assert stats['avg_response_time_ms'] == 1.5

    def test_record_miss(self):
        """测试记录未命中"""
        metrics = CacheMetrics()
        metrics.record_miss(response_time_ms=50.0)

        stats = metrics.get_metrics()
        assert stats['misses'] == 1
        assert stats['total_requests'] == 1
        assert stats['hit_rate'] == '0.00%'
        assert stats['avg_response_time_ms'] == 50.0

    def test_hit_rate_calculation(self):
        """测试命中率计算"""
        metrics = CacheMetrics()

        # 记录5次命中, 5次未命中
        for _ in range(5):
            metrics.record_hit()
            metrics.record_miss()

        assert metrics.get_hit_rate() == 50.0

    def test_response_time_averaging(self):
        """测试响应时间平均"""
        metrics = CacheMetrics()

        # 记录不同的响应时间
        response_times = [10.0, 20.0, 30.0, 40.0, 50.0]
        for rt in response_times:
            metrics.record_hit(response_time_ms=rt)

        stats = metrics.get_metrics()
        expected_avg = sum(response_times) / len(response_times)
        assert stats['avg_response_time_ms'] == expected_avg

    def test_snapshot(self):
        """测试快照功能"""
        metrics = CacheMetrics()

        # 记录一些操作
        metrics.record_hit(response_time_ms=1.0)
        metrics.record_miss(response_time_ms=10.0)

        # 创建快照
        metrics.snapshot()

        # 获取历史记录
        history = metrics.get_history()
        assert len(history) == 1
        assert history[0]['hits'] == 1
        assert history[0]['misses'] == 1

    def test_reset(self):
        """测试重置功能"""
        metrics = CacheMetrics()

        # 记录一些操作
        metrics.record_hit()
        metrics.record_miss()

        # 重置
        metrics.reset()

        stats = metrics.get_metrics()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_requests'] == 0


class TestCacheMonitor:
    """测试缓存监控器"""

    @pytest.fixture
    def mock_cache(self):
        """模拟缓存实例"""

        class MockCache:
            def __init__(self):
                self.stats = {
                    'l1_hits': 0,
                    'l2_hits': 0,
                    'misses': 0,
                    'l1_size': 0,
                    'l1_capacity': 1000,
                    'l1_usage': '0.0%',
                    'l1_evictions': 0,
                    'l1_sets': 0,
                    'l2_sets': 0,
                    'total_requests': 0,
                    'hit_rate': '0.0%',
                }

            def get_stats(self):
                return self.stats

        return MockCache()

    def test_initial_state(self, mock_cache):
        """测试初始状态"""
        monitor = CacheMonitor(mock_cache)
        stats = monitor.get_stats()

        assert 'cache_stats' in stats
        assert 'performance_metrics' in stats
        assert 'recent_alerts' in stats

    def test_record_cache_operation_hit(self, mock_cache):
        """测试记录缓存命中"""
        monitor = CacheMonitor(mock_cache)
        monitor.record_cache_operation('test_key', hit=True, response_time_ms=1.5)

        metrics = monitor.metrics.get_metrics()
        assert metrics['hits'] == 1
        assert metrics['total_requests'] == 1

    def test_record_cache_operation_miss(self, mock_cache):
        """测试记录缓存未命中"""
        monitor = CacheMonitor(mock_cache)
        monitor.record_cache_operation('test_key', hit=False, response_time_ms=50.0)

        metrics = monitor.metrics.get_metrics()
        assert metrics['misses'] == 1
        assert metrics['total_requests'] == 1

    def test_alert_low_hit_rate(self, mock_cache):
        """测试低命中率告警"""
        monitor = CacheMonitor(
            mock_cache,
            alert_thresholds={
                'low_hit_rate': 50.0,
                'high_miss_rate': 50.0,
                'slow_response': 100.0,
            },
        )

        # 记录10次操作, 只有2次命中(20%命中率)
        for _ in range(2):
            monitor.record_cache_operation('key', hit=True)
        for _ in range(8):
            monitor.record_cache_operation('key', hit=False)

        stats = monitor.get_stats()
        # 应该有告警
        assert stats['alert_count'] > 0
        assert any(a['type'] == 'low_hit_rate' for a in stats['recent_alerts'])

    def test_alert_slow_response(self, mock_cache):
        """测试慢响应告警"""
        monitor = CacheMonitor(
            mock_cache,
            alert_thresholds={
                'low_hit_rate': 50.0,
                'high_miss_rate': 50.0,
                'slow_response': 100.0,
            },
        )

        # 记录多次慢响应(需要累积足够的样本)
        for _ in range(5):
            monitor.record_cache_operation('key', hit=False, response_time_ms=150.0)

        stats = monitor.get_stats()
        # 应该有告警
        assert stats['alert_count'] > 0
        assert any(a['type'] == 'slow_response' for a in stats['recent_alerts'])

    def test_performance_summary(self, mock_cache):
        """测试性能摘要"""
        monitor = CacheMonitor(mock_cache)

        # 创建一些历史快照
        for i in range(10):
            if i % 2 == 0:
                monitor.metrics.record_hit(response_time_ms=10.0 + i)
            else:
                monitor.metrics.record_miss(response_time_ms=50.0 + i)
            monitor.metrics.snapshot()

        summary = monitor.get_performance_summary(hours=1)
        assert 'period_hours' in summary
        assert 'avg_hit_rate' in summary
        assert 'total_snapshots' in summary


class TestGlobalMonitor:
    """测试全局监控器"""

    @pytest.fixture
    def mock_cache(self):
        """模拟缓存实例"""

        class MockCache:
            def get_stats(self):
                return {
                    'l1_hits': 0,
                    'l2_hits': 0,
                    'misses': 0,
                    'total_requests': 0,
                    'hit_rate': '0.0%',
                }

        return MockCache()

    def test_get_cache_monitor(self, mock_cache):
        """测试获取全局监控器"""
        # 首次调用需要提供cache_instance
        monitor = get_cache_monitor(mock_cache)
        assert monitor is not None

        # 后续调用可以不提供参数
        monitor2 = get_cache_monitor()
        assert monitor is monitor2

    def test_record_cache_operation_global(self, mock_cache):
        """测试全局记录函数"""
        monitor = get_cache_monitor(mock_cache)

        # 使用全局函数记录
        record_cache_operation('test_key', hit=True, response_time_ms=1.5)

        metrics = monitor.metrics.get_metrics()
        assert metrics['hits'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
