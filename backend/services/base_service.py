#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务基类 (Service Base Class)

提供统一的缓存管理功能:
- CacheInvalidator实例
- 游戏相关缓存失效
- 通用缓存清理

所有Service类应继承此基类以保持一致的缓存管理行为
"""

from backend.core.cache.invalidator import CacheInvalidatorEnhanced

# 别名以保持向后兼容
CacheInvalidator = CacheInvalidatorEnhanced


class BaseService:
    """
    服务基类 - 提供统一的缓存管理

    职责:
    - 提供CacheInvalidator实例
    - 统一的缓存失效方法
    - 缓存键命名规范

    Examples:
        >>> class GameService(BaseService):
        ...     def update_game(self, game_gid: int, data: dict):
        ...         # 更新游戏
        ...         result = self.game_repo.update(game_gid, data)
        ...         # 清理缓存
        ...         self.invalidate_game_cache(game_gid)
        ...         return result
    """

    def __init__(self):
        """初始化服务基类"""
        self.invalidator = CacheInvalidator()

    def invalidate_game_cache(self, game_gid: int):
        """
        清理游戏相关的所有缓存

        清理范围:
        - 游戏详情缓存
        - 游戏事件列表缓存
        - 游戏参数列表缓存
        - 游戏相关统计缓存

        Args:
            game_gid: 游戏GID

        Examples:
            >>> service = BaseService()
            >>> service.invalidate_game_cache(10000147)
        """
        self.invalidator.invalidate_game_related(game_gid)

    def invalidate_pattern(self, pattern: str):
        """
        清理匹配模式的所有缓存

        Args:
            pattern: 缓存键模式（支持通配符）

        Examples:
            >>> service = BaseService()
            >>> # 清理所有游戏列表缓存
            >>> service.invalidate_pattern("games.list:*")
            >>> # 清理所有事件缓存
            >>> service.invalidate_pattern("events:*")
        """
        self.invalidator.invalidate_pattern(pattern)

    def invalidate_all(self):
        """
        清理所有缓存

        警告: 此操作会清理所有缓存, 应谨慎使用

        Examples:
            >>> service = BaseService()
            >>> service.invalidate_all()
        """
        self.invalidator.invalidate_all()
