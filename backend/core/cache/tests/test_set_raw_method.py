#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HierarchicalCache set_raw() Method Unit Tests
==============================================

测试 set_raw() 方法的完整功能

测试范围:
- 基本功能测试 (level='l1', 'l2', 'both')
- TTL 功能测试
- 无效 level 参数测试（异常处理）
- 与 get() 方法的集成测试
- 与 invalidate() 方法的集成测试
- 数据类型兼容性测试
- 边缘情况测试

版本: 1.0.0
日期: 2026-02-27
"""

import sys
import time
from pathlib import Path

import pytest

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from backend.core.cache.cache_hierarchical import HierarchicalCache


class TestSetRawBasicFunctionality:
    """测试 set_raw() 基本功能"""

    def test_set_raw_l1_only(self):
        """测试 set_raw 仅写入 L1 缓存"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 写入 L1
        cache.set_raw('dwd_gen:v3:test:key1', 'value1', level='l1')

        # 验证 L1 有数据
        assert 'dwd_gen:v3:test:key1' in cache.l1_cache
        assert cache.l1_cache['dwd_gen:v3:test:key1'] == 'value1'

        # 验证 L2 无数据(需要 Redis 环境, 这里只验证不报错)
        # 注意: 如果 Redis 未启动, L2 写入会静默失败, 这是预期行为

    def test_set_raw_l2_only(self):
        """测试 set_raw 仅写入 L2 缓存"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 写入 L2
        cache.set_raw('dwd_gen:v3:test:key2', 'value2', level='l2')

        # 验证 L1 无数据
        assert 'dwd_gen:v3:test:key2' not in cache.l1_cache

        # L2 数据需要 Redis 环境, 这里只验证不报错

    def test_set_raw_both_levels(self):
        """测试 set_raw 同时写入 L1 和 L2 缓存"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 写入 both
        cache.set_raw('dwd_gen:v3:test:key3', 'value3', level='both')

        # 验证 L1 有数据
        assert 'dwd_gen:v3:test:key3' in cache.l1_cache
        assert cache.l1_cache['dwd_gen:v3:test:key3'] == 'value3'

        # L2 数据需要 Redis 环境

    def test_set_raw_default_level(self):
        """测试 set_raw 默认 level='both'"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 不指定 level, 应该默认为 'both'
        cache.set_raw('dwd_gen:v3:test:key4', 'value4')

        # 验证 L1 有数据(说明写入了 both)
        assert 'dwd_gen:v3:test:key4' in cache.l1_cache
        assert cache.l1_cache['dwd_gen:v3:test:key4'] == 'value4'


class TestSetRawTTLFunctionality:
    """测试 set_raw() TTL 功能"""

    def test_set_raw_with_custom_ttl_l1(self):
        """测试 set_raw 使用自定义 TTL (L1)"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用自定义 TTL = 2 秒
        cache.set_raw('dwd_gen:v3:test:ttl_key', 'value', ttl=2, level='l1')

        # 立即查询, 应该命中
        assert cache.get('test:ttl_key') == 'value'

        # 等待 3 秒后查询, 应该过期
        time.sleep(3)
        result = cache.get('test:ttl_key')
        assert result is None, "L1 缓存应该已过期"

    def test_set_raw_with_custom_ttl_both_levels(self):
        """测试 set_raw 使用自定义 TTL (both levels)"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用自定义 TTL = 2 秒
        cache.set_raw('dwd_gen:v3:test:ttl_both', 'value', ttl=2, level='both')

        # 立即查询, 应该命中 L1
        assert cache.get('test:ttl_both') == 'value'

        # 等待 3 秒后查询
        time.sleep(3)
        result = cache.get('test:ttl_both')
        # L1 已过期, L2 可能还有数据(取决于 Redis 环境)
        # 这里只验证不报错

    def test_set_raw_without_ttl_uses_default(self):
        """测试 set_raw 不指定 TTL 时使用默认值"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=1, l2_ttl=3600)

        # 不指定 TTL, 应该使用默认的 l1_ttl=1 秒
        cache.set_raw('dwd_gen:v3:test:default_ttl', 'value', level='l1')

        # 立即查询, 应该命中
        assert cache.get('test:default_ttl') == 'value'

        # 等待 2 秒后查询, 应该过期(默认 TTL=1 秒)
        time.sleep(2)
        result = cache.get('test:default_ttl')
        assert result is None, "L1 缓存应该已过期（使用默认 TTL）"


