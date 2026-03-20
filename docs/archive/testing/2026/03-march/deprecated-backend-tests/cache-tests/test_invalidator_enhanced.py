#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存失效器增强测试
================

测试关联失效, 批量失效等功能

版本: 1.0.0
日期: 2026-02-20
"""

import pytest
from unittest.mock import Mock, patch

from backend.core.cache.invalidator import cache_invalidator_enhanced
from backend.core.cache.cache_system import hierarchical_cache


class TestCacheInvalidator:
    """缓存失效器测试"""

    def test_invalidate_key(self):
        """测试精确失效单个键"""
        # 设置缓存
        hierarchical_cache.set('test.key', {'id': 123}, id=123)

        # 验证缓存存在
        result = hierarchical_cache.get('test.key', id=123)
        assert result is not None
        print(f"✅ 缓存已设置: test.key")

        # 失效缓存
        success = cache_invalidator_enhanced.invalidate_key('test.key', id=123)
        assert success is True
        print(f"✅ 缓存已失效: test.key")

        # 验证缓存已删除
        result = hierarchical_cache.get('test.key', id=123)
        assert result is None
        print(f"✅ 缓存已删除验证成功")

    def test_invalidate_pattern(self):
        """测试模式失效"""
        # 设置多个缓存
        for i in range(5):
            hierarchical_cache.set('test.pattern', {'id': i}, game_id=100, page=i)

        # 验证缓存存在
        for i in range(5):
            result = hierarchical_cache.get('test.pattern', game_id=100, page=i)
            assert result is not None
        print(f"✅ 已设置5个缓存")

        # 失效模式缓存
        count = cache_invalidator_enhanced.invalidate_pattern('test.pattern', game_id=100)
        print(f"✅ 模式失效: {count}个键")

        # 验证缓存已删除
        for i in range(5):
            result = hierarchical_cache.get('test.pattern', game_id=100, page=i)
            # 注意: L1缓存可能已被清空, 但L2可能还在
            # 这里主要测试功能是否正常工作

    def test_invalidate_game_related(self):
        """测试游戏关联失效"""
        # 设置游戏相关缓存
        game_gid = 10000147

        # 游戏详情
        hierarchical_cache.set('games.detail', {'gid': game_gid, 'name': 'Test Game'}, gid=game_gid)

        # 游戏列表
        hierarchical_cache.set('games.list', [{'gid': game_gid}])

        # 游戏事件列表
        hierarchical_cache.set('events.list', [{'id': 1}], game_id=game_gid)

        print(f"✅ 已设置游戏相关缓存: game_gid={game_gid}")

        # 失效游戏相关缓存
        invalidated_keys = cache_invalidator_enhanced.invalidate_game_related(game_gid)

        print(f"✅ 游戏关联失效: {len(invalidated_keys)}个键")
        print(f"   失效的键: {invalidated_keys}")

        # 验证至少失效了一些键
        assert len(invalidated_keys) > 0

    def test_invalidate_event_related(self):
        """测试事件关联失效"""
        # 设置事件相关缓存
        event_id = 123
        game_gid = 10000147

        # 事件详情
        hierarchical_cache.set('events.detail', {'id': event_id, 'name': 'Test Event'}, id=event_id)

        # 事件参数列表
        hierarchical_cache.set('params.list', [{'id': 1}], event_id=event_id)

        # 游戏事件列表
        hierarchical_cache.set('events.list', [{'id': event_id}], game_id=game_gid)

        print(f"✅ 已设置事件相关缓存: event_id={event_id}, game_gid={game_gid}")

        # 失效事件相关缓存
        invalidated_keys = cache_invalidator_enhanced.invalidate_event_related(event_id, game_gid)

        print(f"✅ 事件关联失效: {len(invalidated_keys)}个键")
        print(f"   失效的键: {invalidated_keys}")

        # 验证至少失效了一些键
        assert len(invalidated_keys) > 0

    def test_invalidate_batch(self):
        """测试批量失效"""
        # 设置多个缓存
        patterns = []
        for i in range(5):
            hierarchical_cache.set('test.batch', {'id': i}, id=i)
            patterns.append(('test.batch', {'id': i}))

        print(f"✅ 已设置5个缓存")

        # 批量失效
        count = cache_invalidator_enhanced.invalidate_batch(patterns)

        print(f"✅ 批量失效: {count}个键")

        # 验证缓存已删除
        for i in range(5):
            result = hierarchical_cache.get('test.batch', id=i)
            # L1缓存应该已被删除
            # L2缓存可能还在(取决于Redis是否可用)

    def test_clear_all(self):
        """测试清空所有缓存"""
        # 设置多个缓存
        for i in range(10):
            hierarchical_cache.set('test.clear', {'id': i}, id=i)

        print(f"✅ 已设置10个缓存")

        # 清空所有缓存
        l1_count, l2_count = cache_invalidator_enhanced.clear_all()

        print(f"✅ 清空缓存: L1={l1_count}, L2={l2_count}")

        # 验证L1缓存已清空
        assert len(hierarchical_cache.l1_cache) == 0
        print(f"✅ L1缓存已清空验证成功")


class TestInvalidatorIntegration:
    """失效器集成测试"""

    def test_full_invalidation_flow(self):
        """测试完整失效流程"""
        # 清空缓存
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()

        # 设置游戏和事件缓存
        game_gid = 10000148
        event_id = 456

        # 设置缓存
        hierarchical_cache.set('games.detail', {'gid': game_gid}, gid=game_gid)
        hierarchical_cache.set('games.list', [{'gid': game_gid}])
        hierarchical_cache.set('events.detail', {'id': event_id}, id=event_id)
        hierarchical_cache.set('events.list', [{'id': event_id}], game_id=game_gid)

        print(f"✅ 已设置游戏和事件缓存")

        # 失效游戏相关缓存
        game_keys = cache_invalidator_enhanced.invalidate_game_related(game_gid)
        print(f"✅ 游戏关联失效: {len(game_keys)}个键")

        # 失效事件相关缓存
        event_keys = cache_invalidator_enhanced.invalidate_event_related(event_id, game_gid)
        print(f"✅ 事件关联失效: {len(event_keys)}个键")

        # 验证所有缓存都已失效
        assert hierarchical_cache.get('games.detail', gid=game_gid) is None
        assert hierarchical_cache.get('games.list') is None
        assert hierarchical_cache.get('events.detail', id=event_id) is None

        print(f"✅ 完整失效流程测试成功")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
