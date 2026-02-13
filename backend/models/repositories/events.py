#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Repository (事件数据访问层)

提供事件相关的数据访问方法
基于 GenericRepository 实现特定领域的查询
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class EventRepository(GenericRepository):
    """
    事件仓储类

    继承 GenericRepository 并添加事件特定的查询方法
    """

    def __init__(self):
        """
        初始化事件仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="log_events",
            primary_key="id",
            enable_cache=True,
            cache_timeout=60,  # 1分钟缓存
        )

    def find_by_game_gid(
        self, game_gid: int, page: int = 1, per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        根据游戏GID分页查询事件

        Args:
            game_gid: 游戏GID
            page: 页码（从1开始）
            per_page: 每页数量

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.find_by_game_gid(1001, page=1, per_page=20)
        """
        offset = (page - 1) * per_page
        query = """
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                COALESCE(COUNT(DISTINCT ep.id), 0) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            LEFT JOIN event_params ep ON le.id = ep.event_id AND ep.is_active = 1
            WHERE g.gid = ?
            GROUP BY le.id
            ORDER BY le.id DESC
            LIMIT ? OFFSET ?
        """
        return fetch_all_as_dict(query, (game_gid, per_page, offset))

    def count_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的事件数量

        Args:
            game_gid: 游戏GID

        Returns:
            事件数量

        Example:
            >>> repo = EventRepository()
            >>> count = repo.count_by_game_gid(1001)
        """
        query = """
            SELECT COUNT(*) as total
            FROM log_events le
            JOIN games g ON le.game_gid = g.gid
            WHERE g.gid = ?
        """
        result = fetch_one_as_dict(query, (game_gid,))
        return result["total"] if result else 0

    def get_with_parameters(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件及其参数列表

        Args:
            event_id: 事件ID

        Returns:
            包含参数列表的事件字典，不存在返回None

        Example:
            >>> repo = EventRepository()
            >>> event = repo.get_with_parameters(1)
            >>> if event:
            ...     print(f"Event: {event['event_name']}")
            ...     for param in event['parameters']:
            ...         print(f"  - {param['param_name']}")
        """
        # 获取事件基本信息
        event_query = """
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.id = ?
        """
        event = fetch_one_as_dict(event_query, (event_id,))

        if not event:
            return None

        # 获取活跃参数
        params_query = """
            SELECT
                ep.*,
                pt.template_name,
                pt.display_name as type_display_name
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """
        parameters = fetch_all_as_dict(params_query, (event_id,))

        # 组合结果
        event["parameters"] = parameters
        return event

    def find_by_name(self, event_name: str, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        根据事件名和游戏GID查询事件

        Args:
            event_name: 事件名
            game_gid: 游戏GID

        Returns:
            事件字典，不存在返回None

        Example:
            >>> repo = EventRepository()
            >>> event = repo.find_by_name('login', 1001)
        """
        query = """
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.event_name = ? AND g.gid = ?
        """
        return fetch_one_as_dict(query, (event_name, game_gid))

    def find_by_category(
        self, category_id: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据分类ID查询事件

        Args:
            category_id: 分类ID
            limit: 限制数量

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.find_by_category(1, limit=10)
        """
        query = """
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                COALESCE(COUNT(DISTINCT ep.id), 0) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            LEFT JOIN event_params ep ON le.id = ep.event_id AND ep.is_active = 1
            WHERE le.category_id = ?
            GROUP BY le.id
            ORDER BY le.id DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        return fetch_all_as_dict(query, (category_id,))

    def get_events_with_common_params(self, game_gid: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取包含公共参数的事件

        Args:
            game_gid: 可选的游戏GID过滤

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.get_events_with_common_params(game_gid=1001)
        """
        if game_gid:
            query = """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE g.gid = ? AND le.include_in_common_params = 1
                ORDER BY le.id DESC
            """
            return fetch_all_as_dict(query, (game_gid,))
        else:
            query = """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.include_in_common_params = 1
                ORDER BY le.id DESC
            """
            return fetch_all_as_dict(query)

    def search_events(
        self, keyword: str, game_gid: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索事件（支持事件名和中文名模糊搜索）

        Args:
            keyword: 搜索关键词
            game_gid: 可选的游戏GID过滤
            category_id: 可选的分类ID过滤

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.search_events('login', game_gid=1001)
        """
        keyword_pattern = f"%{keyword}%"
        conditions = []
        params = []

        if game_gid:
            conditions.append("g.gid = ?")
            params.append(game_gid)

        if category_id:
            conditions.append("le.category_id = ?")
            params.append(category_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                COALESCE(COUNT(DISTINCT ep.id), 0) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            LEFT JOIN event_params ep ON le.id = ep.event_id AND ep.is_active = 1
            WHERE {where_clause}
            AND (le.event_name LIKE ? OR le.event_name_cn LIKE ?)
            GROUP BY le.id
            ORDER BY le.id DESC
        """

        params.extend([keyword_pattern, keyword_pattern])
        return fetch_all_as_dict(query, tuple(params))

    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近更新的事件

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 限制数量

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.get_recent_events(game_gid=1001, limit=5)
        """
        if game_gid:
            query = """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE g.gid = ?
                ORDER BY le.updated_at DESC
                LIMIT ?
            """
            return fetch_all_as_dict(query, (game_gid, limit))
        else:
            query = """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                ORDER BY le.updated_at DESC
                LIMIT ?
            """
            return fetch_all_as_dict(query, (limit,))

    def get_event_statistics(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件统计信息

        Args:
            event_id: 事件ID

        Returns:
            统计信息字典

        Example:
            >>> repo = EventRepository()
            >>> stats = repo.get_event_statistics(1)
        """
        query = """
            SELECT
                le.id as event_id,
                le.event_name,
                le.event_name_cn,
                COUNT(DISTINCT ep.id) as total_params,
                COUNT(DISTINCT ep.id) FILTER (WHERE ep.is_active = 1) as active_params,
                COUNT(DISTINCT ep.id) FILTER (WHERE ep.is_active = 0) as inactive_params,
                le.created_at,
                le.updated_at
            FROM log_events le
            LEFT JOIN event_params ep ON le.id = ep.event_id
            WHERE le.id = ?
            GROUP BY le.id
        """
        return fetch_one_as_dict(query, (event_id,))

    def bulk_create_with_parameters(self, events_data: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建事件及其参数

        Args:
            events_data: 事件数据列表，每个事件包含 parameters 字段

        Returns:
            创建的事件ID列表

        Example:
            >>> repo = EventRepository()
            >>> event_ids = repo.bulk_create_with_parameters([
            ...     {
            ...         'game_id': 1,
            ...         'event_name': 'test_event',
            ...         'event_name_cn': '测试事件',
            ...         'category_id': 1,
            ...         'source_table': 'ieu_ods.test',
            ...         'target_table': 'ieu_cdm.test',
            ...         'include_in_common_params': 1,
            ...         'parameters': [
            ...             {'param_name': 'param1', 'param_name_cn': '参数1', ...}
            ...         ]
            ...     }
            ... ])
        """
        from backend.core.database.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        created_event_ids = []

        try:
            for event_data in events_data:
                # 提取参数列表
                parameters = event_data.pop("parameters", [])

                # 插入事件
                cursor.execute(
                    """
                    INSERT INTO log_events (
                        game_id, event_name, event_name_cn, category_id,
                        source_table, target_table, include_in_common_params
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event_data["game_id"],
                        event_data["event_name"],
                        event_data["event_name_cn"],
                        event_data["category_id"],
                        event_data["source_table"],
                        event_data["target_table"],
                        event_data.get("include_in_common_params", 0),
                    ),
                )

                event_id = cursor.lastrowid
                created_event_ids.append(event_id)

                # 插入参数
                for param in parameters:
                    cursor.execute(
                        """
                        INSERT INTO event_params (
                            event_id, param_name, param_name_cn,
                            template_id, param_description, is_active, version
                        ) VALUES (?, ?, ?, ?, ?, 1, 1)
                    """,
                        (
                            event_id,
                            param["param_name"],
                            param.get("param_name_cn", ""),
                            param.get("template_id", 1),
                            param.get("param_description", ""),
                        ),
                    )

            conn.commit()
            return created_event_ids

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
