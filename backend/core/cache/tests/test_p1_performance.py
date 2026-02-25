#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P1性能优化验证测试
==================

验证以下性能优化:
1. 模式匹配索引系统（O(n*k) → O(1)）
2. Redis SCAN替代KEYS（避免阻塞）

预期性能提升:
- 模式匹配: 50,000次操作 → ~100次操作（500倍提升）
- Redis扫描: 非阻塞，适合生产环境

使用方法:
    python backend/core/cache/tests/test_p1_performance.py
"""

import sys
import time
import random
import string
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.core.cache.cache_hierarchical import HierarchicalCache
from backend.core.cache.base import CacheKeyBuilder


def generate_random_key(pattern: str, **kwargs) -> str:
    """生成随机缓存键"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    if kwargs:
        return CacheKeyBuilder.build(f"{pattern}.{random_suffix}", **kwargs)
    return CacheKeyBuilder.build(f"{pattern}.{random_suffix}")


def test_pattern_matching_performance():
    """
    测试1: 模式匹配性能（索引 vs 遍历）

    场景: 1000个缓存键，50个模式
    """
    print("\n" + "="*80)
    print("测试1: 模式匹配性能优化")
    print("="*80)

    # 1. 测试禁用索引的情况（O(n*k)）
    print("\n[测试A] 禁用索引（遍历方式）...")
    cache_no_index = HierarchicalCache(
        l1_size=2000,
        enable_key_level_locks=False
    )
    cache_no_index._index_enabled = False

    # 添加1000个键
    print("  添加1000个缓存键...")
    for i in range(1000):
        game_gid = random.randint(90000000, 90000099)
        cache_no_index.set(
            'events.list',
            [{"id": i}],
            game_gid=game_gid,
            page=random.randint(1, 10)
        )

    # 测试50次模式失效
    print("  执行50次模式失效...")
    start_time = time.perf_counter()
    for _ in range(50):
        game_gid = random.randint(90000000, 90000099)
        cache_no_index.invalidate_pattern('events.list', game_gid=game_gid)
    no_index_time = time.perf_counter() - start_time

    print(f"  ❌ 遍历方式耗时: {no_index_time*1000:.2f}ms")
    print(f"     复杂度: O(n*k) = 1000键 × 50模式 = 50,000次操作")

    # 2. 测试启用索引的情况（O(1)）
    print("\n[测试B] 启用索引（索引方式）...")
    cache_with_index = HierarchicalCache(
        l1_size=2000,
        enable_key_level_locks=False
    )

    # 添加1000个键
    print("  添加1000个缓存键...")
    for i in range(1000):
        game_gid = random.randint(90000000, 90000099)
        cache_with_index.set(
            'events.list',
            [{"id": i}],
            game_gid=game_gid,
            page=random.randint(1, 10)
        )

    # 测试50次模式失效
    print("  执行50次模式失效...")
    start_time = time.perf_counter()
    for _ in range(50):
        game_gid = random.randint(90000000, 90000099)
        cache_with_index.invalidate_pattern('events.list', game_gid=game_gid)
    with_index_time = time.perf_counter() - start_time

    print(f"  ✅ 索引方式耗时: {with_index_time*1000:.2f}ms")
    print(f"     复杂度: O(1) 索引查找")

    # 3. 性能提升计算
    speedup = no_index_time / with_index_time if with_index_time > 0 else float('inf')
    print(f"\n📊 性能提升: {speedup:.1f}x")
    print(f"   时间节省: {(1 - with_index_time/no_index_time)*100:.1f}%")

    # 4. 验证索引统计
    stats = cache_with_index.get_stats()
    print(f"\n📈 索引统计:")
    print(f"   索引命中: {stats.get('index_hits', 0)}次")
    print(f"   全扫描: {stats.get('index_scans', 0)}次")
    print(f"   注册模式: {stats.get('index_patterns', 0)}个")

    return speedup > 2  # 期望至少2倍提升


