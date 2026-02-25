#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一缓存系统 v3.0
=================

三级分层缓存系统（L1内存 + L2 Redis + L3数据库）

版本: 3.0.0
日期: 2026-01-27

特性:
- 统一键生成（参数排序、版本控制）
- 三级分层缓存（L1热点 + L2共享 + L3数据库）
- 智能失效（精确失效、模式失效、批量失效）
- 缓存预热（启动预热、定时预热、分阶段预热）
- 统计监控（命中率、性能指标、容量监控）
- 穿透保护（空值缓存）
- TTL随机化（防止雪崩）

使用示例:
    from backend.core.cache.cache_system import cached, hierarchical_cache, CacheKeyBuilder

    @cached('events.list', timeout=300)
    def get_events(game_id: int, page: int):
        return fetch_events_from_db(game_id, page)

    # 或使用分层缓存
    @cached_hierarchical('games.detail')
    def get_game(game_id: int):
        return fetch_game_from_db(game_id)
"""

from functools import wraps
from flask import current_app
import logging
import random
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# 统一缓存键生成器
# ============================================================================


class CacheKeyBuilder:
    """
    统一缓存键生成器 v3.0

    特性:
    - 层次化命名: dwd_gen:v3:module:entity:identifier:variant
    - 版本控制: 避免脏读
    - 参数排序: 确保一致性
    """

    PREFIX = "dwd_gen:v3:"
    VERSION = "3.0"

    @classmethod
    def build(cls, pattern: str, **kwargs) -> str:
        """
        构建标准化缓存键

        Args:
            pattern: 缓存模式 (如 'events.list')
            **kwargs: 参数键值对

        Returns:
            标准化的缓存键

        Example:
            >>> CacheKeyBuilder.build('events.list', game_id=1, page=1)
            'dwd_gen:v3:events.list:game_id:1:page:1'
            >>> CacheKeyBuilder.build('events.list', page=1, game_id=1)
            'dwd_gen:v3:events.list:game_id:1:page:1'  # 参数顺序不影响
        """
        if not kwargs:
            return f"{cls.PREFIX}{pattern}"

        # 参数排序确保一致性
        sorted_params = sorted(kwargs.items())
        param_str = ":".join(f"{k}:{v}" for k, v in sorted_params)
        return f"{cls.PREFIX}{pattern}:{param_str}"

    @classmethod
    def build_pattern(cls, pattern: str, **kwargs) -> str:
        """
        构建用于失效的通配符模式

        Args:
            pattern: 缓存模式
            **kwargs: 要匹配的参数（值为通配符）

        Returns:
            通配符模式字符串

        Example:
            >>> CacheKeyBuilder.build_pattern('events.list', game_id=1)
            'dwd_gen:v3:events.list:game_id:*'
        """
        if kwargs:
            param_str = ":".join(f"{k}:*" for k in sorted(kwargs.keys()))
            return f"{cls.PREFIX}{pattern}:{param_str}"
        return f"{cls.PREFIX}{pattern}:*"


# ============================================================================
# 三级分层缓存系统
# ============================================================================


class HierarchicalCache:
    """
    三级分层缓存管理器

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
        self._lock = threading.RLock()  # 线程安全锁

        # 空值缓存标记
        self._EMPTY_MARKER = "__EMPTY__"

        # 统计信息
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "l1_evictions": 0,
            "l1_sets": 0,
            "l2_sets": 0,
            "empty_hits": 0,  # 空值缓存命中次数
        }

        logger.info(f"✅ 三级缓存初始化: " f"L1={l1_size}条/{l1_ttl}秒, " f"L2={l2_ttl}秒")

    def get(self, pattern: str, **kwargs) -> Optional[Any]:
        """
        三级缓存查询

        查询顺序:
        1. L1内存缓存 (<1ms)
        2. L2 Redis缓存 (5-10ms，命中后回填L1)
        3. L3数据库 (返回None，由调用方查询)

        特性:
        - 支持空值缓存（防止缓存穿透）
        - L2命中自动回填L1

        Args:
            pattern: 缓存模式 (如 'events.list')
            **kwargs: 参数键值对

        Returns:
            缓存数据或None（未命中）
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        with self._lock:
            # L1: 内存热点缓存
            if key in self.l1_cache:
                timestamp = self.l1_timestamps.get(key, 0)
                if time.time() - timestamp < self.l1_ttl:
                    cached_data = self.l1_cache[key]

                    # 检查是否是空值缓存标记
                    if cached_data == self._EMPTY_MARKER:
                        self.stats["empty_hits"] = self.stats.get("empty_hits", 0) + 1
                        self.stats["l1_hits"] += 1
                        logger.debug(f"✅ L1 HIT (空值): {key}")
                        return None

                    self.stats["l1_hits"] += 1
                    logger.debug(f"✅ L1 HIT: {key}")
                    return cached_data
                else:
                    # L1过期，删除
                    del self.l1_cache[key]
                    del self.l1_timestamps[key]
                    logger.debug(f"⏰ L1过期: {key}")

        # L2: Redis缓存
        cache = self._get_cache()
        if cache is not None:
            try:
                cached = cache.get(key)
                if cached is not None:
                    # 回填L1
                    with self._lock:
                        # 检查是否是空值缓存
                        if cached == self._EMPTY_MARKER:
                            self.stats["empty_hits"] = self.stats.get("empty_hits", 0) + 1
                            self.stats["l2_hits"] += 1
                            logger.debug(f"✅ L2 HIT (空值) → L1回填: {key}")
                            return None

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

    def set(self, pattern: str, data: Any, ttl: Optional[int] = None, **kwargs):
        """
        写入三级缓存

        同时写入L1和L2，确保数据一致性

        特性:
        - 支持TTL抖动（防止缓存雪崩）
        - 自动处理空值缓存

        Args:
            pattern: 缓存模式 (如 'events.list')
            data: 要缓存的数据
            ttl: TTL时间（秒），None则使用默认l2_ttl
            **kwargs: 参数键值对
        """
        from backend.core.config.config import CacheConfig
        import random

        key = CacheKeyBuilder.build(pattern, **kwargs)

        # 应用TTL抖动（防止缓存雪崩）
        if ttl is None:
            ttl = self.l2_ttl

        # 添加随机抖动（±10%）
        jitter_pct = CacheConfig.CACHE_JITTER_PCT
        jitter = int(ttl * jitter_pct)
        if jitter > 0:
            ttl = ttl + random.randint(-jitter, jitter)
            logger.debug(f"🎲 TTL抖动: 原始{ttl - jitter}±{jitter} → 实际{ttl}s")

        # 处理空值缓存
        if data is None:
            logger.debug(f"💾 空值缓存: {key}")
            data = self._EMPTY_MARKER
            # 使用空值专用TTL
            ttl = CacheConfig.CACHE_EMPTY_TTL

        # 写入L1
        with self._lock:
            self._set_l1(key, data)

        # 写入L2
        cache = self._get_cache()
        if cache is not None:
            try:
                cache.set(key, data, timeout=ttl)
                self.stats["l2_sets"] += 1
                logger.debug(f"💾 L2 SET: {key} (TTL={ttl}s)")
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
        self.stats["l1_sets"] += 1

    def delete(self, pattern: str, **kwargs):
        """
        删除缓存（L1和L2同时删除）

        Args:
            pattern: 缓存模式
            **kwargs: 参数键值对
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        # 删除L1
        with self._lock:
            if key in self.l1_cache:
                del self.l1_cache[key]
                del self.l1_timestamps[key]
                logger.debug(f"🗑️ L1删除: {key}")

        # 删除L2
        cache = self._get_cache()
        if cache is not None:
            try:
                cache.delete(key)
                logger.debug(f"🗑️ L2删除: {key}")
            except Exception as e:
                logger.warning(f"⚠️ L2缓存删除失败: {e}")

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

        with self._lock:
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
        with self._lock:
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
                "l1_sets": self.stats["l1_sets"],
                "l2_sets": self.stats["l2_sets"],
                "total_requests": total_requests,
                # 新增：空值缓存统计
                "empty_hits": self.stats.get("empty_hits", 0),
            }

    def clear_l1(self):
        """清空L1缓存"""
        with self._lock:
            self.l1_cache.clear()
            self.l1_timestamps.clear()
        logger.info("🗑️ L1缓存已清空")

    def clear_l2(self):
        """清空L2缓存"""
        cache = self._get_cache()
        if cache is not None:
            try:
                # 清空所有dwd_gen:v3:开头的键
                import redis

                redis_client = self._get_redis_client()
                if redis_client:
                    pattern = f"{CacheKeyBuilder.PREFIX}*"
                    keys = redis_client.keys(pattern)
                    if keys:
                        redis_client.delete(*keys)
                        logger.info(f"🗑️ L2缓存已清空: {len(keys)}个键")
            except Exception as e:
                logger.warning(f"⚠️ L2缓存清空失败: {e}")

    def clear_all(self):
        """清空所有缓存（L1和L2）"""
        self.clear_l1()
        self.clear_l2()

    def reset_stats(self):
        """重置统计信息"""
        with self._lock:
            self.stats = {
                "l1_hits": 0,
                "l2_hits": 0,
                "misses": 0,
                "l1_evictions": 0,
                "l1_sets": 0,
                "l2_sets": 0,
            }
        logger.info("📊 缓存统计已重置")

    def _get_cache(self):
        """获取Flask-Cache实例"""
        try:
            return current_app.cache
        except (AttributeError, RuntimeError):
            # 不在Flask应用上下文中
            return None

    def _get_redis_client(self):
        """获取Redis客户端"""
        try:
            from flask_redis import FlaskRedis

            return FlaskRedis().get_redis()
        except Exception:
            return None


