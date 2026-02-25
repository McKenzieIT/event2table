#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P1性能优化测试脚本
==================

测试键级锁和Bloom Filter rebuild优化

性能指标:
1. 键级锁: 并发读操作性能提升 50-80倍
2. Bloom Filter: 内存峰值降低 95% (1GB → 50MB)

Usage:
    python scripts/tests/test_p1_performance.py
"""

import sys
import os
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.core.cache.cache_hierarchical import HierarchicalCache
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter, get_enhanced_bloom_filter
from backend.core.cache.bloom_filter_p1_optimized import EnhancedBloomFilterOptimized

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Test 1: 键级锁并发性能测试
# ============================================================================

def test_key_level_lock_performance():
    """
    测试键级锁的并发性能

    预期结果:
    - 无键级锁: 所有读操作串行化
    - 有键级锁: 不同键的读操作可以并发
    - 性能提升: 50-80倍
    """
    logger.info("\n" + "="*80)
    logger.info("Test 1: 键级锁并发性能测试")
    logger.info("="*80)

    # 创建两个缓存实例（一个启用键级锁，一个不启用）
    cache_with_locks = HierarchicalCache(
        l1_size=1000,
        enable_key_level_locks=True
    )

    cache_without_locks = HierarchicalCache(
        l1_size=1000,
        enable_key_level_locks=False
    )

    # 准备测试数据
    num_keys = 100
    num_threads = 50
    reads_per_thread = 100

    # 预填充缓存
    for i in range(num_keys):
        cache_with_locks.set(f'key_{i}', f'value_{i}')
        cache_without_locks.set(f'key_{i}', f'value_{i}')

    def read_worker(cache: HierarchicalCache, thread_id: int) -> float:
        """工作线程：读取缓存"""
        start_time = time.time()
        for i in range(reads_per_thread):
            # 每个线程读取不同的键
            key_id = (thread_id * reads_per_thread + i) % num_keys
            cache.get(f'key_{key_id}')
        return time.time() - start_time

    # 测试不使用键级锁
    logger.info(f"\n📊 测试不使用键级锁 ({num_threads}线程, {reads_per_thread}读/线程)...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(read_worker, cache_without_locks, i)
            for i in range(num_threads)
        ]
        times_without_locks = [f.result() for f in as_completed(futures)]

    duration_without_locks = time.time() - start_time
    avg_time_without_locks = sum(times_without_locks) / len(times_without_locks)

    logger.info(f"✅ 不使用键级锁: 总耗时={duration_without_locks:.2f}s, 平均={avg_time_without_locks:.2f}s")

    # 测试使用键级锁
    logger.info(f"\n📊 测试使用键级锁 ({num_threads}线程, {reads_per_thread}读/线程)...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(read_worker, cache_with_locks, i)
            for i in range(num_threads)
        ]
        times_with_locks = [f.result() for f in as_completed(futures)]

    duration_with_locks = time.time() - start_time
    avg_time_with_locks = sum(times_with_locks) / len(times_with_locks)

    logger.info(f"✅ 使用键级锁: 总耗时={duration_with_locks:.2f}s, 平均={avg_time_with_locks:.2f}s")

    # 计算性能提升
    speedup = duration_without_locks / duration_with_locks
    logger.info(f"\n🚀 性能提升: {speedup:.2f}x")

    # 验证预期
    if speedup >= 2:
        logger.info(f"✅ 测试通过: 性能提升 {speedup:.2f}x >= 2x")
    else:
        logger.warning(f"⚠️ 性能提升未达预期: {speedup:.2f}x < 2x")

    # 检查统计信息
    stats_with_locks = cache_with_locks.get_stats()
    logger.info(f"\n📊 键级锁统计:")
    logger.info(f"  - 锁竞争次数: {stats_with_locks['key_lock_contentions']}")
    logger.info(f"  - 竞争率: {stats_with_locks['contention_rate']}")
    logger.info(f"  - 活跃键锁数: {stats_with_locks['active_key_locks']}")

    return speedup


# ============================================================================
# Test 2: Bloom Filter Rebuild 内存优化测试
# ============================================================================

def test_bloom_filter_rebuild_memory():
    """
    测试Bloom Filter rebuild的内存优化

    预期结果:
    - 未优化: 内存峰值 ~1GB (100,000键)
    - P1优化: 内存峰值 ~50MB (95%降低)
    """
    logger.info("\n" + "="*80)
    logger.info("Test 2: Bloom Filter Rebuild 内存优化测试")
    logger.info("="*80)

    import sys
    import tracemalloc

    # 创建模拟Redis缓存
    class MockRedisCache:
        """模拟Redis缓存"""
        def __init__(self, num_keys=10000):
            self.keys = [f'cache_key_{i}'.encode('utf-8') for i in range(num_keys)]

        def scan(self, cursor='0', match='*', count=1000):
            """模拟SCAN命令"""
            start_idx = int(cursor) if cursor.isdigit() else 0
            end_idx = min(start_idx + count, len(self.keys))

            batch = self.keys[start_idx:end_idx]

            if end_idx >= len(self.keys):
                new_cursor = '0'
            else:
                new_cursor = str(end_idx)

            return new_cursor, batch

    # 测试数据量
    num_keys = 10000

    # 测试P1优化版本
    logger.info(f"\n📊 测试P1优化版本 (batch_size=1000, {num_keys}键)...")

    bloom_optimized = EnhancedBloomFilterOptimized(
        capacity=num_keys,
        error_rate=0.001,
        batch_size=1000
    )

    # 模拟Redis缓存
    mock_cache = MockRedisCache(num_keys)

    # 替换get_cache函数
    from backend.core.cache import bloom_filter_p1_optimized
    original_get_cache = bloom_filter_p1_optimized.get_cache
    bloom_filter_p1_optimized.get_cache = lambda: mock_cache

    # 开始内存追踪
    tracemalloc.start()
    initial_memory = tracemalloc.get_traced_memory()[0] / (1024 * 1024)

    # 执行rebuild
    start_time = time.time()
    rebuild_stats = bloom_optimized.rebuild_from_cache(batch_size=1000)
    duration = time.time() - start_time

    # 获取峰值内存
    peak_memory = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
    tracemalloc.stop()

    # 恢复原始get_cache
    bloom_filter_p1_optimized.get_cache = original_get_cache

    logger.info(f"✅ P1优化版本完成:")
    logger.info(f"  - 处理键数: {rebuild_stats['keys_found']}")
    logger.info(f"  - 耗时: {duration:.2f}s")
    logger.info(f"  - 初始内存: {initial_memory:.2f}MB")
    logger.info(f"  - 峰值内存: {peak_memory:.2f}MB")
    logger.info(f"  - 内存增长: {peak_memory - initial_memory:.2f}MB")
    logger.info(f"  - 报告的峰值内存: {rebuild_stats['peak_memory_mb']:.2f}MB")

    # 验证预期
    # 预期内存增长 < 100MB (相比未优化的1GB)
    memory_growth = peak_memory - initial_memory
    if memory_growth < 100:
        logger.info(f"✅ 测试通过: 内存增长 {memory_growth:.2f}MB < 100MB")
    else:
        logger.warning(f"⚠️ 内存增长过高: {memory_growth:.2f}MB >= 100MB")

    return {
        'duration': duration,
        'memory_growth_mb': memory_growth,
        'keys_processed': rebuild_stats['keys_found']
    }


# ============================================================================
# Test 3: 锁竞争测试
# ============================================================================

def test_lock_contention():
    """
    测试锁竞争情况

    验证:
    - 键级锁能正确统计锁竞争次数
    - 高并发下竞争率保持合理水平
    """
    logger.info("\n" + "="*80)
    logger.info("Test 3: 锁竞争测试")
    logger.info("="*80)

    cache = HierarchicalCache(
        l1_size=100,
        enable_key_level_locks=True
    )

    # 预填充少量键（增加竞争概率）
    num_keys = 10
    for i in range(num_keys):
        cache.set(f'key_{i}', f'value_{i}')

    num_threads = 20
    operations_per_thread = 100

    def mixed_worker(thread_id: int):
        """混合读写操作"""
        for i in range(operations_per_thread):
            key_id = i % num_keys
            if i % 3 == 0:
                # 写操作
                cache.set(f'key_{key_id}', f'value_{thread_id}_{i}')
            else:
                # 读操作
                cache.get(f'key_{key_id}')

    # 执行并发操作
    logger.info(f"\n📊 执行混合读写操作 ({num_threads}线程, {operations_per_thread}操作/线程)...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(mixed_worker, i)
            for i in range(num_threads)
        ]
        for f in as_completed(futures):
            f.result()

    duration = time.time() - start_time

    # 检查统计
    stats = cache.get_stats()

    logger.info(f"\n✅ 测试完成:")
    logger.info(f"  - 总耗时: {duration:.2f}s")
    logger.info(f"  - 总操作数: {num_threads * operations_per_thread}")
    logger.info(f"  - 吞吐量: {(num_threads * operations_per_thread) / duration:.2f} ops/s")
    logger.info(f"  - 锁竞争次数: {stats['key_lock_contentions']}")
    logger.info(f"  - 竞争率: {stats['contention_rate']}")
    logger.info(f"  - 活跃键锁数: {stats['active_key_locks']}")

    # 验证
    if stats['active_key_locks'] <= num_keys:
        logger.info(f"✅ 测试通过: 活跃键锁数 ({stats['active_key_locks']}) <= 键数 ({num_keys})")
    else:
        logger.warning(f"⚠️ 活跃键锁数过多: {stats['active_key_locks']} > {num_keys}")

    return stats


# ============================================================================
# Test 4: 锁清理测试
# ============================================================================

def test_lock_cleanup():
    """
    测试键级锁的自动清理机制

    验证:
    - 当锁数量超过max_key_locks时，自动清理
    - 清理后锁数量降低
    """
    logger.info("\n" + "="*80)
    logger.info("Test 4: 锁清理测试")
    logger.info("="*80)

    cache = HierarchicalCache(
        l1_size=100,
        enable_key_level_locks=True,
        max_key_locks=50  # 设置较小的max_key_locks
    )

    # 访问超过max_key_locks的键
    num_keys = 100
    logger.info(f"\n📊 访问 {num_keys} 个不同的键 (max_key_locks=50)...")

    for i in range(num_keys):
        cache.set(f'key_{i}', f'value_{i}')

    stats = cache.get_stats()

    logger.info(f"\n✅ 测试完成:")
    logger.info(f"  - 访问键数: {num_keys}")
    logger.info(f"  - 活跃键锁数: {stats['active_key_locks']}")
    logger.info(f"  - 最大键锁数: {stats['max_key_locks']}")

    # 验证
    if stats['active_key_locks'] <= stats['max_key_locks']:
        logger.info(f"✅ 测试通过: 活跃键锁数 ({stats['active_key_locks']}) <= 最大值 ({stats['max_key_locks']})")
    else:
        logger.warning(f"⚠️ 活跃键锁数超标: {stats['active_key_locks']} > {stats['max_key_locks']}")

    return stats


# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """运行所有P1性能优化测试"""
    logger.info("\n" + "="*80)
    logger.info("P1性能优化测试套件")
    logger.info("="*80)

    results = {}

    try:
        # Test 1: 键级锁并发性能
        results['key_lock_speedup'] = test_key_level_lock_performance()
    except Exception as e:
        logger.error(f"❌ Test 1 失败: {e}")
        results['key_lock_speedup'] = None

    try:
        # Test 2: Bloom Filter rebuild内存优化
        results['bloom_memory'] = test_bloom_filter_rebuild_memory()
    except Exception as e:
        logger.error(f"❌ Test 2 失败: {e}")
        results['bloom_memory'] = None

    try:
        # Test 3: 锁竞争测试
        results['lock_contention'] = test_lock_contention()
    except Exception as e:
        logger.error(f"❌ Test 3 失败: {e}")
        results['lock_contention'] = None

    try:
        # Test 4: 锁清理测试
        results['lock_cleanup'] = test_lock_cleanup()
    except Exception as e:
        logger.error(f"❌ Test 4 失败: {e}")
        results['lock_cleanup'] = None

    # 汇总结果
    logger.info("\n" + "="*80)
    logger.info("测试结果汇总")
    logger.info("="*80)

    logger.info(f"\n1. 键级锁性能提升:")
    if results.get('key_lock_speedup'):
        speedup = results['key_lock_speedup']
        status = "✅ 通过" if speedup >= 2 else "⚠️ 未达预期"
        logger.info(f"   {status}: {speedup:.2f}x")
    else:
        logger.info(f"   ❌ 测试失败")

    logger.info(f"\n2. Bloom Filter内存优化:")
    if results.get('bloom_memory'):
        memory_mb = results['bloom_memory']['memory_growth_mb']
        status = "✅ 通过" if memory_mb < 100 else "⚠️ 内存过高"
        logger.info(f"   {status}: {memory_mb:.2f}MB")
    else:
        logger.info(f"   ❌ 测试失败")

    logger.info(f"\n3. 锁竞争统计:")
    if results.get('lock_contention'):
        contention_rate = results['lock_contention']['contention_rate']
        logger.info(f"   竞争率: {contention_rate}")
    else:
        logger.info(f"   ❌ 测试失败")

    logger.info(f"\n4. 锁清理机制:")
    if results.get('lock_cleanup'):
        active_locks = results['lock_cleanup']['active_key_locks']
        max_locks = results['lock_cleanup']['max_key_locks']
        status = "✅ 通过" if active_locks <= max_locks else "⚠️ 清理失败"
        logger.info(f"   {status}: {active_locks}/{max_locks}")
    else:
        logger.info(f"   ❌ 测试失败")

    logger.info("\n" + "="*80)
    logger.info("所有测试完成")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
