#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统简单验证测试
==================

快速验证缓存系统是否正常工作

版本: 1.0.0
日期: 2026-01-28
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_cache_basic_functionality():
    """测试缓存基本功能"""
    from backend.core.cache.cache_system import hierarchical_cache, CacheKeyBuilder

    print("=" * 60)
    print("🔍 缓存系统基本功能验证")
    print("=" * 60)

    # 测试1: 缓存键生成
    print("\n📝 测试1: 缓存键生成")
    print("-" * 60)

    key1 = CacheKeyBuilder.build('games.list')
    print(f"✅ games.list → {key1}")

    key2 = CacheKeyBuilder.build('events.detail', event_id=45)
    print(f"✅ events.detail (event_id=45) → {key2}")

    key3 = CacheKeyBuilder.build('events.list', game_id=1, page=1)
    print(f"✅ events.list (game_id=1, page=1) → {key3}")

    # 验证参数排序一致性
    key4 = CacheKeyBuilder.build('events.list', page=1, game_id=1)
    if key3 == key4:
        print(f"✅ 参数排序一致性: 通过")
    else:
        print(f"❌ 参数排序一致性: 失败")

    # 测试2: 基本读写
    print("\n📝 测试2: 基本读写")
    print("-" * 60)

    test_data = {'id': 123, 'name': 'Test Game', 'value': 999}

    # 写入
    print(f"💾 写入数据...")
    hierarchical_cache.set('test.data', test_data, id=123)

    # 读取
    print(f"⚡ 读取数据...")
    result = hierarchical_cache.get('test.data', id=123)

    if result and result['id'] == 123:
        print(f"✅ 读写测试通过: {result}")
    else:
        print(f"❌ 读写测试失败: {result}")

    # 测试3: L1缓存性能
    print("\n📝 测试3: L1缓存性能")
    print("-" * 60)

    # 写入100个热点数据
    print(f"💾 写入100个热点数据到L1...")
    for i in range(100):
        data = {'id': i, 'name': f'Item {i}'}
        hierarchical_cache.set('test.item', data, id=i)

    # 测试读取性能
    print(f"⚡ 读取100次（应全部命中L1）...")
    total_time = 0
    for i in range(100):
        start = time.perf_counter()
        result = hierarchical_cache.get('test.item', id=i)
        duration = (time.perf_counter() - start) * 1000
        total_time += duration

    avg_time = total_time / 100
    print(f"✅ 平均响应时间: {avg_time:.3f}ms")

    if avg_time < 1.0:
        print(f"✅ 达到目标: <1ms")
    else:
        print(f"⚠️ 未达到目标: {avg_time:.3f}ms (目标<1ms)")

    # 测试4: LRU淘汰
    print("\n📝 测试4: LRU淘汰机制")
    print("-" * 60)

    hierarchical_cache.reset_stats()
    hierarchical_cache.clear_l1()

    l1_capacity = hierarchical_cache.l1_size
    print(f"📦 L1容量: {l1_capacity}条")

    # 写入超过容量的数据
    print(f"💾 写入{l1_capacity + 10}条数据...")
    for i in range(l1_capacity + 10):
        data = {'id': i}
        hierarchical_cache.set('test.lru', data, id=i)

    stats = hierarchical_cache.get_stats()
    print(f"✅ L1大小: {stats['l1_size']}条")
    print(f"✅ L1淘汰次数: {stats['l1_evictions']}次")

    if stats['l1_evictions'] > 0:
        print(f"✅ LRU淘汰正常工作")
    else:
        print(f"⚠️ LRU淘汰未触发")

    # 测试5: 缓存失效
    print("\n📝 测试5: 缓存失效")
    print("-" * 60)

    from backend.core.cache.cache_system import cache_invalidator

    # 写入测试数据
    hierarchical_cache.set('test.invalidate', {'id': 1}, game_id=1)
    hierarchical_cache.set('test.invalidate', {'id': 2}, game_id=2)
    hierarchical_cache.set('test.invalidate', {'id': 3}, game_id=3)

    print(f"💾 写入3条数据")

    # 失效特定游戏
    print(f"🗑️  失效game_id=1的缓存...")
    cache_invalidator.invalidate_pattern('test.invalidate', game_id=1)

    # 验证
    result1 = hierarchical_cache.get('test.invalidate', game_id=1)
    result2 = hierarchical_cache.get('test.invalidate', game_id=2)
    result3 = hierarchical_cache.get('test.invalidate', game_id=3)

    if result1 is None and result2 is not None and result3 is not None:
        print(f"✅ 缓存失效正常工作")
    else:
        print(f"⚠️ 缓存失效可能有问题")

    # 测试6: 统计信息
    print("\n📝 测试6: 统计信息")
    print("-" * 60)

    stats = hierarchical_cache.get_stats()
    print(f"📊 缓存统计:")
    print(f"   - L1大小: {stats['l1_size']}")
    print(f"   - L1容量: {stats['l1_capacity']}")
    print(f"   - L1使用率: {stats['l1_usage']}")
    print(f"   - L1命中: {stats['l1_hits']}")
    print(f"   - L2命中: {stats['l2_hits']}")
    print(f"   - 未命中: {stats['misses']}")
    print(f"   - 总体命中率: {stats['hit_rate']}")

    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_cache_basic_functionality()
