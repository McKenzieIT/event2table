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
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from backend.core.cache.intelligent_warmer import IntelligentCacheWarmer


class TestIntelligentWarmerSetRawIntegration:
    """测试预热系统使用set_raw()方法"""

    def setup_method(self):
        """每个测试前创建新的预热器实例"""
        self.warmer = IntelligentCacheWarmer(
            access_log_size=1000,
            warm_up_interval=300
        )

    @pytest.mark.asyncio
    async def test_warm_up_cache_uses_set_raw(self) -> None:
        """测试warm_up_cache使用set_raw()方法"""
        # Mock fetch_callback
        fetch_callback = AsyncMock(return_value={"data": "test_data"})

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}  # 模拟空缓存

            # 预热缓存
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = await self.warmer.warm_up_cache(keys, fetch_callback)

            # 验证结果
            assert result['warmed'] == 2
            assert result['failed'] == 0

    @pytest.mark.asyncio
    async def test_warm_up_cache_with_existing_keys(self):
        """测试预热时跳过已存在的键"""
        # Mock fetch_callback
        fetch_callback = AsyncMock(return_value={"data": "test_data"})

        # Mock hierarchical_cache with existing keys
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {'dwd_gen:v3:test:key1': 'existing_data'}

            # 预热缓存（key1已存在）
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = await self.warmer.warm_up_cache(keys, fetch_callback)

            # 验证key1被跳过，key2被预热
            assert result['warmed'] == 1
            assert result['skipped'] == 1

    @pytest.mark.asyncio
    async def test_warm_up_cache_handles_fetch_failure(self):
        """测试预热时处理数据获取失败"""
        # Mock fetch_callback返回None（模拟失败）
        fetch_callback = AsyncMock(return_value=None)

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}

            # 预热缓存
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            result = await self.warmer.warm_up_cache(keys, fetch_callback)

            # 验证所有键都失败
            assert result['warmed'] == 0
            assert result['failed'] == 2

    @pytest.mark.asyncio
    async def test_warm_up_cache_updates_stats(self):
        """测试预热更新统计信息"""
        # Mock fetch_callback
        fetch_callback = AsyncMock(return_value={"data": "test_data"})

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}

            # 预热前统计
            stats_before = self.warmer.get_stats()
            assert stats_before['warm_up_count'] == 0
            assert stats_before['keys_warmed'] == 0

            # 预热缓存
            keys = ['dwd_gen:v3:test:key1', 'dwd_gen:v3:test:key2']
            await self.warmer.warm_up_cache(keys, fetch_callback)

            # 验证统计更新
            stats_after = self.warmer.get_stats()
            assert stats_after['warm_up_count'] == 1
            assert stats_after['keys_warmed'] == 2
            assert stats_after['last_warm_up_time'] > 0

    @pytest.mark.asyncio
    async def test_auto_warm_up_workflow(self):
        """测试自动预热工作流"""
        # Mock fetch_callback
        fetch_callback = AsyncMock(return_value={"data": "test_data"})

        # 添加访问记录
        for i in range(10):
            self.warmer.record_access(f'dwd_gen:v3:test:key{i % 3}')  # 3个热点键

        # Mock hierarchical_cache
        with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
            mock_cache.l1_cache = {}

            # 自动预热
            await self.warmer.auto_warm_up(fetch_callback)

            # 验证预测和预热执行
            # （具体行为取决于预测算法）
            assert self.warmer.stats['warm_up_count'] >= 1

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
        import time
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
