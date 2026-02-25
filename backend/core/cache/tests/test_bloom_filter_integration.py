#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bloom Filter集成单元测试
=====================

测试GameService和EventService中Bloom Filter的集成

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import pytest
import os
import tempfile
from pathlib import Path

from backend.services.games.game_service import GameService
from backend.services.events.event_service import EventService
from backend.models.entities import GameEntity, EventEntity
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter


@pytest.fixture
def temp_bloom_file():
    """创建临时Bloom Filter文件（在项目data目录内）"""
    # 在项目data目录内创建临时文件，避免路径验证问题
    temp_dir = Path(__file__).parent.parent.parent.parent.parent / "backend" / "data"
    temp_dir.mkdir(parents=True, exist_ok=True)

    import uuid
    unique_id = str(uuid.uuid4())[:8]
    path = temp_dir / f"test_bloom_{unique_id}.pkl"

    yield str(path)

    # 清理
    if path.exists():
        path.unlink()


@pytest.fixture
def game_service(temp_bloom_file):
    """创建测试用GameService"""
    service = GameService()
    # 替换为临时文件，禁用验证以允许测试键
    service.bloom_filter = EnhancedBloomFilter(
        capacity=1000,
        error_rate=0.001,
        persistence_path=temp_bloom_file,
        strict_validation=False  # 禁用验证以允许测试键
    )
    return service


@pytest.fixture
def event_service(temp_bloom_file):
    """创建测试用EventService"""
    service = EventService()
    # 替换为临时文件，禁用验证以允许测试键
    service.bloom_filter = EnhancedBloomFilter(
        capacity=1000,
        error_rate=0.001,
        persistence_path=temp_bloom_file,
        strict_validation=False  # 禁用验证以允许测试键
    )
    return service


class TestBloomFilterIntegration:
    """Bloom Filter集成测试"""

    def test_game_service_bloom_filter_initialization(self, game_service):
        """测试GameService中Bloom Filter正确初始化"""
        assert game_service.bloom_filter is not None
        assert isinstance(game_service.bloom_filter, EnhancedBloomFilter)

    def test_event_service_bloom_filter_initialization(self, event_service):
        """测试EventService中Bloom Filter正确初始化"""
        assert event_service.bloom_filter is not None
        assert isinstance(event_service.bloom_filter, EnhancedBloomFilter)

    def test_bloom_filter_fast_reject_nonexistent_game(self, game_service):
        """测试Bloom Filter快速拒绝不存在的游戏"""
        game_gid = 99999999  # 不存在的游戏

        # 先添加到Bloom Filter（模拟之前查询过）
        cache_key = f"games:{game_gid}"
        game_service.bloom_filter.add(cache_key)

        # 查询不存在的游戏
        # 注意: 由于我们使用真实的GameService，它会查询数据库
        # 这里我们主要测试Bloom Filter的逻辑
        result = game_service.get_game_by_gid(game_gid)

        # 应该返回None（游戏不存在）
        assert result is None

    def test_bloom_filter_stats(self, game_service):
        """测试获取Bloom Filter统计信息"""
        stats = game_service.get_bloom_filter_stats()

        assert isinstance(stats, dict)
        assert 'total_items' in stats
        assert 'false_positive_rate' in stats
        # capacity字段可能不存在，我们检查total_items即可
        assert 'total_items' in stats or 'item_count' in stats

    def test_bloom_filter_rebuild(self, game_service):
        """测试重建Bloom Filter"""
        # 添加一些测试数据到Bloom Filter
        game_service.bloom_filter.add("games:10000147")
        game_service.bloom_filter.add("games:10000148")

        # 重建Bloom Filter（会清空现有数据）
        stats = game_service.rebuild_bloom_filter()

        assert isinstance(stats, dict)
        assert 'total_items' in stats


