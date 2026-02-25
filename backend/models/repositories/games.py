#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Repository (游戏数据访问层 - 精简架构)

提供游戏相关的数据访问方法
- 返回统一Entity模型 (GameEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.models.entities import GameEntity


class GameRepository(GenericRepository):
    """
    游戏仓储类 (精简架构)

    继承 GenericRepository 并添加游戏特定的查询方法
    返回GameEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化游戏仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="games", primary_key="id", enable_cache=True, cache_timeout=120  # 2分钟缓存
        )

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """
        根据业务GID查询游戏

        Args:
            gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None

        Example:
            >>> repo = GameRepository()
            >>> game = repo.find_by_gid(1001)
            >>> print(game.name) if game else None
        """
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    def find_all(self) -> List[GameEntity]:
        """
        查询所有游戏

        Returns:
            GameEntity列表
        """
        query = "SELECT * FROM games ORDER BY name"
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]

    def find_by_id(self, game_id: int) -> Optional[GameEntity]:
        """
        根据数据库ID查询游戏

        Args:
            game_id: 数据库自增ID

        Returns:
            GameEntity, 不存在返回None
        """
        query = "SELECT * FROM games WHERE id = ?"
        row = fetch_one_as_dict(query, (game_id,))
        return GameEntity(**row) if row else None

    def get_all_with_event_count(self) -> List[GameEntity]:
        """
        获取所有游戏及其事件数量

        Returns:
            GameEntity列表, 包含事件数量统计

        Example:
            >>> repo = GameRepository()
            >>> games = repo.get_all_with_event_count()
            >>> for game in games:
            ...     print(f"{game.name}: {game.event_count} events")
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
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]

    def get_all_with_stats(self) -> List[GameEntity]:
        """
        获取所有游戏及其详细统计信息

        Returns:
            GameEntity列表, 包含事件数、参数数等统计信息

        Example:
            >>> repo = GameRepository()
            >>> games = repo.get_all_with_stats()
            >>> for game in games:
            ...     print(f"{game.name}: {game.event_count} events, {game.param_count} params")
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
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]

    def batch_delete(self, game_gids: List[int]) -> int:
        """
        批量删除游戏

        Args:
            game_gids: 游戏GID列表

        Returns:
            删除的游戏数量
        """
        if not game_gids:
            return 0

        placeholders = ",".join(["?" for _ in game_gids])
        query = f"DELETE FROM games WHERE gid IN ({placeholders})"

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, game_gids)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def update(self, game_gid: int, data: Dict[str, Any]) -> Optional[GameEntity]:
        """
        根据game_gid更新游戏

        Args:
            game_gid: 游戏业务GID
            data: 要更新的字段字典

        Returns:
            更新后的GameEntity, 不存在返回None

        Example:
            >>> repo = GameRepository()
            >>> game = repo.update(10000147, {'name': 'Updated Name'})
        """
        if not data:
            return None

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE games SET {set_clause} WHERE gid = ?"
        values = list(data.values()) + [game_gid]

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        # 返回更新后的游戏
        return self.find_by_gid(game_gid)

    def delete(self, game_gid: int) -> bool:
        """
        根据game_gid删除游戏

        Args:
            game_gid: 游戏业务GID

        Returns:
            是否删除成功

        Example:
            >>> repo = GameRepository()
            >>> success = repo.delete(10000147)
        """
        query = "DELETE FROM games WHERE gid = ?"

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (game_gid,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0
        cursor = conn.cursor()
        cursor.execute(query, game_gids)
        conn.commit()

        return cursor.rowcount

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
