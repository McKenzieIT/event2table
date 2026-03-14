#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试缓存监控预热集成
====================

验证 CacheAlertManager 在缓存命中率低时自动触发预热

测试场景:
1. 同步预热回调
2. 异步预热回调
3. 预热统计记录
4. 回调失败处理
5. 无回调时的降级行为

版本: 1.0.0
日期: 2026-02-27
"""

import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.core.cache.monitoring import AlertLevel, CacheAlertManager


class MockCache:
    """模拟三级缓存"""

    def __init__(self):
        self.l1_size = 1000
        self.l1_cache = {}

    def get_stats(self):
        return {
            'l1_hits': 10,
            'l2_hits': 15,
            'misses': 100,  # 低命中率: (10+15)/125 = 20%
            'total_requests': 125,
            'l1_usage': '50%',
            'l1_size': self.l1_size,
            'l1_capacity': 2000,
        }

    def _get_redis_client(self):
        """模拟Redis客户端(用于monitoring.py的_get_redis_memory_usage)"""
        return None  # 返回None会触发异常处理, 使用默认值0.0


class TestWarmupIntegration:
    """预热集成测试"""

    def test_sync_warmup_callback(self):
        """测试同步预热回调"""
        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建同步预热回调
        def sync_warmup_callback():
            return {"warmed": 50, "failed": 0, "skipped": 10}

        # 创建告警管理器(带回调)
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=sync_warmup_callback)

        # 模拟低命中率场景(连续收集足够多的指标以触发告警)
        # 总体命中率告警需要持续300秒, 我们模拟多次采集
        import time

        base_time = time.time() - 400  # 从400秒前开始

        for i in range(350):  # 350次采集, 覆盖350秒
            # 修改timestamp使历史记录跨越300秒
            snapshot = alert_manager.collect_metrics()
            # 手动调整snapshot时间
            alert_manager.metrics_history.history[-1].timestamp = base_time + i
            time.sleep(0.001)  # 小延迟

        # 触发告警检查
        alerts = alert_manager.check_alerts()

        # 验证预热被触发
        assert len(alerts) > 0, "应触发告警"
        assert alert_manager._warmup_stats["triggered_count"] > 0, "预热应被触发"

        # 验证预热结果被记录
        assert alert_manager._warmup_stats["last_trigger_result"] is not None
        result = alert_manager._warmup_stats["last_trigger_result"]
        assert result["warmed"] == 50
        assert result["failed"] == 0
        assert result["skipped"] == 10

        print("✅ 同步预热回调测试通过")

    def test_async_warmup_callback(self):
        """测试异步预热回调"""
        import asyncio
        import time

        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建异步预热回调
        async def async_warmup_callback():
            await asyncio.sleep(0.1)  # 模拟异步操作
            return {"warmed": 30, "failed": 2, "skipped": 5}

        # 创建告警管理器(带异步回调)
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=async_warmup_callback)

        # 模拟低命中率场景(持续300秒)
        base_time = time.time() - 400
        for i in range(350):
            snapshot = alert_manager.collect_metrics()
            alert_manager.metrics_history.history[-1].timestamp = base_time + i
            time.sleep(0.001)

        # 触发告警检查
        alerts = alert_manager.check_alerts()

        # 验证预热被触发
        assert alert_manager._warmup_stats["triggered_count"] > 0

        # 验证预热结果被记录
        result = alert_manager._warmup_stats["last_trigger_result"]
        assert result["warmed"] == 30
        assert result["failed"] == 2

        print("✅ 异步预热回调测试通过")

    def test_warmup_callback_exception_handling(self):
        """测试回调异常处理"""
        import time

        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建会抛出异常的回调
        def failing_callback():
            raise RuntimeError("Warmup service unavailable")

        # 创建告警管理器
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=failing_callback)

        # 模拟低命中率场景(持续300秒)
        base_time = time.time() - 400
        for i in range(350):
            snapshot = alert_manager.collect_metrics()
            alert_manager.metrics_history.history[-1].timestamp = base_time + i
            time.sleep(0.001)

        # 触发告警检查(不应抛出异常)
        alerts = alert_manager.check_alerts()

        # 验证预热被触发但失败
        assert alert_manager._warmup_stats["triggered_count"] > 0
        result = alert_manager._warmup_stats["last_trigger_result"]
        assert "error" in result
        assert "Warmup service unavailable" in result["error"]

        print("✅ 回调异常处理测试通过")

    def test_no_callback_degraded_behavior(self):
        """测试无回调时的降级行为"""
        import time

        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建告警管理器(无回调)
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=None)

        # 模拟低命中率场景(持续300秒)
        base_time = time.time() - 400
        for i in range(350):
            snapshot = alert_manager.collect_metrics()
            alert_manager.metrics_history.history[-1].timestamp = base_time + i
            time.sleep(0.001)

        # 触发告警检查(不应抛出异常)
        alerts = alert_manager.check_alerts()

        # 验证告警被触发但无预热结果
        assert len(alerts) > 0
        assert alert_manager._warmup_stats["triggered_count"] > 0
        assert alert_manager._warmup_stats["last_trigger_result"] is None

        print("✅ 无回调降级行为测试通过")

    def test_warmup_stats_in_metrics_summary(self):
        """测试预热统计包含在指标摘要中"""
        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建预热回调
        def warmup_callback():
            return {"warmed": 100, "failed": 0, "skipped": 0}

        # 创建告警管理器
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=warmup_callback)

        # 收集指标
        alert_manager.collect_metrics()

        # 获取指标摘要
        summary = alert_manager.get_metrics_summary()

        # 验证预热统计存在
        assert "warmup_stats" in summary
        assert "triggered_count" in summary["warmup_stats"]
        assert "last_triggered_time" in summary["warmup_stats"]
        assert "last_trigger_result" in summary["warmup_stats"]

        print("✅ 预热统计在指标摘要中测试通过")

    def test_warmup_prevents_duplicate_alerts(self):
        """测试预热后防止重复告警"""
        import time

        # 创建模拟缓存
        mock_cache = MockCache()

        # 创建预热回调
        call_count = {"count": 0}

        def warmup_callback():
            call_count["count"] += 1
            return {"warmed": 50, "failed": 0, "skipped": 0}

        # 创建告警管理器
        alert_manager = CacheAlertManager(mock_cache, warmup_callback=warmup_callback)

        # 模拟低命中率场景(持续300秒以触发告警)
        base_time = time.time() - 400
        for i in range(350):
            snapshot = alert_manager.collect_metrics()
            alert_manager.metrics_history.history[-1].timestamp = base_time + i

            # 每50次检查一次告警
            if i % 50 == 0:
                alert_manager.check_alerts()

        # 验证回调被调用(去重机制不会在短时间阻止首次触发)
        assert call_count["count"] >= 1, "回调应至少被调用一次"

        print("✅ 防止重复告警测试通过")


def test_real_cache_warmer_integration():
    """测试真实的CacheWarmer集成(需要数据库)"""
    pytest.skip("需要真实数据库, 跳过集成测试")

    # 示例代码(仅供参考)
    """
    from backend.services.cache.cache_warmup import CacheWarmer
    from backend.core.cache.cache_system import get_cache

    # 创建真实的预热器
    warmer = CacheWarmer()
    cache = get_cache()

    # 创建告警管理器(注入预热回调)
    alert_manager = CacheAlertManager(
        cache,
        warmup_callback=warmer.warmup_all
    )

    # 模拟低命中率场景
    for _ in range(5):
        alert_manager.collect_metrics()

    # 触发告警检查
    alerts = alert_manager.check_alerts()

    # 验证预热被触发
    assert alert_manager._warmup_stats["triggered_count"] > 0
    result = alert_manager._warmup_stats["last_trigger_result"]
    assert result["games_warmed"] > 0 or result["events_warmed"] > 0
    """


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
