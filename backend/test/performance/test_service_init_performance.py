"""
Service初始化性能测试

TDD Cycle: RED → GREEN → REFACTOR

目标: Service初始化应该在<100ms内完成（不包含Bloom Filter初始化）
"""

import pytest
import time
import os

# 设置测试环境
os.environ["TESTING"] = "true"


class TestServiceInitPerformance:
    """Service初始化性能测试"""

    def test_event_service_init_should_be_fast(self):
        """
        EventService初始化应该在<100ms内完成

        当前行为: 初始化会卡住5秒+（等待Bloom Filter和Redis）
        期望行为: 初始化应该在100ms内完成（lazy loading Bloom Filter）
        """
        start = time.time()
        from backend.services.events.event_service import EventService

        service = EventService()
        elapsed = time.time() - start

        # 验证初始化时间<100ms
        assert elapsed < 0.1, (
            f"EventService init took {elapsed*1000:.2f}ms, "
            f"should be <100ms. "
            f"This indicates Bloom Filter is being initialized eagerly."
        )

        # 验证Bloom Filter尚未初始化
        assert (
            service._bloom_filter is None
        ), "Bloom Filter should not be initialized during Service __init__"

        print(f"✅ EventService init: {elapsed*1000:.2f}ms")

    def test_game_service_init_should_be_fast(self):
        """
        GameService初始化应该在<100ms内完成

        当前行为: 初始化会卡住5秒+（等待Bloom Filter和Redis）
        期望行为: 初始化应该在100ms内完成（lazy loading Bloom Filter）
        """
        start = time.time()
        from backend.services.games.game_service import GameService

        service = GameService()
        elapsed = time.time() - start

        # 验证初始化时间<100ms
        assert elapsed < 0.1, (
            f"GameService init took {elapsed*1000:.2f}ms, "
            f"should be <100ms. "
            f"This indicates Bloom Filter is being initialized eagerly."
        )

        # 验证Bloom Filter尚未初始化
        assert (
            service._bloom_filter is None
        ), "Bloom Filter should not be initialized during Service __init__"

        print(f"✅ GameService init: {elapsed*1000:.2f}ms")

    def test_bloom_filter_lazy_loading(self):
        """
        Bloom Filter应该延迟初始化（仅在首次访问时创建）

        期望行为:
        1. Service初始化后bloom_filter属性为None
        2. 首次访问bloom_filter属性时才初始化
        3. 后续访问返回缓存的实例
        """
        from backend.services.events.event_service import EventService

        service = EventService()

        # 验证1: 初始化后bloom_filter属性为None
        assert service._bloom_filter is None, "Bloom Filter should be None after Service init"

        # 验证2: 首次访问触发初始化
        start = time.time()
        bf = service.bloom_filter
        init_time = time.time() - start

        assert bf is not None, "Bloom Filter should be initialized after first access"
        assert init_time < 5.0, f"Bloom Filter init took {init_time:.2f}s (should be <5s)"

        # 验证3: 后续访问返回缓存的实例
        bf2 = service.bloom_filter
        assert bf is bf2, "Should return cached Bloom Filter instance"

        print(f"✅ Bloom Filter lazy init: {init_time*1000:.2f}ms")