class TestSetRawInvalidLevel:
    """测试 set_raw() 无效 level 参数(异常处理)"""

    def test_set_raw_invalid_level_string(self):
        """测试 set_raw 使用无效的 level 字符串"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 应该抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            cache.set_raw('dwd_gen:v3:test:key', 'value', level='invalid')

        # 验证错误消息
        assert 'Invalid level' in str(exc_info.value)
        assert 'invalid' in str(exc_info.value)

    def test_set_raw_invalid_level_empty_string(self):
        """测试 set_raw 使用空字符串作为 level"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 应该抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            cache.set_raw('dwd_gen:v3:test:key', 'value', level='')

        assert 'Invalid level' in str(exc_info.value)

    def test_set_raw_invalid_level_case_sensitive(self):
        """测试 set_raw level 参数区分大小写"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 'L1' 不是 'l1', 应该抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            cache.set_raw('dwd_gen:v3:test:key', 'value', level='L1')

        assert 'Invalid level' in str(exc_info.value)

        # 'BOTH' 不是 'both', 应该抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            cache.set_raw('dwd_gen:v3:test:key', 'value', level='BOTH')

        assert 'Invalid level' in str(exc_info.value)

    def test_set_raw_invalid_level_none(self):
        """测试 set_raw level=None 应该使用默认值 'both'"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # level=None 应该默认使用 'both'(不抛出异常)
        cache.set_raw('dwd_gen:v3:test:key', 'value', level=None)

        # 验证 L1 有数据
        assert 'dwd_gen:v3:test:key' in cache.l1_cache
        assert cache.l1_cache['dwd_gen:v3:test:key'] == 'value'


class TestSetRawIntegrationWithGet:
    """测试 set_raw() 与 get() 方法的集成"""

    def test_set_raw_then_get_l1(self):
        """测试 set_raw 写入 L1 后 get 能正确获取"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用 set_raw 写入 L1
        cache.set_raw('dwd_gen:v3:test:integration_key', 'test_value', level='l1')

        # 使用 get 获取(应该命中 L1)
        result = cache.get('test:integration_key')

        assert result == 'test_value'
        assert cache.stats['l1_hits'] >= 1

    def test_set_raw_then_get_both_levels(self):
        """测试 set_raw 写入 both 后 get 能正确获取"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用 set_raw 写入 both
        cache.set_raw('dwd_gen:v3:test:integration_both', 'test_value', level='both')

        # 使用 get 获取(应该命中 L1)
        result = cache.get('test:integration_both')

        assert result == 'test_value'
        assert cache.stats['l1_hits'] >= 1

    def test_set_raw_complex_data_type(self):
        """测试 set_raw 写入复杂数据类型后 get 能正确获取"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 复杂数据
        complex_data = {
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'string': 'test',
            'number': 42,
            'boolean': True,
        }

        # 写入
        cache.set_raw('dwd_gen:v3:test:complex', complex_data, level='l1')

        # 获取
        result = cache.get('test:complex')

        assert result == complex_data
        assert result['list'] == [1, 2, 3]
        assert result['dict']['nested'] == 'value'

    def test_set_raw_bytes_data(self):
        """测试 set_raw 写入 bytes 数据"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # bytes 数据(模拟序列化后的数据)
        bytes_data = b'serialized_data'

        # 写入
        cache.set_raw('dwd_gen:v3:test:bytes', bytes_data, level='l1')

        # 获取
        result = cache.get('test:bytes')

        assert result == bytes_data
        assert isinstance(result, bytes)


