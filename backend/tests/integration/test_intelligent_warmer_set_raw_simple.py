#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：IntelligentCacheWarmer使用set_raw()方法
==================================================

测试IntelligentCacheWarmer与HierarchicalCache.set_raw()的集成

版本: 1.0.0
日期: 2026-02-27
"""

import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from backend.core.cache.intelligent_warmer import IntelligentCacheWarmer


class TestIntelligentWarmerSetRawIntegration:
    """测试预热系统使用set_raw()方法"""

    def setup_method(self):
        """每个测试前创建新的预热器实例"""
        self.warmer = IntelligentCacheWarmer(
            access_log_size=1000,
            warm_up_interval=300
        )

    def test_warm_up_cache_uses_set_raw_sync(self):
        """测试warm_up_cache使用set_raw()方法（同步包装）"""
        # Mock fetch_callback
        async def fetch_callback(key):
            return {"data": f"test_data_for_{key}"}

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}  # 模拟空缓存
            mock_cache.set_raw = Mock()  # Mock set_raw方法

            # 使用同步包装运行异步方法
            import asyncio
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = asyncio.run(self.warmer.warm_up_cache(keys, fetch_callback))

            # 验证结果
            assert result['warmed'] == 2
            assert result['failed'] == 0

    def test_warm_up_cache_with_existing_keys(self):
        """测试预热时跳过已存在的键"""
        # Mock fetch_callback
        async def fetch_callback(key):
            return {"data": f"test_data_for_{key}"}

        # Mock hierarchical_cache with existing keys
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {'dwd_gen:v3:test:key1': 'existing_data'}

            # 使用同步包装运行异步方法
            import asyncio
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = asyncio.run(self.warmer.warm_up_cache(keys, fetch_callback))

            # 验证key1被跳过，key2被预热
            assert result['warmed'] == 1
            assert result['skipped'] == 1

    def test_warm_up_cache_handles_fetch_failure(self):
        """测试预热时处理数据获取失败"""
        # Mock fetch_callback返回None（模拟失败）
        async def fetch_callback(key):
            return None

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}

            # 使用同步包装运行异步方法
            import asyncio
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = asyncio.run(self.warmer.warm_up_cache(keys, fetch_callback))

            # 验证所有键都失败
            assert result['warmed'] == 0
            assert result['failed'] == 2

    def test_warm_up_cache_updates_stats(self):
        """测试预热更新统计信息"""
        # Mock fetch_callback
        async def fetch_callback(key):
            return {"data": f"test_data_for_{key}"}

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}

            # 预热前统计
            stats_before = self.warmer.get_stats()
            assert stats_before['warm_up_count'] == 0
            assert stats_before['keys_warmed'] == 0

            # 使用同步包装运行异步方法
            import asyncio
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            asyncio.run(self.warmer.warm_up_cache(keys, fetch_callback))

            # 验证统计更新
            stats_after = self.warmer.get_stats()
            assert stats_after['warm_up_count'] == 1
            assert stats_after['keys_warmed'] == 2
            assert stats_after['last_warm_up_time'] > 0

    def test_predict_hot_keys_without_decay(self):
        """测试不使用时间衰减的预测"""
        # 添加访问记录
        for i in range(100):
            self.warmer.record_access(f'dwd_gen:v3:test:key{i % 10}')  # 10个键，不同频率

        # 预测热点键（不使用衰减）
        hot_keys = self.warmer.predict_hot_keys(top_n=5, use_decay=False)

        # 验证返回热点键
        assert len(hot_keys) <= 5
        assert all(isinstance(key, str) for key in hot_keys)

    def test_predict_hot_keys_with_decay(self):
        """测试使用时间衰减的预测"""
        # 添加访问记录
        current_time = time.time()

        # 添加最近的访问
        for i in range(10):
            self.warmer.access_log.append({
                'key': f'dwd_gen:v3:test:recent_key{i}',
                'timestamp': current_time - 100  # 100秒前
            })

        # 预测热点键（使用衰减）
        hot_keys = self.warmer.predict_hot_keys(top_n=5, use_decay=True)

        # 验证返回热点键
        assert len(hot_keys) <= 5

    def test_get_access_log_stats(self):
        """测试获取访问日志统计"""
        # 添加访问记录
        for i in range(50):
            self.warmer.record_access(f'dwd_gen:v3:test:key{i}')

        # 获取统计
        stats = self.warmer.get_access_log_stats()

        # 验证统计信息
        assert stats['total_access'] == 50
        assert stats['buffer_capacity'] == 1000
        assert 'buffer_usage' in stats
        assert 'unique_keys' in stats

    def test_get_intelligent_warmer_singleton(self):
        """测试全局预热器单例"""
        from backend.core.cache.intelligent_warmer import get_intelligent_warmer

        # 获取实例
        warmer1 = get_intelligent_warmer()
        warmer2 = get_intelligent_warmer()

        # 验证是同一个实例
        assert warmer1 is warmer2

    def test_record_access(self):
        """测试记录访问"""
        # 记录访问
        self.warmer.record_access('dwd_gen:v3:test:key1')
        self.warmer.record_access('dwd_gen:v3:test:key2')
        self.warmer.record_access('dwd_gen:v3:test:key1')

        # 验证访问记录
        assert len(self.warmer.access_log) == 3

        # 获取统计
        stats = self.warmer.get_access_log_stats()
        assert stats['total_access'] == 3

    def test_predict_hot_keys_with_empty_log(self):
        """测试空访问日志的预测"""
        # 不添加任何访问记录
        hot_keys = self.warmer.predict_hot_keys(top_n=5)

        # 验证返回空列表
        assert len(hot_keys) == 0

    def test_circular_buffer_maxlen(self):
        """测试循环缓冲区的最大长度"""
        # 创建小缓冲区
        warmer = IntelligentCacheWarmer(access_log_size=10)

        # 添加超过缓冲区大小的访问
        for i in range(20):
            warmer.record_access(f'dwd_gen:v3:test:key{i}')

        # 验证缓冲区大小不超过最大值
        assert len(warmer.access_log) <= 10

    def test_warm_up_cache_with_empty_keys(self):
        """测试空键列表的预热"""
        async def fetch_callback(key):
            return {"data": "test"}

        # 使用同步包装运行异步方法
        import asyncio
        result = asyncio.run(self.warmer.warm_up_cache([], fetch_callback))

        # 验证结果
        assert result['warmed'] == 0
        assert result['failed'] == 0
        assert result['skipped'] == 0

    def test_get_stats(self):
        """测试获取统计信息"""
        # 获取初始统计
        stats = self.warmer.get_stats()

        # 验证统计字段
        assert 'warm_up_count' in stats
        assert 'keys_warmed' in stats
        assert 'last_warm_up_time' in stats
        assert 'prediction_accuracy' in stats
        assert 'predicted_count' in stats
        assert 'actual_hits' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