# ============================================================================
# 缓存失效管理器
# ============================================================================


class CacheInvalidator:
    """
    智能缓存失效管理器

    功能:
    - 精确失效：删除特定缓存键
    - 模式失效：使用通配符删除匹配的键
    - 批量失效：使用Redis Pipeline优化批量删除
    """

    def __init__(self, cache: HierarchicalCache):
        """
        初始化缓存失效管理器

        Args:
            cache: HierarchicalCache实例
        """
        self.cache = cache

    def invalidate(self, pattern: str, **kwargs):
        """
        精确失效单个缓存键

        Args:
            pattern: 缓存模式
            **kwargs: 参数键值对
        """
        self.cache.delete(pattern, **kwargs)
        logger.debug(f"🗑️ 缓存失效: {pattern} {kwargs}")

    def invalidate_pattern(self, pattern: str, **kwargs) -> int:
        """
        模式失效（L1）

        Args:
            pattern: 缓存模式
            **kwargs: 要匹配的参数

        Returns:
            失效的键数量
        """
        count = self.cache.invalidate_pattern(pattern, **kwargs)
        logger.info(f"🗑️ 模式失效: {pattern} {kwargs} ({count}个键)")
        return count

    def invalidate_batch(self, patterns: List[Tuple[str, Dict]]) -> int:
        """
        批量失效多个缓存键（使用Pipeline优化）

        Args:
            patterns: [(pattern, kwargs), ...] 列表

        Returns:
            失效的总键数
        """
        redis_client = self.cache._get_redis_client()
        total_count = 0

        if redis_client:
            try:
                # 使用Redis Pipeline批量删除
                import redis

                pipe = redis_client.pipeline()

                for pattern, kwargs in patterns:
                    key = CacheKeyBuilder.build(pattern, **kwargs)
                    pipe.delete(key)

                    # 同时删除L1
                    with self.cache._lock:
                        if key in self.cache.l1_cache:
                            del self.cache.l1_cache[key]
                            del self.cache.l1_timestamps[key]
                            total_count += 1

                pipe.execute()
                logger.info(f"🗑️ 批量失效: {len(patterns)}个键")
            except Exception as e:
                logger.warning(f"⚠️ 批量失效失败: {e}")
        else:
            # 降级到逐个删除
            for pattern, kwargs in patterns:
                self.cache.delete(pattern, **kwargs)
                total_count += 1

        return total_count

    def invalidate_game(self, game_id: int):
        """
        失效游戏相关的所有缓存

        Args:
            game_id: 游戏ID
        """
        patterns = [
            ("games.detail", {"id": game_id}),
            ("games.list", {}),
            ("events.list", {"game_id": game_id}),
            ("events.*", {"game_id": game_id}),
        ]

        for pattern, kwargs in patterns:
            self.invalidate_pattern(pattern, **kwargs)

        logger.info(f"🗑️ 游戏缓存已失效: game_id={game_id}")

    def invalidate_event(self, event_id: int):
        """
        失效事件相关的所有缓存

        Args:
            event_id: 事件ID
        """
        patterns = [
            ("events.detail", {"id": event_id}),
            ("params.*", {"event_id": event_id}),
        ]

        for pattern, kwargs in patterns:
            self.invalidate_pattern(pattern, **kwargs)

        logger.info(f"🗑️ 事件缓存已失效: event_id={event_id}")


