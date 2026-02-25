#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EventParam Repository (事件参数数据访问层)

提供事件参数相关的数据访问方法
基于 GenericRepository 实现特定领域的查询
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class EventParamRepository(GenericRepository):
    """
    事件参数仓储类

    继承 GenericRepository 并添加事件参数特定的查询方法
    """

    def __init__(self):
        """
        初始化事件参数仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_params",
            primary_key="id",
            enable_cache=True,
            cache_timeout=60,
        )

    def find_by_event_id(self, event_id: int) -> List[Dict[str, Any]]:
        """
        根据事件ID查询参数

        Args:
            event_id: 事件ID

        Returns:
            参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.find_by_event_id(1)
        """
        query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ?
            ORDER BY ep.param_name
        """
        return fetch_all_as_dict(query, (event_id,))

    def find_by_event_ids(self, event_ids: List[int]) -> List[Dict[str, Any]]:
        """
        批量查询事件参数

        Args:
            event_ids: 事件ID列表

        Returns:
            参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.find_by_event_ids([1, 2, 3])
        """
        if not event_ids:
            return []
        placeholders = ",".join(["?"] * len(event_ids))
        query = f"""
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id IN ({placeholders})
            ORDER BY ep.event_id, ep.param_name
        """
        return fetch_all_as_dict(query, tuple(event_ids))

    def find_active_by_event_id(self, event_id: int) -> List[Dict[str, Any]]:
        """
        根据事件ID查询活跃参数

        Args:
            event_id: 事件ID

        Returns:
            活跃参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.find_active_by_event_id(1)
        """
        query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.param_name
        """
        return fetch_all_as_dict(query, (event_id,))

    def find_by_param_name(self, param_name: str) -> List[Dict[str, Any]]:
        """
        根据参数名查询所有事件参数

        Args:
            param_name: 参数名

        Returns:
            参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.find_by_param_name('user_id')
        """
        query = """
            SELECT
                ep.*,
                le.event_name,
                le.event_name_cn,
                g.gid as game_gid,
                g.name as game_name,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_name = ?
            ORDER BY le.event_name
        """
        return fetch_all_as_dict(query, (param_name,))

    def get_params_with_dependencies(self, event_id: int) -> List[Dict[str, Any]]:
        """
        获取事件参数及其依赖关系

        Args:
            event_id: 事件ID

        Returns:
            包含依赖关系的参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.get_params_with_dependencies(1)
        """
        query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name,
                pd.depends_on_param_id,
                pd.dependency_type,
                ep_dep.param_name as depends_on_param_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            LEFT JOIN param_dependencies pd ON ep.id = pd.param_id
            LEFT JOIN event_params ep_dep ON pd.depends_on_param_id = ep_dep.id
            WHERE ep.event_id = ?
            ORDER BY ep.id
        """
        return fetch_all_as_dict(query, (event_id,))

    def count_by_event_id(self, event_id: int) -> int:
        """
        统计事件的参数数量

        Args:
            event_id: 事件ID

        Returns:
            参数数量

        Example:
            >>> repo = EventParamRepository()
            >>> count = repo.count_by_event_id(1)
        """
        query = "SELECT COUNT(*) as count FROM event_params WHERE event_id = ?"
        result = fetch_one_as_dict(query, (event_id,))
        return result["count"] if result else 0

    def find_by_template_id(self, template_id: int) -> List[Dict[str, Any]]:
        """
        根据模板ID查询参数

        Args:
            template_id: 模板ID

        Returns:
            参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.find_by_template_id(1)
        """
        query = """
            SELECT
                ep.*,
                le.event_name,
                le.event_name_cn,
                g.gid as game_gid,
                g.name as game_name,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.template_id = ?
            ORDER BY ep.id DESC
        """
        return fetch_all_as_dict(query, (template_id,))

    def search_by_name_pattern(
        self, pattern: str, game_gid: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据参数名模式搜索

        Args:
            pattern: 搜索模式（支持SQL LIKE）
            game_gid: 可选的游戏GID过滤

        Returns:
            匹配的参数列表

        Example:
            >>> repo = EventParamRepository()
            >>> params = repo.search_by_name_pattern('%user%', game_gid=10000147)
        """
        pattern_like = f"%{pattern}%"

        if game_gid:
            query = """
                SELECT
                    ep.*,
                    le.event_name,
                    le.event_name_cn,
                    g.gid as game_gid,
                    g.name as game_name,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.param_name LIKE ? AND g.gid = ?
                ORDER BY ep.id DESC
            """
            return fetch_all_as_dict(query, (pattern_like, game_gid))
        else:
            query = """
                SELECT
                    ep.*,
                    le.event_name,
                    le.event_name_cn,
                    g.gid as game_gid,
                    g.name as game_name,
                    pt.template_name,
                    pt.display_name as type_display_name
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.param_name LIKE ?
                ORDER BY ep.id DESC
            """
            return fetch_all_as_dict(query, (pattern_like,))
