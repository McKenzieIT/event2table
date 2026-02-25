"""
GraphQL性能监控中间件

监控查询性能、DataLoader命中率、缓存效率等指标
"""

import time
import logging
from graphene import Middleware
from backend.core.cache.cache_system import HierarchicalCache
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class PerformanceMonitorMiddleware:
    """
    性能监控中间件

    记录每个查询的执行时间、复杂度等指标
    """

    def __init__(self):
        self.metrics = defaultdict(list)
        self.cache = HierarchicalCache()

    def resolve(self, next, root, info, **args):
        # 记录开始时间
        start_time = time.time()
        operation_type = info.operation.operation.value
        field_name = info.field_name

        try:
            # 执行查询
            result = next(root, info, **args)
            return result
        finally:
            # 计算执行时间
            duration = time.time() - start_time

            # 记录指标
            metric_key = f"{operation_type}:{field_name}"
            self.metrics[metric_key].append(duration)

            # 存储到Redis用于分析
            try:
                self.cache.redis_client.lpush(
                    f'graphql:performance:{metric_key}',
                    json.dumps({
                        'duration': duration,
                        'timestamp': time.time(),
                        'args': str(args)[:100]  # 限制长度
                    })
                )

                # 只保留最近1000条记录
                self.cache.redis_client.ltrim(
                    f'graphql:performance:{metric_key}',
                    0,
                    999
                )
            except Exception as e:
                logger.error(f"Failed to store performance metric: {e}")

            # 记录慢查询
            if duration > 1.0:  # 超过1秒
                logger.warning(
                    f"Slow GraphQL query: {metric_key} took {duration:.2f}s"
                )
            elif duration > 0.5:  # 超过0.5秒
                logger.info(
                    f"Moderate GraphQL query: {metric_key} took {duration:.2f}s"
                )

    def get_metrics(self):
        """获取性能指标统计"""
        stats = {}
        for key, durations in self.metrics.items():
            if durations:
                stats[key] = {
                    'count': len(durations),
                    'avg': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'total': sum(durations)
                }
        return stats

    def get_slow_queries(self, threshold=1.0):
        """获取慢查询列表"""
        slow_queries = []
        for key, durations in self.metrics.items():
            slow_count = sum(1 for d in durations if d > threshold)
            if slow_count > 0:
                slow_queries.append({
                    'query': key,
                    'slow_count': slow_count,
                    'total_count': len(durations)
                })
        return slow_queries


class DataLoaderMonitorMiddleware:
    """
    DataLoader监控中间件

    监控DataLoader的命中率、批量加载效率
    """

    def __init__(self):
        self.dataloader_stats = defaultdict(lambda: {
            'total_requests': 0,
            'cache_hits': 0,
            'batch_loads': 0,
            'total_keys': 0
        })

    def resolve(self, next, root, info, **args):
        # 在这里可以拦截DataLoader的调用
        # 实际实现中，需要在DataLoader中添加监控逻辑
        return next(root, info, **args)

    def record_dataloader_call(self, loader_name: str, keys_count: int, cache_hits: int):
        """记录DataLoader调用"""
        stats = self.dataloader_stats[loader_name]
        stats['total_requests'] += 1
        stats['total_keys'] += keys_count
        stats['cache_hits'] += cache_hits
        stats['batch_loads'] += 1

    def get_dataloader_stats(self):
        """获取DataLoader统计"""
        stats = {}
        for loader_name, data in self.dataloader_stats.items():
            if data['total_keys'] > 0:
                hit_rate = data['cache_hits'] / data['total_keys']
            else:
                hit_rate = 0

            stats[loader_name] = {
                **data,
                'hit_rate': hit_rate,
                'avg_keys_per_batch': data['total_keys'] / max(data['batch_loads'], 1)
            }
        return stats


class CacheMonitorMiddleware:
    """
    缓存监控中间件

    监控缓存命中率、缓存大小、失效频率
    """

    def __init__(self):
        self.cache = HierarchicalCache()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }

    def resolve(self, next, root, info, **args):
        # 监控缓存使用情况
        return next(root, info, **args)

    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_stats['hits'] += 1

    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_stats['misses'] += 1

    def record_cache_set(self):
        """记录缓存写入"""
        self.cache_stats['sets'] += 1

    def record_cache_delete(self):
        """记录缓存删除"""
        self.cache_stats['deletes'] += 1

    def get_cache_stats(self):
        """获取缓存统计"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / max(total_requests, 1)

        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class QueryComplexityMonitorMiddleware:
    """
    查询复杂度监控中间件

    分析查询复杂度，防止过度复杂的查询
    """

    def __init__(self, max_complexity=1000):
        self.max_complexity = max_complexity
        self.complexity_stats = defaultdict(int)

    def resolve(self, next, root, info, **args):
        # 计算查询复杂度
        complexity = self._calculate_complexity(info)

        # 记录复杂度
        operation = info.operation.operation.value
        field_name = info.field_name
        key = f"{operation}:{field_name}"
        self.complexity_stats[key] += complexity

        # 检查是否超过限制
        if complexity > self.max_complexity:
            logger.warning(
                f"Query complexity {complexity} exceeds limit {self.max_complexity} "
                f"for {key}"
            )

        return next(root, info, **args)

    def _calculate_complexity(self, info):
        """计算查询复杂度"""
        # 简单的复杂度计算
        # 实际实现中需要更复杂的算法
        complexity = 1

        # 检查是否有嵌套字段
        if hasattr(info, 'field_nodes') and info.field_nodes:
            for node in info.field_nodes:
                if hasattr(node, 'selection_set') and node.selection_set:
                    complexity += len(node.selection_set.selections)

        return complexity

    def get_complexity_stats(self):
        """获取复杂度统计"""
        return dict(self.complexity_stats)


class MetricsCollector:
    """
    指标收集器

    收集所有中间件的指标，提供统一的接口
    """

    def __init__(self):
        self.performance_monitor = PerformanceMonitorMiddleware()
        self.dataloader_monitor = DataLoaderMonitorMiddleware()
        self.cache_monitor = CacheMonitorMiddleware()
        self.complexity_monitor = QueryComplexityMonitorMiddleware()

    def get_all_metrics(self):
        """获取所有指标"""
        return {
            'performance': self.performance_monitor.get_metrics(),
            'slow_queries': self.performance_monitor.get_slow_queries(),
            'dataloader': self.dataloader_monitor.get_dataloader_stats(),
            'cache': self.cache_monitor.get_cache_stats(),
            'complexity': self.complexity_monitor.get_complexity_stats(),
            'timestamp': time.time()
        }

    def get_dashboard_data(self):
        """获取Dashboard展示数据"""
        metrics = self.get_all_metrics()

        # 计算总体统计
        total_queries = sum(
            stats['count']
            for stats in metrics['performance'].values()
        )

        avg_response_time = sum(
            stats['avg'] * stats['count']
            for stats in metrics['performance'].values()
        ) / max(total_queries, 1)

        return {
            'summary': {
                'total_queries': total_queries,
                'avg_response_time': avg_response_time,
                'slow_query_count': len(metrics['slow_queries']),
                'cache_hit_rate': metrics['cache']['hit_rate'],
                'dataloader_hit_rate': sum(
                    stats['hit_rate']
                    for stats in metrics['dataloader'].values()
                ) / max(len(metrics['dataloader']), 1)
            },
            'details': metrics
        }


# 全局指标收集器
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
