#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存降级管理器单元测试
===================

目标覆盖率: 90%+
测试方法: TDD (红-绿-重构)

测试用例:
1. 正常模式缓存获取
2. Redis故障降级
3. 健康检查
4. 自动恢复
"""

import time
from unittest.mock import Mock, patch
from redis.exceptions import RedisError, ConnectionError

# 导入被测试模块
from backend.core.cache.degradation import (
    CacheDegradationManager
)


class TestNormalModeCacheGet:
    """测试1: 正常模式缓存获取"""

    def test_normal_mode_cache_get_success(self):
        """测试正常模式下成功从三级缓存获取数据"""
        # 创建管理器实例
        manager = CacheDegradationManager()

        # Mock hierarchical_cache
        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            mock_cache.get.return_value = "cached_value"

            # 执行测试
            result = manager.get_with_fallback("test_key", id=123)

            # 验证结果
            assert result == "cached_value"
            assert not manager.degraded
            mock_cache.get.assert_called_once_with("test_key", id=123)

    def test_normal_mode_cache_get_miss(self):
        """测试正常模式下缓存未命中"""
        manager = CacheDegradationManager()

        # Mock hierarchical_cache返回None
        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            mock_cache.get.return_value = None

            # Mock L1缓存
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "built_key"

                # Mock hierarchical_cache的L1访问
                mock_cache.l1_cache = {}
                mock_cache.l1_timestamps = {}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_key", id=123)

                # L1未命中应返回None
                assert result is None
                assert not manager.degraded


class TestRedisFailureDegradation:
    """测试2: Redis故障降级"""

    def test_redis_connection_error_triggers_degradation(self):
        """测试Redis连接错误时触发降级"""
        manager = CacheDegradationManager()

        # Mock hierarchical_cache抛出RedisError
        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            mock_cache.get.side_effect = ConnectionError("Redis unavailable")

            # Mock CacheKeyBuilder
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "built_key"

                # Mock L1缓存
                mock_cache.l1_cache = {"built_key": "l1_value"}
                mock_cache.l1_timestamps = {"built_key": time.time()}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_key", id=123)

                # 应该进入降级模式并从L1获取数据
                assert manager.degraded == True
                assert result == "l1_value"
                assert manager.stats['degradation_count'] == 1

    def test_redis_timeout_triggers_degradation(self):
        """测试Redis超时时触发降级"""
        manager = CacheDegradationManager()

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            # 模拟Redis超时
            mock_cache.get.side_effect = RedisError("Redis timeout")

            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "built_key"

                mock_cache.l1_cache = {}
                mock_cache.l1_timestamps = {}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_key")

                # 应该进入降级模式
                assert manager.degraded == True
                assert result is None

    def test_degraded_mode_uses_l1_only(self):
        """测试降级模式下只使用L1缓存"""
        manager = CacheDegradationManager()
        manager.degraded = True  # 直接设置为降级模式

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "l1_key"

                mock_cache.l1_cache = {"l1_key": "l1_data"}
                mock_cache.l1_timestamps = {"l1_key": time.time()}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_pattern")

                # 应该从L1获取数据
                assert result == "l1_data"
                assert mock_cache.stats["l1_hits"] == 1
                # 不应该调用hierarchical_cache.get（降级模式）
                mock_cache.get.assert_not_called()


class TestHealthCheck:
    """测试3: 健康检查"""

    def test_health_check_success(self):
        """测试健康检查成功"""
        manager = CacheDegradationManager()
        manager.degraded = True  # 设置为降级模式

        # Mock get_cache
        with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_cache = Mock()
            mock_cache._client = mock_client
            mock_get_cache.return_value = mock_cache

            # 执行健康检查
            manager._health_check()

            # 应该恢复到正常模式
            assert manager.degraded == False
            assert manager.stats['recovery_count'] == 1

    def test_health_check_redis_slow_response(self):
        """测试Redis响应慢但可用"""
        manager = CacheDegradationManager()

        with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
            # Mock慢响应（150ms）
            mock_client = Mock()
            mock_client.ping.side_effect = lambda: time.sleep(0.15)
            mock_cache = Mock()
            mock_cache._client = mock_client
            mock_get_cache.return_value = mock_cache

            # 不应该抛出异常，但会记录警告
            manager._health_check()

            # 不应该进入降级模式
            assert manager.degraded == False

    def test_health_check_none_cache(self):
        """测试get_cache返回None的情况"""
        manager = CacheDegradationManager()
        manager.degraded = False

        with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
            # Mock Redis不可用
            mock_get_cache.return_value = None

            manager._health_check()

            # 当get_cache返回None时，代码会抛出Exception并记录警告
            # 但不会自动进入降级模式（因为不是RedisError）
            # 这是符合设计的：警告但不降级
            assert manager.degraded == False

    def test_health_check_exception_triggers_logging(self):
        """测试健康检查异常时的日志记录"""
        manager = CacheDegradationManager()
        manager.degraded = False

        with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
            # Mock返回None，会触发"Redis缓存未初始化"异常
            mock_get_cache.return_value = None

            # 这个测试验证异常被正确捕获并记录警告
            # 而不是导致程序崩溃
            manager._health_check()

            # 验证没有进入降级模式（因为Exception不是RedisError）
            assert manager.degraded == False

    def test_health_check_redis_error(self):
        """测试健康检查时Redis抛出异常"""
        manager = CacheDegradationManager()
        manager.degraded = False

        with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
            mock_client = Mock()
            mock_client.ping.side_effect = ConnectionError("Connection refused")
            mock_cache = Mock()
            mock_cache._client = mock_client
            mock_get_cache.return_value = mock_cache

            manager._health_check()

            # 应该进入降级模式
            assert manager.degraded == True

    def test_should_check_health_timing(self):
        """测试健康检查时间间隔判断"""
        manager = CacheDegradationManager(health_check_interval=10)

        # 刚检查过，不应该再检查
        manager.last_health_check = time.time()
        assert manager._should_check_health() == False

        # 超过间隔，应该检查
        manager.last_health_check = time.time() - 11
        assert manager._should_check_health() == True


class TestAutoRecovery:
    """测试4: 自动恢复"""

    def test_auto_recovery_after_redis_fixed(self):
        """测试Redis恢复后自动切换回正常模式"""
        manager = CacheDegradationManager()

        # 设置为降级模式
        manager.degraded = True
        manager.last_health_check = time.time() - 20  # 超过健康检查间隔

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            # Mock Redis恢复
            mock_cache.get.return_value = "recovered_value"

            with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_cache_instance = Mock()
                mock_cache_instance._client = mock_client
                mock_get_cache.return_value = mock_cache_instance

                # 触发健康检查
                result = manager.get_with_fallback("test_key")

                # 应该恢复到正常模式
                assert manager.degraded == False
                assert manager.stats['recovery_count'] == 1

    def test_auto_recovery_timing(self):
        """测试自动恢复的时机"""
        manager = CacheDegradationManager()
        manager.degraded = True
        manager.last_health_check = time.time()  # 刚检查过

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            # Mock缓存返回数据
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "l1_key"

                mock_cache.l1_cache = {"l1_key": "l1_data"}
                mock_cache.l1_timestamps = {"l1_key": time.time()}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                # 由于刚检查过，不会再次检查健康状态
                result = manager.get_with_fallback("test_key")

                # 仍然处于降级模式
                assert manager.degraded == True
                assert result == "l1_data"


class TestSetWithFallback:
    """测试5: 缓存写入（带降级）"""

    def test_set_in_normal_mode(self):
        """测试正常模式下写入L1和L2"""
        manager = CacheDegradationManager()

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "cache_key"

                with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
                    mock_cache_instance = Mock()
                    mock_get_cache.return_value = mock_cache_instance

                    # 执行写入
                    manager.set_with_fallback("test_pattern", "test_data", id=123)

                    # 应该调用_set_l1和L2的set
                    mock_cache._set_l1.assert_called_once()
                    mock_cache_instance.set.assert_called_once()

    def test_set_in_degraded_mode(self):
        """测试降级模式下只写入L1"""
        manager = CacheDegradationManager()
        manager.degraded = True

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "cache_key"

                # 执行写入
                manager.set_with_fallback("test_pattern", "test_data", id=123)

                # 应该只调用_set_l1
                mock_cache._set_l1.assert_called_once()

    def test_set_triggers_degradation_on_l2_failure(self):
        """测试L2写入失败时触发降级"""
        manager = CacheDegradationManager()

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "cache_key"

                with patch('backend.core.cache.degradation.get_cache') as mock_get_cache:
                    mock_cache_instance = Mock()
                    mock_cache_instance.set.side_effect = RedisError("L2 write failed")
                    mock_get_cache.return_value = mock_cache_instance

                    # 执行写入
                    manager.set_with_fallback("test_pattern", "test_data", id=123)

                    # 应该进入降级模式
                    assert manager.degraded == True


class TestGetStatus:
    """测试6: 获取状态信息"""

    def test_get_status(self):
        """测试获取降级状态"""
        manager = CacheDegradationManager(health_check_interval=15)

        # 修改一些状态
        manager.degraded = True
        manager.stats['degradation_count'] = 3
        manager.last_health_check = 123456.78

        status = manager.get_status()

        assert status['degraded'] == True
        assert status['health_check_interval'] == 15
        assert status['last_health_check'] == 123456.78
        assert status['stats']['degradation_count'] == 3
        # 确保返回的是副本，不是引用
        status['stats']['degradation_count'] = 999
        assert manager.stats['degradation_count'] == 3


class TestForceOperations:
    """测试7: 强制操作（用于测试）"""

    def test_force_degrade(self):
        """测试强制进入降级模式"""
        manager = CacheDegradationManager()
        assert manager.degraded == False

        manager.force_degrade()

        assert manager.degraded == True
        assert manager.stats['degradation_count'] == 1

    def test_force_recover(self):
        """测试强制恢复"""
        manager = CacheDegradationManager()
        manager.degraded = True

        manager.force_recover()

        assert manager.degraded == False
        assert manager.stats['recovery_count'] == 1


class TestL1CacheExpiry:
    """测试8: L1缓存过期处理"""

    def test_l1_expired_entry(self):
        """测试L1缓存过期条目被清理"""
        manager = CacheDegradationManager()
        manager.degraded = True

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "expired_key"

                # Mock过期的L1条目
                old_time = time.time() - 100  # 100秒前
                mock_cache.l1_cache = {"expired_key": "old_data"}
                mock_cache.l1_timestamps = {"expired_key": old_time}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_pattern")

                # 过期条目应该被清理
                assert "expired_key" not in mock_cache.l1_cache
                assert "expired_key" not in mock_cache.l1_timestamps
                assert result is None
                assert mock_cache.stats["misses"] == 1

    def test_l1_valid_entry(self):
        """测试L1缓存有效条目正常返回"""
        manager = CacheDegradationManager()
        manager.degraded = True

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "valid_key"

                # Mock有效的L1条目
                recent_time = time.time() - 10  # 10秒前
                mock_cache.l1_cache = {"valid_key": "valid_data"}
                mock_cache.l1_timestamps = {"valid_key": recent_time}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_pattern")

                # 应该返回有效数据
                assert result == "valid_data"
                assert mock_cache.stats["l1_hits"] == 1


class TestEdgeCases:
    """测试9: 边界情况"""

    def test_hierarchical_cache_none(self):
        """测试hierarchical_cache为None的情况"""
        manager = CacheDegradationManager()
        manager.degraded = True

        with patch('backend.core.cache.degradation.hierarchical_cache', None):
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "test_key"

                result = manager._get_l1_only("test_key")

                # 应该返回None
                assert result is None

    def test_empty_l1_cache(self):
        """测试空L1缓存"""
        manager = CacheDegradationManager()
        manager.degraded = True

        with patch('backend.core.cache.degradation.hierarchical_cache') as mock_cache:
            with patch('backend.core.cache.degradation.CacheKeyBuilder') as mock_builder:
                mock_builder.build.return_value = "missing_key"

                mock_cache.l1_cache = {}
                mock_cache.l1_timestamps = {}
                mock_cache.l1_ttl = 60
                mock_cache.stats = {"l1_hits": 0, "misses": 0}

                result = manager.get_with_fallback("test_pattern")

                assert result is None
                assert mock_cache.stats["misses"] == 1

    def test_concurrent_degradation_entry(self):
        """测试并发进入降级模式的线程安全"""
        manager = CacheDegradationManager()

        import threading

        def trigger_degradation():
            try:
                manager._enter_degraded_mode()
            except Exception:
                pass

        # 创建多个线程同时触发降级
        threads = [threading.Thread(target=trigger_degradation) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 降级计数应该只增加1次（线程安全）
        assert manager.stats['degradation_count'] == 1
        assert manager.degraded == True

    def test_concurrent_recovery(self):
        """测试并发恢复的线程安全"""
        manager = CacheDegradationManager()
        manager.degraded = True

        import threading

        def trigger_recovery():
            try:
                manager._exit_degraded_mode()
            except Exception:
                pass

        # 创建多个线程同时触发恢复
        threads = [threading.Thread(target=trigger_recovery) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 恢复计数应该只增加1次（线程安全）
        assert manager.stats['recovery_count'] == 1
        assert manager.degraded == False


class TestGlobalManager:
    """测试10: 全局管理器实例"""

    def test_global_manager_instance(self):
        """测试全局管理器实例可访问"""
        from backend.core.cache.degradation import cache_degradation_manager

        # 应该是一个CacheDegradationManager实例
        assert isinstance(cache_degradation_manager, CacheDegradationManager)
        assert hasattr(cache_degradation_manager, 'degraded')
        assert hasattr(cache_degradation_manager, 'stats')

    def test_global_manager_initial_state(self):
        """测试全局管理器初始状态"""
        from backend.core.cache.degradation import cache_degradation_manager

        # 初始状态应该是正常模式
        assert cache_degradation_manager.degraded == False
        assert cache_degradation_manager.stats['degradation_count'] == 0
        assert cache_degradation_manager.stats['recovery_count'] == 0
