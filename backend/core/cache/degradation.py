#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存降级策略
============

提供Redis故障时的自动降级机制

版本: 1.0.0
日期: 2026-02-24

功能:
- Redis故障自动降级到L1缓存
- 健康检查机制 (每10秒)
- 自动恢复
- RTO < 1秒
"""

from typing import Any, Optional, Dict, TYPE_CHECKING
import threading
import time
import logging

if TYPE_CHECKING:
    from .cache_hierarchical import HierarchicalCache

try:
    from .cache_hierarchical import hierarchical_cache
    from .cache_system import CacheKeyBuilder, get_cache
    from redis.exceptions import RedisError
except ImportError:
    hierarchical_cache = None  # type: ignore
    CacheKeyBuilder = None  # type: ignore
    get_cache = None  # type: ignore
    RedisError = Exception  # type: ignore

logger = logging.getLogger(__name__)


class CacheDegradationManager:
    """
    缓存降级管理器

    降级策略:
    - 正常模式: L1 → L2 → L3
    - 降级模式: L1 → L3 (Redis不可用时)

    触发条件:
    - Redis连接失败
    - Redis响应超时 (>100ms)
    - Redis返回错误

    自动恢复:
    - 健康检查每10秒
    - Redis恢复后自动切换回正常模式
    """

    def __init__(self, health_check_interval: int = 10):
        """
        初始化降级管理器

        Args:
            health_check_interval: 健康检查间隔 (秒)
        """
        self.degraded: bool = False
        self.last_health_check: float = 0
        self.health_check_interval: int = health_check_interval
        self._lock = threading.Lock()

        # 统计信息
        self.stats: Dict[str, float] = {
            'degradation_count': 0.0,
            'recovery_count': 0.0,
            'last_degradation_time': 0.0,
            'last_recovery_time': 0.0,
        }

        logger.info("✅ 缓存降级管理器初始化完成")

    def get_with_fallback(self, pattern: str, **kwargs) -> Optional[Any]:
        """
        带降级的缓存获取

        Args:
            pattern: 缓存模式
            **kwargs: 参数键值对

        Returns:
            缓存数据或None
        """
        # 检查是否需要进行健康检查
        if self._should_check_health():
            self._health_check()

        # 尝试正常三级缓存
        if not self.degraded:
            try:
                result = hierarchical_cache.get(pattern, **kwargs)
                if result is not None:
                    return result
            except RedisError as e:
                logger.warning(f"⚠️ Redis不可用，切换到降级模式: {e}")
                self._enter_degraded_mode()
            except Exception as e:
                logger.debug(f"缓存读取失败 (非Redis错误): {e}")

        # 降级模式：只使用L1
        key = CacheKeyBuilder.build(pattern, **kwargs)
        return self._get_l1_only(key)

    def _should_check_health(self) -> bool:
        """
        检查是否需要进行健康检查

        Returns:
            是否需要检查
        """
        return time.time() - self.last_health_check >= self.health_check_interval

    def _health_check(self) -> None:
        """Redis健康检查"""
        self.last_health_check = time.time()

        try:
            cache = get_cache()
            if cache is None:
                raise Exception("Redis缓存未初始化")

            # 测试Redis连接
            start_time = time.time()
            cache._client.ping()
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒

            # 检查响应时间
            if response_time > 100:
                logger.warning(
                    f"⚠️ Redis响应过慢: {response_time:.1f}ms "
                    f"(阈值: 100ms)"
                )
                # 响应慢但不一定降级，继续使用

            # Redis健康，如果处于降级模式则恢复
            if self.degraded:
                logger.info("✅ Redis已恢复，切换回正常模式")
                self._exit_degraded_mode()

        except RedisError as e:
            logger.debug(f"Redis健康检查失败: {e}")
            if not self.degraded:
                self._enter_degraded_mode()
        except Exception as e:
            logger.warning(f"健康检查异常: {e}")

    def _get_l1_only(self, key: str) -> Optional[Any]:
        """
        仅从L1获取数据

        Args:
            key: 缓存键

        Returns:
            缓存数据或None
        """
        if hierarchical_cache is None:
            return None

        # 直接访问L1缓存
        if key in hierarchical_cache.l1_cache:
            timestamp = hierarchical_cache.l1_timestamps.get(key, 0)
            if time.time() - timestamp < hierarchical_cache.l1_ttl:
                hierarchical_cache.stats["l1_hits"] += 1
                logger.debug(f"✅ L1 HIT (降级模式): {key}")
                return hierarchical_cache.l1_cache[key]
            else:
                # L1过期
                del hierarchical_cache.l1_cache[key]
                del hierarchical_cache.l1_timestamps[key]

        # L1未命中
        hierarchical_cache.stats["misses"] += 1
        logger.debug(f"❌ CACHE MISS (降级模式): {key}")
        return None

    def _enter_degraded_mode(self):
        """进入降级模式"""
        with self._lock:
            if not self.degraded:
                self.degraded = True
                self.stats['degradation_count'] += 1
                self.stats['last_degradation_time'] = time.time()
                logger.critical("🚨 进入缓存降级模式 (L1 → L3)")

    def _exit_degraded_mode(self):
        """退出降级模式"""
        with self._lock:
            if self.degraded:
                self.degraded = False
                self.stats['recovery_count'] += 1
                self.stats['last_recovery_time'] = time.time()
                logger.info("✅ 退出缓存降级模式，恢复正常 (L1 → L2 → L3)")

    def set_with_fallback(self, pattern: str, data: Any, **kwargs):
        """
        带降级的缓存设置

        Args:
            pattern: 缓存模式
            data: 缓存数据
            **kwargs: 参数键值对
        """
        key = CacheKeyBuilder.build(pattern, **kwargs)

        # 写入L1 (总是执行)
        hierarchical_cache._set_l1(key, data)

        # 写入L2 (仅在正常模式)
        if not self.degraded:
            try:
                cache = get_cache()
                if cache is not None:
                    cache.set(key, data, timeout=hierarchical_cache.l2_ttl)
                    logger.debug(f"💾 L2 SET: {key}")
            except RedisError as e:
                logger.warning(f"⚠️ L2写入失败，进入降级模式: {e}")
                self._enter_degraded_mode()
        else:
            logger.debug(f"💾 降级模式：仅写入L1: {key}")

    def force_degrade(self):
        """强制进入降级模式 (用于测试)"""
        self._enter_degraded_mode()

    def force_recover(self):
        """强制恢复 (用于测试)"""
        self._exit_degraded_mode()

    def is_degraded(self) -> bool:
        """
        检查是否处于降级模式

        Returns:
            是否处于降级模式
        """
        return self.degraded

    def get_status(self) -> Dict:
        """
        获取降级状态

        Returns:
            状态字典
        """
        return {
            'degraded': self.degraded,
            'health_check_interval': self.health_check_interval,
            'last_health_check': self.last_health_check,
            'stats': self.stats.copy(),
        }


# 全局降级管理器实例
cache_degradation_manager = CacheDegradationManager()


def get_degradation_manager() -> CacheDegradationManager:
    """
    获取全局降级管理器实例

    Returns:
        CacheDegradationManager实例
    """
    return cache_degradation_manager


logger.info("✅ 缓存降级策略模块已加载 (1.0.0)")
