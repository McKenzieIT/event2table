# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

# 导入 decorators 中的 cached 装饰器(支持 ttl 和 key_prefix 参数)
from backend.core.cache.decorators import cached as cached_decorator

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Repository (游戏数据访问层 - 精简架构)

提供游戏相关的数据访问方法
- 返回统一Entity模型 (GameEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Any, Dict, List, Optional

from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
from backend.models.entities import GameEntity


class GameRepository(GenericRepository):
    """
    游戏仓储类 (精简架构)

    继承 GenericRepository 并添加游戏特定的查询方法
    返回GameEntity而非字典,确保类型安全
    """

    def __init__(self) -> None:
        """
        初始化游戏仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="games", primary_key="id", enable_cache=True, cache_timeout=120  # 2分钟缓存
        )

    @cached_decorator(ttl=1800, key_prefix="games.by_gid")
    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """
        根据业务GID查询游戏（带缓存）

        Args:
            gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None

        Performance:
            缓存TTL: 30分钟（静态数据）
            预期命中率: >80%

        Example:
            >>> repo = GameRepository()
            >>> game = repo.find_by_gid(1001)
            >>> print(game.name) if game else None
        """
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None

    @cached_decorator(ttl=1800, key_prefix="games.list")
    def find_all(self) -> List[GameEntity]:
        """
        查询所有游戏（跳过无效数据）

        Returns:
            GameEntity列表
        """
        import logging

        from pydantic import ValidationError

        logger = logging.getLogger(__name__)
        query = "SELECT * FROM games ORDER BY name"
        rows = fetch_all_as_dict(query)

        # 过滤掉无效的游戏数据(避免Pydantic验证失败)
        valid_games = []
        for row in rows:
            try:
                game = GameEntity(**row)
                valid_games.append(game)
            except ValidationError as e:
                logger.warning(f"Skipping invalid game data (id={row.get('id')}): {e}")
                continue

        return valid_games

    @cached_decorator(ttl=1800, key_prefix="games.by_id")
    def find_by_id(self, game_id: int) -> Optional[GameEntity]:
        """
        根据数据库ID查询游戏（带缓存）

        Args:
            game_id: 数据库自增ID

        Returns:
            GameEntity, 不存在返回None

        Performance:
            缓存TTL: 30分钟（静态数据）
            预期命中率: >80%
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
            GameEntity列表, 包含事件数, 参数数等统计信息

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

    def batch_update_by_gid(self, game_gids: List[int], updates: Dict[str, Any]) -> int:
        """
        批量更新游戏（按GID）

        Args:
            game_gids: 游戏GID列表
            updates: 要更新的字段字典

        Returns:
            更新的游戏数量

        Example:
            >>> repo = GameRepository()
            >>> count = repo.batch_update_by_gid([1001, 1002], {'name': 'Updated'})
        """
        if not game_gids or not updates:
            return 0

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        placeholders = ",".join(["?" for _ in game_gids])
        query = f"UPDATE games SET {set_clause} WHERE gid IN ({placeholders})"
        values = list(updates.values()) + game_gids

        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_count

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
            此方法不使用缓存, 确保获取最新数据用于更新操作
        """
        query = "SELECT * FROM games WHERE id = ?"
        return fetch_one_as_dict(query, (game_id,))

    def get_gids_by_list(self, gids: List[str]) -> List[str]:
        """
        批量检查GID是否存在

        Args:
            gids: 游戏GID列表

        Returns:
            已存在的GID列表

        Example:
            >>> repo = GameRepository()
            >>> existing = repo.get_gids_by_list(['1001', '1002'])
            >>> print(existing)  # ['1001'] 如果只有1001存在
        """
        if not gids:
            return []

        placeholders = ",".join(["?" for _ in gids])
        query = f"SELECT gid FROM games WHERE gid IN ({placeholders})"

        rows = fetch_all_as_dict(query, gids)
        return [row['gid'] for row in rows]

    def get_by_ids(self, game_ids: List[int]) -> List[Dict[str, Any]]:
        """
        批量查询游戏（按数据库ID）

        Args:
            game_ids: 游戏ID列表

        Returns:
            游戏列表

        Example:
            >>> repo = GameRepository()
            >>> games = repo.get_by_ids([1, 2, 3])
        """
        if not game_ids:
            return []

        placeholders = ",".join(["?" for _ in game_ids])
        query = f"SELECT * FROM games WHERE id IN ({placeholders})"

        return fetch_all_as_dict(query, game_ids)

    def delete_batch(self, game_ids: List[int]) -> int:
        """
        批量删除游戏（按数据库ID）

        Args:
            game_ids: 游戏ID列表

        Returns:
            删除的游戏数量

        Example:
            >>> repo = GameRepository()
            >>> count = repo.delete_batch([1, 2, 3])
        """
        if not game_ids:
            return 0

        placeholders = ",".join(["?" for _ in game_ids])
        query = f"DELETE FROM games WHERE id IN ({placeholders})"

        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, game_ids)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def create_batch(self, games_data: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建游戏（真正的批量INSERT）

        使用 executemany() 实现, 确保单次数据库往返

        Args:
            games_data: 游戏数据列表

        Returns:
            创建的游戏ID列表

        Performance:
            数据库往返: 1次（executemany）
            预期性能: <1秒 for 100 records

        Example:
            >>> repo = GameRepository()
            >>> games = [
            ...     {'gid': '1001', 'name': 'Game1', 'ods_db': 'ieu_ods'},
            ...     {'gid': '1002', 'name': 'Game2', 'ods_db': 'ieu_ods'}
            ... ]
            >>> ids = repo.create_batch(games)
        """
        if not games_data:
            return []

        from backend.core.database.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 构建批量INSERT SQL(移除name_cn字段, 数据库中不存在)
            query = """
                INSERT INTO games (gid, name, ods_db, description, dwd_prefix, icon_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            # 准备参数列表
            params = [
                (
                    g.get('gid'),
                    g.get('name'),
                    g.get('ods_db', f"ods_game_{g.get('gid')}"),
                    g.get('description', ''),
                    g.get('dwd_prefix', 'dwd'),
                    g.get('icon_path'),
                )
                for g in games_data
            ]

            # 执行批量插入(单次数据库往返)
            cursor.executemany(query, params)

            # 提交事务
            conn.commit()

            # 获取插入的ID列表
            # 注意: executemany不返回lastrowid, 需要查询获取
            inserted_ids = []
            for game_data in games_data:
                gid = game_data.get('gid')
                cursor.execute("SELECT id FROM games WHERE gid = ?", (gid,))
                row = cursor.fetchone()
                if row:
                    inserted_ids.append(row[0])

            return inserted_ids

        except Exception as e:
            # 回滚事务
            conn.rollback()
            raise e
        finally:
            conn.close()
