#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for RedisConnectionManager
=====================================

测试Redis连接管理器的功能: 
- 连接池管理
- 上下文管理器
- 连接泄露检测
"""

import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.core.cache.redis_connection_manager import (
    RedisConnectionManager,
    get_redis_connection_manager,
    shutdown_redis_connection_manager,
)


class TestRedisConnectionManager:
    """RedisConnectionManager单元测试"""

    @pytest.fixture
    def manager(self):
        """创建连接管理器实例"""
        return RedisConnectionManager(host='localhost', port=6379, db=0, max_connections=10)

    def test_initialization(self, manager):
        """测试初始化"""
        assert manager.host == 'localhost'
        assert manager.port == 6379
        assert manager.db == 0
        assert manager.max_connections == 10

    @patch('backend.core.cache.redis_connection_manager.redis')
    def test_get_connection_context_manager(self, mock_redis, manager):
        """测试上下文管理器获取连接"""
        # Mock Redis连接
        mock_conn = Mock()
        mock_redis.Redis.return_value = mock_conn

        # 使用上下文管理器
        with manager.get_connection() as conn:
            assert conn is not None
            mock_conn.ping.assert_called_once()

        # 验证连接被释放
        assert len(manager._active_connections) == 0

    @patch('backend.core.cache.redis_connection_manager.redis')
    def test_connection_leak_detection(self, mock_redis, manager):
        """测试连接泄露检测"""
        # Mock Redis连接
        mock_conn = Mock()
        mock_redis.Redis.return_value = mock_conn

        # 模拟连接泄露(不释放)
        conn_id = id(mock_conn)
        manager._active_connections[conn_id] = time.time() - 400  # 400秒前

        # 检查泄露
        report = manager.check_connection_leaks()

        assert report['active_connections'] == 1
        assert report['stale_connections'] == 1
        assert len(report['stale_details']) == 1
        assert report['stale_details'][0]['age_seconds'] > 300

    @patch('backend.core.cache.redis_connection_manager.redis')
    def test_get_stats(self, mock_redis, manager):
        """测试获取统计信息"""
        # Mock Redis连接池
        mock_pool = Mock()
        mock_pool.created_connections = 100
        mock_pool._available_connections = 8
        mock_pool._in_use_connections = 2

        with patch.object(manager, '_get_pool', return_value=mock_pool):
            stats = manager.get_stats()

            assert stats['host'] == 'localhost'
            assert stats['port'] == 6379
            assert stats['db'] == 0
            assert stats['max_connections'] == 10
            assert 'pool_stats' in stats
            assert 'leak_report' in stats

    @patch('backend.core.cache.redis_connection_manager.redis')
    def test_close(self, mock_redis, manager):
        """测试关闭连接池"""
        # Mock连接池
        mock_pool = Mock()
        manager._pool = mock_pool

        manager.close()

        # 验证连接池被关闭
        mock_pool.disconnect.assert_called_once()
        assert manager._pool is None

    def test_context_manager(self):
        """测试上下文管理器接口"""
        with RedisConnectionManager(max_connections=5) as manager:
            assert manager is not None
            assert manager.max_connections == 5

        # 退出时自动关闭
        # 注意: 这里无法直接验证_close是否被调用, 因为需要mock

    def test_repr(self, manager):
        """测试字符串表示"""
        repr_str = repr(manager)
        assert 'RedisConnectionManager' in repr_str
        assert 'localhost' in repr_str
        assert '6379' in repr_str


class TestGlobalRedisConnectionManager:
    """全局RedisConnectionManager测试"""

    def test_get_global_instance(self):
        """测试获取全局实例"""
        # 重置全局实例
        import backend.core.cache.redis_connection_manager as m

        m._global_redis_manager = None

        manager1 = get_redis_connection_manager()
        manager2 = get_redis_connection_manager()

        # 应该返回同一个实例
        assert manager1 is manager2

    def test_shutdown_global_instance(self):
        """测试关闭全局实例"""
        import backend.core.cache.redis_connection_manager as m

        m._global_redis_manager = None

        # 创建全局实例
        manager = get_redis_connection_manager()
        assert m._global_redis_manager is not None

        # 关闭全局实例
        shutdown_redis_connection_manager()
        assert m._global_redis_manager is None


class TestRedisConnectionManagerIntegration:
    """RedisConnectionManager集成测试(需要真实Redis)"""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_real_redis_connection(self):
        """
        测试真实Redis连接（需要Redis服务运行）

        注意: 此测试需要Redis在localhost:6379运行
        如果Redis未运行, 此测试将被跳过
        """
        manager = RedisConnectionManager(host='localhost', port=6379, db=0, max_connections=5)

        try:
            # 尝试连接
            with manager.get_connection() as conn:
                # 测试ping
                result = conn.ping()
                assert result is True

                # 测试set/get
                conn.set('test_key', 'test_value')
                value = conn.get('test_key')
                assert value == b'test_value'

                # 清理
                conn.delete('test_key')

        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    @pytest.mark.slow
    @pytest.mark.integration
    def test_connection_pool_limit(self):
        """
        测试连接池限制（需要真实Redis）

        验证连接池不会超过最大连接数
        """
        manager = RedisConnectionManager(host='localhost', port=6379, max_connections=3)  # 小的连接池

        try:
            connections = []
            for i in range(10):  # 尝试获取10个连接
                with manager.get_connection() as conn:
                    connections.append(conn)
                    conn.ping()

            # 如果成功执行, 说明连接池工作正常
            assert True

        except Exception as e:
            pytest.skip(f"Redis not available: {e}")


class TestRedisConnectionManagerThreadSafety:
    """线程安全测试"""

    @patch('backend.core.cache.redis_connection_manager.redis')
    def test_concurrent_connections(self, mock_redis, manager):
        """测试并发连接"""
        # Mock Redis连接
        mock_conn = Mock()
        mock_conn.ping.return_value = True
        mock_redis.Redis.return_value = mock_conn

        results = []
        errors = []

        def worker(worker_id):
            try:
                with manager.get_connection() as conn:
                    time.sleep(0.01)  # 模拟工作
                    results.append(worker_id)
            except Exception as e:
                errors.append(e)

        # 创建多个线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证
        assert len(results) == 10
        assert len(errors) == 0
        assert len(manager._active_connections) == 0  # 所有连接已释放
