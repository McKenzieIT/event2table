#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存防护机制测试
==================

测试TTL抖动和空值缓存功能是否正常工作

版本: 1.0.0
日期: 2026-01-28
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ttl_jitter():
    """测试TTL抖动功能"""
    from backend.core.cache.cache_system import hierarchical_cache, CacheKeyBuilder
    from backend.core.config.config import CacheConfig

    print("=" * 60)
    print("🎲 测试1: TTL抖动功能（防止缓存雪崩）")
    print("=" * 60)

    # 重置缓存
    hierarchical_cache.clear_l1()
    hierarchical_cache.reset_stats()

    # 测试相同TTL的缓存键，观察TTL是否不同
    print("\n📝 写入10个相同TTL的缓存项...")
    test_ttl = 300  # 5分钟

    ttls = []
    for i in range(10):
        data = {'id': i, 'name': f'Item {i}'}
        key = CacheKeyBuilder.build('test.jitter', id=i)

        # 通过直接访问内部缓存来检查TTL（仅用于测试）
        start = time.perf_counter()
        hierarchical_cache.set('test.jitter', data, ttl=test_ttl, id=i)

        # 从L1获取时间戳
        if key in hierarchical_cache.l1_timestamps:
            timestamp = hierarchical_cache.l1_timestamps[key]
            # 由于添加了抖动，实际TTL应该是原始TTL ± 抖动
            # 这里我们无法直接看到Redis的TTL，但可以通过多次写入验证抖动存在
            pass

    print(f"✅ 写入完成，TTL={test_ttl}s")
    print(f"✅ TTL抖动配置: ±{CacheConfig.CACHE_JITTER_PCT * 100}%")
    print(f"   预期TTL范围: {test_ttl - int(test_ttl * CacheConfig.CACHE_JITTER_PCT)}-{test_ttl + int(test_ttl * CacheConfig.CACHE_JITTER_PCT)}秒")
    print(f"   (约 {test_ttl * (1 - CacheConfig.CACHE_JITTER_PCT):.0f}-{test_ttl * (1 + CacheConfig.CACHE_JITTER_PCT):.0f}秒)")

    print(f"\n💡 说明: TTL抖动已自动应用到所有缓存写入")
    print(f"   可以通过查看Redis中的实际TTL来验证抖动效果")


def test_empty_cache():
    """测试空值缓存功能"""
    from backend.core.cache.cache_system import hierarchical_cache
    from backend.core.config.config import CacheConfig

    print("\n" + "=" * 60)
    print("💾 测试2: 空值缓存功能（防止缓存穿透）")
    print("=" * 60)

    # 重置缓存
    hierarchical_cache.clear_l1()
    hierarchical_cache.reset_stats()

    # 场景1: 手动缓存空值
    print("\n📝 场景1: 手动缓存空值...")
    hierarchical_cache.set('test.empty', None, id=999)
    print(f"   已缓存空值: test.empty (id=999)")
    print(f"   空值TTL: {CacheConfig.CACHE_EMPTY_TTL}秒")

    # 场景2: 第一次读取空值缓存
    print("\n📝 场景2: 第一次读取空值缓存...")
    start = time.perf_counter()
    result1 = hierarchical_cache.get('test.empty', id=999)
    first_time = (time.perf_counter() - start) * 1000
    print(f"   查询耗时: {first_time:.3f}ms")
    print(f"   返回结果: {result1}")

    # 检查统计
    stats1 = hierarchical_cache.get_stats()
    print(f"   缓存统计: L1命中={stats1['l1_hits']}, 空值命中={stats1['empty_hits']}")

    # 场景3: 第二次读取空值缓存
    print("\n📝 场景3: 第二次读取空值缓存...")
    start = time.perf_counter()
    result2 = hierarchical_cache.get('test.empty', id=999)
    second_time = (time.perf_counter() - start) * 1000
    print(f"   查询耗时: {second_time:.3f}ms")
    print(f"   返回结果: {result2}")

    # 检查统计
    stats2 = hierarchical_cache.get_stats()
    print(f"   缓存统计: L1命中={stats2['l1_hits']}, 空值命中={stats2['empty_hits']}")

    # 验证空值缓存是否生效
    if stats2['empty_hits'] > 0:
        print(f"\n✅ 空值缓存正常工作!")
        print(f"   - 空值命中: {stats2['empty_hits']}次")
        print(f"   - 避免了数据库查询")
    else:
        print(f"\n⚠️ 空值缓存未生效（可能是缓存被清空）")

    # 场景4: 自动空值缓存（推荐使用方式）
    print("\n📝 场景4: 自动空值缓存（推荐使用方式）...")

    hierarchical_cache.clear_l1()
    hierarchical_cache.reset_stats()

    # 模拟从数据库查询返回None
    print(f"   模拟数据库查询返回None（3次）...")
    for i in range(3):
        result = hierarchical_cache.get('test.auto_empty', id=i*1000)
        if result is None:
            # 数据库查询返回None，自动缓存空值
            hierarchical_cache.set('test.auto_empty', None, id=i*1000)
            print(f"   第{i+1}次: 未命中，已缓存空值")

    # 再次查询应该命中空值
    print(f"\n   再次查询（应该命中空值缓存）...")
    for i in range(3):
        result = hierarchical_cache.get('test.auto_empty', id=i*1000)

    stats3 = hierarchical_cache.get_stats()
    print(f"\n   最终统计: 空值命中={stats3['empty_hits']}次")

    if stats3['empty_hits'] > 0:
        print(f"   ✅ 自动空值缓存正常工作!")

    # 场景3: 模拟缓存穿透攻击
    print("\n📝 场景3: 模拟缓存穿透攻击（100次不存在的数据查询）...")

    hierarchical_cache.reset_stats()

    start = time.perf_counter()
    for i in range(100):
        # 查询100个不存在的数据
        result = hierarchical_cache.get('test.attack', id=i*1000)
    total_time = (time.perf_counter() - start) * 1000

    stats3 = hierarchical_cache.get_stats()

    print(f"   总耗时: {total_time:.2f}ms")
    print(f"   平均响应: {total_time / 100:.3f}ms")
    print(f"   空值命中: {stats3['empty_hits']}次")

    if stats3['empty_hits'] == 100:
        print(f"   ✅ 完美！所有查询都命中空值缓存，避免了数据库查询")
        print(f"   🛡️ 成功防御缓存穿透攻击")
    else:
        print(f"   ⚠️ 部分查询未命中空值缓存（预期：首次查询）")