class TestBloomFilterPerformance:
    """Bloom Filter性能测试"""

    def test_bloom_filter_fast_reject_performance(self, game_service):
        """测试Bloom Filter快速拒绝的性能"""
        import time

        game_gid = 99999999  # 不存在的游戏
        cache_key = f"games:{game_gid}"

        # 禁用验证以允许测试键
        game_service.bloom_filter.strict_validation = False
        # 添加到Bloom Filter
        game_service.bloom_filter.add(cache_key)

        # 测试Bloom Filter查询速度
        start = time.time()
        for _ in range(1000):
            game_service.bloom_filter.contains(cache_key)
        duration = time.time() - start

        # 1000次查询应该<100ms（每次<0.1ms）
        # 考虑到测试环境的波动，设置更宽松的阈值
        assert duration < 0.1, f"Bloom Filter too slow: {duration}ms for 1000 queries"

    def test_bloom_filter_memory_efficiency(self, temp_bloom_file):
        """测试Bloom Filter内存效率"""
        # 禁用验证以允许测试键
        bloom = EnhancedBloomFilter(
            capacity=100000,
            error_rate=0.001,
            persistence_path=temp_bloom_file,
            strict_validation=False
        )

        # 添加10万个键
        for i in range(100000):
            bloom.add(f"test_key_{i}")

        stats = bloom.get_stats()

        # Bloom Filter应该仍然有效
        assert stats['total_items'] == 100000

        # 内存占用应该相对较小（<1MB）
        # 实际测试: 10万个键，0.1%误判率，约200KB
        file_size = os.path.getsize(temp_bloom_file)
        assert file_size < 1024 * 1024, f"Bloom Filter too large: {file_size} bytes"


class TestBloomFilterErrorCases:
    """Bloom Filter错误场景测试"""

    def test_bloom_filter_false_positive(self, game_service):
        """测试Bloom Filter误判（假阳性）"""
        # Bloom Filter可能说存在，但实际不存在
        cache_key = "games:99999999"

        # 需要禁用验证才能添加测试键
        game_service.bloom_filter.strict_validation = False
        game_service.bloom_filter.add(cache_key)

        # Bloom Filter说存在
        assert game_service.bloom_filter.contains(cache_key) is True

        # 但实际查询返回None
        result = game_service.get_game_by_gid(99999999)
        assert result is None

    def test_bloom_filter_persistence(self, temp_bloom_file):
        """测试Bloom Filter持久化"""
        # 创建Bloom Filter并添加数据
        # 使用禁用验证模式进行测试
        bloom1 = EnhancedBloomFilter(
            capacity=1000,
            error_rate=0.001,
            persistence_path=temp_bloom_file,
            strict_validation=False  # 禁用验证以允许测试键
        )
        bloom1.add("test_key_1")
        bloom1.add("test_key_2")

        # 强制保存（使用正确的方法名）
        bloom1.force_save()

        # 创建新的Bloom Filter实例，应该从文件加载
        bloom2 = EnhancedBloomFilter(
            capacity=1000,
            error_rate=0.001,
            persistence_path=temp_bloom_file,
            strict_validation=False  # 禁用验证以允许测试键
        )

        # 验证数据已恢复
        assert bloom2.contains("test_key_1") is True
        assert bloom2.contains("test_key_2") is True
        assert bloom2.contains("test_key_3") is False


class TestEventServiceBloomFilter:
    """EventService Bloom Filter集成测试"""

    def test_event_service_bloom_filter_fast_reject(self, event_service):
        """测试EventService中Bloom Filter快速拒绝"""
        event_id = 99999999  # 不存在的事件

        # 先添加到Bloom Filter
        cache_key = f"events:{event_id}"
        event_service.bloom_filter.add(cache_key)

        # 查询不存在的游戏
        result = event_service.get_event_by_id(event_id)

        # 应该返回None（事件不存在）
        assert result is None

    def test_event_service_bloom_filter_stats(self, event_service):
        """测试EventService的Bloom Filter统计"""
        stats = event_service.get_bloom_filter_stats()

        assert isinstance(stats, dict)
        assert 'total_items' in stats or 'item_count' in stats
        # capacity字段可能不存在


@pytest.mark.integration
class TestBloomFilterIntegrationReal:
    """Bloom Filter集成测试（需要真实数据库）"""

    def test_bloom_filter_with_real_game_query(self, game_service):
        """测试Bloom Filter与真实游戏查询的集成"""
        # 查询存在的游戏（STAR001）
        game = game_service.get_game_by_gid(10000147)

        # 第一次查询：Bloom Filter不包含，会查询数据库
        # 如果游戏存在，会添加到Bloom Filter
        if game:
            assert game_service.bloom_filter.contains(f"games:10000147") is True

    def test_bloom_filter_with_real_event_query(self, event_service):
        """测试Bloom Filter与真实事件查询的集成"""
        # 查询第一个事件（如果存在）
        from backend.core.utils.converters import fetch_all_as_dict

        events = fetch_all_as_dict('SELECT * FROM log_events LIMIT 1')
        if events:
            event_id = events[0]['id']
            event = event_service.get_event_by_id(event_id)

            # 如果事件存在，应该添加到Bloom Filter
            if event:
                assert event_service.bloom_filter.contains(f"events:{event_id}") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
