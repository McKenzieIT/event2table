#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HierarchicalCache.set_raw()方法
===================================

测试set_raw()方法的功能：
- 直接设置缓存值（不经过序列化）
- 支持L1和L2层级设置
- 更新缓存统计
- 参数验证

版本: 1.0.0
日期: 2026-02-27
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.core.cache.cache_hierarchical import HierarchicalCache


class TestSetRawMethod:
    """测试set_raw()方法"""

    def setup_method(self):
        """每个测试前创建新的缓存实例"""
        self.cache = HierarchicalCache(l1_size=10, l1_ttl=60, l2_ttl=3600)

    def test_set_raw_l1_only(self):
        """测试仅写入L1缓存"""
        key = "dwd_gen:v3:test:key1"
        value = {"data": "test_value"}

        # 仅写入L1
        self.cache.set_raw(key, value, ttl=120, level='l1')

        # 验证L1缓存
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value
        assert key in self.cache.l1_timestamps

    def test_set_raw_both_levels(self):
        """测试同时写入L1和L2缓存（默认）"""
        key = "dwd_gen:v3:test:key2"
        value = {"data": "test_value_both"}

        # 同时写入L1和L2
        self.cache.set_raw(key, value, ttl=120, level='both')

        # 验证L1缓存
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value

        # 验证L2缓存（通过mock）
        # 注意：实际L2写入依赖Redis，这里只验证L1
        assert key in self.cache.l1_timestamps

    def test_set_raw_with_custom_ttl(self):
        """测试自定义TTL"""
        key = "dwd_gen:v3:test:key3"
        value = {"data": "custom_ttl"}

        # 设置自定义TTL
        custom_ttl = 300
        self.cache.set_raw(key, value, ttl=custom_ttl, level='l1')

        # 验证数据已写入
        assert key in self.cache.l1_cache
        assert self.cache.l1_timestamps[key] > 0

    def test_set_raw_with_default_ttl(self):
        """测试使用默认TTL"""
        key = "dwd_gen:v3:test:key4"
        value = {"data": "default_ttl"}

        # 不指定TTL，使用默认值
        self.cache.set_raw(key, value, level='l1')

        # 验证数据已写入
        assert key in self.cache.l1_cache

    def test_set_raw_with_invalid_level(self):
        """测试无效的level参数"""
        key = "dwd_gen:v3:test:key5"
        value = {"data": "test"}

        # 无效的level参数应该抛出异常
        with pytest.raises(ValueError, match="Invalid level"):
            self.cache.set_raw(key, value, level='invalid')

    def test_set_raw_l1_eviction(self):
        """测试L1缓存满时的LRU淘汰"""
        cache = HierarchicalCache(l1_size=3, l1_ttl=60, l2_ttl=3600)

        # 填满L1缓存
        cache.set_raw("dwd_gen:v3:test:key1", "value1", level='l1')
        time.sleep(0.01)  # 确保时间戳不同
        cache.set_raw("dwd_gen:v3:test:key2", "value2", level='l1')
        time.sleep(0.01)
        cache.set_raw("dwd_gen:v3:test:key3", "value3", level='l1')

        # 添加第4个key，应该淘汰最旧的
        cache.set_raw("dwd_gen:v3:test:key4", "value4", level='l1')

        # 验证最旧的key被淘汰
        assert "dwd_gen:v3:test:key1" not in cache.l1_cache
        assert "dwd_gen:v3:test:key4" in cache.l1_cache
        assert cache.stats["l1_evictions"] == 1

    def test_set_raw_with_bytes_value(self):
        """测试写入bytes类型的值"""
        key = "dwd_gen:v3:test:key_bytes"
        value = b"serialized_data"

        # 写入bytes数据
        self.cache.set_raw(key, value, level='l1')

        # 验证数据正确存储
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value
        assert isinstance(self.cache.l1_cache[key], bytes)

    def test_set_raw_with_string_value(self):
        """测试写入string类型的值"""
        key = "dwd_gen:v3:test:key_string"
        value = "string_data"

        # 写入string数据
        self.cache.set_raw(key, value, level='l1')

        # 验证数据正确存储
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value
        assert isinstance(self.cache.l1_cache[key], str)

    def test_set_raw_with_dict_value(self):
        """测试写入dict类型的值"""
        key = "dwd_gen:v3:test:key_dict"
        value = {"id": 1, "name": "test", "data": [1, 2, 3]}

        # 写入dict数据
        self.cache.set_raw(key, value, level='l1')

        # 验证数据正确存储
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value
        assert isinstance(self.cache.l1_cache[key], dict)

    def test_set_raw_updates_existing_key(self):
        """测试更新已存在的key"""
        key = "dwd_gen:v3:test:key_update"
        old_value = "old_value"
        new_value = "new_value"

        # 写入初始值
        self.cache.set_raw(key, old_value, level='l1')
        assert self.cache.l1_cache[key] == old_value

        # 更新值
        self.cache.set_raw(key, new_value, level='l1')
        assert self.cache.l1_cache[key] == new_value

    def test_set_raw_with_l2_level(self):
        """测试仅写入L2缓存"""
        key = "dwd_gen:v3:test:key_l2_only"
        value = {"data": "l2_only"}

        # 仅写入L2（需要mock Redis）
        with patch('backend.core.cache.cache_hierarchical.get_cache') as mock_get_cache:
            mock_cache = Mock()
            mock_get_cache.return_value = mock_cache

            # 写入L2
            self.cache.set_raw(key, value, ttl=3600, level='l2')

            # 验证L1缓存为空
            assert key not in self.cache.l1_cache

            # 验证L2缓存被调用
            mock_cache.set.assert_called_once_with(key, value, timeout=3600)

    def test_set_raw_l2_failure_handling(self):
        """测试L2写入失败时的处理"""
        key = "dwd_gen:v3:test:key_l2_fail"
        value = {"data": "test"}

        # Mock L2缓存抛出异常
        with patch('backend.core.cache.cache_hierarchical.get_cache') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.set.side_effect = Exception("Redis connection failed")
            mock_get_cache.return_value = mock_cache

            # 写入both级别（L2应该失败，但不影响L1）
            self.cache.set_raw(key, value, ttl=3600, level='both')

            # 验证L1缓存仍然成功
            assert key in self.cache.l1_cache
            assert self.cache.l1_cache[key] == value

    def test_set_raw_preserves_timestamp(self):
        """测试set_raw正确更新时间戳"""
        key = "dwd_gen:v3:test:key_timestamp"
        value = "value"

        # 第一次写入
        self.cache.set_raw(key, value, level='l1')
        first_timestamp = self.cache.l1_timestamps[key]

        # 等待一小段时间
        time.sleep(0.01)

        # 更新写入
        self.cache.set_raw(key, "updated_value", level='l1')
        second_timestamp = self.cache.l1_timestamps[key]

        # 验证时间戳已更新
        assert second_timestamp > first_timestamp

    def test_set_raw_with_none_value(self):
        """测试写入None值"""
        key = "dwd_gen:v3:test:key_none"
        value = None

        # 写入None值
        self.cache.set_raw(key, value, level='l1')

        # 验证None值可以存储
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] is None

    def test_set_raw_with_complex_value(self):
        """测试写入复杂嵌套结构"""
        key = "dwd_gen:v3:test:key_complex"
        value = {
            "users": [
                {"id": 1, "name": "Alice", "tags": ["admin", "active"]},
                {"id": 2, "name": "Bob", "tags": ["user"]},
            ],
            "metadata": {
                "total": 2,
                "page": 1,
                "per_page": 10
            }
        }

        # 写入复杂数据
        self.cache.set_raw(key, value, level='l1')

        # 验证数据完整存储
        assert key in self.cache.l1_cache
        assert self.cache.l1_cache[key] == value
        assert len(self.cache.l1_cache[key]["users"]) == 2


