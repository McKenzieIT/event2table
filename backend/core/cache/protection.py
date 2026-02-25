#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存防护机制模块
================

提供缓存穿透、击穿、雪崩的防护机制

版本: 1.0.0
日期: 2026-02-20

功能:
- 布隆过滤器防止缓存穿透
- 分布式锁防止缓存击穿
- TTL随机化防止缓存雪崩
- 空值缓存防止穿透
"""

from contextlib import contextmanager
from typing import Any, Callable, Optional
import threading
import time
import random
import logging

try:
    from pybloom_live import ScalableBloomFilter
    BLOOM_FILTER_AVAILABLE = True
except ImportError:
    BLOOM_FILTER_AVAILABLE = False
    logging.warning("pybloom_live未安装，布隆过滤器功能不可用")

from backend.core.cache.cache_system import hierarchical_cache, CacheKeyBuilder
from backend.core.config.config import CacheConfig

logger = logging.getLogger(__name__)


class CacheProtection:
    """
    缓存防护机制
    
    提供三级防护:
    1. 布隆过滤器 - 防止缓存穿透
    2. 分布式锁 - 防止缓存击穿
    3. TTL随机化 - 防止缓存雪崩
    """
    
    def __init__(self):
        """初始化缓存防护机制"""
        # 布隆过滤器（用于防止穿透）
        if BLOOM_FILTER_AVAILABLE:
            self.bloom_filter = ScalableBloomFilter(
                initial_capacity=10000,
                error_rate=0.001
            )
            logger.info("✅ 布隆过滤器初始化成功")
        else:
            self.bloom_filter = None
            logger.warning("⚠️ 布隆过滤器不可用，使用空值缓存作为替代方案")
        
        # 分布式锁（用于防止击穿）
        self._locks = {}
        self._lock = threading.Lock()
        
        # 空值标记
        self._EMPTY_MARKER = "__EMPTY__"
        
        # 统计信息
        self.stats = {
            "bloom_filter_rejects": 0,  # 布隆过滤器拦截次数
            "lock_waits": 0,  # 锁等待次数
            "empty_cache_hits": 0,  # 空值缓存命中次数
        }
        
        logger.info("✅ 缓存防护机制初始化完成")
    
    # ========================================================================
    # 布隆过滤器防护（防止缓存穿透）
    # ========================================================================
    
    def add_to_bloom_filter(self, key: str):
        """
        将键添加到布隆过滤器
        
        Args:
            key: 缓存键
        """
        if self.bloom_filter is not None:
            self.bloom_filter.add(key)
            logger.debug(f"布隆过滤器添加: {key}")
    
    def might_exist_in_bloom_filter(self, key: str) -> bool:
        """
        检查键是否可能存在（布隆过滤器）
        
        Args:
            key: 缓存键
        
        Returns:
            True: 可能存在（需要进一步查询）
            False: 一定不存在（可以直接返回）
        """
        if self.bloom_filter is None:
            # 布隆过滤器不可用，返回True表示需要查询
            return True
        
        might_exist = key in self.bloom_filter
        
        if not might_exist:
            self.stats["bloom_filter_rejects"] += 1
            logger.debug(f"布隆过滤器拦截: {key}")
        
        return might_exist
    
    def get_with_bloom_filter(
        self,
        pattern: str,
        func: Callable,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        使用布隆过滤器防止缓存穿透
        
        流程:
        1. 尝试从缓存获取
        2. 缓存未命中，执行函数获取数据
        3. 将数据写入缓存，并添加到布隆过滤器
        
        注意：此方法不使用布隆过滤器预检查，因为会导致新数据无法缓存
        布隆过滤器主要用于防止恶意查询不存在的数据
        
        Args:
            pattern: 缓存模式
            func: 数据获取函数
            ttl: 缓存TTL（秒）
            **kwargs: 缓存键参数
        
        Returns:
            缓存数据或从func获取的数据
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)
        
        # 1. 尝试从缓存获取
        cached = hierarchical_cache.get(pattern, **kwargs)
        if cached is not None:
            # 检查是否是空值标记
            if cached == self._EMPTY_MARKER:
                self.stats["empty_cache_hits"] += 1
                logger.debug(f"空值缓存命中: {key}")
                return None
            return cached
        
        # 2. 执行函数获取数据
        try:
            data = func()
            
            # 3. 写入缓存
            if data is not None:
                hierarchical_cache.set(pattern, data, ttl=ttl, **kwargs)
                # 添加到布隆过滤器
                self.add_to_bloom_filter(key)
            else:
                # 缓存空值（防止穿透）
                hierarchical_cache.set(pattern, self._EMPTY_MARKER, ttl=CacheConfig.CACHE_EMPTY_TTL, **kwargs)
                logger.debug(f"缓存空值: {key}")
            
            return data
        
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            raise
    
    # ========================================================================
    # 分布式锁防护（防止缓存击穿）
    # ========================================================================
    
    @contextmanager
    def distributed_lock(self, key: str, timeout: int = 5):
        """
        分布式锁上下文管理器
        
        防止缓存击穿：热点数据过期时，大量请求同时查询数据库
        
        Args:
            key: 锁的键
            timeout: 锁超时时间（秒）
        
        Yields:
            bool: 是否成功获取锁
        """
        # 获取或创建锁
        with self._lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            lock = self._locks[key]
        
        # 尝试获取锁
        acquired = False
        try:
            acquired = lock.acquire(timeout=timeout)
            if not acquired:
                self.stats["lock_waits"] += 1
                logger.debug(f"锁等待: {key}")
            yield acquired
        finally:
            if acquired:
                try:
                    lock.release()
                except RuntimeError:
                    # 锁已被释放
                    pass
    
    def get_with_lock(
        self,
        pattern: str,
        func: Callable,
        ttl: Optional[int] = None,
        lock_timeout: int = 5,
        **kwargs
    ) -> Any:
        """
        使用分布式锁防止缓存击穿
        
        流程:
        1. 尝试从缓存获取
        2. 缓存未命中，获取分布式锁
        3. 再次检查缓存（可能已被其他线程更新）
        4. 执行函数获取数据
        5. 写入缓存
        
        Args:
            pattern: 缓存模式
            func: 数据获取函数
            ttl: 缓存TTL（秒）
            lock_timeout: 锁超时时间（秒）
            **kwargs: 缓存键参数
        
        Returns:
            缓存数据或从func获取的数据
        """
        # 1. 尝试从缓存获取
        cached = hierarchical_cache.get(pattern, **kwargs)
        if cached is not None:
            if cached == self._EMPTY_MARKER:
                return None
            return cached
        
        key = CacheKeyBuilder.build(pattern, **kwargs)
        
        # 2. 获取分布式锁
        with self.distributed_lock(key, timeout=lock_timeout) as acquired:
            if not acquired:
                # 获取锁失败，等待并重试
                time.sleep(0.1)
                cached = hierarchical_cache.get(pattern, **kwargs)
                if cached is not None:
                    if cached == self._EMPTY_MARKER:
                        return None
                    return cached
                # 仍然未命中，降级执行
                logger.warning(f"锁等待超时，降级执行: {key}")
            
            # 3. 再次检查缓存（可能已被其他线程更新）
            cached = hierarchical_cache.get(pattern, **kwargs)
            if cached is not None:
                if cached == self._EMPTY_MARKER:
                    return None
                return cached
            
            # 4. 执行函数获取数据
            try:
                data = func()
                
                # 5. 写入缓存
                if data is not None:
                    hierarchical_cache.set(pattern, data, ttl=ttl, **kwargs)
                else:
                    # 缓存空值
                    hierarchical_cache.set(pattern, self._EMPTY_MARKER, ttl=CacheConfig.CACHE_EMPTY_TTL, **kwargs)
                
                return data
            
            except Exception as e:
                logger.error(f"获取数据失败: {e}")
                raise
    
    # ========================================================================
    # TTL随机化防护（防止缓存雪崩）
    # ========================================================================
    
    def set_with_random_ttl(
        self,
        pattern: str,
        data: Any,
        base_ttl: int = 300,
        jitter_pct: float = 0.2,
        **kwargs
    ):
        """
        使用随机TTL防止缓存雪崩
        
        在基础TTL上增加随机偏移，避免大量缓存同时过期
        
        Args:
            pattern: 缓存模式
            data: 缓存数据
            base_ttl: 基础TTL（秒）
            jitter_pct: 抖动百分比（默认±20%）
            **kwargs: 缓存键参数
        """
        # 计算随机TTL
        jitter = int(base_ttl * jitter_pct)
        if jitter > 0:
            ttl = base_ttl + random.randint(-jitter, jitter)
        else:
            ttl = base_ttl
        
        # 写入缓存
        hierarchical_cache.set(pattern, data, ttl=ttl, **kwargs)
        
        logger.debug(f"TTL随机化: 基础{base_ttl}s ±{jitter_pct*100}% → 实际{ttl}s")
    
    # ========================================================================
    # 综合防护
    # ========================================================================
    
    def get_with_full_protection(
        self,
        pattern: str,
        func: Callable,
        ttl: Optional[int] = None,
        use_bloom_filter: bool = True,
        use_lock: bool = True,
        use_random_ttl: bool = True,
        **kwargs
    ) -> Any:
        """
        使用完整防护机制
        
        同时启用布隆过滤器、分布式锁、TTL随机化
        
        Args:
            pattern: 缓存模式
            func: 数据获取函数
            ttl: 缓存TTL（秒）
            use_bloom_filter: 是否使用布隆过滤器
            use_lock: 是否使用分布式锁
            use_random_ttl: 是否使用TTL随机化
            **kwargs: 缓存键参数
        
        Returns:
            缓存数据或从func获取的数据
        """
        # 1. 尝试从缓存获取
        cached = hierarchical_cache.get(pattern, **kwargs)
        if cached is not None:
            if cached == self._EMPTY_MARKER:
                self.stats["empty_cache_hits"] += 1
                return None
            return cached
        
        key = CacheKeyBuilder.build(pattern, **kwargs)
        
        # 2. 获取数据（带锁或不带锁）
        def fetch_data():
            data = func()
            
            # 写入缓存
            if data is not None:
                if use_random_ttl and ttl:
                    self.set_with_random_ttl(pattern, data, base_ttl=ttl, **kwargs)
                else:
                    hierarchical_cache.set(pattern, data, ttl=ttl, **kwargs)
                
                # 添加到布隆过滤器
                if use_bloom_filter:
                    self.add_to_bloom_filter(key)
            else:
                # 缓存空值
                hierarchical_cache.set(pattern, self._EMPTY_MARKER, ttl=CacheConfig.CACHE_EMPTY_TTL, **kwargs)
            
            return data
        
        if use_lock:
            return self.get_with_lock(pattern, fetch_data, ttl=ttl, **kwargs)
        else:
            return fetch_data()
    
    # ========================================================================
    # 统计信息
    # ========================================================================
    
    def get_stats(self) -> dict:
        """
        获取防护统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "bloom_filter_available": BLOOM_FILTER_AVAILABLE,
            "bloom_filter_rejects": self.stats["bloom_filter_rejects"],
            "lock_waits": self.stats["lock_waits"],
            "empty_cache_hits": self.stats["empty_cache_hits"],
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "bloom_filter_rejects": 0,
            "lock_waits": 0,
            "empty_cache_hits": 0,
        }
        logger.info("📊 缓存防护统计已重置")


# 全局缓存防护实例
cache_protection = CacheProtection()


logger.info("✅ 缓存防护机制模块已加载 (1.0.0)")
