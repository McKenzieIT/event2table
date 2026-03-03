#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Statement Repository (HQL语句仓储层)

提供HQL语句的数据访问操作
"""

from typing import List, Optional, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict, get_db_connection


class HQLStatementRepository(GenericRepository):
    """
    HQL语句仓储类

    提供HQL语句表的CRUD操作和特定查询方法
    """

    def __init__(self):
        """初始化HQL语句仓储"""
        super().__init__(table_name="hql_statements")

    def find_by_id(self, statement_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取HQL语句

        Args:
            statement_id: HQL语句ID

        Returns:
            HQL语句字典，不存在返回None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE id = ?
            ORDER BY hql_version DESC
            LIMIT 1
        """
        return fetch_one_as_dict(query, (statement_id,))

    def get_latest_version(self, statement_id: int) -> Optional[Dict[str, Any]]:
        """
        获取HQL语句的最新版本信息

        Args:
            statement_id: HQL语句ID

        Returns:
            包含id和hql_version的字典，不存在返回None
        """
        query = f"""
            SELECT id, hql_version FROM {self.table_name}
            WHERE id = ?
            ORDER BY hql_version DESC
            LIMIT 1
        """
        return fetch_one_as_dict(query, (statement_id,))

    def activate(self, statement_id: int) -> bool:
        """
        激活指定版本的HQL语句

        Args:
            statement_id: HQL语句ID

        Returns:
            是否激活成功
        """
        # 获取当前版本信息
        current = self.get_latest_version(statement_id)
        if not current:
            return False

        # 如果当前不是最新版本，则激活
        if current["hql_version"] > 1:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE {self.table_name}
                SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (statement_id,),
            )
            conn.commit()
            conn.close()
            return True

        return False

    def find_by_game_and_event(
        self, game_gid: int, event_name: str
    ) -> List[Dict[str, Any]]:
        """
        根据游戏和事件名称获取HQL语句列表

        Args:
            game_gid: 游戏GID
            event_name: 事件名称

        Returns:
            HQL语句字典列表
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE game_gid = ? AND event_name = ?
            ORDER BY hql_version DESC
        """
        return fetch_all_as_dict(query, (game_gid, event_name))

    def find_active_by_game_and_event(
        self, game_gid: int, event_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        根据游戏和事件名称获取活跃的HQL语句

        Args:
            game_gid: 游戏GID
            event_name: 事件名称

        Returns:
            HQL语句字典，不存在返回None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE game_gid = ? AND event_name = ? AND is_active = 1
            ORDER BY hql_version DESC
            LIMIT 1
        """
        return fetch_one_as_dict(query, (game_gid, event_name))
