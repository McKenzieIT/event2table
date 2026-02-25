#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Repository (事件数据访问层 - 精简架构)

提供事件相关的数据访问方法
- 返回统一Entity模型 (EventEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict, get_db_connection
from backend.models.entities import EventEntity


class EventRepository(GenericRepository):
    """
    事件仓储类 (精简架构)

    继承 GenericRepository 并添加事件特定的查询方法
    返回EventEntity而非字典,确保类型安全
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

    def find_by_id(self, event_id: int) -> Optional[EventEntity]:
        """
        根据数据库ID查询事件

        Args:
            event_id: 数据库自增ID

        Returns:
            EventEntity, 不存在返回None
        """
        query = "SELECT * FROM log_events WHERE id = ?"
        row = fetch_one_as_dict(query, (event_id,))
        return EventEntity(**row) if row else None

    def find_by_name(self, event_name: str, game_gid: int) -> Optional[EventEntity]:
        """
        根据事件名和游戏GID查询事件

        Args:
            event_name: 事件名
            game_gid: 游戏GID

        Returns:
            EventEntity, 不存在返回None

        Example:
            >>> repo = EventRepository()
            >>> event = repo.find_by_name('login', 10000147)
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
        row = fetch_one_as_dict(query, (event_name, game_gid))
        return EventEntity(**row) if row else None

    def find_by_game_gid(
        self, game_gid: int, page: int = 1, per_page: int = 20
    ) -> List[EventEntity]:
        """
        根据游戏GID分页查询事件

        Args:
            game_gid: 游戏GID
            page: 页码（从1开始）
            per_page: 每页数量

        Returns:
            EventEntity列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.find_by_game_gid(10000147, page=1, per_page=20)
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
        rows = fetch_all_as_dict(query, (game_gid, per_page, offset))
        return [EventEntity(**row) for row in rows]

    def find_all(self, game_gid: Optional[int] = None) -> List[EventEntity]:
        """
        查询所有事件（可选游戏过滤）

        Args:
            game_gid: 可选的游戏GID过滤

        Returns:
            EventEntity列表
        """
        if game_gid:
            query = """
                SELECT le.*, g.gid, g.name as game_name, g.ods_db,
                       ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE g.gid = ?
                ORDER BY le.id DESC
            """
            rows = fetch_all_as_dict(query, (game_gid,))
        else:
            query = """
                SELECT le.*, g.gid, g.name as game_name, g.ods_db,
                       ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                ORDER BY le.id DESC
            """
            rows = fetch_all_as_dict(query)
        return [EventEntity(**row) for row in rows]

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
        获取事件及其参数列表（保持返回字典格式以包含参数列表）

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

        # 组合结果（保持字典格式以便包含parameters列表）
        event["parameters"] = parameters
        return event

    def find_by_category(
        self, category_id: int, limit: Optional[int] = None
    ) -> List[EventEntity]:
        """
        根据分类ID查询事件

        Args:
            category_id: 分类ID
            limit: 限制数量

        Returns:
            EventEntity列表

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
        rows = fetch_all_as_dict(query, (category_id,))
        return [EventEntity(**row) for row in rows]

    def get_events_with_common_params(self, game_gid: Optional[int] = None) -> List[EventEntity]:
        """
        获取包含公共参数的事件

        Args:
            game_gid: 可选的游戏GID过滤

        Returns:
            EventEntity列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.get_events_with_common_params(game_gid=10000147)
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
            rows = fetch_all_as_dict(query, (game_gid,))
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
            rows = fetch_all_as_dict(query)
        return [EventEntity(**row) for row in rows]

    def search_events(
        self, keyword: str, game_gid: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[EventEntity]:
        """
        搜索事件（支持事件名和中文名模糊搜索）

        Args:
            keyword: 搜索关键词
            game_gid: 可选的游戏GID过滤
            category_id: 可选的分类ID过滤

        Returns:
            EventEntity列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.search_events('login', game_gid=10000147)
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
        rows = fetch_all_as_dict(query, tuple(params))
        return [EventEntity(**row) for row in rows]

    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[EventEntity]:
        """
        获取最近更新的事件

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 限制数量

        Returns:
            EventEntity列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.get_recent_events(game_gid=10000147, limit=5)
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
            rows = fetch_all_as_dict(query, (game_gid, limit))
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
            rows = fetch_all_as_dict(query, (limit,))
        return [EventEntity(**row) for row in rows]

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

    def create(self, data: Dict[str, Any]) -> Optional[EventEntity]:
        """
        创建事件

        Args:
            data: 事件数据字典 (使用Entity字段名或数据库列名)

        Returns:
            创建的EventEntity, 失败返回None

        Example:
            >>> repo = EventRepository()
            >>> event = repo.create({
            ...     'game_gid': 10000147,
            ...     'event_name': 'test_event',
            ...     'event_name_cn': '测试事件'
            ... })
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 首先需要根据game_gid查找game_id
            game_gid = data.get('game_gid')
            if not game_gid:
                raise ValueError("game_gid is required")

            # 从games表获取game_id
            # games表使用TEXT类型的gid列
            cursor.execute("SELECT id FROM games WHERE gid = ?", (str(game_gid),))
            game_row = cursor.fetchone()
            if not game_row:
                raise ValueError(f"Game not found: gid={game_gid}")
            game_id = game_row[0]

            # 字段映射: Entity字段 -> 数据库列
            db_data = {
                'game_id': game_id,  # 从game_gid查找game_id
                'game_gid': game_gid,
                'event_name': data.get('event_name') or data.get('name'),
                'event_name_cn': data.get('event_name_cn') or data.get('name_cn'),
                'category_id': data.get('category_id'),
                'source_table': data.get('source_table', 'ieu_ods.unknown'),  # 必需字段
                'target_table': data.get('target_table', 'dwd.unknown'),  # 必需字段
                'include_in_common_params': data.get('include_in_common_params', 0),
            }

            # 移除None值
            db_data = {k: v for k, v in db_data.items() if v is not None}

            columns = ", ".join(db_data.keys())
            placeholders = ", ".join(["?" for _ in db_data.keys()])

            query = f"INSERT INTO log_events ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(db_data.values()))
            event_id = cursor.lastrowid
            conn.commit()

            return self.find_by_id(event_id)

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update(self, event_id: int, data: Dict[str, Any]) -> Optional[EventEntity]:
        """
        根据event_id更新事件

        Args:
            event_id: 事件ID
            data: 要更新的字段字典 (使用Entity字段名或数据库列名)

        Returns:
            更新后的EventEntity, 不存在返回None

        Example:
            >>> repo = EventRepository()
            >>> event = repo.update(1, {'event_name_cn': 'Updated Event'})
        """
        if not data:
            return None

        # 字段映射: Entity字段 -> 数据库列
        field_mapping = {
            'name': 'event_name',
            'name_cn': 'event_name_cn',
        }

        db_data = {}
        for key, value in data.items():
            db_key = field_mapping.get(key, key)
            db_data[db_key] = value

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in db_data.keys()])
        query = f"UPDATE log_events SET {set_clause} WHERE id = ?"
        values = list(db_data.values()) + [event_id]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        # 返回更新后的事件
        return self.find_by_id(event_id)

    def delete(self, event_id: int) -> bool:
        """
        根据event_id删除事件

        Args:
            event_id: 事件ID

        Returns:
            是否删除成功

        Example:
            >>> repo = EventRepository()
            >>> success = repo.delete(1)
        """
        query = "DELETE FROM log_events WHERE id = ?"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (event_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0

    def exists_by_name(self, event_name: str, game_gid: int) -> bool:
        """
        检查指定事件名和游戏GID的事件是否存在

        Args:
            event_name: 事件名
            game_gid: 游戏GID

        Returns:
            是否存在

        Example:
            >>> repo = EventRepository()
            >>> if repo.exists_by_name('login', 10000147):
            ...     print("Event exists")
        """
        return self.find_by_name(event_name, game_gid) is not None

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
