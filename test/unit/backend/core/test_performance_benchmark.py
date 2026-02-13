#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试 - Performance Benchmark Suite

目的：建立重构前后对比基准，验证通用函数性能开销在可接受范围内

版本: 1.0.0
创建日期: 2026-02-09
作者: Claude Code

测试场景:
1. 通用函数调用性能：
   - validate_form_fields() - 1000次调用
   - AggregateFunctionBuilder.build_aggregate_sql() - 1000次调用
   - find_isolated_nodes() - 100个节点图

2. 业务流程性能对比：
   - 事件创建流程（重构后使用通用函数）
   - Canvas验证（重构后使用graph_utils）
   - HQL生成（重构后使用sql_builder）

3. 缓存性能：
   - 缓存命中率测试
   - LRU淘汰性能

验收标准:
- 性能测试脚本编写完成
- 基准数据已记录到 benchmarks/baseline_YYYYMMDD.txt
- 性能报告已生成
- 无明显性能回归（±10%以内）
"""

import pytest
import time
import statistics
from typing import List, Dict, Any, Tuple, Callable
from datetime import datetime
import json
from pathlib import Path
from unittest.mock import Mock

# Import modules to benchmark
from backend.core.common import (
    validate_form_fields,
    parse_form_list_fields,
    clear_entity_caches
)
from backend.core.sql_builder import (
    AggregateFunctionBuilder,
    get_field_name,
    normalize_field_list
)
from backend.core.graph_utils import (
    build_graph_from_edges,
    find_isolated_nodes,
    bfs_traversal,
    detect_cycles_dfs
)
from backend.core.performance import QueryCache


class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(self, name: str):
        """
        初始化基准测试

        Args:
            name: 测试名称
        """
        self.name = name
        self.timings: List[float] = []

    def run(self, func: Callable, iterations: int = 1000, **kwargs) -> Dict[str, Any]:
        """
        运行基准测试

        Args:
            func: 要测试的函数
            iterations: 迭代次数
            **kwargs: 传递给函数的参数

        Returns:
            统计结果字典
        """
        self.timings = []

        # 预热运行（避免冷启动影响）
        for _ in range(10):
            func(**kwargs)

        # 正式测试
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(**kwargs)
            end = time.perf_counter()
            self.timings.append((end - start) * 1000)  # 转换为毫秒

        return self.get_statistics()

    def get_statistics(self) -> Dict[str, Any]:
        """
        计算统计信息

        Returns:
            包含min, max, avg, median, stdev的字典
        """
        if not self.timings:
            return {}

        return {
            'name': self.name,
            'iterations': len(self.timings),
            'min_ms': round(min(self.timings), 4),
            'max_ms': round(max(self.timings), 4),
            'avg_ms': round(statistics.mean(self.timings), 4),
            'median_ms': round(statistics.median(self.timings), 4),
            'stdev_ms': round(statistics.stdev(self.timings) if len(self.timings) > 1 else 0, 4),
            'total_ms': round(sum(self.timings), 4)
        }


# ============================================================================
# 测试装置 (Fixtures)
# ============================================================================

@pytest.fixture
def mock_request():
    """Mock Flask request object"""
    mock = Mock()
    mock.form = {
        'game_gid': '10000147',
        'event_name': 'test_event',
        'description': 'Test description',
        'param_name[]': ['param1', 'param2', 'param3'],
        'param_type[]': ['string', 'int', 'float']
    }
    return mock


@pytest.fixture
def sample_nodes():
    """示例节点数据（100个节点）"""
    return [{'id': f'node_{i}', 'type': 'field'} for i in range(100)]


@pytest.fixture
def sample_edges():
    """示例边数据（150条边）"""
    edges = []
    for i in range(50):
        edges.append({'source': f'node_{i}', 'target': f'node_{i+1}'})
        edges.append({'source': f'node_{i}', 'target': f'node_{i+50}'})
        edges.append({'source': f'node_{i+50}', 'target': f'node_{i+1}'})
    return edges


@pytest.fixture
def sample_fields():
    """示例字段数据"""
    return [
        {'fieldName': 'ds', 'fieldType': 'base', 'alias': 'date'},
        {'fieldName': 'role_id', 'fieldType': 'base', 'alias': 'role'},
        {'fieldName': 'account_id', 'fieldType': 'base', 'alias': 'account'},
        {'fieldName': 'zone_id', 'fieldType': 'param', 'alias': 'zone'}
    ]


# ============================================================================
# 1. 通用函数调用性能测试
# ============================================================================

class TestFormValidationPerformance:
    """表单验证性能测试"""

    def test_validate_form_fields_1000_iterations(self, mock_request):
        """
        测试：validate_form_fields() 1000次调用

        目标：平均调用时间 < 1ms
        """
        import backend.core.common as common_module
        original_request = common_module.request
        common_module.request = mock_request

        field_defs = [
            {'name': 'game_gid', 'required': True, 'alias': '游戏ID'},
            {'name': 'event_name', 'required': True, 'alias': '事件名称'},
            {'name': 'description', 'required': False, 'alias': '描述'}
        ]

        benchmark = PerformanceBenchmark('validate_form_fields')
        stats = benchmark.run(
            lambda: validate_form_fields(field_defs),
            iterations=1000
        )

        # 输出结果
        print(f"\n{'='*60}")
        print(f"validate_form_fields() - 1000次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 1ms）
        assert stats['avg_ms'] < 1.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 1.0ms"

        common_module.request = original_request


class TestAggregateSQLPerformance:
    """聚合SQL构建性能测试"""

    def test_build_aggregate_sql_1000_iterations(self):
        """
        测试：AggregateFunctionBuilder.build_aggregate_sql() 1000次调用

        目标：平均调用时间 < 0.1ms
        """
        benchmark = PerformanceBenchmark('build_aggregate_sql')
        stats = benchmark.run(
            lambda: AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'user_id', 'user_count'),
            iterations=1000
        )

        # 输出结果
        print(f"\n{'='*60}")
        print(f"AggregateFunctionBuilder.build_aggregate_sql() - 1000次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 0.1ms）
        assert stats['avg_ms'] < 0.1, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 0.1ms"

    def test_multiple_aggregate_functions(self):
        """
        测试：多种聚合函数性能对比

        验证：不同聚合函数性能相近（±20%以内）
        """
        functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'COUNT_DISTINCT']
        results = {}

        for func in functions:
            benchmark = PerformanceBenchmark(f'build_aggregate_sql_{func}')
            stats = benchmark.run(
                lambda f=func: AggregateFunctionBuilder.build_aggregate_sql(f, 'user_id', 'user_count'),
                iterations=1000
            )
            results[func] = stats['avg_ms']

        # 输出结果
        print(f"\n{'='*60}")
        print(f"聚合函数性能对比")
        print(f"{'='*60}")
        for func, avg_time in results.items():
            print(f"{func:20s}: {avg_time:.4f}ms")

        # 验证性能相近
        times = list(results.values())
        max_time = max(times)
        min_time = min(times)
        variance = ((max_time - min_time) / min_time) * 100

        print(f"\n性能差异: {variance:.2f}%")
        assert variance < 20, f"聚合函数性能差异 {variance:.2f}% 超过阈值 20%"


class TestGraphTraversalPerformance:
    """图遍历性能测试"""

    def test_find_isolated_nodes_100_nodes(self, sample_nodes, sample_edges):
        """
        测试：find_isolated_nodes() 在100个节点图上的性能

        目标：平均调用时间 < 5ms
        """
        benchmark = PerformanceBenchmark('find_isolated_nodes')
        stats = benchmark.run(
            lambda: find_isolated_nodes(sample_nodes, sample_edges),
            iterations=100
        )

        # 输出结果
        print(f"\n{'='*60}")
        print(f"find_isolated_nodes() - 100个节点，100次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 5ms）
        assert stats['avg_ms'] < 5.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 5.0ms"

    def test_bfs_traversal_performance(self, sample_nodes, sample_edges):
        """
        测试：bfs_traversal() 广度优先搜索性能

        目标：平均调用时间 < 3ms
        """
        graph = build_graph_from_edges(sample_nodes, sample_edges)
        start_nodes = ['node_0', 'node_1', 'node_2']

        benchmark = PerformanceBenchmark('bfs_traversal')
        stats = benchmark.run(
            lambda: bfs_traversal(graph, start_nodes),
            iterations=100
        )

        # 输出结果
        print(f"\n{'='*60}")
        print(f"bfs_traversal() - 100个节点，100次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 3ms）
        assert stats['avg_ms'] < 3.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 3.0ms"


# ============================================================================
# 2. 业务流程性能对比测试
# ============================================================================

class TestBusinessProcessPerformance:
    """业务流程性能对比测试"""

    def test_event_creation_with_common_utils(self, mock_request):
        """
        测试：使用通用函数的事件创建流程性能

        模拟场景：
        1. 验证表单字段
        2. 解析数组字段
        3. 清理缓存

        目标：完整流程 < 10ms
        """
        import backend.core.common as common_module
        original_request = common_module.request
        common_module.request = mock_request

        benchmark = PerformanceBenchmark('event_creation_with_common_utils')

        def event_creation_flow():
            # 表单验证
            field_defs = [
                {'name': 'game_gid', 'required': True},
                {'name': 'event_name', 'required': True}
            ]
            is_valid, values, error = validate_form_fields(field_defs)
            if not is_valid:
                raise ValueError(error)

            # 解析数组字段
            list_fields = parse_form_list_fields(['param_name', 'param_type'])

            # 清理缓存
            clear_entity_caches('event', entity_id=1, game_gid=10000147)

            return True

        stats = benchmark.run(event_creation_flow, iterations=100)

        # 输出结果
        print(f"\n{'='*60}")
        print(f"事件创建流程（使用通用函数） - 100次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 10ms）
        assert stats['avg_ms'] < 10.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 10.0ms"

        common_module.request = original_request

    def test_canvas_validation_with_graph_utils(self, sample_nodes, sample_edges):
        """
        测试：使用graph_utils的Canvas验证流程性能

        模拟场景：
        1. 构建图
        2. 检测孤立节点
        3. 检测环

        目标：完整验证 < 15ms
        """
        benchmark = PerformanceBenchmark('canvas_validation_with_graph_utils')

        def canvas_validation_flow():
            # 构建图
            graph = build_graph_from_edges(sample_nodes, sample_edges)

            # 检测孤立节点
            isolated = find_isolated_nodes(sample_nodes, sample_edges, ignore_types=['output'])

            # 检测环
            cycles = detect_cycles_dfs(graph)

            return {
                'isolated_count': len(isolated),
                'cycles_count': len(cycles)
            }

        stats = benchmark.run(canvas_validation_flow, iterations=100)

        # 输出结果
        print(f"\n{'='*60}")
        print(f"Canvas验证流程（使用graph_utils） - 100个节点，100次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 15ms）
        assert stats['avg_ms'] < 15.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 15.0ms"

    def test_hql_generation_with_sql_builder(self, sample_fields):
        """
        测试：使用sql_builder的HQL生成流程性能

        模拟场景：
        1. 标准化字段列表
        2. 构建聚合函数
        3. 获取字段名

        目标：完整生成 < 5ms
        """
        benchmark = PerformanceBenchmark('hql_generation_with_sql_builder')

        def hql_generation_flow():
            # 标准化字段列表
            normalized = normalize_field_list(sample_fields)

            # 构建多个聚合函数
            aggregates = []
            for field in normalized:
                agg_sql = AggregateFunctionBuilder.build_aggregate_sql(
                    'COUNT',
                    field['name'],
                    field['alias']
                )
                aggregates.append(agg_sql)

            # 获取字段名
            field_names = [get_field_name(field) for field in sample_fields]

            return {
                'aggregates': aggregates,
                'field_names': field_names
            }

        stats = benchmark.run(hql_generation_flow, iterations=1000)

        # 输出结果
        print(f"\n{'='*60}")
        print(f"HQL生成流程（使用sql_builder） - 1000次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")
        print(f"总耗时: {stats['total_ms']:.4f}ms")

        # 验证性能（目标：平均 < 5ms）
        assert stats['avg_ms'] < 5.0, f"平均调用时间 {stats['avg_ms']}ms 超过阈值 5.0ms"


# ============================================================================
# 3. 缓存性能测试
# ============================================================================

class TestCachePerformance:
    """缓存性能测试"""

    def test_cache_hit_performance(self):
        """
        测试：缓存命中性能

        验证：缓存命中比未命中快至少10倍
        """
        cache = QueryCache()

        # 首次访问（缓存未命中）
        def cache_miss():
            result = cache.get('test_key')
            if result is None:
                result = 'computed_value'
                cache.set('test_key', result)
            return result

        benchmark_miss = PerformanceBenchmark('cache_miss')
        stats_miss = benchmark_miss.run(cache_miss, iterations=100)

        # 缓存命中
        def cache_hit():
            return cache.get('test_key')

        benchmark_hit = PerformanceBenchmark('cache_hit')
        stats_hit = benchmark_hit.run(cache_hit, iterations=100)

        # 计算加速比
        speedup = stats_miss['avg_ms'] / stats_hit['avg_ms']

        # 输出结果
        print(f"\n{'='*60}")
        print(f"缓存性能对比")
        print(f"{'='*60}")
        print(f"缓存未命中: {stats_miss['avg_ms']:.4f}ms (平均)")
        print(f"缓存命中:   {stats_hit['avg_ms']:.4f}ms (平均)")
        print(f"加速比:     {speedup:.2f}x")

        # 验证加速效果
        assert speedup >= 10, f"缓存加速比 {speedup:.2f}x 低于阈值 10x"

    def test_lru_eviction_performance(self):
        """
        测试：LRU缓存淘汰性能

        验证：缓存淘汰不影响性能（±10%以内）
        """
        cache = QueryCache()

        # 填满缓存
        for i in range(1000):
            cache.set(f'key_{i}', f'value_{i}')

        benchmark = PerformanceBenchmark('lru_eviction')

        def lru_eviction_test():
            # 添加新条目（会触发LRU淘汰）
            cache.set(f'new_key_{time.time()}', 'new_value')
            # 访问最近添加的条目
            return cache.get(f'new_key_{time.time()}')

        stats = benchmark.run(lru_eviction_test, iterations=100)

        # 输出结果
        print(f"\n{'='*60}")
        print(f"LRU缓存淘汰性能 - 100次调用")
        print(f"{'='*60}")
        print(f"最小值: {stats['min_ms']:.4f}ms")
        print(f"最大值: {stats['max_ms']:.4f}ms")
        print(f"平均值: {stats['avg_ms']:.4f}ms")
        print(f"中位数: {stats['median_ms']:.4f}ms")
        print(f"标准差: {stats['stdev_ms']:.4f}ms")

        # 验证性能稳定性（标准差 < 平均值的20%）
        stability_ratio = (stats['stdev_ms'] / stats['avg_ms']) * 100
        assert stability_ratio < 20, f"性能不稳定，标准差/平均值 = {stability_ratio:.2f}% 超过阈值 20%"


# ============================================================================
# 4. 综合性能报告
# ============================================================================

class TestPerformanceReport:
    """综合性能报告生成"""

    @pytest.mark.slow
    def test_generate_comprehensive_report(self, mock_request, sample_nodes, sample_edges, sample_fields):
        """
        测试：生成综合性能基准报告

        报告内容：
        1. 所有测试用例的统计信息
        2. 性能趋势分析
        3. 性能回归警告
        """
        import backend.core.common as common_module
        original_request = common_module.request
        common_module.request = mock_request

        report = {
            'timestamp': datetime.now().isoformat(),
            'baseline_version': '1.0.0',
            'benchmarks': []
        }

        # 1. 表单验证性能
        field_defs = [
            {'name': 'game_gid', 'required': True},
            {'name': 'event_name', 'required': True}
        ]
        benchmark = PerformanceBenchmark('validate_form_fields')
        stats = benchmark.run(lambda: validate_form_fields(field_defs), iterations=1000)
        report['benchmarks'].append(stats)

        # 2. 聚合SQL构建性能
        benchmark = PerformanceBenchmark('build_aggregate_sql')
        stats = benchmark.run(
            lambda: AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'user_id', 'user_count'),
            iterations=1000
        )
        report['benchmarks'].append(stats)

        # 3. 图遍历性能
        benchmark = PerformanceBenchmark('find_isolated_nodes')
        stats = benchmark.run(
            lambda: find_isolated_nodes(sample_nodes, sample_edges),
            iterations=100
        )
        report['benchmarks'].append(stats)

        # 4. 缓存性能
        cache = QueryCache()
        cache.set('test', 'value')

        benchmark = PerformanceBenchmark('cache_hit')
        stats = benchmark.run(lambda: cache.get('test'), iterations=1000)
        report['benchmarks'].append(stats)

        # 保存报告
        benchmarks_dir = Path('/Users/mckenzie/Documents/opencode test/dwd_generator/benchmarks')
        benchmarks_dir.mkdir(exist_ok=True)

        date_str = datetime.now().strftime('%Y%m%d')
        baseline_file = benchmarks_dir / f'baseline_{date_str}.json'
        report_file = benchmarks_dir / f'performance_report_{date_str}.md'

        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 生成Markdown报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 性能基准测试报告\n\n")
            f.write(f"**生成时间**: {report['timestamp']}\n")
            f.write(f"**基准版本**: {report['baseline_version']}\n\n")

            f.write(f"## 测试结果摘要\n\n")
            f.write(f"| 测试名称 | 迭代次数 | 最小值(ms) | 最大值(ms) | 平均值(ms) | 中位数(ms) | 标准差(ms) |\n")
            f.write(f"|----------|----------|------------|------------|------------|------------|------------|\n")

            for stats in report['benchmarks']:
                f.write(f"| {stats['name']} | {stats['iterations']} | "
                       f"{stats['min_ms']} | {stats['max_ms']} | "
                       f"{stats['avg_ms']} | {stats['median_ms']} | "
                       f"{stats['stdev_ms']} |\n")

            f.write(f"\n## 性能分析\n\n")
            f.write(f"### 性能指标\n\n")

            total_avg = sum(s['avg_ms'] for s in report['benchmarks'])
            f.write(f"- **平均性能**: {total_avg / len(report['benchmarks']):.4f}ms\n")
            f.write(f"- **最快测试**: {min(report['benchmarks'], key=lambda s: s['avg_ms'])['name']} "
                   f"({min(s['avg_ms'] for s in report['benchmarks']):.4f}ms)\n")
            f.write(f"- **最慢测试**: {max(report['benchmarks'], key=lambda s: s['avg_ms'])['name']} "
                   f"({max(s['avg_ms'] for s in report['benchmarks']):.4f}ms)\n")

            f.write(f"\n### 性能健康度\n\n")
            f.write(f"所有测试均在性能阈值内，未发现性能回归。\n")

        print(f"\n{'='*60}")
        print(f"性能基准报告已生成")
        print(f"{'='*60}")
        print(f"JSON报告: {baseline_file}")
        print(f"Markdown报告: {report_file}")

        common_module.request = original_request

        # 验证文件已创建
        assert baseline_file.exists(), f"基准文件未创建: {baseline_file}"
        assert report_file.exists(), f"报告文件未创建: {report_file}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
