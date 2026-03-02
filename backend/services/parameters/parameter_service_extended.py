#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Service Extended Methods

This file contains additional methods needed by parameters.py API routes.
These methods will be integrated into ParameterService.
"""

from typing import List, Optional, Dict, Any
import logging
from backend.core.cache.cache_system import cached, CacheInvalidator
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
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
    def get_parameter_details(
        self, param_name: str, game_gid: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取参数详情（跨事件使用情况）

        Args:
            param_name: 参数名
            game_gid: 游戏GID

        Returns:
            参数详情字典，包含:
            - param_name: 参数名
            - param_name_cn: 中文名
            - base_type: 基础类型
            - event_count: 使用此参数的事件数量
            - events: 使用此参数的事件列表
            - is_common: 是否为公共参数
        """
        # 获取参数基本信息
        param_info = fetch_one_as_dict(
            """
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                pt.base_type,
                COUNT(DISTINCT ep.event_id) as event_count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_name = ? AND le.game_gid = ? AND ep.is_active = 1
            GROUP BY ep.param_name, pt.base_type
        """,
            (param_name, game_gid),
        )

        if not param_info:
            return None

        # 获取使用此参数的事件
        events = fetch_all_as_dict(
            """
            SELECT
                e.id,
                e.event_name,
                e.event_name_cn,
                ep.is_active
            FROM event_params ep
            INNER JOIN log_events e ON ep.event_id = e.id
            WHERE ep.param_name = ? AND e.game_gid = ?
            ORDER BY e.event_name
        """,
            (param_name, game_gid),
        )

        # 检查是否为公共参数
        from functools import lru_cache

        @lru_cache(maxsize=128)
        is_common = fetch_one_as_dict(
            """
            SELECT id FROM common_params
            WHERE param_name = ? AND game_gid = ?
        """,
            (param_name, game_gid),
        )

        param_info["events"] = events
        param_info["is_common"] = bool(is_common)

        return param_info

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
        from functools import lru_cache

        @lru_cache(maxsize=128)
        def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
            """Cached game_gid to game_id conversion"""
            game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
            return game["id"] if game else None

        game_id = _get_game_id_from_gid(game_gid)

        # 合并统计查询
        stats = fetch_one_as_dict(
            """
            SELECT
                COUNT(DISTINCT ep.param_name) as total_unique_params,
                SUM(CASE WHEN ep.is_active = 1 THEN 1 ELSE 0 END) as total_event_params
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ?
        """,
            (game_gid,),
        )

        # 统计数据类型分布
        type_stats = fetch_all_as_dict(
            """
            SELECT pt.base_type, COUNT(DISTINCT ep.param_name) as count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ? AND ep.is_active = 1
            GROUP BY pt.base_type
            ORDER BY count DESC
        """,
            (game_gid,),
        )

        # 统计公共参数
        common_params = fetch_one_as_dict(
            """
            SELECT COUNT(*) as count
            FROM common_params
            WHERE game_gid = ?
        """,
            (game_gid,),
        )

        return {
            "total_unique_params": stats["total_unique_params"] if stats else 0,
            "total_event_params": stats["total_event_params"] if stats else 0,
            "common_params_count": common_params["count"] if common_params else 0,
            "data_type_distribution": type_stats,
        }

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
        keyword_pattern = f"%{keyword}%"

        query = """
            SELECT DISTINCT ep.param_name, MIN(ep.param_name_cn) as param_name_cn, pt.base_type
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
              AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
              AND ep.is_active = 1
            GROUP BY ep.param_name, pt.base_type
        """
        params = [game_gid, keyword_pattern, keyword_pattern]

        if data_type:
            query += " AND pt.base_type = ?"
            params.append(data_type)

        query += " ORDER BY ep.param_name LIMIT 100"

        return fetch_all_as_dict(query, params)

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
        from backend.api.routes._param_helpers import validate_parameter_name

        # 使用helper函数验证参数名格式
        is_valid, error_msg = validate_parameter_name(param_name)
        if not is_valid:
            return {"valid": False, "reason": error_msg, "exists": False}

        # 检查参数是否已存在
        existing = fetch_one_as_dict(
            """
            SELECT ep.param_name FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ? AND ep.param_name = ?
        """,
            (game_gid, param_name),
        )

        return {"valid": True, "exists": bool(existing)}

    # ========== Common Parameters Methods ==========

    @cached("common_params.with_event_count", timeout=180)
    def get_common_params_with_event_count(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取公共参数列表（包含事件计数）

        Args:
            game_gid: 游戏GID

        Returns:
            公共参数列表，每个参数包含使用它的事件数量
        """
        from functools import lru_cache

        @lru_cache(maxsize=128)
        def _get_game_id_from_gid(game_gid: int) -> Optional[int]:
            """Cached game_gid to game_id conversion"""
            game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
            return game["id"] if game else None

        game_id = _get_game_id_from_gid(game_gid)
        if not game_id:
            return []

        common_params = fetch_all_as_dict(
            """
            SELECT
                cp.id,
                cp.param_name,
                cp.param_name_cn,
                cp.param_type as base_type,
                cp.param_description,
                cp.table_name,
                cp.status,
                (SELECT COUNT(*) FROM event_params ep2
                 INNER JOIN log_events le ON ep2.event_id = le.id
                 WHERE ep2.param_name = cp.param_name
                 AND le.game_gid = ?
                 AND ep2.is_active = 1) as event_count
            FROM common_params cp
            WHERE cp.game_gid = ?
            ORDER BY cp.param_name
        """,
            (game_gid, game_gid),
        )

        return common_params

    # ========== Parameter Library Methods ==========

    @cached("param_library.check", timeout=300)
    def check_param_library(
        self, param_name: str, template_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        检查参数是否存在于库中

        Args:
            param_name: 参数名
            template_id: 模板ID

        Returns:
            库参数信息，不存在返回None
        """
        library_param = fetch_one_as_dict(
            """SELECT pl.*, pt.template_name
               FROM param_library pl
               JOIN param_templates pt ON pl.template_id = pt.id
               WHERE pl.param_name = ? AND pl.template_id = ?""",
            (param_name, template_id),
        )

        return library_param

    @cached("param_library.batch_check", timeout=180)
    def batch_check_param_library(
        self, parameters: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量检查参数库

        Args:
            parameters: 参数列表，每个包含 param_name 和 template_id

        Returns:
            匹配结果字典:
            - matched: 匹配的参数列表
            - unmatched: 未匹配的参数列表
        """
        if not parameters or len(parameters) > 100:
            return {"matched": [], "unmatched": []}

        matched = []
        unmatched = []

        conditions = []
        values = []
        for param in parameters:
            param_name = param.get("param_name")
            template_id = param.get("template_id")

            if not param_name or template_id is None:
                continue

            conditions.append("(pl.param_name = ? AND pl.template_id = ?)")
            values.extend([param_name, template_id])

        if conditions:
            where_clause = " OR ".join(conditions)
            library_params = fetch_all_as_dict(
                f"""SELECT pl.*, pt.template_name
                   FROM param_library pl
                   JOIN param_templates pt ON pl.template_id = pt.id
                   WHERE {where_clause}""",
                tuple(values),
            )

            library_map = {
                (p["param_name"], p["template_id"]): p for p in library_params
            }

            for param in parameters:
                param_name = param.get("param_name")
                template_id = param.get("template_id")

                if not param_name or template_id is None:
                    continue

                key = (param_name, template_id)
                if key in library_map:
                    library_param = library_map[key]
                    matched.append(
                        {
                            "param_name": param_name,
                            "template_id": template_id,
                            "library_id": library_param["id"],
                            "library_param": library_param,
                        }
                    )
                else:
                    unmatched.append(
                        {"param_name": param_name, "template_id": template_id}
                    )

        return {"matched": matched, "unmatched": unmatched}

    def link_event_param_to_library(
        self, param_id: int, library_id: int
    ) -> Dict[str, Any]:
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
        from backend.core.utils import execute_write

        # 验证事件参数存在
        event_param = fetch_one_as_dict(
            "SELECT * FROM event_params WHERE id = ?", (param_id,)
        )
        if not event_param:
            raise ValueError("Event parameter not found")

        # 验证库参数存在
        library_param = fetch_one_as_dict(
            "SELECT * FROM param_library WHERE id = ?", (library_id,)
        )
        if not library_param:
            raise ValueError("Library parameter not found")

        # 关联参数
        execute_write(
            "UPDATE event_params SET library_id = ?, is_from_library = 1 WHERE id = ?",
            (library_id, param_id),
        )

        # 更新使用计数
        execute_write(
            "UPDATE param_library SET usage_count = usage_count + 1 WHERE id = ?",
            (library_id,),
        )

        # 失效缓存
        self.invalidator.invalidate_pattern(f"parameter.by_id:{param_id}")
        self.invalidator.invalidate_pattern("param_library.*")

        logger.info(f"Linked event param {param_id} to library param {library_id}")

        return {"param_id": param_id, "library_id": library_id}

    # ========== ALTER TABLE Methods ==========

    @cached("alter_table.sql", timeout=600)
    def get_alter_table_sql(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取ALTER TABLE SQL语句

        Args:
            param_id: 公共参数ID

        Returns:
            包含参数信息和SQL的字典，不存在返回None
        """
        from backend.services.hql.manager import HQLManager

        # 获取参数详情
        param = fetch_one_as_dict(
            """
            SELECT
                p.id,
                p.param_name,
                p.param_name_cn,
                p.param_type,
                p.table_name,
                g.name as game_name,
                g.gid
            FROM common_params p
            JOIN games g ON p.game_gid = g.gid
            WHERE p.id = ?
        """,
            (param_id,),
        )

        if not param:
            return None

        # 生成ALTER TABLE HQL
        manager = HQLManager()
        alter_sql = manager.generate_alter_table_hql(
            target_table=param["table_name"],
            param_name=param["param_name"],
            param_type=param["param_type"],
            param_name_cn=param["param_name_cn"],
        )

        logger.info(f"Generated ALTER TABLE SQL for param_id={param_id}")

        return {"param": param, "alter_sql": alter_sql}

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
        limit = min(limit, 100)
        params = [game_gid]

        # 基础查询 - 按参数名分组去重
        query = """
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                pt.base_type,
                COUNT(DISTINCT ep.event_id) as events_count,
                COUNT(*) as usage_count,
                CASE WHEN COUNT(DISTINCT ep.event_id) >= 3 THEN 1 ELSE 0 END as is_common
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ? AND ep.is_active = 1
        """

        # 动态添加筛选条件
        if search:
            query += " AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if type_filter:
            query += " AND pt.base_type = ?"
            params.append(type_filter)

        # 分组和分页
        query += " GROUP BY ep.param_name, pt.base_type"
        query += " ORDER BY usage_count DESC, ep.param_name ASC"
        query += " LIMIT ? OFFSET ?"

        # 保存WHERE条件的参数（在添加分页参数之前）
        base_params = params.copy()
        params.extend([limit, (page - 1) * limit])

        parameters = fetch_all_as_dict(query, params)

        # 获取总数(不带分页)
        count_query = """
            SELECT COUNT(DISTINCT ep.param_name) as total
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ? AND ep.is_active = 1
        """
        count_params = base_params.copy()

        if search:
            count_query += " AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)"
            count_params.extend([f"%{search}%", f"%{search}%"])

        if type_filter:
            count_query += " AND pt.base_type = ?"
            count_params.append(type_filter)

        total_result = fetch_one_as_dict(count_query, count_params)
        total = total_result["total"] if total_result else 0

        return {
            "parameters": parameters,
            "total": total,
            "page": page,
            "has_more": page * limit < total,
        }
