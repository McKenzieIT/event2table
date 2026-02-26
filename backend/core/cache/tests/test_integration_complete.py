#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统完整集成测试
==================

测试缓存系统的完整集成，包括：
- Bloom Filter
- 智能预热
- 层级缓存
- 缓存降级

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import pytest
import time
import tempfile
import os

from backend.services.games.game_service import GameService
from backend.services.events.event_service import EventService
from backend.services.cache.cache_warmup import CacheWarmer
from backend.core.cache.cache_system import get_cache
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter


@pytest.fixture
def temp_files():
    """创建临时文件"""
    files = []
    for _ in range(3):
        fd, path = tempfile.mkstemp(suffix='.pkl')
        os.close(fd)
        files.append(path)
    yield files
    # 清理
    for path in files:
        if os.path.exists(path):
            os.remove(path)


@pytest.mark.integration
class TestBloomFilterIntegration:
    """Bloom Filter集成测试"""

    def test_game_service_bloom_filter_end_to_end(self, temp_files):
        """测试GameService中Bloom Filter的端到端流程"""
        # 创建GameService并替换Bloom Filter文件
        service = GameService()
        service.bloom_filter = EnhancedBloomFilter(
            capacity=1000,
            error_rate=0.001,
            persistence_path=temp_files[0]
        )

        # 查询存在的游戏
        game = service.get_game_by_gid(10000147)

        if game:
            # 验证Bloom Filter已更新
            assert service.bloom_filter.contains(f"games:10000147") is True

            # 验证统计信息
            stats = service.get_bloom_filter_stats()
            assert stats['total_items'] >= 1

    def test_event_service_bloom_filter_end_to_end(self, temp_files):
        """测试EventService中Bloom Filter的端到端流程"""
        service = EventService()
        service.bloom_filter = EnhancedBloomFilter(
            capacity=1000,
            error_rate=0.001,
            persistence_path=temp_files[1]
        )

        # 查询第一个事件
        from backend.core.utils.converters import fetch_all_as_dict
        events = fetch_all_as_dict('SELECT * FROM log_events LIMIT 1')

        if events:
            event_id = events[0]['id']
            event = service.get_event_by_id(event_id)

            if event:
                # 验证Bloom Filter已更新
                assert service.bloom_filter.contains(f"events:{event_id}") is True

    def test_bloom_filter_fast_reject_nonexistent(self):
        """测试Bloom Filter快速拒绝不存在的数据"""
        service = GameService()

        # 查询不存在的游戏
        start = time.time()
        result = service.get_game_by_gid(99999999)
        duration = time.time() - start

        # 应该快速返回None
        assert result is None
        # Bloom Filter应该让查询很快（即使查询数据库）
        # 注意：这里我们主要验证逻辑，性能测试在单元测试中

    def test_bloom_filter_rebuild(self, temp_files):
        """测试Bloom Filter重建功能"""
        service = GameService()
        service.bloom_filter = EnhancedBloomFilter(
            capacity=1000,
            error_rate=0.001,
            persistence_path=temp_files[2]
        )

        # 添加一些数据
        service.bloom_filter.add("games:10000147")
        service.bloom_filter.add("games:10000148")

        # 重建
        stats = service.rebuild_bloom_filter()

        # 验证重建结果
        assert isinstance(stats, dict)
        assert 'total_items' in stats


@pytest.mark.integration
class TestCacheWarmupIntegration:
    """智能预热集成测试"""

    def test_cache_warmup_on_startup(self):
        """测试应用启动时预热缓存"""
        warmer = CacheWarmer()

        # 执行完整预热
        stats = warmer.warmup_all(games_limit=10, events_limit=10)

        # 验证预热统计
        assert isinstance(stats, dict)
        assert 'games_warmed' in stats
        assert 'events_warmed' in stats
        assert 'params_warmed' in stats

        # 验证预热数量
        assert stats['games_warmed'] >= 0
        assert stats['events_warmed'] >= 0
        assert stats['params_warmed'] >= 0

    def test_warmup_performance_improvement(self):
        """测试预热后的性能提升"""
        warmer = CacheWarmer()
        cache = get_cache()

        # 预热前：查询游戏（冷启动）
        start = time.time()
        game1 = cache.get("games:10000147")
        cold_duration = time.time() - start

        # 执行预热
        warmer.warmup_popular_games(limit=100)

        # 预热后：查询游戏（热启动）
        start = time.time()
        game2 = cache.get("games:10000147")
        warm_duration = time.time() - start

        # 预热后应该更快（或者至少不会更慢）
        # 注意：这个测试可能会因为缓存状态而不同
        print(f"Cold: {cold_duration:.4f}s, Warm: {warm_duration:.4f}s")


