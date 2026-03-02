#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Library Manager - REFACTORED
=======================================

Refactored to use Repository pattern instead of direct database access.

Migration Status: Repository Pattern Implementation (2026-03-02)
- Added ParameterRepository integration
- Added get_param_library() with caching
- Refactored methods to use Repository layer
- Maintained backward compatibility

Note: This module is still marked as DEPRECATED for future migration to ParameterService.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from collections import Counter

from backend.core.cache.cache_system import cached
from backend.models.repositories.parameters import ParameterRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
from backend.core.utils import execute_write
from backend.services.parameters.param_type_manager import param_type_manager

logger = logging.getLogger(__name__)


class ParamLibraryManager:
    """
    Parameter Library Manager (Repository Pattern Implementation)

    This class provides parameter library functionality using the Repository pattern.

    Migration Status (2026-03-02):
    - Refactored to use ParameterRepository
    - Added caching support for get_param_library()
    - Deprecated methods still use direct DB access (to be migrated)

    Future: Migrate to ParameterService for unified parameter management.
    """

    def __init__(self):
        """Initialize library manager with Repository"""
        self.param_repo = ParameterRepository()
        logger.debug(
            "ParamLibraryManager initialized with ParameterRepository. "
            "This module is DEPRECATED - migrate to ParameterService when possible."
        )

    @cached("params.library", timeout=300)
    def get_param_library(self, game_gid: int) -> Dict[str, Any]:
        """
        获取参数库（带缓存）

        Args:
            game_gid: 游戏GID

        Returns:
            参数库字典，包含:
            - parameters: 参数列表
            - stats: 统计信息
              - total: 总数
              - by_type: 按类型统计
              - by_category: 按类别统计

        Example:
            >>> manager = ParamLibraryManager()
            >>> library = manager.get_param_library(90000001)
            >>> print(library['stats']['total'])
        """
        # Get common parameters for the game
        parameters = self.param_repo.get_common_params_by_game(game_gid)

        # Calculate statistics
        stats = {
            'total': len(parameters),
            'by_type': self._count_by_type(parameters),
            'by_category': self._count_by_category(parameters)
        }

        return {
            'parameters': parameters,
            'stats': stats
        }

    def _count_by_type(self, parameters: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        按类型统计参数数量

        Args:
            parameters: 参数列表

        Returns:
            类型统计字典
        """
        if not parameters:
            return {}

        types = [p.get('param_type', 'unknown') for p in parameters]
        return dict(Counter(types))

    def _count_by_category(self, parameters: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        按类别统计参数数量

        Args:
            parameters: 参数列表

        Returns:
            类别统计字典
        """
        if not parameters:
            return {}

        # For common_params, use table_name as category
        categories = [p.get('table_name', 'unknown') for p in parameters]
        return dict(Counter(categories))

    def get_all_parameters(
        self, game_id: Optional[int] = None, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取参数库中的所有参数 (DEPRECATED)

        Note: This method is kept for backward compatibility.
        Direct database access is used since library parameters
        are not yet fully migrated to ParameterService.

        Args:
            game_id: Optional game ID filter (Note: uses game_id, not game_gid)
            category: Optional category filter

        Returns:
            List of library parameter dictionaries
        """
        logger.warning(
            "get_all_parameters() is deprecated. "
            "Migrate to ParameterService when library parameters are fully integrated."
        )

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
                # If game not found, add condition that returns no results
                query += " AND pl.id IN (SELECT DISTINCT library_id FROM event_params ep JOIN log_events le ON ep.event_id = le.id WHERE le.game_gid = ?)"
                params.append(game_id)

        if category:
            query += " AND pl.category = ?"
            params.append(category)

        query += " ORDER BY pl.usage_count DESC, pl.param_name"

        return fetch_all_as_dict(query, tuple(params) if params else ())

    def get_parameter_by_id(self, library_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取库参数 (DEPRECATED)

        Args:
            library_id: Library parameter ID

        Returns:
            Library parameter dictionary or None
        """
        logger.warning(
            f"get_parameter_by_id({library_id}) is deprecated. "
            "Use direct database access until library migration is complete."
        )

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
        """
        根据参数名获取库参数 (DEPRECATED)

        Args:
            param_name: Parameter name

        Returns:
            Library parameter dictionary or None
        """
        logger.warning(
            f"get_parameter_by_name({param_name}) is deprecated. "
            "Use direct database access until library migration is complete."
        )

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
        """
        创建新的库参数 (DEPRECATED)

        Args:
            param_data: Parameter data dictionary with keys:
                - param_name: Parameter name (required)
                - param_name_cn: Chinese name (required)
                - param_type: Type string (optional, default "string")
                - param_description: Description (optional)
                - category: Category (optional, default "custom")
                - is_standard: Whether standard (optional, default 0)

        Returns:
            Created library parameter ID
        """
        logger.warning(
            "create_parameter() is deprecated. "
            "Use direct database access until library migration is complete."
        )

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
        """
        从现有参数中提取常用参数到库中 (DEPRECATED)

        Args:
            min_usage: Minimum usage count to be considered for extraction

        Returns:
            Number of parameters extracted
        """
        logger.warning(
            "extract_from_existing_params() is deprecated. "
            "Use direct database access until library migration is complete."
        )

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

        from backend.core.database import get_db_connection
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

    def update_usage_count(self, library_id: int) -> None:
        """
        更新参数使用次数 (DEPRECATED)

        Args:
            library_id: Library parameter ID
        """
        logger.warning(
            f"update_usage_count({library_id}) is deprecated. "
            "Use direct database access until library migration is complete."
        )

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
        """
        更新库参数 (DEPRECATED)

        Args:
            library_id: Library parameter ID
            param_data: Update data dictionary

        Returns:
            True if updated successfully, False otherwise
        """
        logger.warning(
            f"update_parameter({library_id}) is deprecated. "
            "Use direct database access until library migration is complete."
        )

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
        """
        删除库参数 (DEPRECATED)

        Args:
            library_id: Library parameter ID

        Returns:
            True if deleted successfully, False if still referenced
        """
        logger.warning(
            f"delete_parameter({library_id}) is deprecated. "
            "Use direct database access until library migration is complete."
        )

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


# Singleton instance (DEPRECATED)
param_library_manager = ParamLibraryManager()
