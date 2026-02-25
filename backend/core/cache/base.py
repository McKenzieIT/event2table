#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统基础类和接口

此模块提供缓存系统的抽象基类和接口，用于打破循环依赖。

版本: 1.0.0
日期: 2026-02-24
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class CacheInterface(ABC):
    """缓存接口定义 - 所有缓存实现必须遵循此接口"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""

    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""


class BaseCache(CacheInterface):
    """缓存基类 - 提供通用功能和统计记录"""

    def __init__(self, name: str):
        """
        初始化缓存基类

        Args:
            name: 缓存实例名称
        """
        self.name = name
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self._stats.copy()

    def _record_hit(self):
        """记录缓存命中"""
        self._stats['hits'] += 1

    def _record_miss(self):
        """记录缓存未命中"""
        self._stats['misses'] += 1

    def _record_set(self):
        """记录缓存设置"""
        self._stats['sets'] += 1

    def _record_delete(self):
        """记录缓存删除"""
        self._stats['deletes'] += 1


class CacheException(Exception):
    """缓存异常基类"""


class CacheKeyError(CacheException):
    """缓存键错误"""


class CacheValueError(CacheException):
    """缓存值错误"""


class CacheConnectionError(CacheException):
    """缓存连接错误"""


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
# 缓存获取辅助函数
# ============================================================================


def get_cache():
    """
    获取Flask-Cache实例

    Returns:
        Flask-Cache实例或None
    """
    try:
        return getattr(current_app, 'cache', None)
    except (AttributeError, RuntimeError):
        # 不在Flask应用上下文中
        return None
