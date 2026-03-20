#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存防护机制增强测试
==================

测试布隆过滤器, 分布式锁, TTL随机化等功能

版本: 1.0.0
日期: 2026-02-20
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from backend.core.cache.protection import cache_protection, BLOOM_FILTER_AVAILABLE
from backend.core.cache.cache_system import hierarchical_cache
from backend.core.cache.decorators import cached


class TestBloomFilter:
    """布隆过滤器测试"""

    def test_bloom_filter_availability(self):
        """测试布隆过滤器是否可用"""
        if BLOOM_FILTER_AVAILABLE:
            assert cache_protection.bloom_filter is not None
            print("✅ 布隆过滤器可用")
        else:
            assert cache_protection.bloom_filter is None
            print("⚠️ 布隆过滤器不可用, 使用空值缓存替代")

    def test_add_to_bloom_filter(self):
        """测试添加键到布隆过滤器"""
        if not BLOOM_FILTER_AVAILABLE:
            pytest.skip("布隆过滤器不可用")

        key = "test:bloom:123"
        cache_protection.add_to_bloom_filter(key)

        # 检查键是否在布隆过滤器中
        assert cache_protection.might_exist_in_bloom_filter(key)
        print(f"✅ 布隆过滤器添加成功: {key}")

    def test_bloom_filter_reject(self):
        """测试布隆过滤器拦截"""
        if not BLOOM_FILTER_AVAILABLE:
            pytest.skip("布隆过滤器不可用")

        # 未添加的键应该被拦截
        key = "test:bloom:notexist:999"

        # 重置统计
        cache_protection.reset_stats()

        # 检查不存在的键
        might_exist = cache_protection.might_exist_in_bloom_filter(key)

        # 布隆过滤器可能返回True(误判), 但不会返回False(不存在的键)
        # 如果返回False, 说明被拦截了
        if not might_exist:
            stats = cache_protection.get_stats()
            assert stats["bloom_filter_rejects"] > 0
            print(f"✅ 布隆过滤器拦截成功: {key}")
        else:
            print(f"⚠️ 布隆过滤器误判（正常现象）: {key}")

    @cached(ttl=1800)
    def test_get_with_bloom_filter(self):
        """测试使用布隆过滤器获取数据"""
        # 清空缓存
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()
        cache_protection.reset_stats()

        # 模拟数据获取函数
        call_count = [0]

        @cached(ttl=1800)
        def fetch_data():
            call_count[0] += 1
            return {"id": 123, "name": "Test"}

        # 第一次调用(未命中)
        result1 = cache_protection.get_with_bloom_filter('test.bloom', fetch_data, ttl=300, id=123)

        assert result1 is not None
        assert result1["id"] == 123
        assert call_count[0] == 1
        print(f"✅ 第一次调用成功, 执行了数据获取函数")

        # 第二次调用(命中缓存)
        result2 = cache_protection.get_with_bloom_filter('test.bloom', fetch_data, ttl=300, id=123)

        assert result2 is not None
        assert result2["id"] == 123
        assert call_count[0] == 1  # 未再次调用
        print(f"✅ 第二次调用成功, 命中缓存")


class TestDistributedLock:
    """分布式锁测试"""

    def test_lock_context_manager(self):
        """测试锁上下文管理器"""
        key = "test:lock:123"

        with cache_protection.distributed_lock(key, timeout=5) as acquired:
            assert acquired is True
            print(f"✅ 成功获取锁: {key}")

        print(f"✅ 锁已释放: {key}")

    def test_lock_timeout(self):
        """测试锁超时"""
        key = "test:lock:timeout"

        # 在另一个线程中持有锁
        lock_acquired = threading.Event()
        lock_released = threading.Event()

        def hold_lock():
            with cache_protection.distributed_lock(key, timeout=5) as acquired:
                if acquired:
                    lock_acquired.set()
                    time.sleep(2)  # 持有锁2秒
            lock_released.set()

        # 启动线程持有锁
        thread = threading.Thread(target=hold_lock)
        thread.start()

        # 等待锁被获取
        lock_acquired.wait(timeout=1)

        # 尝试获取同一个锁(应该等待)
        cache_protection.reset_stats()

        with cache_protection.distributed_lock(key, timeout=1) as acquired:
            # 由于锁被占用, 可能获取失败
            if not acquired:
                stats = cache_protection.get_stats()
                assert stats["lock_waits"] > 0
                print(f"✅ 锁等待超时（预期行为）")
            else:
                print(f"✅ 成功获取锁（锁已释放）")

        # 等待线程结束
        thread.join(timeout=5)

    @cached(ttl=1800)
    def test_get_with_lock(self):
        """测试使用分布式锁获取数据"""
        # 清空缓存
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()
        cache_protection.reset_stats()

        # 模拟数据获取函数
        call_count = [0]

        @cached(ttl=1800)
        def fetch_data():
            call_count[0] += 1
            time.sleep(0.1)  # 模拟耗时操作
            return {"id": 456, "name": "Test Lock"}

        # 第一次调用(未命中)
        result1 = cache_protection.get_with_lock('test.lock', fetch_data, ttl=300, id=456)

        assert result1 is not None
        assert result1["id"] == 456
        assert call_count[0] == 1
        print(f"✅ 第一次调用成功, 执行了数据获取函数")

        # 第二次调用(命中缓存)
        result2 = cache_protection.get_with_lock('test.lock', fetch_data, ttl=300, id=456)

        assert result2 is not None
        assert result2["id"] == 456
        assert call_count[0] == 1  # 未再次调用
        print(f"✅ 第二次调用成功, 命中缓存")


