#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能对比测试

对比缓存启用前后的性能差异
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.cache.cache_system import hierarchical_cache
from backend.core.utils.converters import fetch_all_as_dict


def benchmark_query(use_cache: bool = True, iterations: int = 10) -> dict:
    """
    基准测试查询性能

    Args:
        use_cache: 是否使用缓存
        iterations: 测试迭代次数

    Returns:
        性能统计字典
    """
    query = '''
        SELECT
            g.id, g.gid, g.name, g.ods_db,
            COUNT(DISTINCT le.id) as event_count
        FROM games g
        LEFT JOIN log_events le ON g.game_gid = le.game_gid
        GROUP BY g.id, g.gid, g.name, g.ods_db
        ORDER BY g.id
    '''

    times = []
    cache_hits = 0
    cache_misses = 0

    for i in range(iterations):
        start = time.perf_counter()

        if use_cache:
            # 使用缓存
            result = hierarchical_cache.get("benchmark:games:all")
            if result is None:
                cache_misses += 1
                result = fetch_all_as_dict(query)
                hierarchical_cache.set("benchmark:games:all", result, ttl=60)
            else:
                cache_hits += 1
        else:
            # 不使用缓存，直接查询
            result = fetch_all_as_dict(query)

        end = time.perf_counter()
        times.append((end - start) * 1000)  # 转换为毫秒

    return {
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "hit_rate": cache_hits / iterations if cache_hits + cache_misses > 0 else 0
    }


def format_ms(ms: float) -> str:
    """格式化毫秒显示"""
    if ms < 1:
        return f"{ms*1000:.2f}μs"
    elif ms < 1000:
        return f"{ms:.2f}ms"
    else:
        return f"{ms/1000:.2f}s"


def main():
    print("=" * 70)
    print("📊 缓存性能对比测试")
    print("=" * 70)

    # 预热：先执行一次查询
    print("\n🔥 预热数据库...")
    fetch_all_as_dict('SELECT * FROM games LIMIT 1')

    # 测试1: 无缓存（模拟）
    print("\n" + "=" * 70)
    print("测试1: 无缓存性能")
    print("-" * 70)

    stats_no_cache = benchmark_query(use_cache=False, iterations=5)

    print(f"平均响应时间: {format_ms(stats_no_cache['avg_time'])}")
    print(f"最快响应时间: {format_ms(stats_no_cache['min_time'])}")
    print(f"最慢响应时间: {format_ms(stats_no_cache['max_time'])}")

    # 清理缓存
    hierarchical_cache.delete("benchmark:games:all")

    # 测试2: 有缓存
    print("\n" + "=" * 70)
    print("测试2: 启用缓存性能")
    print("-" * 70)

    stats_with_cache = benchmark_query(use_cache=True, iterations=20)

    print(f"平均响应时间: {format_ms(stats_with_cache['avg_time'])}")
    print(f"最快响应时间: {format_ms(stats_with_cache['min_time'])}")
    print(f"最慢响应时间: {format_ms(stats_with_cache['max_time'])}")
    print(f"缓存命中次数: {stats_with_cache['cache_hits']}")
    print(f"缓存未命中次数: {stats_with_cache['cache_misses']}")
    print(f"缓存命中率: {stats_with_cache['hit_rate']*100:.1f}%")

    # 计算性能提升
    print("\n" + "=" * 70)
    print("📈 性能提升分析")
    print("=" * 70)

    speedup = stats_no_cache['avg_time'] / stats_with_cache['avg_time']
    improvement = ((stats_no_cache['avg_time'] - stats_with_cache['avg_time']) / stats_no_cache['avg_time']) * 100

    print(f"性能提升倍数: {speedup:.2f}x")
    print(f"响应时间减少: {improvement:.1f}%")
    print(f"平均时间差异: {format_ms(stats_no_cache['avg_time'] - stats_with_cache['avg_time'])}")

    # 结论
    print("\n" + "=" * 70)
    if speedup > 2:
        print("✅ 缓存效果显著！性能提升超过2倍")
    elif speedup > 1.5:
        print("✅ 缓存效果良好！性能提升超过1.5倍")
    else:
        print("⚠️ 缓存效果一般，可能需要优化")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
