#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Importer Service (Refactored to use EventService)

批量导入事件数据的业务服务层
- 使用EventService进行业务逻辑处理
- 移除直接数据库访问
- 集成缓存失效和Bloom Filter
"""

from typing import List, Dict, Any
import html

from backend.core.logging import get_logger
from backend.models.entities import EventEntity
from backend.models.repositories.events import EventRepository
from backend.models.repositories.category_repository import CategoryRepository
from backend.services.events.event_service import EventService

logger = get_logger(__name__)


class EventImporter:
    """
    事件导入器 (重构版 - 使用EventService)

    职责：
    - 批量导入事件的业务流程编排
    - 使用EventService处理单个事件创建
    - 使用CategoryRepository处理分类管理
    - 返回导入结果统计

    不再直接访问数据库，所有数据访问通过Service/Repository层
    """

    def __init__(self):
        """初始化导入器"""
        self.event_service = EventService()
        self.event_repo = EventRepository()
        self.category_repo = CategoryRepository()
        logger.info("✅ EventImporter initialized (using EventService)")

    def import_events(
        self, game_gid: int, events_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量导入事件 (使用EventService)

        Args:
            game_gid: 游戏GID
            events_data: 事件数据列表

        Returns:
            导入结果统计 {
                "imported": 成功数量,
                "failed": 失败数量,
                "errors": 错误列表,
                "total": 总数
            }
        """
        imported = 0
        failed = 0
        errors = []

        # 验证游戏是否存在 (通过EventService)
        try:
            # 尝试获取游戏的事件列表来验证游戏存在
            self.event_service.get_events_by_game(game_gid, page=1, per_page=1)
        except ValueError as e:
            return {
                "imported": 0,
                "failed": len(events_data),
                "errors": [f"Game with gid {game_gid} not found"],
                "total": len(events_data),
            }

        # 批量检查已存在的事件 (避免在循环中重复查询)
        existing_set = self._get_existing_event_names(game_gid, events_data)

        # 批量导入事件
        for idx, event_data in enumerate(events_data, 1):
            try:
                event_code = event_data.get("event_code")
                if not event_code:
                    errors.append(f"Row {idx}: Missing event_code")
                    failed += 1
                    continue

                # 检查事件是否已存在
                if event_code in existing_set:
                    errors.append(f"Row {idx}: Event {event_code} already exists")
                    failed += 1
                    continue

                # 转换为EventEntity并创建
                event_entity = self._convert_to_event_entity(
                    game_gid, event_data
                )

                # 使用EventService创建事件 (自动处理缓存失效和Bloom Filter)
                created_event = self.event_service.create_event(event_entity)

                if created_event:
                    imported += 1
                    logger.info(
                        f"✅ Imported event: {event_code} (ID: {created_event.id})"
                    )
                else:
                    errors.append(f"Row {idx}: Failed to create event {event_code}")
                    failed += 1

            except ValueError as e:
                # 业务逻辑错误 (如游戏不存在、事件已存在)
                errors.append(f"Row {idx}: {str(e)}")
                failed += 1
                logger.warning(f"Validation error at row {idx}: {e}")
            except Exception as e:
                # 未预期的错误
                errors.append(f"Row {idx}: {str(e)}")
                failed += 1
                logger.error(f"Failed to import event at row {idx}: {e}", exc_info=True)

        result = {
            "imported": imported,
            "failed": failed,
            "errors": errors,
            "total": len(events_data),
        }

        logger.info(
            f"📊 Import completed: {imported}/{len(events_data)} imported, "
            f"{failed} failed"
        )

        return result

    def _get_existing_event_names(
        self, game_gid: int, events_data: List[Dict[str, Any]]
    ) -> set:
        """
        批量获取已存在的事件名 (优化性能)

        Args:
            game_gid: 游戏GID
            events_data: 事件数据列表

        Returns:
            已存在的事件名集合
        """
        event_names = [e.get("event_code") for e in events_data if e.get("event_code")]

        if not event_names:
            return set()

        # 使用EventRepository批量查询
        existing_events = self.event_repo.find_all(game_gid)
        return {event.name for event in existing_events if event.name in event_names}

    def _convert_to_event_entity(
        self, game_gid: int, event_data: Dict[str, Any]
    ) -> EventEntity:
        """
        转换导入数据为EventEntity

        Args:
            game_gid: 游戏GID
            event_data: 事件数据 (来自Excel/CSV)

        Returns:
            EventEntity对象

        Raises:
            ValueError: 数据验证失败
        """
        event_code = event_data.get("event_code")
        event_name_cn = event_data.get("event_name_cn") or event_data.get("event_name")
        category_name = event_data.get("category", "默认分类")

        # 查找或创建分类
        category_id = self._get_or_create_category(category_name)

        # 生成表名
        source_table = event_data.get(
            "source_table", f"ieu_ods.ods_{game_gid}_all_view"
        )
        target_table = event_data.get(
            "target_table", f"dwd.v_dwd_{game_gid}_{event_code}_di"
        )

        # 构建EventEntity (Pydantic会自动验证)
        entity_data = {
            "game_gid": game_gid,
            "name": event_code,
            "name_cn": event_name_cn or event_code,
            "category_id": category_id,
            "source_table": source_table,
            "target_table": target_table,
            "include_in_common_params": event_data.get("include_in_common_params", 1),
        }

        return EventEntity(**entity_data)

    def _get_or_create_category(self, category_name: str) -> int:
        """
        获取或创建分类 (使用CategoryRepository)

        Args:
            category_name: 分类名称

        Returns:
            分类ID
        """
        # 查找分类
        category = self.category_repo.find_by_name(category_name)

        if category:
            return category.id

        # 创建新分类 (使用CategoryRepository)
        category_data = {
            "name": category_name,
            "description": f"Auto-created category for {category_name}",
        }

        new_category = self.category_repo.create(category_data)

        if new_category:
            logger.info(
                f"✅ Created new category: {category_name} (ID: {new_category.id})"
            )
            return new_category.id
        else:
            # 如果创建失败，返回默认分类ID
            logger.warning(
                f"⚠️ Failed to create category {category_name}, using default"
            )
            default_category = self.category_repo.find_by_name("默认分类")
            return default_category.id if default_category else 1
