#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Category Service - 业务逻辑层 (精简架构)

提供事件类别相关的业务逻辑服务
- 使用统一Entity模型 (EventCategoryEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
"""

from typing import List, Optional, Dict, Any
import logging
from backend.models.entities import EventCategoryEntity
from backend.models.repositories.category_repository import CategoryRepository
from backend.core.cache.cache_system import CacheInvalidator, cached

logger = logging.getLogger(__name__)


class CategoryService:
    """事件类别业务服务 (精简架构)"""

    def __init__(self):
        self.category_repo = CategoryRepository()
        from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
        logger.info("✅ CategoryService initialized")

    @cached("categories.list", timeout=120)
    def get_all_categories(self, game_gid: Optional[int] = None) -> List[EventCategoryEntity]:
        """
        获取所有类别 (带缓存)

        Args:
            game_gid: 可选的游戏GID，用于过滤特定游戏的事件统计

        Returns:
            类别Entity列表

        Raises:
            DatabaseError: 数据库查询失败
        """
        if game_gid:
            categories = self.category_repo.find_all_with_event_count(game_gid)
        else:
            categories = self.category_repo.find_all()

        return categories

    @cached("categories.detail", timeout=300)
    def get_category_by_id(self, category_id: int) -> Optional[EventCategoryEntity]:
        """
        根据ID获取类别 (带缓存)

        Args:
            category_id: 类别数据库ID

        Returns:
            EventCategoryEntity, 不存在返回None

        Raises:
            ValueError: category_id格式不正确
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError(f"Invalid category_id: {category_id}")

        return self.category_repo.find_by_id(category_id)

    @cached("categories.detail.name", timeout=300)
    def get_category_by_name(self, name: str) -> Optional[EventCategoryEntity]:
        """
        根据名称获取类别 (带缓存)

        Args:
            name: 类别名称

        Returns:
            EventCategoryEntity, 不存在返回None

        Raises:
            ValueError: name格式不正确
        """
        if not name or not isinstance(name, str):
            raise ValueError(f"Invalid category name: {name}")

        return self.category_repo.find_by_name(name)

    def create_category(self, category_data: EventCategoryEntity) -> EventCategoryEntity:
        """
        创建类别 (自动失效缓存)

        Args:
            category_data: 类别Entity (已通过Pydantic验证)

        Returns:
            创建的EventCategoryEntity

        Raises:
            ValueError: 名称已存在
            ValidationError: 数据验证失败
        """
        # 验证名称唯一性
        existing = self.category_repo.find_by_name(category_data.name)
        if existing:
            raise ValueError(f"Category name '{category_data.name}' already exists")

        # 创建类别 (Entity已通过Pydantic验证)
        result = self.category_repo.create(category_data.model_dump())
        if result is None:
            raise ValueError("Failed to create category")

        # 失效类别列表缓存
        self.invalidator.invalidate_pattern("categories.list")

        logger.info(f"类别创建成功,已失效缓存: name={category_data.name}")

        return result

    def update_category(self, category_id: int, updates: dict) -> EventCategoryEntity:
        """
        更新类别 (自动失效缓存)

        Args:
            category_id: 类别数据库ID
            updates: 更新字段字典

        Returns:
            更新后的EventCategoryEntity

        Raises:
            ValueError: 类别不存在
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError(f"Invalid category_id: {category_id}")

        # 验证类别存在
        existing = self.category_repo.find_by_id(category_id)
        if not existing:
            raise ValueError(f"Category ID {category_id} not found")

        # 如果更新name，检查唯一性
        if "name" in updates:
            name_check = self.category_repo.find_by_name(updates["name"])
            if name_check and name_check.id != category_id:
                raise ValueError(f"Category name '{updates['name']}' already exists")

        # 更新类别
        self.category_repo.update(category_id, updates)

        # 失效缓存
        self.invalidator.invalidate_pattern("categories.list")
        self.invalidator.invalidate_pattern(f"categories.detail:{category_id}")
        logger.info(f"类别更新成功,已失效缓存: id={category_id}")

        return self.get_category_by_id(category_id)

    def delete_category(self, category_id: int) -> None:
        """
        删除类别 (自动失效缓存)

        Args:
            category_id: 类别数据库ID

        Raises:
            ValueError: 类别不存在或有关联数据
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError(f"Invalid category_id: {category_id}")

        # 验证类别存在
        existing = self.category_repo.find_by_id(category_id)
        if not existing:
            raise ValueError(f"Category ID {category_id} not found")

        # 删除类别
        self.category_repo.delete(category_id)

        # 失效缓存
        self.invalidator.invalidate_pattern("categories.list")
        self.invalidator.invalidate_pattern(f"categories.detail:{category_id}")

        logger.info(f"类别删除成功,已失效缓存: id={category_id}")

    def batch_delete_categories(self, category_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除类别 (自动失效缓存 + 详细结果)

        Args:
            category_ids: 类别ID列表

        Returns:
            包含删除结果的字典：
            - deleted_count: 成功删除的数量
            - failed_ids: 删除失败的ID列表
            - failed_reasons: 失败原因字典 {id: reason}
            - message: 操作结果消息

        Raises:
            ValueError: category_id包含无效值
        """
        if not category_ids:
            return {
                "deleted_count": 0,
                "failed_ids": [],
                "failed_reasons": {},
                "message": "No category IDs provided"
            }

        # 验证所有ID
        for category_id in category_ids:
            if not isinstance(category_id, int) or category_id <= 0:
                raise ValueError(f"Invalid category_id: {category_id}")

        # 批量删除
        result = self.category_repo.batch_delete(category_ids)

        # 失效缓存（只针对成功删除的）
        if result["deleted_count"] > 0:
            self.invalidator.invalidate_pattern("categories.list")
            # 失效所有相关缓存（包括失败的ID，以防有缓存）
            for category_id in category_ids:
                self.invalidator.invalidate_pattern(f"categories.detail:{category_id}")

            logger.info(
                f"批量删除类别完成: 成功={result['deleted_count']}, "
                f"失败={len(result['failed_ids'])}"
            )

        # 生成消息
        total = len(category_ids)
        deleted = result["deleted_count"]
        failed = len(result["failed_ids"])

        if failed == 0:
            result["message"] = f"Successfully deleted all {deleted} categories"
        elif deleted == 0:
            result["message"] = f"Failed to delete any categories ({failed} errors)"
        else:
            result["message"] = f"Successfully deleted {deleted} out of {total} categories ({failed} failed)"

        return result

    def batch_update_categories(self, category_ids: List[int], updates: dict) -> int:
        """
        批量更新类别 (自动失效缓存)

        Args:
            category_ids: 类别ID列表
            updates: 更新字段字典

        Returns:
            更新的类别数量

        Raises:
            ValueError: category_ids或updates为空
        """
        if not category_ids or not updates:
            return 0

        # 验证所有ID
        for category_id in category_ids:
            if not isinstance(category_id, int) or category_id <= 0:
                raise ValueError(f"Invalid category_id: {category_id}")

        # 批量更新
        updated_count = self.category_repo.batch_update(category_ids, updates)

        # 失效缓存
        if updated_count > 0:
            self.invalidator.invalidate_pattern("categories.list")
            for category_id in category_ids:
                self.invalidator.invalidate_pattern(f"categories.detail:{category_id}")
            logger.info(f"批量更新类别成功,已失效缓存: count={updated_count}")

        return updated_count

    @cached("categories.search", timeout=120)
    def search_categories(self, name_pattern: str) -> List[EventCategoryEntity]:
        """
        搜索类别 (带缓存)

        Args:
            name_pattern: 名称匹配模式（支持SQL LIKE语法）

        Returns:
            匹配的类别列表
        """
        return self.category_repo.search_by_name(name_pattern)

    @cached("categories.stats", timeout=600)
    def get_statistics(self, game_gid: Optional[int] = None) -> Dict[str, Any]:
        """
        获取类别统计信息

        Args:
            game_gid: 可选的游戏GID，用于获取游戏级别的统计

        Returns:
            包含统计信息的字典:
            - total_categories: 总分类数量
            - active_categories: 活跃分类数量 (is_active=True)
            - categories_with_events: 有事件的分类数量
            - category_breakdown: 各分类的详细统计列表

        Raises:
            ValueError: game_gid无效
        """
        from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict

        # 验证game_gid（如果提供）
        if game_gid is not None and game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # 构建SQL查询（根据是否提供game_gid）
        if game_gid:
            # 游戏级别统计
            stats_query = """
                SELECT
                    COUNT(DISTINCT ec.id) as total_categories,
                    COUNT(DISTINCT CASE WHEN ec.is_active = 1 THEN ec.id END) as active_categories,
                    COUNT(DISTINCT CASE WHEN le.id IS NOT NULL THEN ec.id END) as categories_with_events
                FROM event_categories ec
                LEFT JOIN log_events le ON ec.id = le.category_id AND le.game_gid = ?
                WHERE ec.game_gid IS NULL OR ec.game_gid = ?
            """

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
        else:
            # 全局统计
            stats_query = """
                SELECT
                    COUNT(DISTINCT ec.id) as total_categories,
                    COUNT(DISTINCT CASE WHEN ec.is_active = 1 THEN ec.id END) as active_categories,
                    COUNT(DISTINCT CASE WHEN le.id IS NOT NULL THEN ec.id END) as categories_with_events
                FROM event_categories ec
                LEFT JOIN log_events le ON ec.id = le.category_id
            """

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
                "is_active": bool(row.get("is_active", 1)),
                "display_order": row.get("display_order", 0),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
                "event_count": row.get("event_count") or 0,
            })

        return {
            **stats,
            "category_breakdown": category_breakdown,
        }
