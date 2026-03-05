# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

from backend.core.cache.decorators import cached

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


    @cached(ttl=1800)
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

    def batch_delete(self, category_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除类别（带外键约束检查）

        Args:
            category_ids: 类别ID列表

        Returns:
            包含删除结果的字典：
            - deleted_count: 成功删除的数量
            - failed_ids: 删除失败的ID列表
            - failed_reasons: 失败原因字典 {id: reason}
        """
        from backend.core.utils.converters import get_db_connection

        if not category_ids:
            return {
                "deleted_count": 0,
                "failed_ids": [],
                "failed_reasons": {}
            }

        result = {
            "deleted_count": 0,
            "failed_ids": [],
            "failed_reasons": {}
        }

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 检查每个类别的外键约束
            for category_id in category_ids:
                # 检查类别是否存在
                cursor.execute("SELECT id FROM event_categories WHERE id = ?", (category_id,))
                if not cursor.fetchone():
                    result["failed_ids"].append(category_id)
                    result["failed_reasons"][category_id] = "Category not found"
                    continue

                # 检查是否有事件引用此类别
                cursor.execute(
                    "SELECT COUNT(*) FROM log_events WHERE category_id = ?",
                    (category_id,)
                )
                event_count = cursor.fetchone()[0]

                if event_count > 0:
                    result["failed_ids"].append(category_id)
                    result["failed_reasons"][category_id] = f"Category has {event_count} associated events"
                    continue

                # 可以删除
                cursor.execute("DELETE FROM event_categories WHERE id = ?", (category_id,))
                if cursor.rowcount > 0:
                    result["deleted_count"] += 1

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return result

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

    def get_game_statistics(self, game_gid: int) -> Dict[str, Any]:
        """
        获取特定游戏的类别统计信息

        Args:
            game_gid: 游戏业务GID

        Returns:
            包含统计信息和详细分类的字典:
            - total_categories: 总分类数量
            - active_categories: 活跃分类数量 (is_active=True)
            - categories_with_events: 有事件的分类数量
            - category_breakdown: 各分类的详细统计列表

        Raises:
            ValueError: game_gid无效
        """
        if game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # 统计查询
        stats_query = """
            SELECT
                COUNT(DISTINCT ec.id) as total_categories,
                COUNT(DISTINCT CASE WHEN ec.is_active = 1 THEN ec.id END) as active_categories,
                COUNT(DISTINCT CASE WHEN le.id IS NOT NULL THEN ec.id END) as categories_with_events
            FROM event_categories ec
            LEFT JOIN log_events le ON ec.id = le.category_id AND le.game_gid = ?
            WHERE ec.game_gid IS NULL OR ec.game_gid = ?
        """

        # 详细分类查询
        breakdown_query = """
            SELECT
                ec.id,
                ec.name,
                ec.name_cn,
                ec.description,
                ec.color,
                ec.icon,
                ec.is_active,
                ec.display_order,
                ec.created_at,
                ec.updated_at,
                COUNT(DISTINCT le.id) as event_count
            FROM event_categories ec
            LEFT JOIN log_events le ON ec.id = le.category_id AND le.game_gid = ?
            WHERE ec.game_gid IS NULL OR ec.game_gid = ?
            GROUP BY ec.id
            ORDER BY ec.display_order, ec.name
        """

        stats = fetch_one_as_dict(stats_query, (game_gid, game_gid))
        breakdown = fetch_all_as_dict(breakdown_query, (game_gid, game_gid))

        # 确保统计字段不为NULL
        stats = {
            "total_categories": stats.get("total_categories") or 0,
            "active_categories": stats.get("active_categories") or 0,
            "categories_with_events": stats.get("categories_with_events") or 0,
        }

        # 构建详细分类统计列表
        category_breakdown = []
        for row in breakdown:
            category_breakdown.append({
                "id": row["id"],
                "name": row["name"],
                "name_cn": row.get("name_cn"),
                "description": row.get("description"),
                "color": row.get("color"),
                "icon": row.get("icon"),
                "is_active": bool(row.get("is_active")),
                "display_order": row.get("display_order"),
                "event_count": row.get("event_count") or 0,
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            })

        stats["category_breakdown"] = category_breakdown
        return stats

    def get_global_statistics(self) -> Dict[str, Any]:
        """
        获取全局类别统计信息（跨所有游戏）

        Returns:
            包含统计信息和详细分类的字典:
            - total_categories: 总分类数量
            - active_categories: 活跃分类数量 (is_active=True)
            - categories_with_events: 有事件的分类数量
            - category_breakdown: 各分类的详细统计列表
        """
        # 统计查询
        stats_query = """
            SELECT
                COUNT(DISTINCT ec.id) as total_categories,
                COUNT(DISTINCT CASE WHEN ec.is_active = 1 THEN ec.id END) as active_categories,
                COUNT(DISTINCT CASE WHEN le.id IS NOT NULL THEN ec.id END) as categories_with_events
            FROM event_categories ec
            LEFT JOIN log_events le ON ec.id = le.category_id
        """

        # 详细分类查询
        breakdown_query = """
            SELECT
                ec.id,
                ec.name,
                ec.name_cn,
                ec.description,
                ec.color,
                ec.icon,
                ec.is_active,
                ec.display_order,
                ec.created_at,
                ec.updated_at,
                COUNT(DISTINCT le.id) as event_count
            FROM event_categories ec
            LEFT JOIN log_events le ON ec.id = le.category_id
            GROUP BY ec.id
            ORDER BY ec.display_order, ec.name
        """

        stats = fetch_one_as_dict(stats_query)
        breakdown = fetch_all_as_dict(breakdown_query)

        # 确保统计字段不为NULL
        stats = {
            "total_categories": stats.get("total_categories") or 0,
            "active_categories": stats.get("active_categories") or 0,
            "categories_with_events": stats.get("categories_with_events") or 0,
        }

        # 构建详细分类统计列表
        category_breakdown = []
        for row in breakdown:
            category_breakdown.append({
                "id": row["id"],
                "name": row["name"],
                "name_cn": row.get("name_cn"),
                "description": row.get("description"),
                "color": row.get("color"),
                "icon": row.get("icon"),
                "is_active": bool(row.get("is_active")),
                "display_order": row.get("display_order"),
                "event_count": row.get("event_count") or 0,
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            })

        stats["category_breakdown"] = category_breakdown
        return stats
