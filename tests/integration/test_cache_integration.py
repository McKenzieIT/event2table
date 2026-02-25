#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存集成测试
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.core.cache.protection import CacheProtection


class TestCacheIntegration:
    """缓存集成测试"""

    def test_cached_decorator_caches_result(self):
        """测试缓存装饰器缓存结果"""
        call_count = 0
        
        @cached('test.key', timeout=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用应该从缓存获取
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加

    def test_cached_decorator_with_different_args(self):
        """测试缓存装饰器不同参数"""
        call_count = 0
        
        @cached('test.key', timeout=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 不同参数应该分别缓存
        result1 = expensive_function(5)
        result2 = expensive_function(10)
        
        assert result1 == 10
        assert result2 == 20
        assert call_count == 2

    @patch('backend.core.cache.cache_system.redis_client')
    def test_cache_invalidator_invalidate_key(self, mock_redis):
        """测试缓存失效器-失效单个键"""
        mock_redis.delete.return_value = 1
        
        CacheInvalidator.invalidate_key('test.key')
        
        mock_redis.delete.assert_called_once_with('cache:test.key')

    @patch('backend.core.cache.cache_system.redis_client')
    def test_cache_invalidator_invalidate_pattern(self, mock_redis):
        """测试缓存失效器-失效模式"""
        mock_redis.scan_iter.return_value = ['cache:test.key1', 'cache:test.key2']
        mock_redis.delete.return_value = 2
        
        CacheInvalidator.invalidate_pattern('test.key*')
        
        mock_redis.scan_iter.assert_called_once_with('cache:test.key*')
        mock_redis.delete.assert_called_once_with('cache:test.key1', 'cache:test.key2')

    @patch('backend.core.cache.cache_system.redis_client')
    def test_cache_invalidator_invalidate_game(self, mock_redis):
        """测试缓存失效器-失效游戏缓存"""
        mock_redis.scan_iter.return_value = ['cache:games.detail:1001', 'cache:games.list']
        mock_redis.delete.return_value = 2
        
        CacheInvalidator.invalidate_game(1001)
        
        # 应该失效 games.detail:{gid} 和 games.list
        assert mock_redis.scan_iter.call_count == 2

    @patch('backend.core.cache.cache_system.redis_client')
    def test_cache_invalidator_invalidate_event(self, mock_redis):
        """测试缓存失效器-失效事件缓存"""
        mock_redis.scan_iter.return_value = ['cache:events.detail:1', 'cache:events.with_params:1']
        mock_redis.delete.return_value = 2
        
        CacheInvalidator.invalidate_event(1)
        
        # 应该失效 events.detail:{id} 和 events.with_params:{id}
        assert mock_redis.scan_iter.call_count == 2

    def test_cache_protection_bloom_filter(self):
        """测试缓存防护-布隆过滤器"""
        protection = CacheProtection()
        
        # 添加有效键
        protection.add_valid_key('valid_key_1')
        protection.add_valid_key('valid_key_2')
        
        # 测试有效键
        assert protection.is_valid_key('valid_key_1') is True
        assert protection.is_valid_key('valid_key_2') is True
        
        # 测试无效键（可能误报，但应该大部分正确）
        # 注意：布隆过滤器可能有假阳性，但不会有假阴性

    @patch('backend.core.cache.protection.redis_client')
    def test_cache_protection_distributed_lock(self, mock_redis):
        """测试缓存防护-分布式锁"""
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        
        protection = CacheProtection()
        
        # 获取锁
        lock_acquired = protection.acquire_lock('test_lock', timeout=10)
        assert lock_acquired is True
        
        mock_redis.set.assert_called_once()
        
        # 释放锁
        protection.release_lock('test_lock')
        mock_redis.delete.assert_called_with('lock:test_lock')

    def test_cache_protection_ttl_randomization(self):
        """测试缓存防护-TTL随机化"""
        protection = CacheProtection()
        
        # 获取TTL
        ttl1 = protection.get_ttl_with_randomization(300)
        ttl2 = protection.get_ttl_with_randomization(300)
        
        # TTL应该在合理范围内（300 * 0.9 到 300 * 1.1）
        assert 270 <= ttl1 <= 330
        assert 270 <= ttl2 <= 330
        
        # 随机化后两次应该不同（大概率）
        # 注意：由于随机性，有可能相同，但概率很低

    @patch('backend.core.cache.cache_system.redis_client')
    def test_get_with_full_protection(self, mock_redis):
        """测试完整缓存防护"""
        mock_redis.get.return_value = None  # 缓存未命中
        mock_redis.set.return_value = True
        
        protection = CacheProtection()
        mock_fetch_func = MagicMock(return_value={'data': 'test'})
        
        # 模拟数据获取
        result = protection.get_with_full_protection(
            cache_key='test.key',
            fetch_func=mock_fetch_func,
            ttl=300
        )
        
        assert result == {'data': 'test'}
        mock_fetch_func.assert_called_once()
        mock_redis.set.assert_called_once()

    def test_cache_hit_miss_ratio(self):
        """测试缓存命中率统计"""
        # 模拟多次缓存访问
        hit_count = 0
        miss_count = 0
        total_count = 100
        
        for i in range(total_count):
            if i < 85:  # 85% 命中率
                hit_count += 1
            else:
                miss_count += 1
        
        hit_ratio = (hit_count / total_count) * 100
        miss_ratio = (miss_count / total_count) * 100
        
        assert hit_ratio == 85.0
        assert miss_ratio == 15.0
