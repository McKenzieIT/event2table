#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Repository (游戏数据访问层)

提供游戏相关的数据访问方法
基于 GenericRepository 实现特定领域的查询
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class GameRepository(GenericRepository):
    """
    游戏仓储类

    继承 GenericRepository 并添加游戏特定的查询方法
    """

    def __init__(self):
        """
        初始化游戏仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="games", primary_key="id", enable_cache=True, cache_timeout=120  # 2分钟缓存
        )

    def find_by_gid(self, gid: int) -> Optional[Dict[str, Any]]:
        """
        根据业务GID查询游戏

        Args:
            gid: 游戏业务GID

        Returns:
            游戏字典，不存在返回None

        Example:
            >>> repo = GameRepository()
            >>> game = repo.find_by_gid(1001)
            >>> print(game['name']) if game else None
        """
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))

    def get_all_with_event_count(self) -> List[Dict[str, Any]]:
        """
        获取所有游戏及其事件数量

        Returns:
            游戏列表，每个游戏包含事件数量统计

        Example:
            >>> repo = GameRepository()
            >>> games = repo.get_all_with_event_count()
            >>> for game in games:
            ...     print(f"{game['name']}: {game['event_count']} events")
        """
        query = """
            SELECT
                g.*,
                COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            GROUP BY g.id
            ORDER BY g.name
        """
        return fetch_all_as_dict(query)

    def get_all_with_stats(self) -> List[Dict[str, Any]]:
        """
        获取所有游戏及其详细统计信息

        Returns:
            游戏列表，包含事件数、参数数等统计信息

        Example:
            >>> repo = GameRepository()
            >>> games = repo.get_all_with_stats()
            >>> for game in games:
            ...     print(f"{game['name']}: {game['event_count']} events, {game['param_count']} params")
        """
        query = """
            SELECT
                g.*,
                COUNT(DISTINCT le.id) as event_count,
                COUNT(DISTINCT ep.id) as param_count,
                MAX(le.updated_at) as last_event_update
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            LEFT JOIN event_params ep ON le.id = ep.event_id
            GROUP BY g.id
            ORDER BY g.name
        """
        return fetch_all_as_dict(query)

    def find_by_ods_db(self, ods_db: str) -> List[Dict[str, Any]]:
        """
        根据ODS数据库查询游戏列表

        Args:
            ods_db: ODS数据库名称 ('ieu_ods' 或 'overseas_ods')

        Returns:
            游戏列表

        Example:
            >>> repo = GameRepository()
            >>> games = repo.find_by_ods_db('ieu_ods')
        """
        query = "SELECT * FROM games WHERE ods_db = ? ORDER BY name"
        return fetch_all_as_dict(query, (ods_db,))

    def search_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        根据名称模糊搜索游戏

        Args:
            name_pattern: 名称匹配模式（支持SQL LIKE语法）

        Returns:
            匹配的游戏列表

        Example:
            >>> repo = GameRepository()
            >>> games = repo.search_by_name('%王者%')
        """
        query = "SELECT * FROM games WHERE name LIKE ? ORDER BY name"
        return fetch_all_as_dict(query, (name_pattern,))

    def get_game_categories_summary(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取游戏的分类统计摘要

        Args:
            game_gid: 游戏GID

        Returns:
            分类统计列表

        Example:
            >>> repo = GameRepository()
            >>> summary = repo.get_game_categories_summary(1001)
        """
        query = """
            SELECT
                ec.id as category_id,
                ec.name as category_name,
                COUNT(DISTINCT le.id) as event_count
            FROM games g
            JOIN log_events le ON g.gid = le.game_gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE g.gid = ?
            GROUP BY ec.id, ec.name
            ORDER BY event_count DESC
        """
        return fetch_all_as_dict(query, (game_gid,))

    def exists_by_gid(self, gid: int) -> bool:
        """
        检查指定GID的游戏是否存在

        Args:
            gid: 游戏业务GID

        Returns:
            是否存在

        Example:
            >>> repo = GameRepository()
            >>> if repo.exists_by_gid(1001):
            ...     print("Game exists")
        """
        return self.find_by_gid(gid) is not None

    def get_game_for_update(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        获取游戏信息用于更新操作

        Args:
            game_id: 游戏ID

        Returns:
            游戏字典

        Note:
            此方法不使用缓存，确保获取最新数据用于更新操作
        """
        query = "SELECT * FROM games WHERE id = ?"
        return fetch_one_as_dict(query, (game_id,))
