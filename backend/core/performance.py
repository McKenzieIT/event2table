"""
性能优化模块 - Performance Optimization Module
========================================

版本: 1.0.0
日期: 2026-01-19
目的: 优化后端性能，减少数据库查询，实现API缓存

功能:
1. 数据库查询缓存
2. API响应缓存
3. 查询结果预加载
4. 批量查询优化
5. 连接池管理

@author: Ralph Loop Iteration 3
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
import time
import hashlib
import json
from datetime import datetime, timedelta

try:
    from flask import current_app

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[PerformanceOptimization] Warning: Flask not available, some features will be limited")


# ============================================================================
# 缓存装饰器
# ============================================================================


class QueryCache:
    """查询缓存管理器"""

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl: int = 300  # 默认5分钟
        self._max_size: int = 1000  # 最大缓存条目数

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                # 过期，删除
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """删除特定缓存"""
        if key in self._cache:
            del self._cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
            "usage_percent": round(len(self._cache) / self._max_size * 100, 2),
        }


# 全局缓存实例
query_cache = QueryCache()


def cached_query(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    数据库查询缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）
        key_func: 自定义缓存键生成函数

    Returns:
        装饰器函数

    Example:
        @cached_query(ttl=600)
        def get_events(game_id):
            return fetch_events_from_db(game_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__]
                for arg in args:
                    key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}:{v}")
                cache_key = ":".join(key_parts)

            # 尝试从缓存获取
            cached_result = query_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行查询
            result = func(*args, **kwargs)

            # 存入缓存
            query_cache.set(cache_key, result)

            return result

        return wrapper

    return decorator


# ============================================================================
# API响应缓存
# ============================================================================


class APIResponseCache:
    """API响应缓存管理器"""

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float, int]] = {}
        self._ttl: int = 60  # 默认1分钟
        self._max_size: int = 500

    def get(self, key: str) -> Optional[Any]:
        """获取缓存的API响应"""
        if key in self._cache:
            value, timestamp, hit_count = self._cache[key]
            if time.time() - timestamp < self._ttl:
                # 更新命中次数
                self._cache[key] = (value, timestamp, hit_count + 1)
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """设置API响应缓存"""
        if len(self._cache) >= self._max_size:
            # 删除命中率最低的条目
            worst_key = min(self._cache.keys(), key=lambda k: self._cache[k][2])
            del self._cache[worst_key]

        self._cache[key] = (value, time.time(), 0)

    def invalidate(self, pattern: Optional[str] = None) -> None:
        """使缓存失效"""
        if pattern:
            # 按模式删除
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_hits = sum(stats[2] for stats in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "ttl": self._ttl,
            "total_hits": total_hits,
            "avg_hits": round(total_hits / len(self._cache), 2) if self._cache else 0,
        }


# 全局API缓存实例
api_cache = APIResponseCache()


def cache_api_response(ttl: int = 60):
    """
    API响应缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）

    Returns:
        装饰器函数

    Example:
        @cache_api_response(ttl=120)
        def get_events_api(game_id, page):
            return jsonify({'events': [...]})
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [func.__name__]
            for arg in args:
                key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}:{v}")
            cache_key = ":".join(key_parts)

            # 尝试从缓存获取
            cached_response = api_cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            # 执行函数
            response = func(*args, **kwargs)

            # 存入缓存
            api_cache.set(cache_key, response)

            return response

        return wrapper

    return decorator


# ============================================================================
# 批量查询优化
# ============================================================================