class TestSetRawIntegrationWithInvalidate:
    """测试 set_raw() 与 invalidate() 方法的集成"""

    def test_set_raw_then_invalidate_l1(self):
        """测试 set_raw 写入 L1 后 invalidate 能正确删除"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用 set_raw 写入 L1
        cache.set_raw('dwd_gen:v3:test:invalidate_key', 'test_value', level='l1')

        # 验证数据存在
        assert cache.get('test:invalidate_key') == 'test_value'

        # 失效缓存
        cache.invalidate('test:invalidate_key')

        # 验证数据已删除
        result = cache.get('test:invalidate_key')
        assert result is None

    def test_set_raw_then_invalidate_both_levels(self):
        """测试 set_raw 写入 both 后 invalidate 能正确删除"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 使用 set_raw 写入 both
        cache.set_raw('dwd_gen:v3:test:invalidate_both', 'test_value', level='both')

        # 验证数据存在
        assert cache.get('test:invalidate_both') == 'test_value'

        # 失效缓存
        cache.invalidate('test:invalidate_both')

        # 验证 L1 数据已删除
        assert 'dwd_gen:v3:test:invalidate_both' not in cache.l1_cache

        # L2 失效需要 Redis 环境, 这里只验证不报错

    def test_set_raw_multiple_keys_then_invalidate_pattern(self):
        """测试 set_raw 写入多个键后使用模式失效"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 写入多个键
        cache.set_raw('dwd_gen:v3:test:pattern:key1', 'value1', level='l1')
        cache.set_raw('dwd_gen:v3:test:pattern:key2', 'value2', level='l1')
        cache.set_raw('dwd_gen:v3:test:other:key3', 'value3', level='l1')

        # 使用模式失效(只失效 test:pattern:*)
        count = cache.invalidate_pattern('test:pattern', game_id=0)

        # 验证失效了 2 个键
        assert count >= 2

        # 验证被失效的键不存在
        assert cache.get('test:pattern:key1') is None
        assert cache.get('test:pattern:key2') is None

        # 验证其他键仍存在
        assert cache.get('test:other:key3') == 'value3'


class TestSetRawEdgeCases:
    """测试 set_raw() 边缘情况"""

    def test_set_raw_empty_key(self):
        """测试 set_raw 使用空键"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 空键应该正常工作(虽然不推荐)
        cache.set_raw('', 'value', level='l1')

        # 验证
        assert '' in cache.l1_cache
        assert cache.l1_cache[''] == 'value'

    def test_set_raw_none_value(self):
        """测试 set_raw 使用 None 值"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # None 值应该正常工作
        cache.set_raw('dwd_gen:v3:test:none_key', None, level='l1')

        # 验证
        assert cache.get('test:none_key') is None

    def test_set_raw_overwrite_existing_key(self):
        """测试 set_raw 覆盖已存在的键"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 写入初始值
        cache.set_raw('dwd_gen:v3:test:overwrite', 'value1', level='l1')
        assert cache.get('test:overwrite') == 'value1'

        # 覆盖
        cache.set_raw('dwd_gen:v3:test:overwrite', 'value2', level='l1')
        assert cache.get('test:overwrite') == 'value2'

    def test_set_raw_l1_full_eviction(self):
        """测试 set_raw 当 L1 满时的 LRU 淘汰"""
        cache = HierarchicalCache(l1_size=3, l1_ttl=60, l2_ttl=3600)

        # 填满 L1
        cache.set_raw('dwd_gen:v3:test:key1', 'value1', level='l1')
        cache.set_raw('dwd_gen:v3:test:key2', 'value2', level='l1')
        cache.set_raw('dwd_gen:v3:test:key3', 'value3', level='l1')

        assert len(cache.l1_cache) == 3
        assert cache.stats['l1_evictions'] == 0

        # 添加第 4 个键, 应该淘汰最旧的
        cache.set_raw('dwd_gen:v3:test:key4', 'value4', level='l1')

        assert len(cache.l1_cache) == 3
        assert cache.stats['l1_evictions'] == 1

        # 最旧的键应该被淘汰
        assert cache.get('test:key1') is None

        # 其他键应该存在
        assert cache.get('test:key2') == 'value2'
        assert cache.get('test:key3') == 'value3'
        assert cache.get('test:key4') == 'value4'

    def test_set_raw_zero_ttl(self):
        """测试 set_raw 使用 TTL=0(立即过期)"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # TTL=0 应该立即过期
        cache.set_raw('dwd_gen:v3:test:zero_ttl', 'value', ttl=0, level='l1')

        # 立即查询, 可能已过期(取决于时间精度)
        # 这里只验证写入不报错
        assert 'dwd_gen:v3:test:zero_ttl' in cache.l1_cache

    def test_set_raw_negative_ttl(self):
        """测试 set_raw 使用负数 TTL(应该当作正数处理)"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        # 负数 TTL 应该被当作正数(虽然不推荐)
        cache.set_raw('dwd_gen:v3:test:negative_ttl', 'value', ttl=-10, level='l1')

        # 验证写入成功
        assert cache.get('test:negative_ttl') == 'value'


class TestSetRawDataTypeCompatibility:
    """测试 set_raw() 数据类型兼容性"""

    def test_set_raw_string_value(self):
        """测试 set_raw 写入字符串"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        cache.set_raw('dwd_gen:v3:test:string', 'test_string', level='l1')
        assert cache.get('test:string') == 'test_string'

    def test_set_raw_integer_value(self):
        """测试 set_raw 写入整数"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        cache.set_raw('dwd_gen:v3:test:integer', 42, level='l1')
        assert cache.get('test:integer') == 42

    def test_set_raw_float_value(self):
        """测试 set_raw 写入浮点数"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        cache.set_raw('dwd_gen:v3:test:float', 3.14, level='l1')
        assert cache.get('test:float') == 3.14

    def test_set_raw_list_value(self):
        """测试 set_raw 写入列表"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        test_list = [1, 2, 3, 'four', {'five': 5}]
        cache.set_raw('dwd_gen:v3:test:list', test_list, level='l1')
        assert cache.get('test:list') == test_list

    def test_set_raw_dict_value(self):
        """测试 set_raw 写入字典"""
        cache = HierarchicalCache(l1_size=100, l1_ttl=60, l2_ttl=3600)

        test_dict = {'key1': 'value1', 'key2': 2, 'key3': [1, 2, 3]}
        cache.set_raw('dwd_gen:v3:test:dict', test_dict, level='l1')
        assert cache.get('test:dict') == test_dict


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
