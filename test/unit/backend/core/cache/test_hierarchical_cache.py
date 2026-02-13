#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级分层缓存系统测试
==================
测试L1/L2/L3缓存功能、LRU淘汰、缓存回填等特性

版本: 1.0.0
日期: 2026-01-20
"""

import sys
import time
import unittest
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.cache.cache_hierarchical import (
    HierarchicalCache,
    cached_hierarchical,
    hierarchical_cache,
)
from unittest.mock import MagicMock, patch


class TestHierarchicalCache(unittest.TestCase):
    """测试三级分层缓存"""

    def setUp(self):
        """每个测试前创建新实例"""
        self.cache = HierarchicalCache(l1_size=5, l1_ttl=1, l2_ttl=10)

    def tearDown(self):
        """每个测试后清理"""
        self.cache.clear_l1()

    def test_l1_cache_set_and_get(self):
        """测试L1缓存的set和get"""
        # 设置缓存
        self.cache.set("test.key", {"data": "value"}, id=1)

        # 从L1获取
        result = self.cache.get("test.key", id=1)

        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "value")

    def test_l1_cache_hit(self):
        """测试L1缓存命中"""
        self.cache.set("test.key", {"data": "value"}, id=1)
        result = self.cache.get("test.key", id=1)

        stats = self.cache.get_stats()
        self.assertEqual(stats["l1_hits"], 1)
        self.assertEqual(stats["l2_hits"], 0)
        self.assertEqual(stats["misses"], 0)

    def test_l1_cache_expiration(self):
        """测试L1缓存过期"""
        # 设置TTL为1秒
        self.cache.set("test.key", {"data": "value"}, id=1)

        # 立即获取，应该命中
        result = self.cache.get("test.key", id=1)
        self.assertIsNotNone(result)

        # 等待2秒后获取，应该过期
        time.sleep(2)
        result = self.cache.get("test.key", id=1)
        self.assertIsNone(result)

    def test_l1_lru_eviction(self):
        """测试L1缓存的LRU淘汰"""
        # L1容量为5，写入6个条目
        for i in range(6):
            self.cache.set("test.key", {"data": f"value{i}"}, id=i)

        # 验证L1只有5个条目
        stats = self.cache.get_stats()
        self.assertEqual(stats["l1_size"], 5)
        self.assertEqual(stats["l1_evictions"], 1)

    def test_l2_cache_miss(self):
        """测试L2缓存未命中"""
        # Mock L2缓存（Redis）
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        with patch("backend.core.cache.cache_hierarchical.get_cache", return_value=mock_cache):
            result = self.cache.get("test.key", id=999)

        # 应该返回None
        self.assertIsNone(result)

        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 1)

    def test_l2_cache_hit_with_l1_warmup(self):
        """测试L2缓存命中后回填L1"""
        # Mock L2缓存返回数据
        mock_cache = MagicMock()
        mock_cache.get.return_value = {"data": "value_from_l2"}

        with patch("backend.core.cache.cache_hierarchical.get_cache", return_value=mock_cache):
            result = self.cache.get("test.key", id=1)

        # 应该返回L2的数据
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "value_from_l2")

        # 验证L2命中
        stats = self.cache.get_stats()
        self.assertEqual(stats["l2_hits"], 1)

        # 验证L1被回填
        self.assertEqual(stats["l1_size"], 1)

    def test_cache_invalidation(self):
        """测试缓存失效"""
        # 设置缓存
        self.cache.set("test.key", {"data": "value"}, id=1)

        # 失效缓存
        self.cache.invalidate("test.key", id=1)

        # 再次获取应该未命中
        result = self.cache.get("test.key", id=1)
        self.assertIsNone(result)

    def test_pattern_invalidation(self):
        """测试模式失效"""
        # 设置多个缓存
        for i in range(3):
            self.cache.set("test.key", {"data": f"value{i}"}, game_id=1, event_id=i)

        # 失效所有game_id=1的缓存
        count = self.cache.invalidate_pattern("test.key", game_id=1)

        # 应该失效3个键
        self.assertEqual(count, 3)
        self.assertEqual(self.cache.get_stats()["l1_size"], 0)

    def test_decorator_cached_hierarchical(self):
        """测试cached_hierarchical装饰器"""
        call_count = 0

        @cached_hierarchical("test.function")
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用，执行函数
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)

        # 第二次调用，从缓存获取
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # 不应该再次调用

    def test_stats_reset(self):
        """测试统计信息重置"""
        # 生成一些统计数据
        self.cache.set("test.key", {"data": "value"}, id=1)
        self.cache.get("test.key", id=1)
        self.cache.get("test.key", id=999)

        # 重置统计
        self.cache.reset_stats()

        # 验证统计已清零
        stats = self.cache.get_stats()
        self.assertEqual(stats["l1_hits"], 0)
        self.assertEqual(stats["l2_hits"], 0)
        self.assertEqual(stats["misses"], 0)
        self.assertEqual(stats["l1_evictions"], 0)


class TestCacheWarmer(unittest.TestCase):
    """测试缓存预热"""

    def setUp(self):
        """Mock数据库查询"""
        self.mock_games = [
            {"id": 1, "name": "Game 1", "gid": 100001},
            {"id": 2, "name": "Game 2", "gid": 100002},
        ]
        self.mock_events = [
            {"id": 1, "name": "Event 1", "game_id": 1},
            {"id": 2, "name": "Event 2", "game_id": 1},
        ]

        # 清空缓存统计
        from backend.core.cache.cache_warmer import cache_warmer

        cache_warmer.reset_stats()

    @patch("backend.core.cache.cache_warmer.fetch_all_as_dict")
    def test_warmup_games(self, mock_fetch):
        """测试游戏列表预热"""
        from backend.core.cache.cache_warmer import cache_warmer

        # Mock数据库返回
        mock_fetch.return_value = self.mock_games

        # 执行预热
        cache_warmer.warmup_games()

        # 验证预热统计
        stats = cache_warmer.get_warmup_stats()
        self.assertEqual(stats["warmed_games"], 2)

    @patch("backend.core.cache.cache_warmer.fetch_all_as_dict")
    def test_warmup_hot_events(self, mock_fetch):
        """测试热门事件预热"""
        from backend.core.cache.cache_warmer import cache_warmer

        # Mock数据库返回
        mock_fetch.return_value = self.mock_events

        # 执行预热
        cache_warmer.warmup_hot_events(limit=100)

        # 验证预热统计
        stats = cache_warmer.get_warmup_stats()
        self.assertEqual(stats["warmed_events"], 2)

    @patch("backend.core.cache.cache_warmer.fetch_all_as_dict")
    def test_periodic_warmup_thread(self, mock_fetch):
        """测试定时预热线程创建"""
        from backend.core.cache.cache_warmer import cache_warmer
        import time

        # Mock数据库返回
        mock_fetch.return_value = []

        # 启动定时预热（短间隔用于测试）
        cache_warmer.start_periodic_warmup(interval_hours=0.001)  # ~3.6秒

        # 验证线程已启动
        self.assertIsNotNone(cache_warmer._warming_thread)
        self.assertTrue(cache_warmer._warming_thread.is_alive())

        # 等待一小段时间让线程运行
        time.sleep(0.5)

        # 停止定时预热
        cache_warmer.stop_periodic_warmup()

        # 等待线程结束
        cache_warmer._warming_thread.join(timeout=2)

        # 验证线程已停止
        self.assertFalse(cache_warmer._warming_thread.is_alive())


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "=" * 60)
    print("三级分层缓存性能测试")
    print("=" * 60)

    cache = HierarchicalCache(l1_size=1000, l1_ttl=60, l2_ttl=3600)

    # 测试L1缓存性能
    print("\n测试1: L1缓存性能")
    start_time = time.time()
    for i in range(1000):
        cache.set("test.key", {"data": f"value{i}"}, id=i)
    l1_set_time = time.time() - start_time
    print(f"  L1写入1000条: {l1_set_time:.4f}秒")

    start_time = time.time()
    for i in range(1000):
        cache.get("test.key", id=i)
    l1_get_time = time.time() - start_time
    print(f"  L1读取1000次: {l1_get_time:.4f}秒")
    print(f"  平均响应时间: {l1_get_time / 1000 * 1000:.2f}毫秒")

    # 显示统计
    stats = cache.get_stats()
    print(f"\n缓存统计:")
    print(f"  L1大小: {stats['l1_size']}/{stats['l1_capacity']}")
    print(f"  L1命中率: 100%")
    print(f"  L1淘汰数: {stats['l1_evictions']}")


if __name__ == "__main__":
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[""], verbosity=2, exit=False)

    # 运行性能测试
    run_performance_tests()
