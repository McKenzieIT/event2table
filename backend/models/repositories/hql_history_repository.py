# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL History Repository (HQL历史数据访问层 - 精简架构)

提供HQL历史记录相关的数据访问方法
- 返回统一Entity模型 (HQLHistoryEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import List, Dict, Optional, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.utils import execute_write
from backend.models.entities import HQLHistoryEntity
from backend.core.utils.json_helpers import serialize_json_field, deserialize_json_field


class HQLHistoryRepository(GenericRepository):
    """
    HQL历史仓储类 (精简架构)

    继承 GenericRepository 并添加HQL历史特定的查询方法
    返回HQLHistoryEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化HQL历史仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="hql_history",
            primary_key="id",
            enable_cache=True,
            cache_timeout=300  # 5分钟缓存 (历史数据变化不频繁)
        )

    def find_by_id(self, history_id: int) -> Optional[HQLHistoryEntity]:
        """
        根据ID查找HQL历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            HQLHistoryEntity, 不存在返回None

        Example:
            >>> repo = HQLHistoryRepository()
            >>> history = repo.find_by_id(1)
            >>> print(history.hql) if history else None
        """
        query = f'SELECT * FROM "{self.table_name}" WHERE id = ?'
        row = fetch_one_as_dict(query, (history_id,))

        if row:
            row = self._deserialize_json_fields(row)

        return HQLHistoryEntity(**row) if row else None

    def find_by_user_id(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[HQLHistoryEntity]:
        """
        根据用户ID查找HQL历史记录

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表

        Example:
            >>> repo = HQLHistoryRepository()
            >>> histories = repo.find_by_user_id(1, limit=10)
            >>> for h in histories:
            ...     print(h.hql)
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        rows = fetch_all_as_dict(query, (user_id, limit, offset))

        # 反序列化JSON字段并转换为Entity
        entities = []
        for row in rows:
            row = self._deserialize_json_fields(row)
            entities.append(HQLHistoryEntity(**row))

        return entities

    def find_by_session_id(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[HQLHistoryEntity]:
        """
        根据会话ID查找HQL历史记录

        Args:
            session_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        rows = fetch_all_as_dict(query, (session_id, limit, offset))

        # 反序列化JSON字段并转换为Entity
        entities = []
        for row in rows:
            row = self._deserialize_json_fields(row)
            entities.append(HQLHistoryEntity(**row))

        return entities

    def find_by_game_gid(
        self, game_gid: int, limit: int = 50, offset: int = 0
    ) -> List[HQLHistoryEntity]:
        """
        根据游戏GID查找HQL历史记录

        Args:
            game_gid: 游戏GID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE game_gid = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        rows = fetch_all_as_dict(query, (game_gid, limit, offset))

        entities = []
        for row in rows:
            row = self._deserialize_json_fields(row)
            entities.append(HQLHistoryEntity(**row))

        return entities

    def search_by_keyword(
        self,
        keyword: str,
        user_id: Optional[int] = None,
        hql_type: Optional[str] = None,
        game_gid: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HQLHistoryEntity]:
        """
        根据关键词搜索HQL历史记录

        Args:
            keyword: 搜索关键词
            user_id: 用户ID过滤
            hql_type: HQL类型过滤
            game_gid: 游戏GID过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            HQLHistoryEntity列表
        """
        # 构建查询条件
        where_conditions = ["(name_en LIKE ? OR name_cn LIKE ? OR hql LIKE ?)"]
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]

        if user_id is not None:
            where_conditions.append("user_id = ?")
            params.append(user_id)

        if hql_type is not None:
            where_conditions.append("hql_type = ?")
            params.append(hql_type)

        if game_gid is not None:
            where_conditions.append("game_gid = ?")
            params.append(game_gid)

        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE {' AND '.join(where_conditions)}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])

        rows = fetch_all_as_dict(query, tuple(params))

        entities = []
        for row in rows:
            row = self._deserialize_json_fields(row)
            entities.append(HQLHistoryEntity(**row))

        return entities

    def count_by_user_id(self, user_id: int) -> int:
        """
        统计用户的HQL历史记录数量

        Args:
            user_id: 用户ID

        Returns:
            记录数量
        """
        query = f'SELECT COUNT(*) as count FROM "{self.table_name}" WHERE user_id = ?'
        result = fetch_one_as_dict(query, (user_id,))
        return result["count"] if result else 0

    def create(self, history: HQLHistoryEntity) -> int:
        """
        创建新HQL历史记录

        Args:
            history: HQLHistoryEntity实例

        Returns:
            新创建的历史记录ID

        Example:
            >>> from backend.models.entities import HQLHistoryEntity
            >>> repo = HQLHistoryRepository()
            >>> history = HQLHistoryEntity(
            ...     user_id=1,
            ...     events_json=[{"event_name": "login"}],
            ...     fields_json=[{"name": "role_id"}],
            ...     mode="single",
            ...     hql="SELECT role_id FROM table"
            ... )
            >>> history_id = repo.create(history)
        """
        insert_sql = f'''
            INSERT INTO "{self.table_name}" (
                user_id, session_id, events_json, fields_json, conditions_json,
                mode, hql, performance_score, metadata_json,
                hql_type, game_gid, name_en, name_cn, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        '''

        params = (
            history.user_id,
            history.session_id,
            serialize_json_field(history.events_json),
            serialize_json_field(history.fields_json),
            serialize_json_field(history.conditions_json or []),
            history.mode,
            history.hql,
            history.performance_score,
            serialize_json_field(history.metadata_json),
            history.hql_type,
            history.game_gid,
            history.name_en,
            history.name_cn,
        )

        return execute_write(insert_sql, params, return_last_id=True)

    def update(self, history_id: int, history: HQLHistoryEntity) -> bool:
        """
        更新HQL历史记录

        注意：通常不允许修改HQL历史记录，此方法仅用于特殊情况

        Args:
            history_id: 历史记录ID
            history: HQLHistoryEntity实例

        Returns:
            是否更新成功
        """
        update_parts = [
            "hql = ?",
            "performance_score = ?",
            "name_en = ?",
            "name_cn = ?",
        ]

        params = (
            history.hql,
            history.performance_score,
            history.name_en,
            history.name_cn,
            history_id,
        )

        update_sql = f'''
            UPDATE "{self.table_name}" SET
            {", ".join(update_parts)}
            WHERE id = ?
        '''

        result = execute_write(update_sql, params)
        return result > 0

    def delete(self, history_id: int) -> bool:
        """
        删除HQL历史记录

        Args:
            history_id: 历史记录ID

        Returns:
            是否删除成功

        Example:
            >>> repo = HQLHistoryRepository()
            >>> success = repo.delete(1)
        """
        delete_sql = f'DELETE FROM "{self.table_name}" WHERE id = ?'
        result = execute_write(delete_sql, (history_id,))
        return result > 0

    def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        反序列化JSON字段

        Args:
            row: 数据库行数据

        Returns:
            反序列化后的数据
        """
        row["events_json"] = deserialize_json_field(row.get("events_json"))
        row["fields_json"] = deserialize_json_field(row.get("fields_json"))
        row["conditions_json"] = deserialize_json_field(row.get("conditions_json"))
        row["metadata_json"] = deserialize_json_field(row.get("metadata_json"))
        return row
