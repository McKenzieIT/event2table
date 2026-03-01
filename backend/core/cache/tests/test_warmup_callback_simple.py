#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的预热回调测试
==================

验证 CacheAlertManager._trigger_warm_up 方法正确调用回调

版本: 1.0.0
日期: 2026-02-27
"""

import pytest
from unittest.mock import Mock, patch
from backend.core.cache.monitoring import CacheAlertManager


class MockCache:
    """模拟三级缓存"""

    def __init__(self):
        self.l1_size = 1000
        self.l1_cache = {}

    def get_stats(self):
        return {
            'l1_hits': 10,
            'l2_hits': 15,
            'misses': 100,
            'total_requests': 125,
            'l1_usage': '50%',
            'l1_size': self.l1_size,
            'l1_capacity': 2000
        }

    def _get_redis_client(self):
        return None


def test_warmup_callback_direct_call():
    """测试直接调用 _trigger_warm_up 方法"""

    # 创建模拟缓存
    mock_cache = MockCache()

    # 创建预热回调
    callback_called = {"called": False, "result": None}

    def warmup_callback():
        callback_called["called"] = True
        callback_called["result"] = {"warmed": 100, "failed": 0, "skipped": 0}
        return callback_called["result"]

    # 创建告警管理器（带回调）
    alert_manager = CacheAlertManager(
        mock_cache,
        warmup_callback=warmup_callback
    )

    # 直接调用预热方法
    alert_manager._trigger_warm_up()

    # 验证回调被调用
    assert callback_called["called"], "回调应被调用"
    assert callback_called["result"] == {"warmed": 100, "failed": 0, "skipped": 0}

    # 验证统计信息被记录
    assert alert_manager._warmup_stats["triggered_count"] == 1
    assert alert_manager._warmup_stats["last_triggered_time"] > 0
    assert alert_manager._warmup_stats["last_trigger_result"] == callback_called["result"]

    print("✅ 直接调用预热方法测试通过")


def test_warmup_callback_with_sync_function():
    """测试同步回调函数"""

    mock_cache = MockCache()

    def sync_callback():
        return {"games_warmed": 10, "events_warmed": 20, "params_warmed": 30}

    alert_manager = CacheAlertManager(mock_cache, warmup_callback=sync_callback)

    # 直接调用
    alert_manager._trigger_warm_up()

    # 验证结果
    result = alert_manager._warmup_stats["last_trigger_result"]
    assert result["games_warmed"] == 10
    assert result["events_warmed"] == 20
    assert result["params_warmed"] == 30

    print("✅ 同步回调函数测试通过")


def test_warmup_callback_with_async_function():
    """测试异步回调函数"""
    import asyncio

    mock_cache = MockCache()

    async def async_callback():
        await asyncio.sleep(0.01)
        return {"warmed": 50, "failed": 2, "skipped": 5}

    alert_manager = CacheAlertManager(mock_cache, warmup_callback=async_callback)

    # 直接调用（应自动处理异步）
    alert_manager._trigger_warm_up()

    # 验证结果
    result = alert_manager._warmup_stats["last_trigger_result"]
    assert result["warmed"] == 50
    assert result["failed"] == 2
    assert result["skipped"] == 5

    print("✅ 异步回调函数测试通过")


def test_warmup_callback_exception_handling():
    """测试回调异常处理"""

    mock_cache = MockCache()

    def failing_callback():
        raise ValueError("Test error")

    alert_manager = CacheAlertManager(mock_cache, warmup_callback=failing_callback)

    # 直接调用（不应抛出异常）
    alert_manager._trigger_warm_up()

    # 验证错误被捕获
    result = alert_manager._warmup_stats["last_trigger_result"]
    assert result is not None
    assert "error" in result
    assert "Test error" in result["error"]

    print("✅ 回调异常处理测试通过")


def test_warmup_callback_none():
    """测试无回调的情况"""

    mock_cache = MockCache()

    alert_manager = CacheAlertManager(mock_cache, warmup_callback=None)

    # 直接调用（不应抛出异常）
    alert_manager._trigger_warm_up()

    # 验证无结果
    assert alert_manager._warmup_stats["last_trigger_result"] is None

    print("✅ 无回调测试通过")


def test_warmup_stats_in_summary():
    """测试预热统计包含在摘要中"""

    mock_cache = MockCache()

    def warmup_callback():
        return {"warmed": 123}

    alert_manager = CacheAlertManager(mock_cache, warmup_callback=warmup_callback)

    # 调用预热
    alert_manager._trigger_warm_up()

    # 收集指标
    alert_manager.collect_metrics()

    # 获取摘要
    summary = alert_manager.get_metrics_summary()

    # 验证预热统计存在
    assert "warmup_stats" in summary
    assert summary["warmup_stats"]["triggered_count"] == 1
    assert summary["warmup_stats"]["last_trigger_result"]["warmed"] == 123

    print("✅ 预热统计在摘要中测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