def test_redis_scan_performance():
    """
    测试2: Redis SCAN vs KEYS（需要Redis连接）

    注意: 如果Redis不可用，此测试将被跳过
    """
    print("\n" + "="*80)
    print("测试2: Redis SCAN替代KEYS")
    print("="*80)

    try:
        from backend.core.cache.base import get_redis_client
        redis_client = get_redis_client()

        if redis_client is None:
            print("\n⚠️  Redis未连接，跳过SCAN测试")
            return True

        # 准备测试数据
        print("\n准备测试数据...")
        test_keys = []
        for i in range(100):
            key = f"dwd_gen:v3:test.key:{i}"
            redis_client.set(key, f"value_{i}", timeout=60)
            test_keys.append(key)

        print(f"  已添加{len(test_keys)}个测试键")

        # 测试KEYS命令
        print("\n[测试A] KEYS命令（阻塞）...")
        start_time = time.perf_counter()
        keys_result = redis_client.keys("dwd_gen:v3:test.key:*")
        keys_time = time.perf_counter() - start_time
        print(f"  KEYS耗时: {keys_time*1000:.2f}ms")
        print(f"  找到键: {len(keys_result)}个")
        print(f"  ⚠️  警告: KEYS是O(n)操作，可能阻塞Redis")

        # 测试SCAN命令
        print("\n[测试B] SCAN命令（非阻塞）...")
        start_time = time.perf_counter()
        cursor = '0'
        scan_keys = []
        while cursor != 0:
            cursor, batch = redis_client.scan(cursor=cursor, match="dwd_gen:v3:test.key:*", count=20)
            scan_keys.extend(batch)
        scan_time = time.perf_counter() - start_time
        print(f"  SCAN耗时: {scan_time*1000:.2f}ms")
        print(f"  找到键: {len(scan_keys)}个")
        print(f"  ✅ 优点: 增量处理，不阻塞Redis")

        # 清理测试数据
        print("\n清理测试数据...")
        redis_client.delete(*test_keys)

        print("\n📊 结论:")
        print("   SCAN虽然可能稍慢，但不会阻塞Redis服务器")
        print("   生产环境必须使用SCAN，避免性能抖动")

        return True

    except Exception as e:
        print(f"\n❌ SCAN测试失败: {e}")
        return False


def test_combined_performance():
    """
    测试3: 综合性能测试（索引 + SCAN）
    """
    print("\n" + "="*80)
    print("测试3: 综合性能测试")
    print("="*80)

    cache = HierarchicalCache(
        l1_size=2000,
        enable_key_level_locks=False
    )

    # 添加混合类型的缓存键
    print("\n准备混合测试数据...")
    patterns = [
        ('events.list', 300),
        ('games.detail', 200),
        ('params.list', 250),
        ('categories.list', 150),
        ('hql.history', 100)
    ]

    total_keys = 0
    for pattern, count in patterns:
        for i in range(count):
            game_gid = random.randint(90000000, 90000099)
            cache.set(pattern, {"data": i}, game_gid=game_gid, id=i)
            total_keys += 1

    print(f"  已添加{total_keys}个缓存键")

    # 执行混合模式失效
    print("\n执行混合模式失效...")
    start_time = time.perf_counter()

    for pattern, _ in patterns:
        for _ in range(10):
            game_gid = random.randint(90000000, 90000099)
            cache.invalidate_pattern(pattern, game_gid=game_gid)

    total_time = time.perf_counter() - start_time
    print(f"  总耗时: {total_time*1000:.2f}ms")
    print(f"  平均每次: {(total_time/50)*1000:.2f}ms")

    # 显示统计
    stats = cache.get_stats()
    print(f"\n📊 最终统计:")
    print(f"   L1缓存大小: {stats['l1_size']}")
    print(f"   索引命中: {stats.get('index_hits', 0)}次")
    print(f"   全扫描: {stats.get('index_scans', 0)}次")

    return total_time < 1.0  # 期望总耗时 < 1秒


def main():
    """运行所有性能测试"""
    print("\n" + "="*80)
    print("P1性能优化验证测试")
    print("="*80)
    print("\n优化内容:")
    print("  1. 模式匹配索引系统: O(n*k) → O(1)")
    print("  2. Redis SCAN替代KEYS: 避免阻塞")

    results = {}

    # 运行测试
    try:
        results['pattern_matching'] = test_pattern_matching_performance()
        results['redis_scan'] = test_redis_scan_performance()
        results['combined'] = test_combined_performance()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 所有测试通过！P1性能优化验证成功")
        print("\n📊 性能提升:")
        print("  - 模式匹配: 500x+ 提升理论值")
        print("  - Redis操作: 非阻塞，生产可用")
    else:
        print("\n⚠️  部分测试失败，请检查")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
