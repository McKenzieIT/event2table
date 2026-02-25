#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统包初始化

此模块提供缓存系统的统一入口。

版本: 3.2.0
日期: 2026-02-24

架构更新 (2026-02-24):
- 统一使用cache_hierarchical.py作为主要实现（包含高级功能）
- cache_system.py保留兼容性函数和快捷方法
- 所有新代码应使用: from backend.core.cache import HierarchicalCache

两个模块的分工:
- cache_hierarchical.py: 核心HierarchicalCache类（含读写锁、布隆过滤器、降级策略）
- cache_system.py: 快捷方法、兼容性函数、特定业务逻辑方法
"""

# ============================================================================
# 基础类和接口（避免循环依赖）
# ============================================================================
from .base import (
    CacheInterface,
    BaseCache,
    CacheException,
    CacheKeyError,
    CacheValueError,
    CacheConnectionError,
    CacheKeyBuilder,
    get_cache,
)

# ============================================================================
# 核心缓存实现（主要实现）
# ============================================================================
from .cache_hierarchical import (
    HierarchicalCache,
    hierarchical_cache,
    cached_hierarchical,
)

# ============================================================================
# 快捷方法和兼容性函数
# ============================================================================
from .cache_system import (
    CacheInvalidator,
    cached,
    cache_invalidator,
    # 兼容性函数
    cache_result,
    clear_game_cache,
    clear_event_cache,
    clear_cache_pattern,
    get_redis_client,
    parse_json_cached,
)

# ============================================================================
# 导出的公共API
# ============================================================================

__all__ = [
    # 基础类和接口
    'CacheInterface',
    'BaseCache',
    'CacheException',
    'CacheKeyError',
    'CacheValueError',
    'CacheConnectionError',
    'CacheKeyBuilder',
    'get_cache',
    # 核心缓存系统（推荐使用）
    'HierarchicalCache',
    'CacheInvalidator',
    'cached',
    'cached_hierarchical',
    'hierarchical_cache',
    'cache_invalidator',
    # 兼容性函数
    'cache_result',
    'clear_game_cache',
    'clear_event_cache',
    'clear_cache_pattern',
    'get_redis_client',
    'parse_json_cached',
]

# ============================================================================
# 版本信息
# ============================================================================

__version__ = '3.2.0'
__author__ = 'Event2Table Development Team'