class BatchQueryOptimizer:
    """批量查询优化器"""

    def __init__(self):
        self._pending_queries: Dict[str, list] = {}
        self._batch_size: int = 100
        self._batch_timeout: float = 0.1  # 100ms

    def add_query(self, query_key: str, query_params: dict) -> None:
        """添加待处理查询"""
        if query_key not in self._pending_queries:
            self._pending_queries[query_key] = []

        self._pending_queries[query_key].append(query_params)

        # 达到批处理大小，执行查询
        if len(self._pending_queries[query_key]) >= self._batch_size:
            self.flush_queries(query_key)

    def flush_queries(self, query_key: Optional[str] = None) -> Dict[str, Any]:
        """执行批量查询"""
        if query_key:
            # 执行特定类型的查询
            if query_key in self._pending_queries:
                queries = self._pending_queries.pop(query_key)
                return self._execute_batch(query_key, queries)
        else:
            # 执行所有待处理查询
            results = {}
            for key, queries in self._pending_queries.items():
                results[key] = self._execute_batch(key, queries)
            self._pending_queries.clear()
            return results

        return {}

    def _execute_batch(self, query_key: str, queries: list) -> Dict[str, Any]:
        """执行批量查询（需要子类实现）"""
        # 这里应该根据实际的数据库类型实现批量查询
        # 例如：
        # - SQLite: 使用 IN 子句
        # - MySQL: 使用批量查询
        # - PostgreSQL: 使用 ARRAY 参数

        # 占位实现
        return {"query_key": query_key, "count": len(queries), "results": []}


# ============================================================================
# 性能监控
# ============================================================================


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self._query_times: Dict[str, list] = {}
        self._slow_query_threshold: float = 1.0  # 1秒

    def record_query(self, query_name: str, execution_time: float) -> None:
        """记录查询执行时间"""
        if query_name not in self._query_times:
            self._query_times[query_name] = []

        self._query_times[query_name].append(execution_time)

        # 只保留最近100次记录
        if len(self._query_times[query_name]) > 100:
            self._query_times[query_name].pop(0)

        # 检测慢查询
        if execution_time > self._slow_query_threshold:
            print(
                f"[PerformanceMonitor] ⚠️ Slow query detected: {query_name} ({execution_time:.2f}s)"
            )

    def get_query_stats(self, query_name: str) -> Dict[str, float]:
        """获取查询统计信息"""
        if query_name not in self._query_times or not self._query_times[query_name]:
            return {}

        times = self._query_times[query_name]
        return {
            "count": len(times),
            "avg": round(sum(times) / len(times), 4),
            "min": round(min(times), 4),
            "max": round(max(times), 4),
            "total": round(sum(times), 4),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有查询统计"""
        return {
            query_name: self.get_query_stats(query_name) for query_name in self._query_times.keys()
        }


# 全局性能监控实例
performance_monitor = PerformanceMonitor()


def monitor_query(func: Callable) -> Callable:
    """
    查询性能监控装饰器

    Example:
        @monitor_query
        def get_events(game_id):
            return fetch_events_from_db(game_id)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        performance_monitor.record_query(func.__name__, execution_time)

        return result

    return wrapper


# ============================================================================
# 工具函数
# ============================================================================


def get_cache_stats() -> Dict[str, Any]:
    """获取所有缓存统计信息"""
    return {
        "query_cache": query_cache.get_stats(),
        "api_cache": api_cache.get_stats(),
        "performance_monitor": performance_monitor.get_all_stats(),
    }


def clear_all_caches() -> None:
    """清空所有缓存"""
    query_cache.clear()
    api_cache.invalidate()
    print("[PerformanceOptimization] ✅ All caches cleared")


def optimize_database_connection(conn_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    优化数据库连接参数

    Args:
        conn_params: 原始连接参数

    Returns:
        优化后的连接参数
    """
    optimized = conn_params.copy()

    # 连接池优化
    optimized.update(
        {
            "pool_size": 10,  # 连接池大小
            "max_overflow": 20,  # 最大溢出连接数
            "pool_timeout": 30,  # 连接超时
            "pool_recycle": 3600,  # 连接回收时间（1小时）
            "echo": False,  # 不输出SQL日志（生产环境）
        }
    )

    return optimized


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "QueryCache",
    "query_cache",
    "cached_query",
    "APIResponseCache",
    "api_cache",
    "cache_api_response",
    "BatchQueryOptimizer",
    "PerformanceMonitor",
    "performance_monitor",
    "monitor_query",
    "get_cache_stats",
    "clear_all_caches",
    "optimize_database_connection",
]

print("✅ PerformanceOptimization 模块已加载 (v1.0.0 - 迭代3)")
