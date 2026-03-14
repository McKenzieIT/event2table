#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis内存监控功能测试
==================

测试内容:
- Redis内存信息获取
- 内存使用率计算
- 异常处理

版本: 1.0.0
日期: 2026-02-27
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.core.cache.cache_hierarchical import HierarchicalCache
from backend.core.cache.monitoring import CacheAlertManager


class TestRedisMemoryMonitoring:
    """Redis内存监控测试"""

    def setup_method(self):
        """测试前准备"""
        self.cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)
        self.alert_manager = CacheAlertManager(self.cache)

    def test_get_redis_memory_usage_with_maxmemory(self):
        """测试获取Redis内存使用情况(有maxmemory限制)"""
        # Mock Redis客户端
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 536870912,  # 512MB
            "maxmemory": 1073741824,  # 1GB
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 调用方法
        usage_rate = self.alert_manager._get_redis_memory_usage()

        # 验证结果
        assert usage_rate == 0.5  # 512MB / 1GB = 50%
        mock_redis.info.assert_called_once_with("memory")

    def test_get_redis_memory_usage_without_maxmemory(self):
        """测试获取Redis内存使用情况(无maxmemory限制)"""
        # Mock Redis客户端
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 536870912,  # 512MB
            "maxmemory": 0,  # 无限制
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 调用方法
        usage_rate = self.alert_manager._get_redis_memory_usage()

        # 验证结果(无限制时返回0.0)
        assert usage_rate == 0.0
        mock_redis.info.assert_called_once_with("memory")

    def test_get_redis_memory_usage_redis_unavailable(self):
        """测试Redis不可用时的情况"""
        # Mock Redis客户端返回None
        self.cache._get_redis_client = Mock(return_value=None)

        # 调用方法
        usage_rate = self.alert_manager._get_redis_memory_usage()

        # 验证结果
        assert usage_rate == 0.0

    def test_get_redis_memory_usage_exception_handling(self):
        """测试异常处理"""
        # Mock Redis客户端抛出异常
        mock_redis = Mock()
        mock_redis.info.side_effect = Exception("Redis connection error")

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 调用方法
        usage_rate = self.alert_manager._get_redis_memory_usage()

        # 验证结果(异常时返回0.0)
        assert usage_rate == 0.0

    def test_collect_metrics_includes_redis_memory(self):
        """测试指标采集包含Redis内存使用情况"""
        # Mock Redis客户端
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 268435456,  # 256MB
            "maxmemory": 1073741824,  # 1GB
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 采集指标
        snapshot = self.alert_manager.collect_metrics()

        # 验证Redis内存使用率被包含在快照中
        assert snapshot.l2_memory_usage == 0.25  # 256MB / 1GB = 25%

    def test_collect_metrics_redis_memory_high_usage(self):
        """测试高Redis内存使用率场景"""
        # Mock Redis客户端(90%使用率)
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 966367641,  # ~922MB
            "maxmemory": 1073741824,  # 1GB
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 采集指标
        snapshot = self.alert_manager.collect_metrics()

        # 验证高使用率被正确计算
        assert snapshot.l2_memory_usage == pytest.approx(0.9, rel=0.01)

    def test_get_redis_memory_usage_bytes_to_mb_conversion(self):
        """测试字节到MB的转换"""
        # Mock Redis客户端
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 1048576,  # 1MB
            "maxmemory": 104857600,  # 100MB
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 调用方法
        usage_rate = self.alert_manager._get_redis_memory_usage()

        # 验证转换正确
        assert usage_rate == 0.01  # 1MB / 100MB = 1%

    def test_metrics_summary_includes_l2_memory(self):
        """测试指标摘要包含L2内存使用情况"""
        # Mock Redis客户端
        mock_redis = Mock()
        mock_redis.info.return_value = {
            "used_memory": 536870912,  # 512MB
            "maxmemory": 1073741824,  # 1GB
        }

        # Mock cache._get_redis_client
        self.cache._get_redis_client = Mock(return_value=mock_redis)

        # 采集指标
        self.alert_manager.collect_metrics()

        # 获取指标摘要
        summary = self.alert_manager.get_metrics_summary()

        # 验证摘要包含L2内存使用情况
        assert "l2_memory_usage" in summary or "l2_usage" in summary


class TestRedisMemoryMonitoringIntegration:
    """Redis内存监控集成测试"""

    def test_redis_memory_usage_in_alert_rules(self):
        """测试Redis内存使用率可以用于告警规则"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 创建带有L2内存告警规则的管理器
        alert_manager = CacheAlertManager(cache)

        # 验证可以添加自定义告警规则
        from backend.core.cache.monitoring import AlertLevel, AlertRule

        custom_rule = AlertRule(
            name="l2_memory_high",
            metric="l2_memory_usage",
            threshold=0.8,  # 80%
            duration=300,
            level=AlertLevel.WARNING,
            description="L2缓存内存使用率超过80%",
        )

        alert_manager.alert_rules.append(custom_rule)

        # 验证规则已添加
        assert any(rule.name == "l2_memory_high" for rule in alert_manager.alert_rules)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
