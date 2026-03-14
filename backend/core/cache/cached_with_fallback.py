#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存降级装饰器
==============

提供简单的缓存降级装饰器, 自动处理Redis故障

使用示例:
    @cached_with_fallback(ttl=3600)
    def get_data(key):
        return fetch_from_database(key)

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def cached_with_fallback(ttl: int = 3600, key_prefix: Optional[str] = None):
    """
    带降级策略的缓存装饰器

    Redis不可用时自动降级到L1缓存

    Args:
        ttl: 缓存生存时间（秒）
        key_prefix: 缓存键前缀（可选）

    Example:
        @cached_with_fallback(ttl=3600)
        def get_games():
            return fetch_all_as_dict('SELECT * FROM games')
    """
    from backend.core.cache.cache_hierarchical import HierarchicalCache

    cache = HierarchicalCache()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _build_cache_key(func, args, kwargs, key_prefix)

            # 尝试从L1+L2缓存获取
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    logger.debug(f"✅ Cache HIT (L1/L2): {cache_key}")
                    return cached_data
            except Exception as e:
                logger.warning(f"⚠️  Cache read failed: {e}, falling back to database")

            # 缓存未命中, 执行函数
            logger.debug(f"❌ Cache MISS: {cache_key}")
            result = func(*args, **kwargs)

            # 尝试写入缓存(可能失败, 但不影响主流程)
            try:
                cache.set(cache_key, result, ttl=ttl)
            except Exception as e:
                logger.warning(f"⚠️  Cache write failed: {e}, continuing without cache")

            return result

        return wrapper

    return decorator


def _build_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: Optional[str]) -> str:
    """构建缓存键"""
    # 简单的键生成策略
    func_name = func.__name__
    args_str = "_".join(str(arg) for arg in args)
    kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

    if prefix:
        return f"{prefix}:{func_name}:{args_str}:{kwargs_str}"
    else:
        return f"cache:{func_name}:{args_str}:{kwargs_str}"


class CacheWithFallback:
    """
    带降级策略的缓存包装器

    提供更细粒度的降级控制
    """

    def __init__(self):
        from backend.core.cache.cache_hierarchical import HierarchicalCache

        self._cache = HierarchicalCache()
        self._degraded = False
        self._failure_count = 0
        self._threshold = 3  # 连续失败3次后降级

    def get(self, key: str, query_fn: Optional[Callable] = None) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            key: 缓存键
            query_fn: 缓存未命中时的查询函数（可选）

        Returns:
            缓存数据或None
        """
        # 尝试从L1+L2获取
        try:
            data = self._cache.get(key)
            if data is not None:
                self._reset_failure_count()
                return data
        except Exception as e:
            self._increment_failure_count()
            logger.warning(f"Cache get failed: {e}")

        # 缓存未命中, 执行查询函数
        if query_fn:
            return query_fn()

        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）

        Returns:
            是否成功
        """
        try:
            self._cache.set(key, value, ttl=ttl)
            self._reset_failure_count()
            return True
        except Exception as e:
            self._increment_failure_count()
            logger.warning(f"Cache set failed: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存数据

        Args:
            key: 缓存键

        Returns:
            是否成功
        """
        try:
            self._cache.delete(key)
            self._reset_failure_count()
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False

    def is_degraded(self) -> bool:
        """是否处于降级模式"""
        return self._degraded

    def get_failure_count(self) -> int:
        """获取失败计数"""
        return self._failure_count

    def _increment_failure_count(self):
        """增加失败计数"""
        self._failure_count += 1
        if self._failure_count >= self._threshold:
            self._degraded = True
            logger.warning(f"⚠️  Cache degraded after {self._failure_count} failures")

    def _reset_failure_count(self):
        """重置失败计数"""
        if self._failure_count > 0:
            self._failure_count = 0
            if self._degraded:
                self._degraded = False
                logger.info("✅ Cache recovered from degradation")


# 全局降级缓存实例
_fallback_cache = CacheWithFallback()


def get_fallback_cache():
    """获取降级缓存实例"""
    return _fallback_cache