class TestSetRawIntegration:
    """集成测试：set_raw与get的配合"""

    def setup_method(self):
        """每个测试前创建新的缓存实例"""
        self.cache = HierarchicalCache(l1_size=10, l1_ttl=60, l2_ttl=3600)

    def test_set_raw_then_get(self):
        """测试set_raw写入后get能读取"""
        key = "dwd_gen:v3:test:integration:key1"
        value = {"data": "integration_test"}

        # 使用set_raw写入
        self.cache.set_raw(key, value, level='l1')

        # 使用get读取
        result = self.cache.get("test", integration="key1")

        # 验证读取成功
        assert result is not None
        assert result == value

    def test_set_raw_with_ttl_expiration(self):
        """测试set_raw设置的TTL生效"""
        cache = HierarchicalCache(l1_size=10, l1_ttl=1, l2_ttl=3600)  # L1 TTL = 1秒

        key = "dwd_gen:v3:test:ttl:key1"
        value = {"data": "ttl_test"}

        # 写入缓存
        cache.set_raw(key, value, ttl=1, level='l1')

        # 立即读取应该成功
        result = cache.get("test", ttl="key1")
        assert result is not None

        # 等待TTL过期
        time.sleep(1.1)

        # 再次读取应该失败（L1过期）
        result = cache.get("test", ttl="key1")
        assert result is None  # L2也没有数据，所以返回None

    def test_set_raw_stats_update(self):
        """测试set_raw不影响统计"""
        key = "dwd_gen:v3:test:stats:key1"
        value = {"data": "stats_test"}

        # 记录初始统计
        initial_stats = self.cache.get_stats().copy()

        # 写入缓存
        self.cache.set_raw(key, value, level='l1')

        # 验证统计未变化（set_raw不增加hit/miss计数）
        stats_after = self.cache.get_stats()
        assert stats_after["l1_hits"] == initial_stats["l1_hits"]
        assert stats_after["l2_hits"] == initial_stats["l2_hits"]
        assert stats_after["misses"] == initial_stats["misses"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
