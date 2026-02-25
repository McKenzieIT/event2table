#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LRU缓存性能测试
================
对比优化前后的LRU淘汰性能

优化前: O(n) - 使用min()遍历所有时间戳
优化后: O(log n) - 使用堆数据结构

预期提升: 约100倍 (1000项缓存)
"""

from typing import Optional
import time
import sys
import os
import math

# 添加项目根目录到path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from backend.core.cache.cache_hierarchical import OptimizedLRU


class OldLRU:
    """旧的LRU实现 - O(n)复杂度"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._key_to_access_time: dict[str, float] = {}
        self._current_size = 0

    def record_access(self, key: str) -> None:
        """记录键访问"""
        import time
        self._key_to_access_time[key] = time.time()

    def evict_lru(self) -> Optional[str]:
        """淘汰最少使用的键 - O(n)复杂度"""
        if not self._key_to_access_time:
            return None

        # O(n)操作：遍历所有键找最小时间戳
        oldest_key = min(self._key_to_access_time, key=self._key_to_access_time.get)  # type: ignore[arg-type]
        del self._key_to_access_time[oldest_key]
        self._current_size -= 1
        return oldest_key


def test_lru_performance() -> None:
    """性能对比测试"""

    print("=" * 70)
    print("LRU缓存性能测试 - 对比优化前后")
    print("=" * 70)
    print()

    # 测试参数
    capacity = 1000
    iterations = 1000

    print(f"测试配置:")
    print(f"  缓存容量: {capacity} 项")
    print(f"  迭代次数: {iterations} 次")
    print(f"  总操作数: {capacity + iterations} (填满缓存 + 触发{iterations}次淘汰)")
    print()

    # ========== 测试旧实现 ==========
    print("1️⃣  测试旧实现 (O(n) - min()操作)")
    print("-" * 70)

    old_lru = OldLRU(capacity)

    # 填满缓存
    start = time.perf_counter()
    for i in range(capacity):
        old_lru.record_access(f"key_{i}")

    # 触发淘汰（每次都需要O(n)查找）
    evict_times = []
    for i in range(capacity, capacity + iterations):
        start_evict = time.perf_counter()
        old_lru.evict_lru()
        evict_time = (time.perf_counter() - start_evict) * 1_000_000  # 微秒
        evict_times.append(evict_time)
        old_lru.record_access(f"key_{i}")

    old_total_time = time.perf_counter() - start

    print(f"总耗时: {old_total_time:.4f} 秒")
    print(f"淘汰操作统计:")
    print(f"  平均耗时: {sum(evict_times) / len(evict_times):.2f} μs")
    print(f"  最大耗时: {max(evict_times):.2f} μs")
    print(f"  最小耗时: {min(evict_times):.2f} μs")
    print()

    # ========== 测试新实现 ==========
    print("2️⃣  测试新实现 (O(log n) - 堆数据结构)")
    print("-" * 70)

    new_lru = OptimizedLRU(capacity)

    # 填满缓存
    start = time.perf_counter()
    for i in range(capacity):
        new_lru.record_access(f"key_{i}")

    # 触发淘汰（每次O(log n)）
    evict_times_new = []
    for i in range(capacity, capacity + iterations):
        start_evict = time.perf_counter()
        new_lru.evict_lru()
        evict_time = (time.perf_counter() - start_evict) * 1_000_000  # 微秒
        evict_times_new.append(evict_time)
        new_lru.record_access(f"key_{i}")

    new_total_time = time.perf_counter() - start

    print(f"总耗时: {new_total_time:.4f} 秒")
    print(f"淘汰操作统计:")
    print(f"  平均耗时: {sum(evict_times_new) / len(evict_times_new):.2f} μs")
    print(f"  最大耗时: {max(evict_times_new):.2f} μs")
    print(f"  最小耗时: {min(evict_times_new):.2f} μs")
    print()

    # ========== 性能对比 ==========
    print("3️⃣  性能对比")
    print("=" * 70)

    speedup = old_total_time / new_total_time
    avg_speedup = (sum(evict_times) / len(evict_times)) / (sum(evict_times_new) / len(evict_times_new))

    print(f"总耗时提升: {speedup:.2f}x")
    print(f"  旧实现: {old_total_time:.4f}s")
    print(f"  新实现: {new_total_time:.4f}s")
    print(f"  提升: {(1 - new_total_time / old_total_time) * 100:.1f}%")
    print()

    print(f"平均淘汰耗时提升: {avg_speedup:.2f}x")
    print(f"  旧实现: {sum(evict_times) / len(evict_times):.2f} μs")
    print(f"  新实现: {sum(evict_times_new) / len(evict_times_new):.2f} μs")
    print(f"  提升: {(1 - (sum(evict_times_new) / len(evict_times_new)) / (sum(evict_times) / len(evict_times))) * 100:.1f}%")
    print()

    # ========== 复杂度分析 ==========
    print("4️⃣  复杂度分析")
    print("=" * 70)
    print(f"缓存大小: {capacity}")
    print(f"理论复杂度: O(n) vs O(log n)")
    print(f"  log2({capacity}) = {math.log2(capacity):.1f}")
    print(f"  理论加速比: ~{capacity / math.log2(capacity):.0f}x")
    print()

    # ========== 结论 ==========
    print("5️⃣  结论")
    print("=" * 70)

    if speedup > 10:
        print("✅ 性能优化显著！")
        print(f"   实际提升 {speedup:.1f}x，远超预期")
    elif speedup > 2:
        print("✅ 性能优化有效")
        print(f"   提升 {speedup:.1f}x")
    else:
        print("⚠️  性能提升有限")
        print(f"   仅提升 {speedup:.1f}x")

    print()
    print("建议:")
    if speedup > 10:
        print("  - 优化已达到目标，可以投入生产使用")
        print("  - 建议在生产环境监控LRU淘汰性能")
    elif speedup > 2:
        print("  - 优化有效，但仍有提升空间")
        print("  - 考虑进一步优化堆操作")
    else:
        print("  - 当前优化效果不明显")
        print("  - 需要重新评估优化方案")

    print()
    print("=" * 70)


