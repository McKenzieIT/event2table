#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Library Manager
Manages reusable parameter definitions
"""

import json
from typing import Dict, List, Optional, Any
from backend.core.database import get_db_connection
from backend.core.logging import get_logger
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict, execute_write
from backend.services.parameters.param_type_manager import param_type_manager

logger = get_logger(__name__)


class ParamLibraryManager:
    """Parameter library for reusable parameter definitions"""

    def __init__(self):
        """Initialize library manager"""
        pass

    def get_all_parameters(
        self, game_id: Optional[int] = None, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取参数库中的所有参数"""
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE 1=1
        """
        params = []

        if game_id:
            # Convert game_id to game_gid for data association
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                query += " AND pl.id IN (SELECT DISTINCT library_id FROM event_params ep JOIN log_events le ON ep.event_id = le.id WHERE le.game_gid = ?)"
                params.append(game["gid"])
            else:
                query += " AND pl.id IN (SELECT DISTINCT library_id FROM event_params ep JOIN log_events le ON ep.event_id = le.id WHERE le.game_gid = ?)"
                params.append(game_id)  # Will return no results

        if category:
            query += " AND pl.category = ?"
            params.append(category)

        query += " ORDER BY pl.usage_count DESC, pl.param_name"

        return fetch_all_as_dict(query, tuple(params) if params else ())

    def get_parameter_by_id(self, library_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取库参数"""
        return fetch_one_as_dict(
            """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.id = ?
        """,
            (library_id,),
        )

    def get_parameter_by_name(self, param_name: str) -> Optional[Dict[str, Any]]:
        """根据参数名获取库参数"""
        return fetch_one_as_dict(
            """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.param_name = ?
        """,
            (param_name,),
        )

    def create_parameter(self, param_data: Dict[str, Any]) -> int:
        """创建新的库参数"""
        from backend.core.database import get_db_connection

        # 解析类型字符串
        type_str = param_data.get("param_type", "string")
        type_def = param_type_manager.parse_type_string(type_str)

        # 查找或创建对应的模板
        template = param_type_manager.get_template_by_name(type_str)
        if not template:
            template_id = param_type_manager.create_template(
                {
                    "template_name": type_str,
                    "display_name": type_str,
                    "type_definition": json.dumps(type_def),
                    "description": f"Auto-generated template for {type_str}",
                }
            )
        else:
            template_id = template["id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO param_library
            (param_name, param_name_cn, template_id, param_description, category, is_standard)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                param_data["param_name"],
                param_data["param_name_cn"],
                template_id,
                param_data.get("param_description", ""),
                param_data.get("category", "custom"),
                param_data.get("is_standard", 0),
            ),
        )

        library_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created library parameter: {param_data['param_name']}")
        return library_id

    def extract_from_existing_params(self, min_usage: int = 2) -> int:
        """从现有参数中提取常用参数到库中"""
        # Find frequently used parameters
        frequently_used = fetch_all_as_dict(
            """
            SELECT param_name, param_name_cn, template_id, param_description, COUNT(*) as usage_count
            FROM event_params
            WHERE is_active = 1
            GROUP BY param_name, param_name_cn, template_id, param_description
            HAVING COUNT(*) >= ?
            ORDER BY usage_count DESC
        """,
            (min_usage,),
        )

        conn = get_db_connection()
        extracted_count = 0

        for param in frequently_used:
            # Check if already in library
            existing = fetch_one_as_dict(
                "SELECT id FROM param_library WHERE param_name = ?", (param["param_name"],)
            )

            if not existing:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO param_library
                    (param_name, param_name_cn, template_id, param_description, usage_count, is_standard)
                    VALUES (?, ?, ?, ?, ?, 1)
                """,
                    (
                        param["param_name"],
                        param["param_name_cn"],
                        param["template_id"],
                        param["param_description"],
                        param["usage_count"],
                    ),
                )
                extracted_count += 1

        conn.commit()
        conn.close()
        logger.info(f"Extracted {extracted_count} parameters to library")
        return extracted_count

    def update_usage_count(self, library_id: int):
        """更新参数使用次数"""
        execute_write(
            """
            UPDATE param_library
            SET usage_count = (
                SELECT COUNT(*) FROM event_params WHERE library_id = ?
            )
            WHERE id = ?
        """,
            (library_id, library_id),
        )

    def update_parameter(self, library_id: int, param_data: Dict[str, Any]) -> bool:
        """更新库参数"""
        # 如果更新了类型，需要更新template_id
        if "param_type" in param_data:
            type_str = param_data["param_type"]
            template = param_type_manager.get_template_by_name(type_str)
            if template:
                param_data["template_id"] = template["id"]

        # 构建更新字段
        update_fields = []
        update_values = []

        allowed_fields = [
            "param_name_cn",
            "template_id",
            "param_description",
            "category",
            "is_standard",
        ]

        for field in allowed_fields:
            if field in param_data:
                update_fields.append(f"{field} = ?")
                update_values.append(param_data[field])

        if not update_fields:
            return False

        update_values.append(library_id)

        execute_write(
            f"""
            UPDATE param_library
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            tuple(update_values),
        )

        logger.info(f"Updated library parameter: {library_id}")
        return True

    def delete_parameter(self, library_id: int) -> bool:
        """删除库参数"""
        # 检查是否被引用
        referenced = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM event_params WHERE library_id = ?", (library_id,)
        )

        if referenced and referenced["count"] > 0:
            logger.warning(
                f"Cannot delete library parameter {library_id}: still referenced by {referenced['count']} event params"
            )
            return False

        execute_write("DELETE FROM param_library WHERE id = ?", (library_id,))
        logger.info(f"Deleted library parameter: {library_id}")
        return True


# Singleton instance
param_library_manager = ParamLibraryManager()
