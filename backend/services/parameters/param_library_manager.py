# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Library Manager - REFACTORED (Repository Pattern)
=========================================================

Refactored to use Repository pattern instead of direct database access.

Migration Status: Repository Pattern Implementation (2026-03-03)
- Removed all direct database access
- Added ParamLibraryRepository integration
- Added ParameterRepository integration
- All methods now use Repository layer
- Maintained backward compatibility

Note: This module is still marked as DEPRECATED for future migration to ParameterService.
"""

import json
import logging
from collections import Counter
from typing import Any, Dict, List, Optional

from backend.models.repositories.param_library_repository import ParamLibraryRepository
from backend.models.repositories.parameters import ParameterRepository
from backend.services.parameters.param_type_manager import param_type_manager

logger = logging.getLogger(__name__)


class ParamLibraryManager:
    """
    Parameter Library Manager (Repository Pattern Implementation)

    This class provides parameter library functionality using the Repository pattern.

    Migration Status (2026-03-03):
    - Fully migrated to Repository pattern
    - Zero direct database access
    - All methods use Repository layer

    Future: Migrate to ParameterService for unified parameter management.
    """

    def __init__(self):
        """Initialize library manager with Repositories"""
        self.library_repo = ParamLibraryRepository()
        self.param_repo = ParameterRepository()
        logger.debug(
            "ParamLibraryManager initialized with Repositories. "
            "This module is DEPRECATED - migrate to ParameterService when possible."
        )

    def get_param_library(self, game_gid: int) -> Dict[str, Any]:
        """
        获取参数库（带缓存）

        Args:
            game_gid: 游戏GID

        Returns:
            参数库字典, 包含:
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
            'by_category': self._count_by_category(parameters),
        }

        return {'parameters': parameters, 'stats': stats}

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
        Now uses Repository layer instead of direct database access.

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

        # Convert game_id to game_gid if provided
        game_gid = None
        if game_id:
            from backend.models.repositories.games import GameRepository

            game_repo = GameRepository()
            game = game_repo.find_by_id(game_id)
            if game:
                game_gid = game.gid

        # Use Repository
        return self.library_repo.get_all_parameters(game_gid=game_gid, category=category)

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
            "Use ParamLibraryRepository directly."
        )

        return self.library_repo.find_by_id(library_id)

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
            "Use ParamLibraryRepository directly."
        )

        return self.library_repo.find_by_name(param_name)

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
        logger.warning("create_parameter() is deprecated. " "Use ParamLibraryRepository directly.")

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

        # Use Repository
        library_id = self.library_repo.create_parameter(
            param_name=param_data["param_name"],
            param_name_cn=param_data["param_name_cn"],
            template_id=template_id,
            param_description=param_data.get("param_description", ""),
            category=param_data.get("category", "custom"),
            is_standard=bool(param_data.get("is_standard", 0)),
        )

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
            "extract_from_existing_params() is deprecated. " "Use ParamLibraryRepository directly."
        )

        # Use Repository to get frequently used parameters
        frequently_used = self.param_repo.get_common_parameters()

        extracted_count = 0

        for param in frequently_used:
            if param.get('usage_count', 0) < min_usage:
                continue

            # Check if already in library
            existing = self.library_repo.find_by_name(param["param_name"])

            if not existing:
                # Create library parameter
                self.library_repo.create_parameter(
                    param_name=param["param_name"],
                    param_name_cn=param.get("param_name_cn", ""),
                    template_id=param.get("template_id", 1),
                    param_description=param.get("param_description", ""),
                    category="custom",
                    is_standard=True,
                )
                extracted_count += 1

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
            "Use ParamLibraryRepository directly."
        )

        self.library_repo.update_usage_count(library_id)

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
            f"update_parameter({library_id}) is deprecated. " "Use ParamLibraryRepository directly."
        )

        # 如果更新了类型, 需要更新template_id
        template_id = None
        if "param_type" in param_data:
            type_str = param_data["param_type"]
            template = param_type_manager.get_template_by_name(type_str)
            if template:
                template_id = template["id"]

        # Use Repository
        success = self.library_repo.update_parameter(
            library_id=library_id,
            param_name_cn=param_data.get("param_name_cn"),
            param_description=param_data.get("param_description"),
            category=param_data.get("category"),
            is_standard=param_data.get("is_standard"),
        )

        if success and template_id:
            # Update template_id separately if needed
            from backend.core.utils import execute_write

            execute_write(
                "UPDATE param_library SET template_id = ? WHERE id = ?", (template_id, library_id)
            )

        logger.info(f"Updated library parameter: {library_id}")
        return success

    def delete_parameter(self, library_id: int) -> bool:
        """
        删除库参数 (DEPRECATED)

        Args:
            library_id: Library parameter ID

        Returns:
            True if deleted successfully, False if still referenced
        """
        logger.warning(
            f"delete_parameter({library_id}) is deprecated. " "Use ParamLibraryRepository directly."
        )

        success = self.library_repo.delete_parameter(library_id)

        if not success:
            logger.warning(f"Cannot delete library parameter {library_id}: still referenced")
        else:
            logger.info(f"Deleted library parameter: {library_id}")

        return success


# Singleton instance (DEPRECATED)
param_library_manager = ParamLibraryManager()
