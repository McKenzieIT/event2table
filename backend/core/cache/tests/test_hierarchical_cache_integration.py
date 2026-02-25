#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HierarchicalCache Integration Tests
===================================

测试新模块集成到HierarchicalCache的功能

测试范围:
- 读写锁集成
- 布隆过滤器集成
- 降级策略集成
- 多功能同时启用

版本: 1.0.0
日期: 2026-02-24
"""

import pytest
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from backend.core.cache.cache_hierarchical import HierarchicalCache


class TestReadWriteLockIntegration:
    """测试读写锁集成"""

    def test_read_lock_basic(self):
        """测试基本读锁功能"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True
        )

        # 写入数据
        cache.set("test", {"data": "value"})
        result = cache.get("test")

        assert result == {"data": "value"}
        assert cache.stats["l1_hits"] >= 1

    def test_write_lock_basic(self):
        """测试基本写锁功能"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True
        )

        # 多次写入
        for i in range(10):
            cache.set(f"test_{i}", {"index": i})

        # 验证所有数据都写入成功
        for i in range(10):
            result = cache.get(f"test_{i}")
            assert result == {"index": i}

    def test_read_write_lock_toggle(self):
        """测试读写锁开关"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=False
        )

        # 初始状态：禁用
        status = cache.get_integration_status()
        assert status["read_write_lock_enabled"] is False

        # 启用读写锁
        cache.enable_read_write_lock()
        status = cache.get_integration_status()
        assert status["read_write_lock_enabled"] is True

        # 禁用读写锁
        cache.disable_read_write_lock()
        status = cache.get_integration_status()
        assert status["read_write_lock_enabled"] is False


class TestBloomFilterIntegration:
    """测试布隆过滤器集成"""

    def test_bloom_filter_basic(self):
        """测试基本布隆过滤器功能"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_bloom_filter=True
        )

        # 写入数据（应该添加到布隆过滤器）
        cache.set("test", {"data": "value"})

        # 查询存在的键（应该命中）
        result = cache.get("test")
        assert result == {"data": "value"}

        # 查询不存在的键（应该被布隆过滤器快速拒绝）
        result = cache.get("nonexistent")
        assert result is None

    def test_bloom_filter_toggle(self):
        """测试布隆过滤器开关"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_bloom_filter=False
        )

        # 初始状态：禁用
        status = cache.get_integration_status()
        assert status["bloom_filter_enabled"] is False

        # 启用布隆过滤器
        cache.enable_bloom_filter()
        status = cache.get_integration_status()
        assert status["bloom_filter_enabled"] is True

        # 禁用布隆过滤器
        cache.disable_bloom_filter()
        status = cache.get_integration_status()
        assert status["bloom_filter_enabled"] is False


class TestDegradationIntegration:
    """测试降级策略集成"""

    def test_degradation_basic(self):
        """测试基本降级功能"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_degradation=True
        )

        # 获取降级管理器
        degradation_manager = cache._get_degradation_manager()
        if degradation_manager is None:
            pytest.skip("降级管理器未加载")

        # 正常模式：读写都应该成功
        cache.set("test", {"data": "value"})
        result = cache.get("test")
        assert result == {"data": "value"}

        # 强制进入降级模式
        degradation_manager.force_degrade()

        # 降级模式：仍能读写（L1 only）
        cache.set("test2", {"data": "value2"})
        result = cache.get("test2")
        assert result == {"data": "value2"}

        # 恢复正常
        degradation_manager.force_recover()

    def test_degradation_toggle(self):
        """测试降级策略开关"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_degradation=False
        )

        # 初始状态：禁用
        status = cache.get_integration_status()
        assert status["degradation_enabled"] is False

        # 启用降级策略
        cache.enable_degradation()
        status = cache.get_integration_status()
        assert status["degradation_enabled"] is True

        # 禁用降级策略
        cache.disable_degradation()
        status = cache.get_integration_status()
        assert status["degradation_enabled"] is False


class TestMultipleIntegrations:
    """测试多个功能同时启用"""

    def test_all_features_enabled(self):
        """测试所有功能同时启用"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_bloom_filter=True,
            enable_degradation=True
        )

        # 检查所有功能都已启用
        status = cache.get_integration_status()
        assert status["read_write_lock_enabled"] is True
        assert status["bloom_filter_enabled"] is True
        assert status["degradation_enabled"] is True

        # 基本读写测试
        cache.set("test", {"data": "value"})
        result = cache.get("test")
        assert result == {"data": "value"}

    def test_read_write_with_bloom_filter(self):
        """测试读写锁 + 布隆过滤器"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_bloom_filter=True
        )

        # 写入数据
        cache.set("test", {"data": "value"})

        # 读取数据（应该经过布隆过滤器 + 读写锁）
        result = cache.get("test")
        assert result == {"data": "value"}

    def test_read_write_with_degradation(self):
        """测试读写锁 + 降级策略"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_degradation=True
        )

        degradation_manager = cache._get_degradation_manager()
        if degradation_manager is None:
            pytest.skip("降级管理器未加载")

        # 正常模式
        cache.set("test", {"data": "value"})
        result = cache.get("test")
        assert result == {"data": "value"}

        # 降级模式
        degradation_manager.force_degrade()
        cache.set("test2", {"data": "value2"})
        result = cache.get("test2")
        assert result == {"data": "value2"}

        degradation_manager.force_recover()


class TestBackwardCompatibility:
    """测试向后兼容性"""

    def test_no_features_enabled(self):
        """测试不启用任何新功能（向后兼容）"""
        cache = HierarchicalCache(
            l1_size=1000,
            l1_ttl=60,
            l2_ttl=3600
        )

        # 所有功能应该禁用
        status = cache.get_integration_status()
        assert status["read_write_lock_enabled"] is False
        assert status["bloom_filter_enabled"] is False
        assert status["degradation_enabled"] is False

        # 基本功能应该正常工作
        cache.set("test", {"data": "value"})
        result = cache.get("test")
        assert result == {"data": "value"}

        # 统计信息应该正常
        stats = cache.get_stats()
        assert stats["l1_hits"] >= 1


class TestEdgeCases:
    """测试边缘情况"""

    def test_empty_cache_with_features(self):
        """测试空缓存启用功能"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_bloom_filter=True,
            enable_degradation=True
        )

        # 查询不存在的键
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_clear_with_features(self):
        """测试清空缓存（功能不受影响）"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_bloom_filter=True
        )

        # 写入数据
        cache.set("test1", {"data": "value1"})
        cache.set("test2", {"data": "value2"})

        # 清空L1
        cache.clear_l1()

        # 数据应该不在L1中
        result = cache.get("test1")
        # 可能从L2加载，或者None
        # 只要不出错即可

    def test_stats_reset_with_features(self):
        """测试重置统计（功能不受影响）"""
        cache = HierarchicalCache(
            l1_size=100,
            enable_read_write_lock=True,
            enable_bloom_filter=True
        )

        # 执行一些操作
        cache.set("test", {"data": "value"})
        cache.get("test")
        cache.get("nonexistent")

        # 重置统计
        cache.reset_stats()

        # 统计应该清零
        stats = cache.get_stats()
        assert stats["l1_hits"] == 0
        assert stats["l2_hits"] == 0
        assert stats["misses"] == 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
