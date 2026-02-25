#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Repository (参数数据访问层)

提供参数相关的数据访问方法
基于 GenericRepository 实现特定领域的查询
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class ParameterRepository(GenericRepository):
    """
    参数仓储类

    继承 GenericRepository 并添加参数特定的查询方法
    """

    def __init__(self):
        """
        初始化参数仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_params",
            primary_key="id",
            enable_cache=True,
            cache_timeout=60,  # 1分钟缓存
        )

    def get_active_by_event(self, event_id: int) -> List[Dict[str, Any]]:
        """
        获取指定事件的所有活跃参数

        Args:
            event_id: 事件ID

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_active_by_event(1)
        """
        query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """
        return fetch_all_as_dict(query, (event_id,))

    def find_by_name_and_event(self, param_name: str, event_id: int) -> Optional[Dict[str, Any]]:
        """
        根据参数名和事件ID查询参数

        Args:
            param_name: 参数名
            event_id: 事件ID

        Returns:
            参数字典，不存在返回None

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.find_by_name_and_event('user_id', 1)
        """
        query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_name = ? AND ep.event_id = ?
        """
        return fetch_one_as_dict(query, (param_name, event_id))

    def get_all_by_event(
        self, event_id: int, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取指定事件的所有参数（包含非活跃参数）

        Args:
            event_id: 事件ID
            include_inactive: 是否包含非活跃参数

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_all_by_event(1, include_inactive=True)
        """
        if include_inactive:
            query = """
                SELECT
                    ep.*,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ?
                ORDER BY ep.id
            """
        else:
            query = """
                SELECT
                    ep.*,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ? AND ep.is_active = 1
                ORDER BY ep.id
            """
        return fetch_all_as_dict(query, (event_id,))

    def find_by_template(
        self, template_id: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据模板ID查询参数

        Args:
            template_id: 模板ID
            limit: 限制数量

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.find_by_template(1, limit=10)
        """
        query = """
            SELECT
                ep.*,
                le.event_name,
                le.event_name_cn,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.template_id = ?
            ORDER BY ep.id DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        return fetch_all_as_dict(query, (template_id,))

    def search_parameters(
        self, keyword: str, event_id: Optional[int] = None, template_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索参数（支持参数名和中文名模糊搜索）

        Args:
            keyword: 搜索关键词
            event_id: 可选的事件ID过滤
            template_id: 可选的模板ID过滤

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.search_parameters('user', event_id=1)
        """
        keyword_pattern = f"%{keyword}%"
        conditions = []
        params = []

        if event_id:
            conditions.append("ep.event_id = ?")
            params.append(event_id)

        if template_id:
            conditions.append("ep.template_id = ?")
            params.append(template_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                ep.*,
                le.event_name,
                le.event_name_cn,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE {where_clause}
            AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
            ORDER BY ep.id DESC
        """

        params.extend([keyword_pattern, keyword_pattern])
        return fetch_all_as_dict(query, tuple(params))

    def get_common_parameters(self, game_gid: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取公共参数列表

        Args:
            game_gid: 可选的游戏GID过滤

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_common_parameters(game_gid=1001)
        """
        if game_gid:
            query = """
                SELECT DISTINCT
                    ep.param_name,
                    ep.param_name_cn,
                    ep.template_id,
                    pt.template_name,
                    pt.display_name as type_display_name,
                    COUNT(DISTINCT ep.event_id) as usage_count
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                JOIN games g ON le.game_gid = g.gid
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE g.gid = ? AND le.include_in_common_params = 1 AND ep.is_active = 1
                GROUP BY ep.param_name, ep.param_name_cn, ep.template_id
                ORDER BY usage_count DESC, ep.param_name
            """
            return fetch_all_as_dict(query, (game_gid,))
        else:
            query = """
                SELECT DISTINCT
                    ep.param_name,
                    ep.param_name_cn,
                    ep.template_id,
                    pt.template_name,
                    pt.display_name as type_display_name,
                    COUNT(DISTINCT ep.event_id) as usage_count
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE le.include_in_common_params = 1 AND ep.is_active = 1
                GROUP BY ep.param_name, ep.param_name_cn, ep.template_id
                ORDER BY usage_count DESC, ep.param_name
            """
            return fetch_all_as_dict(query)

    def get_parameter_usage_stats(self, param_name: str) -> Optional[Dict[str, Any]]:
        """
        获取参数使用统计

        Args:
            param_name: 参数名

        Returns:
            统计信息字典

        Example:
            >>> repo = ParameterRepository()
            >>> stats = repo.get_parameter_usage_stats('user_id')
        """
        query = """
            SELECT
                ep.param_name,
                ep.param_name_cn,
                COUNT(DISTINCT ep.event_id) as event_count,
                GROUP_CONCAT(DISTINCT le.event_name) as event_names,
                MIN(ep.created_at) as first_seen,
                MAX(ep.updated_at) as last_seen
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.param_name = ?
            GROUP BY ep.param_name, ep.param_name_cn
        """
        return fetch_one_as_dict(query, (param_name,))

    def get_parameter_by_id_with_event(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        根据参数ID获取参数及其关联事件信息

        Args:
            param_id: 参数ID

        Returns:
            参数字典，包含事件信息

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.get_parameter_by_id_with_event(1)
        """
        query = """
            SELECT
                ep.*,
                le.event_name,
                le.event_name_cn,
                le.game_id,
                g.name as game_name,
                g.gid as game_gid,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.id = ?
        """
        return fetch_one_as_dict(query, (param_id,))

    def bulk_create_parameters(
        self, event_id: int, parameters_data: List[Dict[str, Any]]
    ) -> List[int]:
        """
        批量为事件创建参数

        Args:
            event_id: 事件ID
            parameters_data: 参数数据列表

        Returns:
            创建的参数ID列表

        Example:
            >>> repo = ParameterRepository()
            >>> param_ids = repo.bulk_create_parameters(1, [
            ...     {'param_name': 'param1', 'param_name_cn': '参数1', ...},
            ...     {'param_name': 'param2', 'param_name_cn': '参数2', ...}
            ... ])
        """
        from backend.core.database.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        created_param_ids = []

        try:
            for param_data in parameters_data:
                cursor.execute(
                    """
                    INSERT INTO event_params (
                        event_id, param_name, param_name_cn,
                        template_id, param_description, json_path, is_active, version
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, 1)
                """,
                    (
                        event_id,
                        param_data["param_name"],
                        param_data.get("param_name_cn", ""),
                        param_data.get("template_id", 1),
                        param_data.get("param_description", ""),
                        param_data.get("json_path", ""),
                    ),
                )

                created_param_ids.append(cursor.lastrowid)

            conn.commit()
            return created_param_ids

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def deactivate_parameters(self, event_id: int, param_ids: List[int]) -> int:
        """
        批量停用参数

        Args:
            event_id: 事件ID
            param_ids: 要停用的参数ID列表

        Returns:
            实际停用的参数数量

        Example:
            >>> repo = ParameterRepository()
            >>> count = repo.deactivate_parameters(1, [1, 2, 3])
        """
        from backend.core.utils import execute_write  # noqa: F401

        if not param_ids:
            return 0

        placeholders = ",".join(["?" for _ in param_ids])
        query = f"""
            UPDATE event_params
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE event_id = ? AND id IN ({placeholders})
        """
        return execute_write(query, (event_id, *param_ids))

    def reactivate_parameters(self, event_id: int, param_ids: List[int]) -> int:
        """
        批量重新激活参数

        Args:
            event_id: 事件ID
            param_ids: 要激活的参数ID列表

        Returns:
            实际激活的参数数量

        Example:
            >>> repo = ParameterRepository()
            >>> count = repo.reactivate_parameters(1, [1, 2, 3])
        """
        from backend.core.utils import execute_write  # noqa: F401

        if not param_ids:
            return 0

        placeholders = ",".join(["?" for _ in param_ids])
        query = f"""
            UPDATE event_params
            SET is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE event_id = ? AND id IN ({placeholders})
        """
        return execute_write(query, (event_id, *param_ids))

    def get_parameters_by_type(
        self, template_id: int, event_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据参数类型获取参数列表

        Args:
            template_id: 模板ID（参数类型）
            event_id: 可选的事件ID过滤

        Returns:
            参数列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_parameters_by_type(1, event_id=1)
        """
        if event_id:
            query = """
                SELECT
                    ep.*,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.template_id = ? AND ep.event_id = ? AND ep.is_active = 1
                ORDER BY ep.id
            """
            return fetch_all_as_dict(query, (template_id, event_id))
        else:
            query = """
                SELECT
                    ep.*,
                    le.event_name,
                    le.event_name_cn,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.template_id = ? AND ep.is_active = 1
                ORDER BY ep.id DESC
            """
            return fetch_all_as_dict(query, (template_id,))
