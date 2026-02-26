#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Category Repository (事件类别数据访问层 - 精简架构)

提供事件类别相关的数据访问方法
- 返回统一Entity模型 (EventCategoryEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.models.entities import EventCategoryEntity


class CategoryRepository(GenericRepository):
    """
    事件类别仓储类 (精简架构)

    继承 GenericRepository 并添加类别特定的查询方法
    返回EventCategoryEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化类别仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_categories",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120  # 2分钟缓存
        )

    def find_by_id(self, category_id: int) -> Optional[EventCategoryEntity]:
        """
        根据数据库ID查询类别

        Args:
            category_id: 类别数据库ID

        Returns:
            EventCategoryEntity, 不存在返回None
        """
        query = "SELECT * FROM event_categories WHERE id = ?"
        row = fetch_one_as_dict(query, (category_id,))
        return EventCategoryEntity(**row) if row else None

    def find_by_name(self, name: str) -> Optional[EventCategoryEntity]:
        """
        根据名称查询类别

        Args:
            name: 类别名称

        Returns:
            EventCategoryEntity, 不存在返回None
        """
        query = "SELECT * FROM event_categories WHERE name = ?"
        row = fetch_one_as_dict(query, (name,))
        return EventCategoryEntity(**row) if row else None

    def find_all(self) -> List[EventCategoryEntity]:
        """
        查询所有类别

        Returns:
            EventCategoryEntity列表
        """
        query = "SELECT * FROM event_categories ORDER BY name"
        rows = fetch_all_as_dict(query)
        return [EventCategoryEntity(**row) for row in rows]

    def find_all_with_event_count(self, game_gid: Optional[int] = None) -> List[EventCategoryEntity]:
        """
        获取所有类别及其事件数量

        Args:
            game_gid: 可选的游戏GID，用于过滤特定游戏的事件

        Returns:
            EventCategoryEntity列表, 包含事件数量统计
        """
        if game_gid:
            query = """
                SELECT
                    ec.id,
                    ec.name,
                    ec.name_cn,
                    ec.description,
                    ec.color,
                    ec.icon,
                    ec.created_at,
                    ec.updated_at,
                    COUNT(DISTINCT le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le
                    ON ec.id = le.category_id
                    AND le.game_gid = ?
                GROUP BY ec.id
                ORDER BY ec.name
            """
            rows = fetch_all_as_dict(query, (game_gid,))
        else:
            query = """
                SELECT
                    ec.id,
                    ec.name,
                    ec.name_cn,
                    ec.description,
                    ec.color,
                    ec.icon,
                    ec.created_at,
                    ec.updated_at,
                    COUNT(DISTINCT le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON ec.id = le.category_id
                GROUP BY ec.id
                ORDER BY ec.name
            """
            rows = fetch_all_as_dict(query)

        return [EventCategoryEntity(**row) for row in rows]

    def create(self, data: Dict[str, Any]) -> Optional[EventCategoryEntity]:
        """
        创建类别

        Args:
            data: 类别数据字典

        Returns:
            创建的EventCategoryEntity
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建INSERT语句
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO event_categories ({columns}) VALUES ({placeholders})"

        cursor.execute(query, list(data.values()))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.find_by_id(category_id)

    def update(self, category_id: int, data: Dict[str, Any]) -> Optional[EventCategoryEntity]:
        """
        更新类别

        Args:
            category_id: 类别数据库ID
            data: 要更新的字段字典

        Returns:
            更新后的EventCategoryEntity, 不存在返回None
        """
        if not data:
            return None

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE event_categories SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [category_id]

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        # 返回更新后的类别
        return self.find_by_id(category_id)

    def delete(self, category_id: int) -> bool:
        """
        删除类别

        Args:
            category_id: 类别数据库ID

        Returns:
            是否删除成功
        """
        query = "DELETE FROM event_categories WHERE id = ?"

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (category_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0

    def batch_delete(self, category_ids: List[int]) -> int:
        """
        批量删除类别

        Args:
            category_ids: 类别ID列表

        Returns:
            删除的类别数量
        """
        if not category_ids:
            return 0

        placeholders = ",".join(["?" for _ in category_ids])
        query = f"DELETE FROM event_categories WHERE id IN ({placeholders})"

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, category_ids)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def batch_update(self, category_ids: List[int], updates: Dict[str, Any]) -> int:
        """
        批量更新类别

        Args:
            category_ids: 类别ID列表
            updates: 要更新的字段字典

        Returns:
            更新的类别数量
        """
        if not category_ids or not updates:
            return 0

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        placeholders = ",".join(["?" for _ in category_ids])
        query = f"UPDATE event_categories SET {set_clause} WHERE id IN ({placeholders})"

        values = list(updates.values()) + category_ids

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_count

    def exists_by_name(self, name: str) -> bool:
        """
        检查指定名称的类别是否存在

        Args:
            name: 类别名称

        Returns:
            是否存在
        """
        return self.find_by_name(name) is not None

    def search_by_name(self, name_pattern: str) -> List[EventCategoryEntity]:
        """
        根据名称模糊搜索类别

        Args:
            name_pattern: 名称匹配模式（支持SQL LIKE语法）

        Returns:
            匹配的类别列表
        """
        query = "SELECT * FROM event_categories WHERE name LIKE ? ORDER BY name"
        rows = fetch_all_as_dict(query, (name_pattern,))
        return [EventCategoryEntity(**row) for row in rows]
