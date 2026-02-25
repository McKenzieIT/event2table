#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控模块

提供缓存命中率、响应时间、系统吞吐量等性能指标监控
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.metrics = defaultdict(lambda: defaultdict(int))
            self.metrics['cache_hits'] = 0
            self.metrics['cache_misses'] = 0
            self.metrics['total_requests'] = 0
            self.metrics['total_response_time'] = 0.0
            self.metrics['slow_requests'] = 0  # 响应时间 > 100ms
            self.metrics['error_count'] = 0
            self.metrics['db_queries'] = 0
            self.metrics['db_query_time'] = 0.0
            self.metrics['api_calls'] = defaultdict(int)
            self.metrics['api_response_times'] = defaultdict(list)
            self.metrics['start_time'] = datetime.now()
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics['cache_misses'] += 1
    
    def record_request(self, response_time: float, is_error: bool = False):
        """记录请求"""
        self.metrics['total_requests'] += 1
        self.metrics['total_response_time'] += response_time
        if response_time > 0.1:  # 100ms
            self.metrics['slow_requests'] += 1
        if is_error:
            self.metrics['error_count'] += 1
    
    def record_db_query(self, query_time: float):
        """记录数据库查询"""
        self.metrics['db_queries'] += 1
        self.metrics['db_query_time'] += query_time
    
    def record_api_call(self, endpoint: str, response_time: float):
        """记录API调用"""
        self.metrics['api_calls'][endpoint] += 1
        self.metrics['api_response_times'][endpoint].append(response_time)
        # 只保留最近100次记录
        if len(self.metrics['api_response_times'][endpoint]) > 100:
            self.metrics['api_response_times'][endpoint].pop(0)
    
    def get_cache_hit_ratio(self) -> float:
        """获取缓存命中率"""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return (self.metrics['cache_hits'] / total) * 100
    
    def get_avg_response_time(self) -> float:
        """获取平均响应时间"""
        if self.metrics['total_requests'] == 0:
            return 0.0
        return self.metrics['total_response_time'] / self.metrics['total_requests']
    
    def get_avg_db_query_time(self) -> float:
        """获取平均数据库查询时间"""
        if self.metrics['db_queries'] == 0:
            return 0.0
        return self.metrics['db_query_time'] / self.metrics['db_queries']
    
    def get_throughput(self) -> float:
        """获取系统吞吐量（QPS）"""
        elapsed = (datetime.now() - self.metrics['start_time']).total_seconds()
        if elapsed == 0:
            return 0.0
        return self.metrics['total_requests'] / elapsed
    
    def get_slow_request_ratio(self) -> float:
        """获取慢请求比例"""
        if self.metrics['total_requests'] == 0:
            return 0.0
        return (self.metrics['slow_requests'] / self.metrics['total_requests']) * 100
    
    def get_error_ratio(self) -> float:
        """获取错误率"""
        if self.metrics['total_requests'] == 0:
            return 0.0
        return (self.metrics['error_count'] / self.metrics['total_requests']) * 100
    
    def get_api_stats(self, endpoint: str) -> Dict[str, Any]:
        """获取API统计信息"""
        calls = self.metrics['api_calls'].get(endpoint, 0)
        times = self.metrics['api_response_times'].get(endpoint, [])
        
        if not times:
            return {
                'endpoint': endpoint,
                'calls': calls,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0
            }
        
        return {
            'endpoint': endpoint,
            'calls': calls,
            'avg_response_time': sum(times) / len(times),
            'min_response_time': min(times),
            'max_response_time': max(times)
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            'cache_hit_ratio': self.get_cache_hit_ratio(),
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'avg_response_time': self.get_avg_response_time(),
            'avg_db_query_time': self.get_avg_db_query_time(),
            'throughput': self.get_throughput(),
            'slow_request_ratio': self.get_slow_request_ratio(),
            'error_ratio': self.get_error_ratio(),
            'total_requests': self.metrics['total_requests'],
            'total_db_queries': self.metrics['db_queries'],
            'uptime': (datetime.now() - self.metrics['start_time']).total_seconds()
        }
    
    def reset_metrics(self):
        """重置指标"""
        self.metrics.clear()
        self.metrics['cache_hits'] = 0
        self.metrics['cache_misses'] = 0
        self.metrics['total_requests'] = 0
        self.metrics['total_response_time'] = 0.0
        self.metrics['slow_requests'] = 0
        self.metrics['error_count'] = 0
        self.metrics['db_queries'] = 0
        self.metrics['db_query_time'] = 0.0
        self.metrics['api_calls'] = defaultdict(int)
        self.metrics['api_response_times'] = defaultdict(list)
        self.metrics['start_time'] = datetime.now()


def monitor_performance(endpoint: Optional[str] = None):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            is_error = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                is_error = True
                raise e
            finally:
                response_time = time.time() - start_time
                monitor.record_request(response_time, is_error)
                if endpoint:
                    monitor.record_api_call(endpoint, response_time)
        return wrapper
    return decorator


class PerformanceAlerts:
    """性能告警"""
    
    @staticmethod
    def check_cache_hit_ratio(monitor: PerformanceMonitor, threshold: float = 70.0) -> bool:
        """检查缓存命中率"""
        ratio = monitor.get_cache_hit_ratio()
        if ratio < threshold:
            logger.warning(f"缓存命中率低于阈值: {ratio:.2f}% < {threshold}%")
            return False
        return True
    
    @staticmethod
    def check_response_time(monitor: PerformanceMonitor, threshold: float = 0.1) -> bool:
        """检查平均响应时间"""
        avg_time = monitor.get_avg_response_time()
        if avg_time > threshold:
            logger.warning(f"平均响应时间超过阈值: {avg_time:.3f}s > {threshold}s")
            return False
        return True
    
    @staticmethod
    def check_error_ratio(monitor: PerformanceMonitor, threshold: float = 5.0) -> bool:
        """检查错误率"""
        ratio = monitor.get_error_ratio()
        if ratio > threshold:
            logger.warning(f"错误率超过阈值: {ratio:.2f}% > {threshold}%")
            return False
        return True
    
    @staticmethod
    def check_all_alerts(monitor: PerformanceMonitor) -> Dict[str, bool]:
        """检查所有告警"""
        return {
            'cache_hit_ratio': PerformanceAlerts.check_cache_hit_ratio(monitor),
            'response_time': PerformanceAlerts.check_response_time(monitor),
            'error_ratio': PerformanceAlerts.check_error_ratio(monitor)
        }


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()
