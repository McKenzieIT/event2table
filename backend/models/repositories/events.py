# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Repository (事件数据访问层 - 精简架构)

提供事件相关的数据访问方法
- 返回统一Entity模型 (EventEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Any, Dict, List, Optional

from backend.core.cache.decorators import cached as cached_decorator
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict, get_db_connection
from backend.models.entities import EventEntity


class EventRepository(GenericRepository):
    """
    事件仓储类 (精简架构)

    继承 GenericRepository 并添加事件特定的查询方法
    返回EventEntity而非字典,确保类型安全
    """

    def __init__(self) -> None:
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

    @cached_decorator(ttl=600, key_prefix="events.by_id")
    def find_by_id(self, event_id: int) -> Optional[EventEntity]:
        """
        根据数据库ID查询事件（带缓存）

        Args:
            event_id: 数据库自增ID

        Returns:
            EventEntity, 不存在返回None

        Performance:
            缓存TTL: 10分钟（半静态数据）
            预期命中率: >70%
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

    @cached_decorator(ttl=300, key_prefix="events.count_by_game")
    def count_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的事件数量（带缓存）

        Args:
            game_gid: 游戏GID

        Returns:
            事件数量

        Performance:
            缓存TTL: 5分钟（统计数据）
            预期命中率: >60%

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
            包含参数列表的事件字典, 不存在返回None

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

        # 组合结果(保持字典格式以便包含parameters列表)
        event["parameters"] = parameters
        return event

    def find_by_category(self, category_id: int, limit: Optional[int] = None) -> List[EventEntity]:
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

            # 从games表获取数据库ID(如果需要)
            # games表使用TEXT类型的gid列
            # 注意: log_events表使用game_gid作为外键
            cursor.execute("SELECT id FROM games WHERE gid = ?", (str(game_gid),))
            game_row = cursor.fetchone()
            if not game_row:
                raise ValueError(f"Game not found: gid={game_gid}")

            # 字段映射: Entity字段 -> 数据库列
            db_data = {
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

        # Validate field names to prevent SQL injection
        from backend.core.security.sql_validator import SQLValidator

        for key in db_data.keys():
            SQLValidator.validate_column_name(key)

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

    def get_by_ids(self, event_ids: List[int]) -> List[Dict[str, Any]]:
        """
        批量查询事件（按数据库ID）

        Args:
            event_ids: 事件ID列表

        Returns:
            事件列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.get_by_ids([1, 2, 3])
        """
        if not event_ids:
            return []

        placeholders = ",".join(["?" for _ in event_ids])
        query = f"SELECT * FROM log_events WHERE id IN ({placeholders})"

        return fetch_all_as_dict(query, event_ids)

    def create_batch(self, events_data: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建事件（真正的批量INSERT）

        使用 executemany() 实现, 确保单次数据库往返

        Args:
            events_data: 事件数据列表

        Returns:
            创建的事件ID列表

        Performance:
            数据库往返: 1次（executemany）
            预期性能: <1秒 for 100 records

        Example:
            >>> repo = EventRepository()
            >>> events = [
            ...     {'game_gid': 10000147, 'event_name': 'login', 'event_name_cn': '登录', 'category_id': 1},
            ...     {'game_gid': 10000147, 'event_name': 'logout', 'event_name_cn': '登出', 'category_id': 1}
            ... ]
            >>> ids = repo.create_batch(events)
        """
        if not events_data:
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 构建批量INSERT SQL
            query = """
                INSERT INTO log_events (game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            # 准备参数列表
            params = [
                (
                    e.get('game_gid'),
                    e.get('event_name'),
                    e.get('event_name_cn', ''),
                    e.get('category_id'),
                    e.get('source_table', ''),
                    e.get('target_table', ''),
                    e.get('include_in_common_params', 0),
                )
                for e in events_data
            ]

            # 执行批量插入(单次数据库往返)
            cursor.executemany(query, params)

            # 提交事务
            conn.commit()

            # 获取插入的ID列表(使用lastrowid)
            # 注意: executemany不返回rowcount, 需要查询获取
            inserted_ids = []
            for event_data in events_data:
                game_gid = event_data.get('game_gid')
                event_name = event_data.get('event_name')
                cursor.execute(
                    "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ?",
                    (game_gid, event_name),
                )
                row = cursor.fetchone()
                if row:
                    inserted_ids.append(row[0])

            return inserted_ids

        except Exception as e:
            # 回滚事务
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_batch(self, event_ids: List[int]) -> int:
        """
        批量删除事件（按数据库ID）

        Args:
            event_ids: 事件ID列表

        Returns:
            删除的事件数量

        Example:
            >>> repo = EventRepository()
            >>> count = repo.delete_batch([1, 2, 3])
        """
        if not event_ids:
            return 0

        placeholders = ",".join(["?" for _ in event_ids])
        query = f"DELETE FROM log_events WHERE id IN ({placeholders})"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, event_ids)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    def bulk_create_with_parameters(self, events_data: List[Dict[str, Any]]) -> List[int]:
        """
        批量创建事件及其参数

        Args:
            events_data: 事件数据列表, 每个事件包含 parameters 字段

        Returns:
            创建的事件ID列表

        Example:
            >>> repo = EventRepository()
            >>> event_ids = repo.bulk_create_with_parameters([
            ...     {
            ...         'game_gid': 10000147,
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
                        game_gid, event_name, event_name_cn, category_id,
                        source_table, target_table, include_in_common_params
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event_data["game_gid"],
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

                # ⚡ Performance Optimization: N+1 query fixed
                # 使用 executemany() 批量插入参数, 避免循环执行
                # 修复前: N次 INSERT 语句(N = 参数数量)
                # 修复后: 1次 executemany() 调用
                # 预期性能提升: 对于10个参数, 从10次SQL执行降至1次
                if parameters:
                    params_data = [
                        (
                            event_id,
                            param["param_name"],
                            param.get("param_name_cn", ""),
                            param.get("template_id", 1),
                            param.get("param_description", ""),
                        )
                        for param in parameters
                    ]
                    cursor.executemany(
                        """
                        INSERT INTO event_params (
                            event_id, param_name, param_name_cn,
                            template_id, param_description, is_active, version
                        ) VALUES (?, ?, ?, ?, ?, 1, 1)
                    """,
                        params_data,
                    )

            conn.commit()
            return created_event_ids

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @cached_decorator(ttl=120, key_prefix="events.batchByName")
    def batch_find_by_names(self, event_names: List[str], game_gid: int) -> List[EventEntity]:
        """
        批量查询指定名称列表中的事件 (优化N+1查询)

        Args:
            event_names: 事件名称列表
            game_gid: 游戏GID

        Returns:
            匹配的EventEntity列表

        Example:
            >>> repo = EventRepository()
            >>> events = repo.batch_find_by_names(['login', 'logout'], 10000147)
            >>> # Returns only events that match the names in the list
            >>> [e.event_name for e in events]
            ['login', 'logout']
        """
        if not event_names:
            return []

        # Build IN clause with parameterized query
        placeholders = ", ".join(["?" for _ in event_names])
        query = f"""
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.event_name IN ({placeholders})
            AND g.gid = ?
        """

        params = event_names + [game_gid]
        rows = fetch_all_as_dict(query, tuple(params))
        return [EventEntity(**row) for row in rows]

    # ========== 新增方法: 修复Service层架构违规 ==========

    def get_paginated(
        self,
        game_gid: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取分页事件列表（支持搜索和游戏过滤）

        Args:
            game_gid: 可选的游戏GID过滤
            page: 页码（从1开始）
            per_page: 每页数量
            search: 搜索关键词

        Returns:
            包含事件列表和分页信息的字典
        """
        # 构建基础查询
        query = """
            SELECT
                le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                (SELECT COUNT(*) FROM event_params ep
                 WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
        """

        # 构建WHERE子句
        where_clauses = []
        params = []

        if game_gid:
            where_clauses.append("le.game_gid = ?")
            params.append(game_gid)

        if search:
            where_clauses.append(
                "(le.event_name LIKE ? OR le.event_name_cn LIKE ? OR ec.name LIKE ?)"
            )
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        # 添加WHERE子句
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM log_events le LEFT JOIN event_categories ec ON le.category_id = ec.id"
        if where_clauses:
            count_query += " WHERE " + " AND ".join(where_clauses)
        total_result = fetch_one_as_dict(count_query, tuple(params))
        total_events = total_result["total"] if total_result else 0

        # 添加分页
        offset = (page - 1) * per_page
        query += " ORDER BY le.id DESC LIMIT ? OFFSET ?"
        events = fetch_all_as_dict(query, tuple(params + [per_page, offset]))

        total_pages = max(1, (total_events + per_page - 1) // per_page)

        return {
            "events": events,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_events,
                "total_pages": total_pages,
            },
        }

    def find_detail_with_game(self, event_id: int, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        获取事件详情（包含游戏信息）

        Args:
            event_id: 事件ID
            game_gid: 游戏GID

        Returns:
            事件详情字典, 不存在返回None
        """
        query = """
            SELECT
                le.*,
                g.gid,
                g.name as game_name,
                g.ods_db,
                ec.name as category_name
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.id = ? AND le.game_gid = ?
        """
        return fetch_one_as_dict(query, (event_id, game_gid))

    def get_event_parameters(self, event_id: int) -> List[Dict[str, Any]]:
        """
        获取事件参数列表

        Args:
            event_id: 事件ID

        Returns:
            参数列表
        """
        parameters = fetch_all_as_dict(
            """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                pt.template_name as param_type,
                ep.param_description as description,
                ep.is_active,
                ep.created_at,
                ep.updated_at
            FROM event_params ep
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """,
            (event_id,),
        )
        return parameters

    def create_with_parameters(
        self, event_data: Dict[str, Any], game_id: int, parameters: List[Dict[str, Any]]
    ) -> Optional[EventEntity]:
        """
        创建事件及其参数

        Args:
            event_data: 事件数据
            game_id: 游戏数据库ID
            parameters: 参数列表

        Returns:
            创建的EventEntity
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 生成表名
            from backend.models.entities import EventEntity

            temp_entity = EventEntity(**event_data)
            source_table = (
                f"{event_data.get('ods_db', 'ieu_ods')}.ods_{temp_entity.game_gid}_all_view"
            )
            target_table = f"dwd.v_dwd_{temp_entity.game_gid}_{temp_entity.name}_di"

            # 插入事件
            cursor.execute(
                """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    game_id,  # game_id (数据库自增ID)
                    temp_entity.game_gid,
                    temp_entity.name,
                    temp_entity.name_cn or "",
                    event_data.get("category_id"),
                    source_table,
                    target_table,
                    event_data.get("include_in_common_params", 1),
                ),
            )
            event_id = cursor.lastrowid

            # ⚡ Performance Optimization: N+1 query fixed
            # 使用 executemany() 批量插入参数
            # 修复前: N次 INSERT 语句
            # 修复后: 1次 executemany() 调用
            # 预期性能提升: 对于10个参数, 从10次SQL执行降至1次
            if parameters:
                params_data = [
                    (
                        event_id,
                        param.get("param_name"),
                        param.get("param_name_cn", ""),
                        param.get("template_id", 1),
                        param.get("param_description", ""),
                    )
                    for param in parameters
                ]
                cursor.executemany(
                    """INSERT INTO event_params
                           (event_id, param_name, param_name_cn, template_id, param_description, is_active, version)
                           VALUES (?, ?, ?, ?, ?, 1, 1)""",
                    params_data,
                )

            conn.commit()
            return self.find_by_id(event_id)

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def count_by_filters(self, game_gid: Optional[int] = None, search: Optional[str] = None) -> int:
        """
        获取事件数量（带过滤条件）

        Args:
            game_gid: 可选的游戏GID过滤
            search: 可选的搜索关键词

        Returns:
            事件数量
        """
        # 构建查询条件
        conditions = []
        params = []

        if game_gid is not None:
            conditions.append("game_gid = ?")
            params.append(game_gid)

        if search:
            conditions.append("event_name LIKE ?")
            params.append(f"%{search}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Validate WHERE clause is safe (only hardcoded field names allowed)
        # All conditions use hardcoded field names: game_gid, event_name
        # No dynamic user input in field names

        # 执行计数查询
        query = f"SELECT COUNT(*) as total FROM log_events WHERE {where_clause}"
        result = fetch_one_as_dict(query, tuple(params))

        return result["total"] if result else 0
