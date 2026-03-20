#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache System 单元测试

测试 backend.core.cache.cache_system 模块
"""

import pytest
from backend.core.cache.cache_system import CacheKeyBuilder


class TestCacheKeyBuilder:
    """测试 CacheKeyBuilder 类"""

    def test_build_no_params(self):
        """测试无参数构建缓存键"""
        key = CacheKeyBuilder.build('events.list')
        assert key == "dwd_gen:v3:events.list"

    def test_build_with_params(self):
        """测试带参数构建缓存键"""
        key = CacheKeyBuilder.build('events.list', game_id=1, page=1)
        assert key == "dwd_gen:v3:events.list:game_id:1:page:1"

    def test_build_param_ordering(self):
        """测试参数排序不影响缓存键"""
        key1 = CacheKeyBuilder.build('events.list', game_id=1, page=1)
        key2 = CacheKeyBuilder.build('events.list', page=1, game_id=1)
        assert key1 == key2

    def test_build_with_string_params(self):
        """测试字符串参数"""
        key = CacheKeyBuilder.build('games.detail', gid='10000147')
        assert key == "dwd_gen:v3:games.detail:gid:10000147"

    def test_build_pattern_no_params(self):
        """测试构建无参数的模式"""
        pattern = CacheKeyBuilder.build_pattern('events.list')
        assert 'events.list' in pattern
        assert '*' in pattern or pattern.endswith('events.list')

    def test_build_prefix_constant(self):
        """测试前缀常量"""
        assert CacheKeyBuilder.PREFIX == "dwd_gen:v3:"
        assert CacheKeyBuilder.VERSION == "3.0"

    def test_build_multiple_params(self):
        """测试多个参数"""
        key = CacheKeyBuilder.build('test', a=1, b=2, c=3, d=4)
        # 参数应该被排序
        assert ':a:1:b:2:c:3:d:4' in key

    def test_build_with_special_chars(self):
        """测试特殊字符参数"""
        key = CacheKeyBuilder.build('test', name='test-game')
        assert 'name:test-game' in key

    def test_build_consistency(self):
        """测试多次构建结果一致"""
        key1 = CacheKeyBuilder.build('events.list', game_id=123, page=5)
        key2 = CacheKeyBuilder.build('events.list', game_id=123, page=5)
        assert key1 == key2

    def test_build_different_params(self):
        """测试不同参数生成不同键"""
        key1 = CacheKeyBuilder.build('events.list', game_id=1)
        key2 = CacheKeyBuilder.build('events.list', game_id=2)
        assert key1 != key2

    def test_cache_key_prefix(self):
        """测试缓存键前缀格式"""
        key = CacheKeyBuilder.build('test')
        assert key.startswith('dwd_gen:v3:')

    def test_cache_key_namespace(self):
        """测试缓存键命名空间隔离"""
        key1 = CacheKeyBuilder.build('events.list', game_id=1)
        key2 = CacheKeyBuilder.build('games.detail', game_id=1)
        # 不同的模式应该生成不同的键
        assert key1 != key2