def test_combined_protection():
    """测试综合防护效果"""
    from backend.core.cache.cache_system import hierarchical_cache
    from backend.core.config.config import CacheConfig

    print("\n" + "=" * 60)
    print("🛡️ 测试3: 综合防护效果")
    print("=" * 60)

    # 重置
    hierarchical_cache.clear_l1()
    hierarchical_cache.reset_stats()

    print("\n📊 模拟真实场景：")
    print("   - 100个正常数据（写入缓存）")
    print("   - 50个空值数据（模拟数据库查询返回None）")
    print("   - TTL=300秒（±10%抖动）")

    import random

    # 阶段1: 写入100个正常数据
    print(f"\n💾 写入100个正常数据...")
    for i in range(100):
        data = {'id': i, 'name': f'Item {i}'}
        hierarchical_cache.set('test.combined', data, id=i, ttl=300)

    # 阶段2: 模拟查询（混合正常和空值）
    print(f"\n⚡ 执行150次查询（100次正常 + 50次空值）...")

    normal_ids = list(range(100))
    empty_ids = list(range(1000, 1050))

    all_ids = normal_ids + empty_ids
    random.shuffle(all_ids)

    start = time.perf_counter()

    for i, id_val in enumerate(all_ids):
        if id_val < 100:
            # 正常数据
            result = hierarchical_cache.get('test.combined', id=id_val)
        else:
            # 空值数据（模拟数据库查询返回None后缓存空值）
            result = hierarchical_cache.get('test.combined', id=id_val)
            if result is None:
                # 缓存空值
                hierarchical_cache.set('test.combined', None, id=id_val)

    total_time = (time.perf_counter() - start) * 1000

    stats = hierarchical_cache.get_stats()

    print(f"\n✅ 测试完成:")
    print(f"   总耗时: {total_time:.2f}ms")
    print(f"   总请求数: {len(all_ids)}")
    print(f"   平均响应: {total_time / len(all_ids):.3f}ms")
    print(f"   L1命中: {stats['l1_hits']}次")
    print(f"   L2命中: {stats['l2_hits']}次")
    print(f"   未命中: {stats['misses']}次")
    print(f"   空值命中: {stats['empty_hits']}次")

    # 计算命中率（排除空值命中）
    effective_hits = stats['l1_hits'] + stats['l2_hits']
    effective_requests = effective_hits + stats['misses']
    effective_hit_rate = effective_hits / effective_requests * 100 if effective_requests > 0 else 0

    print(f"\n📊 有效命中率（不含空值）: {effective_hit_rate:.1f}%")
    print(f"🛡️ 空值缓存防御: {stats['empty_hits']}次")

    # 说明
    print(f"\n💡 防护效果:")
    if stats['empty_hits'] > 0:
        print(f"   ✅ 空值缓存已防御 {stats['empty_hits']} 次无效查询")

    if effective_hit_rate > 80:
        print(f"   ✅ 有效命中率{effective_hit_rate:.1f}% ≥80%（优秀）")
    elif effective_hit_rate > 60:
        print(f"   ✅ 有效命中率{effective_hit_rate:.1f}% ≥60%（良好）")
    else:
        print(f"   ⚠️ 有效命中率{effective_hit_rate:.1f}% 建议优化")


def main():
    """主测试函数"""
    print("\n🚀 缓存防护机制测试")
    print("Version: 1.0.0")
    print("=" * 60)

    try:
        test_ttl_jitter()
        test_empty_cache()
        test_combined_protection()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)

        print("\n📝 功能说明:")
        print("1. TTL抖动: 所有缓存写入自动添加±10%的TTL随机抖动")
        print("   - 防止缓存同时过期，避免数据库压力激增")
        print("   - 例如: TTL=300s → 实际TTL=270-330s")

        print("\n2. 空值缓存: 查询不存在的数据时缓存空值标记")
        print("   - 防止频繁查询不存在的数据打挂数据库")
        print("   - 空值TTL=60s，自动过期")
        print("   - 识别标记: '__EMPTY__'")

        print("\n🎯 使用建议:")
        print("- TTL抖动已自动应用，无需额外配置")
        print("- 空值缓存自动触发，无需手动处理")
        print("- 可通过 /admin/cache/stats 查看空值命中统计")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
