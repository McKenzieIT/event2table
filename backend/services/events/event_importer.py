#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Importer Service

批量导入事件数据的业务服务层
"""

from typing import List, Dict, Any
import html

from backend.core.logging import get_logger
from backend.core.utils import fetch_one_as_dict, execute_write
from backend.models.schemas import EventImportItem

logger = get_logger(__name__)


class EventImporter:
    """事件导入器"""

    def import_events(
        self, game_gid: int, events_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量导入事件

        Args:
            game_gid: 游戏GID
            events_data: 事件数据列表

        Returns:
            导入结果统计
        """
        imported = 0
        failed = 0
        errors = []

        # 验证游戏是否存在
        game = fetch_one_as_dict(
            "SELECT id, gid, ods_db FROM games WHERE gid = ?", (game_gid,)
        )
        if not game:
            return {
                "imported": 0,
                "failed": len(events_data),
                "errors": [f"Game with gid {game_gid} not found"],
            }

        db_game_id = game["id"]
        ods_db = game["ods_db"]

        event_names = [e["event_code"] for e in events_data]
        existing_set = set()

        if event_names:
            placeholders = ",".join(["?"] * len(event_names))
            existing_events = fetch_all_as_dict(
                f"SELECT event_name FROM log_events WHERE game_gid = ? AND event_name IN ({placeholders})",
                (game_gid, *event_names),
            )
            existing_set = {e["event_name"] for e in existing_events}

        for idx, event_data in enumerate(events_data, 1):
            try:
                event = EventImportItem(**event_data)

                if event.event_code in existing_set:
                    errors.append(f"Row {idx}: Event {event.event_code} already exists")
                    failed += 1
                    continue

                # 查找或创建分类
                category_id = self._get_or_create_category(event.category)

                # 生成表名
                source_table = f"{ods_db}.ods_{game_gid}_all_view"
                target_table = f"dwd.v_dwd_{game_gid}_{event.event_code}_di"

                # 创建事件
                event_id = execute_write(
                    """INSERT INTO log_events
                       (game_id, game_gid, event_name, event_name_cn, category_id,
                        source_table, target_table, include_in_common_params)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        db_game_id,
                        game_gid,
                        event.event_code,
                        event.event_name_cn or event.event_name,
                        category_id,
                        source_table,
                        target_table,
                        1,  # include_in_common_params
                    ),
                    return_last_id=True,
                )

                if event_id:
                    imported += 1
                    logger.info(f"Imported event: {event.event_code} (ID: {event_id})")
                else:
                    errors.append(
                        f"Row {idx}: Failed to create event {event.event_code}"
                    )
                    failed += 1

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                failed += 1
                logger.error(f"Failed to import event at row {idx}: {e}")

        return {
            "imported": imported,
            "failed": failed,
            "errors": errors,
        }

    def _get_or_create_category(self, category_name: str) -> int:
        """
        获取或创建分类

        Args:
            category_name: 分类名称

        Returns:
            分类ID
        """
        # 查找分类
        category = fetch_one_as_dict(
            "SELECT id FROM event_categories WHERE name = ?", (category_name,)
        )

        if category:
            return category["id"]

        # 创建新分类
        category_id = execute_write(
            "INSERT INTO event_categories (name, description) VALUES (?, ?)",
            (category_name, f"Auto-created category for {category_name}"),
            return_last_id=True,
        )

        logger.info(f"Created new category: {category_name} (ID: {category_id})")
        return category_id
