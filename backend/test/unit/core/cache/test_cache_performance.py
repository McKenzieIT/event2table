#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统性能测试
==================

测试三级分层缓存系统的性能表现, 验证是否达到预期目标: 

目标指标: 
- L1命中率: ≥60%
- L2命中率: ≥30%
- 总体命中率: ≥90%
- L1响应时间: <1ms
- L2响应时间: 5-10ms
- L3响应时间: 50-200ms

版本: 1.0.0
日期: 2026-01-28
"""

import sys
import os
import time
import statistics
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.cache.cache_system import hierarchical_cache, CacheKeyBuilder
from backend.core.config.config import CacheConfig


class CachePerformanceTester:
    """缓存性能测试器"""

    def __init__(self):
        self.test_data = {}
        self.results = {}

    def setup_test_data(self, hot_items: int = 100, warm_items: int = 1000):
        """
        准备测试数据

        Args:
            hot_items: 热点数据数量（用于L1缓存）
            warm_items: 温热数据数量（用于L2缓存）
        """
        print("=" * 60)
        print("准备测试数据...")
        print("=" * 60)

        # 热点数据(预期会被L1缓存)
        print(f"📦 准备{hot_items}个热点数据...")
        for i in range(hot_items):
            key = f'hot_item_{i}'
            self.test_data[key] = {'id': i, 'name': f'Hot Item {i}', 'value': i * 100}

        # 温热数据(预期会被L2缓存)
        print(f"📦 准备{warm_items}个温热数据...")
        for i in range(warm_items):
            key = f'warm_item_{i}'
            self.test_data[key] = {
                'id': hot_items + i,
                'name': f'Warm Item {i}',
                'value': (hot_items + i) * 100,
            }

        print(f"✅ 测试数据准备完成: {len(self.test_data)}个数据项")

    def test_write_performance(self):
        """测试写入性能"""
        print("\n" + "=" * 60)
        print("📊 测试1: 写入性能")
        print("=" * 60)

        # 测试L1写入性能
        print("\n🔥 测试L1写入性能（热点数据）...")
        l1_write_times = []
        for i in range(100):
            key = f'hot_item_{i}'
            data = self.test_data[key]

            start = time.perf_counter()
            hierarchical_cache.set('test.data', data, id=key)
            duration = (time.perf_counter() - start) * 1000  # 转换为毫秒

            l1_write_times.append(duration)

        print(f"✅ L1写入性能:")
        print(f"   - 平均: {statistics.mean(l1_write_times):.3f}ms")
        print(f"   - 最小: {min(l1_write_times):.3f}ms")
        print(f"   - 最大: {max(l1_write_times):.3f}ms")

        # 测试L2写入性能
        print("\n🔥 测试L2写入性能（温热数据）...")
        l2_write_times = []
        for i in range(100):
            key = f'warm_item_{i}'
            data = self.test_data[key]

            start = time.perf_counter()
            hierarchical_cache.set('test.data', data, id=key)
            duration = (time.perf_counter() - start) * 1000

            l2_write_times.append(duration)

        print(f"✅ L2写入性能:")
        print(f"   - 平均: {statistics.mean(l2_write_times):.3f}ms")
        print(f"   - 最小: {min(l2_write_times):.3f}ms")
        print(f"   - 最大: {max(l2_write_times):.3f}ms")

        self.results['write'] = {
            'l1_avg_ms': statistics.mean(l1_write_times),
            'l2_avg_ms': statistics.mean(l2_write_times),
        }

    def test_l1_read_performance(self):
        """测试L1读取性能"""
        print("\n" + "=" * 60)
        print("📊 测试2: L1读取性能（热点数据）")
        print("=" * 60)

        # 预热: 将热点数据写入缓存
        print("\n🔥 预热L1缓存...")
        for i in range(100):
            key = f'hot_item_{i}'
            data = self.test_data[key]
            hierarchical_cache.set('test.data', data, id=key)

        # 测试L1读取
        print("\n⚡ 测试L1读取性能（1000次读取）...")
        l1_read_times = []
        for i in range(1000):
            key = f'hot_item_{i % 100}'  # 循环使用前100个热点数据

            start = time.perf_counter()
            result = hierarchical_cache.get('test.data', id=key)
            duration = (time.perf_counter() - start) * 1000

            l1_read_times.append(duration)

        print(f"✅ L1读取性能:")
        print(f"   - 平均: {statistics.mean(l1_read_times):.3f}ms")
        print(f"   - 最小: {min(l1_read_times):.3f}ms")
        print(f"   - 最大: {max(l1_read_times):.3f}ms")
        print(f"   - P95: {sorted(l1_read_times)[int(len(l1_read_times) * 0.95)]:.3f}ms")

        # 验证是否达到目标(<1ms)
        avg_time = statistics.mean(l1_read_times)
        if avg_time < 1.0:
            print(f"   ✅ 达到目标: <1ms")
        else:
            print(f"   ⚠️ 未达到目标: 当前{avg_time:.3f}ms, 目标<1ms")

        self.results['l1_read'] = {
            'avg_ms': avg_time,
            'min_ms': min(l1_read_times),
            'max_ms': max(l1_read_times),
            'p95_ms': sorted(l1_read_times)[int(len(l1_read_times) * 0.95)],
        }

    def test_l2_read_performance(self):
        """测试L2读取性能"""
        print("\n" + "=" * 60)
        print("📊 测试3: L2读取性能（温热数据）")
        print("=" * 60)

        # 清空L1缓存, 确保从L2读取
        hierarchical_cache.clear_l1()

        # 预热: 将温热数据写入L2
        print("\n🔥 预热L2缓存...")
        for i in range(100):
            key = f'warm_item_{i}'
            data = self.test_data[key]
            hierarchical_cache.set('test.data', data, id=key)

        # 测试L2读取
        print("\n⚡ 测试L2读取性能（1000次读取）...")
        l2_read_times = []
        for i in range(1000):
            key = f'warm_item_{i % 100}'  # 循环使用前100个温热数据

            start = time.perf_counter()
            result = hierarchical_cache.get('test.data', id=key)
            duration = (time.perf_counter() - start) * 1000

            l2_read_times.append(duration)

        print(f"✅ L2读取性能:")
        print(f"   - 平均: {statistics.mean(l2_read_times):.3f}ms")
        print(f"   - 最小: {min(l2_read_times):.3f}ms")
        print(f"   - 最大: {max(l2_read_times):.3f}ms")
        print(f"   - P95: {sorted(l2_read_times)[int(len(l2_read_times) * 0.95)]:.3f}ms")

        # 验证是否达到目标(5-10ms)
        avg_time = statistics.mean(l2_read_times)
        if 5.0 <= avg_time <= 10.0:
            print(f"   ✅ 达到目标: 5-10ms")
        else:
            print(f"   ⚠️ 未完全达到目标: 当前{avg_time:.3f}ms, 目标5-10ms")

        self.results['l2_read'] = {
            'avg_ms': avg_time,
            'min_ms': min(l2_read_times),
            'max_ms': max(l2_read_times),
            'p95_ms': sorted(l2_read_times)[int(len(l2_read_times) * 0.95)],
        }

    def test_hit_rate(self):
        """测试缓存命中率"""
        print("\n" + "=" * 60)
        print("📊 测试4: 缓存命中率")
        print("=" * 60)

        # 重置统计
        hierarchical_cache.reset_stats()

        # 准备测试场景: 70%热点数据 + 30%温热数据
        hot_count = 70
        warm_count = 30

        # 预热数据
        print(f"\n🔥 预热数据: {hot_count}个热点 + {warm_count}个温热...")

        # 热点数据(会被L1缓存)
        for i in range(hot_count):
            key = f'hot_item_{i}'
            data = self.test_data.get(key, {'id': i, 'name': f'Hot {i}'})
            hierarchical_cache.set('test.data', data, id=key)

        # 温热数据(会被L2缓存)
        for i in range(warm_count):
            key = f'warm_item_{i}'
            data = self.test_data.get(key, {'id': 100 + i, 'name': f'Warm {i}'})
            hierarchical_cache.set('test.data', data, id=key)

        # 清空L1, 强制使用L2
        hierarchical_cache.clear_l1()

        # 执行混合读取测试
        print(f"\n⚡ 执行混合读取测试（1000次: {hot_count}%热点 + {warm_count}%温热）...")

        for i in range(1000):
            if i < hot_count * 10:  # 前700次: 热点数据
                key = f'hot_item_{i % hot_count}'
            else:  # 后300次: 温热数据
                key = f'warm_item_{i % warm_count}'

            result = hierarchical_cache.get('test.data', id=key)

        # 获取统计信息
        stats = hierarchical_cache.get_stats()

        print(f"\n✅ 缓存命中率统计:")
        print(
            f"   - L1命中: {stats['l1_hits']}次 ({stats['l1_hits'] / stats['total_requests'] * 100:.1f}%)"
        )
        print(
            f"   - L2命中: {stats['l2_hits']}次 ({stats['l2_hits'] / stats['total_requests'] * 100:.1f}%)"
        )
        print(
            f"   - 未命中: {stats['misses']}次 ({stats['misses'] / stats['total_requests'] * 100:.1f}%)"
        )
        print(f"   - 总体命中率: {stats['hit_rate']}")

        # 验证是否达到目标
        hit_rate = float(stats['hit_rate'].rstrip('%'))
        if hit_rate >= 90.0:
            print(f"   ✅ 达到目标: 总体命中率 ≥90%")
        else:
            print(f"   ⚠️ 未达到目标: 当前{hit_rate:.1f}%, 目标≥90%")

        self.results['hit_rate'] = {
            'l1_hits': stats['l1_hits'],
            'l2_hits': stats['l2_hits'],
            'misses': stats['misses'],
            'hit_rate': hit_rate,
            'total_requests': stats['total_requests'],
        }

    def test_cache_capacity(self):
        """测试缓存容量管理"""
        print("\n" + "=" * 60)
        print("📊 测试5: 缓存容量管理（LRU淘汰）")
        print("=" * 60)

        # 重置统计
        hierarchical_cache.reset_stats()
        hierarchical_cache.clear_l1()

        l1_capacity = hierarchical_cache.l1_size

        print(f"\n📦 L1缓存容量: {l1_capacity}条")
        print(f"🔥 写入{l1_capacity + 100}条数据以触发LRU淘汰...")

        # 写入超过L1容量的数据
        for i in range(l1_capacity + 100):
            data = {'id': i, 'name': f'Item {i}'}
            hierarchical_cache.set('test.data', data, id=f'item_{i}')

        stats = hierarchical_cache.get_stats()

        print(f"\n✅ L1缓存状态:")
        print(f"   - 当前大小: {stats['l1_size']}条")
        print(f"   - 容量: {stats['l1_capacity']}条")
        print(f"   - 使用率: {stats['l1_usage']}")
        print(f"   - L1淘汰次数: {stats['l1_evictions']}次")

        # 验证LRU是否工作
        if stats['l1_evictions'] > 0:
            print(f"   ✅ LRU淘汰正常工作: 已淘汰{stats['l1_evictions']}个旧条目")
        else:
            print(f"   ⚠️ LRU淘汰未触发")

        self.results['capacity'] = {
            'l1_size': stats['l1_size'],
            'l1_capacity': stats['l1_capacity'],
            'l1_evictions': stats['l1_evictions'],
        }

    def test_concurrent_access(self):
        """测试并发访问性能"""
        print("\n" + "=" * 60)
        print("📊 测试6: 并发访问性能")
        print("=" * 60)

        # 预热数据
        print(f"\n🔥 预热100个数据...")
        for i in range(100):
            data = {'id': i, 'name': f'Item {i}'}
            hierarchical_cache.set('test.data', data, id=f'item_{i}')

        # 模拟并发访问(使用循环模拟)
        print(f"\n⚡ 模拟并发访问（100个线程, 每个10次读取）...")
        import threading

        read_times = []

        def worker(worker_id):
            """工作线程"""
            for i in range(10):
                key = f'item_{(worker_id * 10 + i) % 100}'

                start = time.perf_counter()
                result = hierarchical_cache.get('test.data', id=key)
                duration = (time.perf_counter() - start) * 1000

                read_times.append(duration)

        # 启动100个工作线程
        threads = []
        start_time = time.perf_counter()

        for i in range(100):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        total_time = (time.perf_counter() - start_time) * 1000

        print(f"\n✅ 并发访问性能:")
        print(f"   - 总耗时: {total_time:.2f}ms")
        print(f"   - 总请求数: {len(read_times)}")
        print(f"   - QPS: {len(read_times) / (total_time / 1000):.0f}")
        print(f"   - 平均响应时间: {statistics.mean(read_times):.3f}ms")

        # 验证QPS是否达到目标(≥1000)
        qps = len(read_times) / (total_time / 1000)
        if qps >= 1000:
            print(f"   ✅ 达到目标: QPS ≥1000")
        else:
            print(f"   ⚠️ 未达到目标: 当前{qps:.0f} QPS, 目标≥1000")

        self.results['concurrent'] = {
            'total_time_ms': total_time,
            'total_requests': len(read_times),
            'qps': qps,
            'avg_response_ms': statistics.mean(read_times),
        }

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📋 性能测试报告")
        print("=" * 60)

        # 写入性能
        if 'write' in self.results:
            print(f"\n✍️  写入性能:")
            print(f"   - L1平均: {self.results['write']['l1_avg_ms']:.3f}ms")
            print(f"   - L2平均: {self.results['write']['l2_avg_ms']:.3f}ms")

        # 读取性能
        if 'l1_read' in self.results:
            print(f"\n⚡ L1读取性能:")
            print(f"   - 平均: {self.results['l1_read']['avg_ms']:.3f}ms")
            print(f"   - P95: {self.results['l1_read']['p95_ms']:.3f}ms")
            status = "✅" if self.results['l1_read']['avg_ms'] < 1.0 else "⚠️"
            print(f"   - 目标<1ms: {status}")

        if 'l2_read' in self.results:
            print(f"\n⚡ L2读取性能:")
            print(f"   - 平均: {self.results['l2_read']['avg_ms']:.3f}ms")
            print(f"   - P95: {self.results['l2_read']['p95_ms']:.3f}ms")
            status = "✅" if 5.0 <= self.results['l2_read']['avg_ms'] <= 10.0 else "⚠️"
            print(f"   - 目标5-10ms: {status}")

        # 命中率
        if 'hit_rate' in self.results:
            print(f"\n🎯 缓存命中率:")
            print(f"   - L1命中: {self.results['hit_rate']['l1_hits']}次")
            print(f"   - L2命中: {self.results['hit_rate']['l2_hits']}次")
            print(f"   - 总体命中率: {self.results['hit_rate']['hit_rate']:.1f}%")
            status = "✅" if self.results['hit_rate']['hit_rate'] >= 90.0 else "⚠️"
            print(f"   - 目标≥90%: {status}")

        # 容量管理
        if 'capacity' in self.results:
            print(f"\n📦 缓存容量管理:")
            print(
                f"   - L1使用: {self.results['capacity']['l1_size']}/{self.results['capacity']['l1_capacity']}"
            )
            print(f"   - L1淘汰: {self.results['capacity']['l1_evictions']}次")

        # 并发性能
        if 'concurrent' in self.results:
            print(f"\n🚀 并发性能:")
            print(f"   - QPS: {self.results['concurrent']['qps']:.0f}")
            print(f"   - 平均响应: {self.results['concurrent']['avg_response_ms']:.3f}ms")
            status = "✅" if self.results['concurrent']['qps'] >= 1000 else "⚠️"
            print(f"   - 目标≥1000 QPS: {status}")

        # 总体评估
        print("\n" + "=" * 60)
        print("📊 总体评估")
        print("=" * 60)

        passed = 0
        total = 0

        # L1响应时间
        if 'l1_read' in self.results:
            total += 1
            if self.results['l1_read']['avg_ms'] < 1.0:
                passed += 1

        # L2响应时间
        if 'l2_read' in self.results:
            total += 1
            if 5.0 <= self.results['l2_read']['avg_ms'] <= 10.0:
                passed += 1

        # 命中率
        if 'hit_rate' in self.results:
            total += 1
            if self.results['hit_rate']['hit_rate'] >= 90.0:
                passed += 1

        # QPS
        if 'concurrent' in self.results:
            total += 1
            if self.results['concurrent']['qps'] >= 1000:
                passed += 1

        print(f"\n✅ 通过测试: {passed}/{total}")

        if passed == total:
            print(f"🎉 所有性能指标均达到预期目标！")
        else:
            print(f"⚠️ 部分性能指标未达到预期, 建议进一步优化")

        print("=" * 60)

    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始缓存性能测试...")
        print("=" * 60)

        # 准备测试数据
        self.setup_test_data(hot_items=100, warm_items=1000)

        # 运行测试
        self.test_write_performance()
        self.test_l1_read_performance()
        self.test_l2_read_performance()
        self.test_hit_rate()
        self.test_cache_capacity()
        self.test_concurrent_access()

        # 生成报告
        self.generate_report()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("缓存系统性能测试工具")
    print("Version: 1.0.0")
    print("=" * 60)

    tester = CachePerformanceTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