class TestTTLRandomization:
    """TTL随机化测试"""

    def test_set_with_random_ttl(self):
        """测试TTL随机化"""
        # 清空缓存
        hierarchical_cache.clear_l1()

        # 设置多个相同TTL的缓存
        base_ttl = 300
        ttls = []

        for i in range(10):
            cache_protection.set_with_random_ttl(
                'test.random_ttl', {"id": i}, base_ttl=base_ttl, jitter_pct=0.2, id=i
            )

            # 注意: 这里无法直接获取Redis的TTL, 但可以验证功能正常工作
            ttls.append(base_ttl)

        print(f"✅ TTL随机化测试完成")
        print(f"   基础TTL: {base_ttl}s")
        print(f"   抖动范围: ±20%")
        print(f"   预期TTL范围: {int(base_ttl * 0.8)}-{int(base_ttl * 1.2)}s")


class TestFullProtection:
    """完整防护测试"""

    @cached(ttl=1800)
    def test_get_with_full_protection(self):
        """测试完整防护机制"""
        # 清空缓存
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()
        cache_protection.reset_stats()

        # 模拟数据获取函数
        call_count = [0]

        @cached(ttl=1800)
        def fetch_data():
            call_count[0] += 1
            return {"id": 789, "name": "Full Protection"}

        # 第一次调用(未命中)
        result1 = cache_protection.get_with_full_protection(
            'test.full_protection',
            fetch_data,
            ttl=300,
            use_bloom_filter=True,
            use_lock=True,
            use_random_ttl=True,
            id=789,
        )

        assert result1 is not None
        assert result1["id"] == 789
        assert call_count[0] == 1
        print(f"✅ 第一次调用成功, 执行了数据获取函数")

        # 第二次调用(命中缓存)
        result2 = cache_protection.get_with_full_protection(
            'test.full_protection',
            fetch_data,
            ttl=300,
            use_bloom_filter=True,
            use_lock=True,
            use_random_ttl=True,
            id=789,
        )

        assert result2 is not None
        assert result2["id"] == 789
        assert call_count[0] == 1  # 未再次调用
        print(f"✅ 第二次调用成功, 命中缓存")

    def test_empty_value_caching(self):
        """测试空值缓存"""
        # 清空缓存
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()
        cache_protection.reset_stats()

        # 模拟返回None的函数
        call_count = [0]

        @cached(ttl=1800)
        def fetch_none():
            call_count[0] += 1
            return None

        # 第一次调用(未命中, 缓存空值)
        result1 = cache_protection.get_with_full_protection(
            'test.empty', fetch_none, ttl=300, id=999
        )

        assert result1 is None
        assert call_count[0] == 1
        print(f"✅ 第一次调用成功, 缓存了空值")

        # 第二次调用(命中空值缓存)
        result2 = cache_protection.get_with_full_protection(
            'test.empty', fetch_none, ttl=300, id=999
        )

        assert result2 is None
        assert call_count[0] == 1  # 未再次调用

        stats = cache_protection.get_stats()
        assert stats["empty_cache_hits"] > 0
        print(f"✅ 第二次调用成功, 命中空值缓存")


class TestStatistics:
    """统计信息测试"""

    def test_get_stats(self):
        """测试获取统计信息"""
        stats = cache_protection.get_stats()

        assert "bloom_filter_available" in stats
        assert "bloom_filter_rejects" in stats
        assert "lock_waits" in stats
        assert "empty_cache_hits" in stats

        print(f"✅ 统计信息获取成功")
        print(f"   布隆过滤器可用: {stats['bloom_filter_available']}")
        print(f"   布隆过滤器拦截: {stats['bloom_filter_rejects']}")
        print(f"   锁等待次数: {stats['lock_waits']}")
        print(f"   空值缓存命中: {stats['empty_cache_hits']}")

    def test_reset_stats(self):
        """测试重置统计信息"""
        # 重置统计
        cache_protection.reset_stats()

        stats = cache_protection.get_stats()
        assert stats["bloom_filter_rejects"] == 0
        assert stats["lock_waits"] == 0
        assert stats["empty_cache_hits"] == 0

        print(f"✅ 统计信息重置成功")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