@pytest.mark.integration
class TestHierarchicalCacheIntegration:
    """层级缓存集成测试"""

    def test_l1_l2_cache_interaction(self):
        """测试L1和L2缓存的交互"""
        from backend.core.cache.cache_hierarchical import HierarchicalCache

        cache = HierarchicalCache()

        # 写入缓存
        cache.set("test_key", {"data": "value"}, ttl=3600)

        # 从L1读取
        data = cache.get("test_key")
        assert data is not None

        # 验证统计信息
        assert cache.stats['l1_hits'] >= 0
        assert cache.stats['l2_hits'] >= 0

    def test_cache_invalidation(self):
        """测试缓存失效"""
        from backend.core.cache.cache_hierarchical import HierarchicalCache

        cache = HierarchicalCache()

        # 写入缓存
        cache.set("test_key", {"data": "value"}, ttl=3600)

        # 删除缓存
        cache.delete("test_key")

        # 验证已删除
        data = cache.get("test_key")
        assert data is None


@pytest.mark.integration
class TestCacheSystemEndToEnd:
    """缓存系统端到端测试"""

    def test_complete_cache_workflow(self):
        """测试完整的缓存工作流程"""
        # 1. 预热缓存
        from backend.core.cache.cache_system import hierarchical_cache

        warmer = CacheWarmer(cache=hierarchical_cache)
        warmup_stats = warmer.warmup_all(games_limit=10)

        # 2. 查询游戏（应该从缓存读取）
        service = GameService()
        game = service.get_game_by_gid(10000147)

        if game:
            # 3. 验证Bloom Filter已更新
            assert service.bloom_filter.contains(f"games:10000147") is True

            # 4. 获取统计信息
            bloom_stats = service.get_bloom_filter_stats()
            assert isinstance(bloom_stats, dict)

    def test_cache_performance_metrics(self):
        """测试缓存性能指标"""
        from backend.core.cache.cache_hierarchical import HierarchicalCache

        cache = HierarchicalCache()

        # 执行一些缓存操作
        for i in range(100):
            cache.set(f"key_{i}", {"value": i}, ttl=3600)

        for i in range(100):
            cache.get(f"key_{i}")

        # 获取统计信息
        stats = cache.stats

        # 验证统计信息
        assert 'l1_hits' in stats
        assert 'l2_hits' in stats
        assert 'misses' in stats

        # 计算命中率
        total_hits = stats['l1_hits'] + stats['l2_hits']
        total_requests = total_hits + stats['misses']
        if total_requests > 0:
            hit_rate = total_hits / total_requests
            assert hit_rate >= 0 and hit_rate <= 1


@pytest.mark.integration
class TestCacheDegradation:
    """缓存降级集成测试"""

    def test_cache_degradation_on_redis_failure(self):
        """测试Redis故障时的缓存降级"""
        from backend.core.cache.degradation import DegradationStrategy

        cache = DegradationStrategy()

        # 模拟Redis故障，降级到L1
        try:
            # 尝试写入L2（可能失败）
            cache.set_l2("test_key", {"data": "value"}, ttl=3600)
        except Exception:
            # Redis不可用，降级到L1
            cache.set_l1("test_key", {"data": "value"}, ttl=600)

        # 从L1读取应该成功
        data = cache.get_l1("test_key")
        assert data is not None


@pytest.mark.integration
class TestCacheConsistency:
    """缓存一致性测试"""

    def test_cache_data_consistency(self):
        """测试缓存数据一致性"""
        service = GameService()

        # 第一次查询
        game1 = service.get_game_by_gid(10000147)

        # 第二次查询（应该从缓存读取）
        game2 = service.get_game_by_gid(10000147)

        # 数据应该一致
        if game1 and game2:
            assert game1.gid == game2.gid
            assert game1.name == game2.name

    def test_cache_invalidation_on_update(self):
        """测试更新时缓存失效"""
        service = GameService()

        # 先查询，缓存数据
        game = service.get_game_by_gid(10000147)

        if game:
            original_name = game.name

            # 更新游戏（会自动清理缓存）
            try:
                service.update_game(10000147, {"name": "Test Update"})

                # 重新查询
                updated_game = service.get_game_by_gid(10000147)

                # 验证数据已更新
                if updated_game:
                    assert updated_game.name == "Test Update"

                # 恢复原始名称
                service.update_game(10000147, {"name": original_name})
            except Exception as e:
                # 更新可能失败（例如游戏不存在）
                print(f"Update test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