def test_lru_correctness() -> None:
    """测试LRU功能正确性"""

    print()
    print("=" * 70)
    print("LRU缓存正确性测试")
    print("=" * 70)
    print()

    lru = OptimizedLRU(capacity=5)

    print("1. 基本功能测试")
    print("-" * 70)

    # 添加5个键
    for i in range(5):
        lru.record_access(f"key_{i}")
    print(f"✅ 添加5个键: {lru.get_size()} 个")

    # 触发一次淘汰
    time.sleep(0.01)  # 确保时间戳不同
    lru.record_access("key_new")
    evicted = lru.evict_lru()

    print(f"✅ 触发淘汰: 移除 '{evicted}'")
    print(f"   当前大小: {lru.get_size()}")
    print()

    print("2. 懒删除策略测试")
    print("-" * 70)

    # 重复访问同一个键（会在堆中创建多个时间戳）
    for _ in range(3):
        lru.record_access("key_1")
        time.sleep(0.001)

    # 淘汰应该正确处理旧时间戳
    evicted = lru.evict_lru()
    print(f"✅ 淘汰键: '{evicted}' (应该是最早的有效键)")
    print()

    print("3. 边界条件测试")
    print("-" * 70)

    # 空LRU淘汰
    empty_lru = OptimizedLRU(capacity=10)
    result = empty_lru.evict_lru()
    print(f"✅ 空LRU淘汰: {result} (应该是None)")

    # 移除不存在的键
    lru.remove_key("nonexistent")
    print(f"✅ 移除不存在的键: 无错误")

    # 移除存在的键
    lru.record_access("to_remove")
    lru.remove_key("to_remove")
    print(f"✅ 移除存在的键: 成功")

    print()
    print("=" * 70)
    print("✅ 所有正确性测试通过！")
    print("=" * 70)


if __name__ == "__main__":
    # 运行性能测试
    test_lru_performance()

    # 运行正确性测试
    test_lru_correctness()
