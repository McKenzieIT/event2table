#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级分层缓存系统
==================
L1: 内存热点缓存 (LRU, 1000条, 1分钟)
L2: Redis共享缓存 (10万条, 1小时)
L3: 数据库查询

版本: 1.0.0
日期: 2026-01-20
"""

from functools import wraps
from typing import Any, Optional, Dict
from backend.core.cache.cache_system import CacheKeyBuilder, get_cache
import logging
import time

logger = logging.getLogger(__name__)


class HierarchicalCache:
    """三级分层缓存管理器

    缓存层级:
    - L1: 内存热点缓存 (1000条, 60秒TTL) - 响应时间 <1ms
    - L2: Redis共享缓存 (10万条, 3600秒TTL) - 响应时间 5-10ms
    - L3: 数据库查询 - 响应时间 50-200ms

    优势:
    - 热点数据极快访问（L1）
    - 大容量缓存存储（L2）
    - 自动LRU淘汰，节省内存
    - L2命中自动回填L1
    """

    def __init__(self, l1_size=1000, l1_ttl=60, l2_ttl=3600):
        """
        初始化分层缓存

        Args:
            l1_size: L1缓存大小（条数），默认1000
            l1_ttl: L1缓存TTL（秒），默认60
            l2_ttl: L2缓存TTL（秒），默认3600
        """
        self.l1_size = l1_size
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        self.l1_cache: Dict[str, Any] = {}  # 简单字典缓存（带TTL）
        self.l1_timestamps: Dict[str, float] = {}

        # 统计信息
        self.stats = {"l1_hits": 0, "l2_hits": 0, "misses": 0, "l1_evictions": 0}

        logger.info(f"✅ 三级缓存初始化: " f"L1={l1_size}条/{l1_ttl}秒, " f"L2={l2_ttl}秒")

    def get(self, pattern: str, **kwargs) -> Optional[Any]:
        """
        三级缓存查询

        查询顺序:
        1. L1内存缓存 (<1ms)
        2. L2 Redis缓存 (5-10ms，命中后回填L1)
        3. L3数据库 (返回None，由调用方查询)

        Args:
            pattern: 缓存模式 (如 'events.list')
            **kwargs: 参数键值对

        Returns:
            缓存数据或None（未命中）
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        # L1: 内存热点缓存
        if key in self.l1_cache:
            timestamp = self.l1_timestamps.get(key, 0)
            if time.time() - timestamp < self.l1_ttl:
                self.stats["l1_hits"] += 1
                logger.debug(f"✅ L1 HIT: {key}")
                return self.l1_cache[key]
            else:
                # L1过期，删除
                del self.l1_cache[key]
                del self.l1_timestamps[key]
                logger.debug(f"⏰ L1过期: {key}")

        # L2: Redis缓存
        cache = get_cache()
        if cache is not None:
            try:
                cached = cache.get(key)
                if cached is not None:
                    # 回填L1
                    self._set_l1(key, cached)
                    self.stats["l2_hits"] += 1
                    logger.debug(f"✅ L2 HIT → L1回填: {key}")
                    return cached
            except Exception as e:
                logger.warning(f"⚠️ L2缓存读取失败: {e}")

        # L3: 缓存未命中，返回None
        self.stats["misses"] += 1
        logger.debug(f"❌ CACHE MISS: {key}")
        return None

    def set(self, pattern: str, data: Any, **kwargs):
        """
        写入三级缓存

        同时写入L1和L2，确保数据一致性

        Args:
            pattern: 缓存模式 (如 'events.list')
            data: 要缓存的数据
            **kwargs: 参数键值对
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        # 写入L1
        self._set_l1(key, data)

        # 写入L2
        cache = get_cache()
        if cache is not None:
            try:
                cache.set(key, data, timeout=self.l2_ttl)
                logger.debug(f"💾 L2 SET: {key}")
            except Exception as e:
                logger.warning(f"⚠️ L2缓存写入失败: {e}")

    def _set_l1(self, key: str, data: Any):
        """
        写入L1缓存（带LRU淘汰）

        当L1缓存满时，删除最旧的条目

        Args:
            key: 缓存键
            data: 缓存数据
        """
        # 如果L1已满，删除最旧的条目
        if len(self.l1_cache) >= self.l1_size:
            oldest_key = min(self.l1_timestamps, key=self.l1_timestamps.get)
            del self.l1_cache[oldest_key]
            del self.l1_timestamps[oldest_key]
            self.stats["l1_evictions"] += 1
            logger.debug(f"🗑️ L1淘汰: {oldest_key}")

        self.l1_cache[key] = data
        self.l1_timestamps[key] = time.time()

    def invalidate(self, pattern: str, **kwargs):
        """
        失效缓存（L1和L2同时失效）

        Args:
            pattern: 缓存模式
            **kwargs: 参数键值对
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        # 失效L1
        if key in self.l1_cache:
            del self.l1_cache[key]
            del self.l1_timestamps[key]
            logger.debug(f"🗑️ L1失效: {key}")

        # 失效L2
        cache = get_cache()
        if cache is not None:
            try:
                cache.delete(key)
                logger.debug(f"🗑️ L2失效: {key}")
            except Exception as e:
                logger.warning(f"⚠️ L2缓存失效失败: {e}")

    def invalidate_pattern(self, pattern: str, **kwargs) -> int:
        """
        失效匹配模式的所有L1缓存键

        Args:
            pattern: 缓存模式
            **kwargs: 要匹配的参数

        Returns:
            失效的键数量
        """
        wildcard = CacheKeyBuilder.build_pattern(pattern, **kwargs)
        count = 0

        # 收集要删除的键
        keys_to_delete = []
        for key in self.l1_cache:
            if self._match_pattern(key, wildcard):
                keys_to_delete.append(key)

        # 删除匹配的键
        for key in keys_to_delete:
            del self.l1_cache[key]
            del self.l1_timestamps[key]
            count += 1
            logger.debug(f"🗑️ L1模式失效: {key}")

        return count

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """
        参数感知的通配符匹配

        匹配逻辑:
        - 从pattern中提取指定的参数约束（如 game_id:*)
        - 检查key中是否满足这些约束
        - 忽略key中的其他参数

        Args:
            key: 缓存键（如 'dwd_gen:v3:test.key:event_id:0:game_id:1'）
            pattern: 通配符模式（如 'dwd_gen:v3:test.key:game_id:*'）

        Returns:
            是否匹配

        Example:
            >>> key = 'dwd_gen:v3:test.key:event_id:0:game_id:1'
            >>> pattern = 'dwd_gen:v3:test.key:game_id:*'
            >>> _match_pattern(key, pattern)
            True  # game_id=1匹配，忽略event_id参数
        """
        # Remove common prefix
        prefix = CacheKeyBuilder.PREFIX
        if not key.startswith(prefix) or not pattern.startswith(prefix):
            return False

        key_suffix = key[len(prefix) :]
        pattern_suffix = pattern[len(prefix) :]

        # Split by ':' to get components
        key_parts = key_suffix.split(":")
        pattern_parts = pattern_suffix.split(":")

        # The format is: base_pattern:param1:value1:param2:value2:...
        # pattern_parts: ['test.key', 'game_id', '*']
        # key_parts: ['test.key', 'event_id', '0', 'game_id', '1']

        # Base pattern is always the first part
        base_pattern = pattern_parts[0]

        # Check base pattern matches
        if key_parts[0] != base_pattern:
            return False

        # Extract parameter constraints from pattern (key:value pairs where value is '*')
        pattern_constraints = {}
        for i in range(1, len(pattern_parts), 2):
            if i + 1 < len(pattern_parts):
                param_name = pattern_parts[i]
                if pattern_parts[i + 1] == "*":
                    pattern_constraints[param_name] = None  # Wildcard value
                else:
                    pattern_constraints[param_name] = pattern_parts[i + 1]

        # Extract parameters from key (key:value pairs starting from index 1)
        key_params = {}
        for i in range(1, len(key_parts), 2):
            if i + 1 < len(key_parts):
                key_params[key_parts[i]] = key_parts[i + 1]

        # Check if all pattern constraints are satisfied in key
        for param_name, param_value in pattern_constraints.items():
            if param_name not in key_params:
                return False
            if param_value is not None and key_params[param_name] != param_value:
                return False

        return True

    def get_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        total_requests = self.stats["l1_hits"] + self.stats["l2_hits"] + self.stats["misses"]

        if total_requests == 0:
            hit_rate = 0
        else:
            hit_rate = (self.stats["l1_hits"] + self.stats["l2_hits"]) / total_requests * 100

        return {
            "l1_size": len(self.l1_cache),
            "l1_capacity": self.l1_size,
            "l1_usage": f"{len(self.l1_cache) / self.l1_size * 100:.1f}%",
            "l1_hits": self.stats["l1_hits"],
            "l2_hits": self.stats["l2_hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.2f}%",
            "l1_evictions": self.stats["l1_evictions"],
            "total_requests": total_requests,
        }

    def clear_l1(self):
        """清空L1缓存"""
        self.l1_cache.clear()
        self.l1_timestamps.clear()
        logger.info("🗑️ L1缓存已清空")

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {"l1_hits": 0, "l2_hits": 0, "misses": 0, "l1_evictions": 0}
        logger.info("📊 缓存统计已重置")


# 全局分层缓存实例
hierarchical_cache = HierarchicalCache()


def cached_hierarchical(pattern: str):
    """
    分层缓存装饰器

    Usage:
        @cached_hierarchical('events.list')
        def get_events(game_id: int, page: int):
            return fetch_events_from_db(game_id, page)

    Args:
        pattern: 缓存模式 (如 'events.list')
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            result = hierarchical_cache.get(pattern, **kwargs)
            if result is not None:
                return result

            # 执行函数
            result = f(*args, **kwargs)

            # 写入缓存
            hierarchical_cache.set(pattern, result, **kwargs)

            return result

        return wrapper

    return decorator


logger.info("✅ 三级分层缓存系统已加载 (1.0.0)")
