#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Service Extended Methods

This file contains additional methods needed by parameters.py API routes.
These methods will be integrated into ParameterService.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.models.repositories.parameters import ParameterRepository

logger = logging.getLogger(__name__)


class ParameterServiceExtended:
    """
    Extended ParameterService methods for API routes support

    These methods handle specific queries needed by the API layer
    that are not covered by the core ParameterService.
    """

    def __init__(self):
        self.param_repo = ParameterRepository()
        from backend.core.cache.cache_system import HierarchicalCache

        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

    # ========== Parameter Details Methods ==========

    @cached("parameter.details", timeout=300)
    def get_parameter_details(self, param_name: str, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        获取参数详情（跨事件使用情况）

        Args:
            param_name: 参数名
            game_gid: 游戏GID

        Returns:
            参数详情字典, 包含:
            - param_name: 参数名
            - param_name_cn: 中文名
            - base_type: 基础类型
            - event_count: 使用此参数的事件数量
            - events: 使用此参数的事件列表
            - is_common: 是否为公共参数
        """
        return self.param_repo.get_parameter_details(param_name, game_gid)

    # ========== Parameter Statistics Methods ==========

    @cached("parameter.stats", timeout=300)
    def get_parameter_stats(self, game_gid: int) -> Dict[str, Any]:
        """
        获取参数统计信息

        Args:
            game_gid: 游戏GID

        Returns:
            统计信息字典:
            - total_unique_params: 唯一参数总数
            - total_event_params: 事件参数总数
            - common_params_count: 公共参数数量
            - data_type_distribution: 数据类型分布
        """
        return self.param_repo.get_parameter_stats(game_gid)

    # ========== Parameter Search Methods ==========

    @cached("parameter.search.advanced", timeout=120)
    def search_parameters_advanced(
        self, game_gid: int, keyword: str, data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        高级参数搜索

        Args:
            game_gid: 游戏GID
            keyword: 搜索关键词
            data_type: 可选的数据类型过滤

        Returns:
            匹配的参数列表
        """
        return self.param_repo.search_parameters_advanced(game_gid, keyword, data_type)

    # ========== Parameter Validation Methods ==========

    @cached("parameter.validate", timeout=60)
    def validate_parameter_name(self, game_gid: int, param_name: str) -> Dict[str, Any]:
        """
        验证参数名

        Args:
            game_gid: 游戏GID
            param_name: 参数名

        Returns:
            验证结果字典:
            - valid: 是否符合格式要求
            - exists: 是否已存在
        """
        return self.param_repo.validate_parameter_name(game_gid, param_name)

    # ========== Common Parameters Methods ==========

    @cached("common_params.with_event_count", timeout=180)
    def get_common_params_with_event_count(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取公共参数列表（包含事件计数）

        Args:
            game_gid: 游戏GID

        Returns:
            公共参数列表, 每个参数包含使用它的事件数量
        """
        return self.param_repo.get_common_params_with_event_count(game_gid)

    # ========== Parameter Library Methods ==========

    @cached("param_library.check", timeout=300)
    def check_param_library(self, param_name: str, template_id: int) -> Optional[Dict[str, Any]]:
        """
        检查参数是否存在于库中

        Args:
            param_name: 参数名
            template_id: 模板ID

        Returns:
            库参数信息, 不存在返回None
        """
        return self.param_repo.check_param_library(param_name, template_id)

    @cached("param_library.batch_check", timeout=180)
    def batch_check_param_library(
        self, parameters: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量检查参数库

        Args:
            parameters: 参数列表, 每个包含 param_name 和 template_id

        Returns:
            匹配结果字典:
            - matched: 匹配的参数列表
            - unmatched: 未匹配的参数列表
        """
        return self.param_repo.batch_check_param_library(parameters)

    def link_event_param_to_library(self, param_id: int, library_id: int) -> Dict[str, Any]:
        """
        关联事件参数到库参数

        Args:
            param_id: 事件参数ID
            library_id: 库参数ID

        Returns:
            关联结果字典

        Raises:
            ValueError: 参数不存在
        """
        # 失效缓存(在更新前失效)
        self.invalidator.invalidate_pattern(f"parameter.by_id:{param_id}")
        self.invalidator.invalidate_pattern("param_library.*")

        result = self.param_repo.link_event_param_to_library(param_id, library_id)

        logger.info(f"Linked event param {param_id} to library param {library_id}")

        return result

    # ========== ALTER TABLE Methods ==========

    @cached("alter_table.sql", timeout=600)
    def get_alter_table_sql(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取ALTER TABLE SQL语句

        Args:
            param_id: 公共参数ID

        Returns:
            包含参数信息和SQL的字典, 不存在返回None
        """
        return self.param_repo.get_alter_table_sql(param_id)

    # ========== All Parameters with Pagination ==========

    @cached("parameters.all.paginated", timeout=300)
    def get_all_parameters_paginated(
        self,
        game_gid: int,
        search: str = "",
        type_filter: str = "",
        page: int = 1,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        获取所有参数（分页）

        Args:
            game_gid: 游戏GID
            search: 搜索关键词
            type_filter: 类型过滤
            page: 页码
            limit: 每页数量

        Returns:
            分页结果字典:
            - parameters: 参数列表
            - total: 总数
            - page: 当前页
            - has_more: 是否有更多
        """
        return self.param_repo.get_all_parameters_paginated(
            game_gid, search, type_filter, page, limit
        )
