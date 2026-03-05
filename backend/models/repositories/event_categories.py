#!/usr/bin/env python3
from backend.core.cache.decorators import cached

# -*- coding: utf-8 -*-
"""
Event Category Repository (事件类别数据访问层)

提供事件类别相关的数据访问方法
- 返回统一Entity模型 (EventCategoryEntity)
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict, get_db_connection


class EventCategoryRepository(GenericRepository):
    """
    事件类别仓储类

    继承 GenericRepository 并添加类别特定的查询方法
    返回EventCategoryEntity而非字典,确保类型安全
    """

    def __init__(self) -> None:
        """
        初始化事件类别仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_categories",
            primary_key="id",
            enable_cache=True,
            cache_timeout=1800,  # 30分钟缓存（类别很少变化）
        )


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称查询类别

        Args:
            name: 类别名称

        Returns:
            类别字典，不存在返回None

        Example:
            >>> repo = EventCategoryRepository()
            >>> category = repo.find_by_name('充值/付费')
        """
        query = "SELECT * FROM event_categories WHERE name = ?"
        return fetch_one_as_dict(query, (name,))


    @cached(ttl=1800)  # Cache for 30 minutes
    def get_or_create_default(self) -> int:
        """
        获取或创建"未分类"默认类别

        Returns:
            类别ID

        Example:
            >>> repo = EventCategoryRepository()
            >>> category_id = repo.get_or_create_default()
        """
        # 尝试获取"未分类"类别
        default_category = self.find_by_name("未分类")
        if default_category:
            return default_category["id"]

        # 创建"未分类"类别
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO event_categories (name) VALUES (?)",
            ("未分类",)
        )
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id

    def exists_by_id(self, category_id: int) -> bool:
        """
        检查指定ID的类别是否存在

        Args:
            category_id: 类别ID

        Returns:
            是否存在

        Example:
            >>> repo = EventCategoryRepository()
            >>> if repo.exists_by_id(1):
            ...     print("Category exists")
        """
        query = "SELECT id FROM event_categories WHERE id = ?"
        result = fetch_one_as_dict(query, (category_id,))
        return result is not None


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_all(self) -> List[Dict[str, Any]]:
        """
        查询所有类别

        Returns:
            类别字典列表

        Example:
            >>> repo = EventCategoryRepository()
            >>> categories = repo.find_all()
        """
        query = "SELECT * FROM event_categories ORDER BY name"
        return fetch_all_as_dict(query)

    def count_events(self, category_id: int) -> int:
        """
        统计指定类别的事件数量

        Args:
            category_id: 类别ID

        Returns:
            事件数量

        Example:
            >>> repo = EventCategoryRepository()
            >>> count = repo.count_events(1)
        """
        query = """
            SELECT COUNT(*) as total
            FROM log_events
            WHERE category_id = ?
        """
        result = fetch_one_as_dict(query, (category_id,))
        return result["total"] if result else 0
