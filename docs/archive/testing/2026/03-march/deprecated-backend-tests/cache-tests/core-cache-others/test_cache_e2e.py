#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统端到端性能测试
========================

模拟真实API使用场景, 测试缓存的端到端性能表现

版本: 1.0.0
日期: 2026-01-28
"""

import sys
import os
import time
import statistics

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_api_cache_performance():
    """测试实际API场景的缓存性能"""
    from backend.core.cache.cache_system import hierarchical_cache
    from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict
    from backend.core.config.config import CacheConfig

    print("=" * 70)
    print("🚀 端到端缓存性能测试")
    print("=" * 70)

    # 重置统计
    hierarchical_cache.reset_stats()

    # ========================================================================
    # 场景1: 热点数据缓存(游戏列表)
    # ========================================================================
    print("\n📊 场景1: 热点数据缓存（游戏列表）")
    print("-" * 70)

    print("\n🔥 第一次请求（缓存未命中, 从数据库读取）...")
    start = time.perf_counter()
    games = fetch_all_as_dict('SELECT * FROM games ORDER BY id')
    db_time = (time.perf_counter() - start) * 1000
    print(f"   数据库查询耗时: {db_time:.2f}ms")
    print(f"   查询结果: {len(games)}个游戏")

    # 写入缓存
    print("\n💾 写入缓存...")
    start = time.perf_counter()
    hierarchical_cache.set('games.list', games, timeout=CacheConfig.CACHE_TIMEOUT_GAMES)
    cache_write_time = (time.perf_counter() - start) * 1000
    print(f"   缓存写入耗时: {cache_write_time:.3f}ms")

    # 读取缓存(L1命中)
    print("\n⚡ 第二次请求（从L1缓存读取）...")
    start = time.perf_counter()
    cached_games = hierarchical_cache.get('games.list')
    l1_read_time = (time.perf_counter() - start) * 1000
    print(f"   L1缓存读取耗时: {l1_read_time:.3f}ms")

    if l1_read_time < 1.0:
        print(f"   ✅ 性能提升: {db_time / l1_read_time:.0f}x")
    else:
        print(f"   ⚠️ L1响应时间: {l1_read_time:.3f}ms（目标<1ms）")

    # ========================================================================
    # 场景2: 热点数据重复访问
    # ========================================================================
    print("\n📊 场景2: 热点数据重复访问（100次）")
    print("-" * 70)

    # 重置统计
    hierarchical_cache.reset_stats()

    print("\n⚡ 执行100次游戏列表请求...")
    read_times = []
    for i in range(100):
        start = time.perf_counter()
        result = hierarchical_cache.get('games.list')
        duration = (time.perf_counter() - start) * 1000
        read_times.append(duration)

    stats = hierarchical_cache.get_stats()

    print(f"\n✅ 性能统计:")
    print(f"   - L1命中: {stats['l1_hits']}次")
    print(f"   - L2命中: {stats['l2_hits']}次")
    print(f"   - 未命中: {stats['misses']}次")
    print(f"   - 平均响应时间: {statistics.mean(read_times):.3f}ms")
    print(f"   - 最小响应时间: {min(read_times):.3f}ms")
    print(f"   - 最大响应时间: {max(read_times):.3f}ms")

    # ========================================================================
    # 场景3: 缓存预热效果
    # ========================================================================
    print("\n📊 场景3: 缓存预热效果验证")
    print("-" * 70)

    from backend.services.cache.cache_warmup import CacheWarmer

    # 重置统计
    hierarchical_cache.reset_stats()

    print("\n🔥 执行缓存预热...")
    start = time.perf_counter()

    # 使用新CacheWarmer API (2026-02-26)
    warmer = CacheWarmer(cache=hierarchical_cache)
    warmer.warmup_popular_games(limit=100)
    warmer.warmup_recent_events(limit=50)
    warmup_time = time.perf_counter() - start
    print(f"   预热耗时: {warmup_time:.2f}秒")

    warmup_stats = warmer.stats
    print(f"   预热数据:")
    print(f"   - 游戏: {warmup_stats['games_warmed']}个")
    print(f"   - 事件: {warmup_stats['events_warmed']}个")
    print(f"   - 参数: {warmup_stats['params_warmed']}个")
    print(f"   - 总计: {warmup_stats['total_keys']}个")

    # 测试预热后的读取性能
    print("\n⚡ 测试预热后的读取性能...")
    hierarchical_cache.reset_stats()

    start = time.perf_counter()
    games = hierarchical_cache.get('games.list')
    read_time = (time.perf_counter() - start) * 1000

    stats = hierarchical_cache.get_stats()
    print(f"   读取耗时: {read_time:.3f}ms")
    print(
        f"   命中级别: {'L1' if stats['l1_hits'] > 0 else 'L2' if stats['l2_hits'] > 0 else '未命中'}"
    )

    # ========================================================================
    # 场景4: 缓存失效性能
    # ========================================================================
    print("\n📊 场景4: 缓存失效性能")
    print("-" * 70)

    from backend.core.cache.cache_system import cache_invalidator

    print("\n🗑️  测试游戏缓存失效...")
    start = time.perf_counter()
    cache_invalidator.invalidate_game(game_id=1)
    invalidate_time = (time.perf_counter() - start) * 1000
    print(f"   失效操作耗时: {invalidate_time:.3f}ms")

    # ========================================================================
    # 场景5: Redis L2缓存性能
    # ========================================================================
    print("\n📊 场景5: Redis L2缓存性能")
    print("-" * 70)

    from backend.core.cache.cache_system import get_redis_client

    redis_client = get_redis_client()
    if redis_client:
        print("\n📊 Redis统计信息:")
        info = redis_client.info()

        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses

        if total > 0:
            hit_rate = hits / total * 100
            print(f"   - 总键数: {redis_client.dbsize()}")
            print(f"   - 命中次数: {hits}")
            print(f"   - 未命中次数: {misses}")
            print(f"   - 命中率: {hit_rate:.2f}%")
            print(f"   - 内存使用: {info.get('used_memory_human', '0B')}")
            print(f"   - 运行时间: {info.get('uptime_in_seconds', 0) / 86400:.2f}天")
        else:
            print(f"   ⚠️ 暂无Redis操作记录")

    # ========================================================================
    # 综合评估
    # ========================================================================
    print("\n" + "=" * 70)
    print("📋 综合评估报告")
    print("=" * 70)

    stats = hierarchical_cache.get_stats()

    print(f"\n📊 缓存统计:")
    print(f"   - L1缓存大小: {stats['l1_size']}/{stats['l1_capacity']}")
    print(f"   - L1使用率: {stats['l1_usage']}")
    print(f"   - L1命中: {stats['l1_hits']}次")
    print(f"   - L2命中: {stats['l2_hits']}次")
    print(f"   - 总请求数: {stats['total_requests']}")

    if stats['total_requests'] > 0:
        hit_rate = (stats['l1_hits'] + stats['l2_hits']) / stats['total_requests'] * 100
        print(f"   - 总体命中率: {hit_rate:.1f}%")

        if hit_rate >= 90.0:
            print(f"   ✅ 达到目标: 命中率 ≥90%")
        else:
            print(f"   ⚠️ 未达到目标: 命中率 {hit_rate:.1f}%, 目标≥90%")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_api_cache_performance()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