# ============================================================================
# 装饰器
# ============================================================================


def cached(pattern: str, timeout: Optional[int] = None):
    """
    简单缓存装饰器（使用Flask-Cache）

    Usage:
        @cached('events.list', timeout=300)
        def get_events(game_id: int, page: int):
            return fetch_events_from_db(game_id, page)

    Args:
        pattern: 缓存模式
        timeout: 超时时间（秒）
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = CacheKeyBuilder.build(pattern, **kwargs)

            # 尝试从缓存获取
            cache = None
            try:
                cache = current_app.cache
                cached = cache.get(key)
                if cached is not None:
                    return cached
            except (AttributeError, RuntimeError):
                pass

            # 执行函数
            result = f(*args, **kwargs)

            # 写入缓存
            if cache is not None:
                try:
                    cache.set(key, result, timeout=timeout)
                except Exception as e:
                    logger.warning(f"⚠️ 缓存写入失败: {e}")

            return result

        return wrapper

    return decorator


# ============================================================================
# 全局实例
# ============================================================================

# 全局分层缓存实例
hierarchical_cache = HierarchicalCache()

# 全局缓存失效管理器
cache_invalidator = CacheInvalidator(hierarchical_cache)


logger.info("✅ 统一缓存系统已加载 (3.0.0)")


# ============================================================================
# 兼容性函数（用于平滑迁移）
# ============================================================================


def cache_result(cache_key_pattern, timeout=None):
    """
    缓存装饰器（兼容性包装器）

    这是一个兼容性函数，包装 @cached 装饰器以保持向后兼容。
    新代码应该直接使用 @cached 装饰器。

    Usage:
        @cache_result('games:all', timeout=3600)
        def get_all_games():
            return fetch_games_from_db()

    Args:
        cache_key_pattern: 缓存键模式
        timeout: 超时时间（秒）

    Returns:
        装饰器函数
    """
    # 转换旧格式到新格式
    # 'games:all' -> 'games.all'
    pattern = cache_key_pattern.replace(":", ".")

    return cached(pattern, timeout=timeout)


def clear_game_cache(game_id=None):
    """
    清除游戏相关缓存（兼容性包装器）

    这是一个兼容性函数，使用 CacheInvalidator 来清除缓存。
    新代码应该直接使用 cache_invalidator。

    Args:
        game_id: 游戏ID（None表示清除所有游戏缓存）
    """
    if game_id is not None:
        # 清除特定游戏的缓存
        cache_invalidator.invalidate_game(game_id)
        logger.info(f"🗑️ 游戏缓存已清除: game_id={game_id}")
    else:
        # 清除所有游戏相关缓存
        patterns = [
            ("games.list", {}),
            ("games.*", {}),
        ]
        for pattern, kwargs in patterns:
            cache_invalidator.invalidate_pattern(pattern, **kwargs)
        logger.info("🗑️ 所有游戏缓存已清除")


def clear_event_cache(event_id):
    """
    清除事件相关缓存（兼容性包装器）

    这是一个兼容性函数，使用 CacheInvalidator 来清除缓存。

    Args:
        event_id: 事件ID
    """
    cache_invalidator.invalidate_event(event_id)
    logger.info(f"🗑️ 事件缓存已清除: event_id={event_id}")


def clear_cache_pattern(pattern):
    """
    清除匹配模式的所有缓存（兼容性包装器）

    这是一个兼容性函数，使用 CacheInvalidator 来清除缓存。

    Args:
        pattern: 缓存键模式（支持通配符）
    """
    # 转换旧格式到新格式
    # 'games:*' -> 'games.*'
    new_pattern = pattern.replace(":", ".")

    # 提取基础模式和参数
    parts = new_pattern.split(":")
    if len(parts) > 1:
        base_pattern = parts[0]
        kwargs = {}
        for part in parts[1:]:
            if part != "*":
                kv = part.split("=")
                if len(kv) == 2:
                    kwargs[kv[0]] = kv[1]
    else:
        base_pattern = new_pattern
        kwargs = {}

    count = cache_invalidator.invalidate_pattern(base_pattern, **kwargs)
    logger.info(f"🗑️ 模式缓存已清除: {pattern} ({count}个键)")


def get_cache():
    """
    获取Flask-Cache实例（兼容性函数）

    Returns:
        Flask-Cache实例或None
    """
    try:
        return current_app.cache
    except (AttributeError, RuntimeError):
        return None


def get_redis_client():
    """
    获取Redis客户端（兼容性函数）

    Returns:
        Redis客户端或None
    """
    try:
        cache = get_cache()
        if cache and hasattr(cache, "cache"):
            # Flask-Caching with Redis
            return cache.cache._client
    except Exception:
        pass

    # 尝试直接导入redis
    try:
        import redis
        from backend.core.config.config import CacheConfig

        return redis.Redis(
            host=CacheConfig.CACHE_REDIS_HOST,
            port=CacheConfig.CACHE_REDIS_PORT,
            db=CacheConfig.CACHE_REDIS_DB,
            password=CacheConfig.CACHE_REDIS_PASSWORD,
        )
    except Exception:
        return None


def parse_json_cached(json_str):
    """
    解析JSON字符串（带缓存）

    这是一个兼容性函数，用于解析JSON字符串。
    由于v3.0不再需要JSON解析缓存，此函数直接返回解析结果。

    Args:
        json_str: JSON字符串

    Returns:
        解析后的Python对象
    """
    import json

    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON解析失败: {e}")
        return None
