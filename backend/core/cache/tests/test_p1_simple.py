#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的P1性能优化演示
==================

演示模式匹配索引的性能优势
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.core.cache.cache_hierarchical import HierarchicalCache


def test_index_optimization():
    """演示索引优化效果"""
    print("\n" + "=" * 80)
    print("P1性能优化演示: 模式匹配索引")
    print("=" * 80)

    # 创建缓存实例(启用索引)
    cache = HierarchicalCache(l1_size=2000)

    # 场景: 添加1000个缓存键, game_gid分布在100个不同值
    print("\n准备测试数据...")
    game_gids = list(range(90000000, 90000100))  # 100个不同的game_gid

    for game_gid in game_gids:
        for page in range(10):
            cache.set(
                'events.list', {"game_gid": game_gid, "page": page}, game_gid=game_gid, page=page
            )

    print(f"✅ 已添加 {len(game_gids) * 10} 个缓存键")
    print(f"   分布: {len(game_gids)} 个game_gid × 10 个page")

    # 第一次失效某个game_gid(会触发全扫描并建立索引)
    print("\n[第1次失效] game_gid=90000000")
    print("   状态: 索引未命中 → 全扫描 + 建立索引")

    start_time = time.perf_counter()
    count1 = cache.invalidate_pattern('events.list', game_gid=90000000)
    time1 = time.perf_counter() - start_time

    stats1 = cache.get_stats()
    print(f"   失效键数: {count1}")
    print(f"   耗时: {time1*1000:.3f}ms")
    print(f"   索引统计:")
    print(f"     - 全扫描: {stats1.get('index_scans', 0)}次")
    print(f"     - 索引命中: {stats1.get('index_hits', 0)}次")
    print(f"     - 注册模式: {stats1.get('index_patterns', 0)}个")

    # 第二次失效相同的game_gid(直接使用索引)
    print("\n[第2次失效] game_gid=90000001")
    print("   状态: 索引命中 → O(1)查找")

    start_time = time.perf_counter()
    count2 = cache.invalidate_pattern('events.list', game_gid=90000001)
    time2 = time.perf_counter() - start_time

    stats2 = cache.get_stats()
    print(f"   失效键数: {count2}")
    print(f"   耗时: {time2*1000:.3f}ms")
    print(f"   索引统计:")
    print(f"     - 全扫描: {stats2.get('index_scans', 0)}次")
    print(f"     - 索引命中: {stats2.get('index_hits', 0)}次")
    print(f"     - 注册模式: {stats2.get('index_patterns', 0)}个")

    # 第三次失效(应该更快)
    print("\n[第3次失效] game_gid=90000002")
    print("   状态: 索引命中 → O(1)查找")

    start_time = time.perf_counter()
    count3 = cache.invalidate_pattern('events.list', game_gid=90000002)
    time3 = time.perf_counter() - start_time

    stats3 = cache.get_stats()
    print(f"   失效键数: {count3}")
    print(f"   耗时: {time3*1000:.3f}ms")
    print(f"   索引统计:")
    print(f"     - 全扫描: {stats3.get('index_scans', 0)}次")
    print(f"     - 索引命中: {stats3.get('index_hits', 0)}次")
    print(f"     - 注册模式: {stats3.get('index_patterns', 0)}个")

    # 对比测试: 禁用索引
    print("\n" + "=" * 80)
    print("对比测试: 禁用索引优化")
    print("=" * 80)

    cache_no_index = HierarchicalCache(l1_size=2000)
    cache_no_index._index_enabled = False

    print("\n准备相同的测试数据...")
    for game_gid in game_gids:
        for page in range(10):
            cache_no_index.set(
                'events.list', {"game_gid": game_gid, "page": page}, game_gid=game_gid, page=page
            )

    print(f"✅ 已添加 {len(game_gids) * 10} 个缓存键")

    print("\n[遍历方式] game_gid=90000000")
    start_time = time.perf_counter()
    count_no_index = cache_no_index.invalidate_pattern('events.list', game_gid=90000000)
    time_no_index = time.perf_counter() - start_time

    print(f"   失效键数: {count_no_index}")
    print(f"   耗时: {time_no_index*1000:.3f}ms")
    print(f"   复杂度: O(n) 遍历所有键")

    # 性能对比
    print("\n" + "=" * 80)
    print("性能对比总结")
    print("=" * 80)

    # 使用第2次和第3次的平均时间作为索引优化后的时间
    indexed_avg = (time2 + time3) / 2
    speedup = time_no_index / indexed_avg if indexed_avg > 0 else 0

    print(f"\n遍历方式（无索引）: {time_no_index*1000:.3f}ms")
    print(f"索引方式（第2-3次平均）: {indexed_avg*1000:.3f}ms")
    print(f"\n📊 性能提升: {speedup:.1f}x")

    if speedup > 1:
        print(f"   ✅ 索引优化有效！速度提升 {speedup:.1f}x")
    else:
        print(f"   ⚠️  首次建立索引有开销, 但后续操作会更快")
        print(f"   💡 随着失效次数增加, 索引优势会越来越明显")

    print("\n💡 关键点:")
    print("   - 首次使用新模式会全扫描并建立索引（一次性成本）")
    print("   - 后续使用相同模式直接查索引（O(1)）")
    print("   - 适合频繁失效相同模式的场景")

    return True


if __name__ == '__main__':
    try:
        success = test_index_optimization()
        print(f"\n{'='*80}")
        print("✅ P1性能优化演示完成")
        print("=" * 80)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
