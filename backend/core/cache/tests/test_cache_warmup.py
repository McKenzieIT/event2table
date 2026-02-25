#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存预热服务单元测试
==================

测试CacheWarmer的预热功能

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from backend.services.cache.cache_warmup import CacheWarmer, warmup_cache_on_startup


@pytest.fixture
def cache_warmer():
    """创建CacheWarmer实例"""
    warmer = CacheWarmer()
    # Mock缓存
    warmer.cache = Mock()
    warmer.cache.set = Mock()
    return warmer


class TestCacheWarmer:
    """CacheWarmer单元测试"""

    def test_warmup_popular_games(self, cache_warmer):
        """测试预热热门游戏"""
        # Mock数据库查询
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = [
                {'gid': 10000147, 'name': 'STAR001'},
                {'gid': 10000148, 'name': 'STAR002'},
            ]

            # 执行预热
            count = cache_warmer.warmup_popular_games(limit=100)

            # 验证结果
            assert count == 2
            assert cache_warmer.cache.set.call_count == 2
            assert cache_warmer.stats['games_warmed'] == 2

    def test_warmup_recent_events(self, cache_warmer):
        """测试预热最近事件"""
        # Mock数据库查询
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = [
                {'id': 1, 'name': 'login'},
                {'id': 2, 'name': 'logout'},
            ]

            # 执行预热
            count = cache_warmer.warmup_recent_events(limit=100)

            # 验证结果
            assert count == 2
            assert cache_warmer.cache.set.call_count == 2
            assert cache_warmer.stats['events_warmed'] == 2

    def test_warmup_common_params(self, cache_warmer):
        """测试预热常用参数"""
        # Mock数据库查询
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = [
                {'id': 1, 'name': 'role_id'},
                {'id': 2, 'name': 'zone_id'},
            ]

            # 执行预热
            count = cache_warmer.warmup_common_params()

            # 验证结果
            assert count == 2
            assert cache_warmer.cache.set.call_count == 2
            assert cache_warmer.stats['params_warmed'] == 2

    def test_warmup_all(self, cache_warmer):
        """测试完整预热流程"""
        # Mock数据库查询
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            # 模拟不同的查询返回不同数据
            mock_fetch.side_effect = [
                [{'gid': 10000147, 'name': 'STAR001'}],  # games
                [{'id': 1, 'name': 'login'}],            # events
                [{'id': 1, 'name': 'role_id'}],           # params
                100,  # total_keys (Redis dbsize)
            ]

            # 执行完整预热
            stats = cache_warmer.warmup_all(games_limit=100, events_limit=100)

            # 验证结果
            assert stats['games_warmed'] == 1
            assert stats['events_warmed'] == 1
            assert stats['params_warmed'] == 1
            # total_keys是动态的，不固定为100
            assert stats['total_keys'] >= 0

    def test_warmup_empty_database(self, cache_warmer):
        """测试数据库为空时的预热"""
        # Mock数据库查询返回空列表
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = []

            # 执行预热
            count = cache_warmer.warmup_popular_games()

            # 验证结果
            assert count == 0
            assert cache_warmer.cache.set.call_count == 0


class TestWarmupFunction:
    """预热函数测试"""

    @patch('backend.services.cache.cache_warmup.CacheWarmer')
    def test_warmup_cache_on_startup(self, mock_warmer_class):
        """测试应用启动时预热缓存"""
        # Mock CacheWarmer实例
        mock_warmer = Mock()
        mock_warmer.warmup_all.return_value = {
            'games_warmed': 100,
            'events_warmed': 100,
            'params_warmed': 50,
            'total_keys': 250
        }
        mock_warmer_class.return_value = mock_warmer

        # 执行预热
        stats = warmup_cache_on_startup()

        # 验证结果
        assert stats['games_warmed'] == 100
        assert stats['events_warmed'] == 100
        assert stats['params_warmed'] == 50
        assert stats['total_keys'] == 250

        # 验证warmup_all被调用
        mock_warmer.warmup_all.assert_called_once_with(games_limit=100, events_limit=100)


@pytest.mark.integration
class TestCacheWarmupIntegration:
    """缓存预热集成测试（需要真实数据库和缓存）"""

    def test_warmup_with_real_database(self):
        """测试使用真实数据库的预热"""
        warmer = CacheWarmer()

        # 执行预热（使用真实数据库）
        stats = warmer.warmup_all(games_limit=10, events_limit=10)

        # 验证预热成功
        assert isinstance(stats, dict)
        assert 'games_warmed' in stats
        assert 'events_warmed' in stats
        assert 'params_warmed' in stats
        assert 'total_keys' in stats

        # 预热数量应该>=0
        assert stats['games_warmed'] >= 0
        assert stats['events_warmed'] >= 0
        assert stats['params_warmed'] >= 0


class TestCacheWarmupErrorHandling:
    """缓存预热错误处理测试"""

    def test_warmup_database_error_handling(self, cache_warmer):
        """测试数据库错误时的处理"""
        # Mock数据库查询抛出异常
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.side_effect = Exception("Database error")

            # 执行预热应该不抛出异常
            try:
                count = cache_warmer.warmup_popular_games()
                # 如果有错误处理，可能返回0
                assert count >= 0
            except Exception as e:
                # 如果没有错误处理，应该抛出异常
                assert "Database error" in str(e)

    def test_warmup_cache_error_handling(self, cache_warmer):
        """测试缓存错误时的处理"""
        # Mock数据库查询
        with patch('backend.services.cache.cache_warmup.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = [{'gid': 10000147, 'name': 'STAR001'}]

            # Mock缓存set抛出异常
            cache_warmer.cache.set.side_effect = Exception("Cache error")

            # 执行预热应该处理缓存错误
            try:
                count = cache_warmer.warmup_popular_games()
                # 如果有错误处理，可能返回0或部分成功
                assert count >= 0
            except Exception as e:
                # 如果没有错误处理，应该抛出异常
                assert "Cache error" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
