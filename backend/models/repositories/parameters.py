#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Repository (参数数据访问层 - 精简架构)

提供参数相关的数据访问方法
- 返回统一Entity模型 (ParameterEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict, get_db_connection
from backend.models.entities import ParameterEntity, CommonParameterEntity


class ParameterRepository(GenericRepository):
    """
    参数仓储类 (精简架构)

    继承 GenericRepository 并添加参数特定的查询方法
    返回ParameterEntity而非字典,确保类型安全
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

    @staticmethod
    def _row_to_entity(row: Dict[str, Any]) -> ParameterEntity:
        """
        将数据库行映射到ParameterEntity

        数据库字段名 → Entity字段名映射:
        - param_name → name
        - param_name_cn → name_cn (暂不使用)
        - param_description → description
        - 需要查询log_events获取game_gid

        Args:
            row: 数据库行字典

        Returns:
            ParameterEntity实例
        """
        # 从关联的log_events获取game_gid
        game_gid = row.get('game_gid')
        if not game_gid and 'event_id' in row:
            # 如果没有game_gid,查询获取
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT game_gid FROM log_events WHERE id = ?", (row['event_id'],))
            result = cursor.fetchone()
            if result:
                game_gid = result[0]
            conn.close()

        # 映射字段
        entity_data = {
            'id': row.get('id'),
            'event_id': row.get('event_id'),
            'game_gid': game_gid or 0,  # 提供默认值
            'name': row.get('param_name', ''),
            'param_type': 'base',  # 默认值,数据库中没有这个字段
            'json_path': row.get('json_path'),
            'hive_type': 'STRING',  # 默认值
            'description': row.get('param_description'),
            'is_common': False,  # 默认值
            'created_at': row.get('created_at'),
            'updated_at': row.get('updated_at'),
        }

        return ParameterEntity(**entity_data)

    def create(self, data: Dict[str, Any]) -> Optional[ParameterEntity]:
        """
        创建参数

        处理字段名映射:
        - name → param_name
        - description → param_description

        Args:
            data: 参数数据 (使用Entity字段名)

        Returns:
            创建的ParameterEntity, 失败返回None
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 字段映射: Entity字段 → 数据库列
            db_data = {
                'event_id': data.get('event_id'),
                'game_gid': data.get('game_gid'),
                'param_name': data.get('name'),
                'param_name_cn': data.get('name_cn'),  # 暂不使用
                'param_type': data.get('param_type', 'base'),
                'json_path': data.get('json_path'),
                'hive_type': data.get('hive_type', 'STRING'),
                'param_description': data.get('description'),
                'is_common': data.get('is_common', False),
                'template_id': 1,  # 默认模板ID (NOT NULL)
                'is_active': 1,  # 默认激活
                'version': 1,  # 默认版本
            }

            # 移除None值
            db_data = {k: v for k, v in db_data.items() if v is not None}

            columns = ", ".join(db_data.keys())
            placeholders = ", ".join(["?" for _ in db_data.keys()])

            query = f"INSERT INTO event_params ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(db_data.values()))
            param_id = cursor.lastrowid
            conn.commit()

            return self.find_by_id(param_id)

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_active_by_event(self, event_id: int) -> List[ParameterEntity]:
        """
        获取指定事件的所有活跃参数

        Args:
            event_id: 事件ID

        Returns:
            ParameterEntity列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_active_by_event(1)
        """
        query = """
            SELECT
                ep.*,
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """
        rows = fetch_all_as_dict(query, (event_id,))
        return [self._row_to_entity(row) for row in rows]

    def find_by_name_and_event(self, param_name: str, event_id: int) -> Optional[ParameterEntity]:
        """
        根据参数名和事件ID查询参数

        Args:
            param_name: 参数名
            event_id: 事件ID

        Returns:
            ParameterEntity, 不存在返回None

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.find_by_name_and_event('user_id', 1)
        """
        query = """
            SELECT
                ep.*,
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.param_name = ? AND ep.event_id = ?
        """
        row = fetch_one_as_dict(query, (param_name, event_id))
        return self._row_to_entity(row) if row else None

    def get_all_by_event(
        self, event_id: int, include_inactive: bool = False
    ) -> List[ParameterEntity]:
        """
        获取指定事件的所有参数（包含非活跃参数）

        Args:
            event_id: 事件ID
            include_inactive: 是否包含非活跃参数

        Returns:
            ParameterEntity列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_all_by_event(1, include_inactive=True)
        """
        if include_inactive:
            query = """
                SELECT
                    ep.*,
                    le.game_gid
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                WHERE ep.event_id = ?
                ORDER BY ep.id
            """
        else:
            query = """
                SELECT
                    ep.*,
                    le.game_gid
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                WHERE ep.event_id = ? AND ep.is_active = 1
                ORDER BY ep.id
            """
        rows = fetch_all_as_dict(query, (event_id,))
        return [self._row_to_entity(row) for row in rows]

    def find_by_id(self, param_id: int) -> Optional[ParameterEntity]:
        """
        根据参数ID查询参数

        Args:
            param_id: 参数ID

        Returns:
            ParameterEntity, 不存在返回None
        """
        query = """
            SELECT
                ep.*,
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.id = ?
        """
        row = fetch_one_as_dict(query, (param_id,))
        return self._row_to_entity(row) if row else None

    def find_by_template(
        self, template_id: int, limit: Optional[int] = None
    ) -> List[ParameterEntity]:
        """
        根据模板ID查询参数

        Args:
            template_id: 模板ID
            limit: 限制数量

        Returns:
            ParameterEntity列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.find_by_template(1, limit=10)
        """
        query = """
            SELECT
                ep.*,
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.template_id = ?
            ORDER BY ep.id DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        rows = fetch_all_as_dict(query, (template_id,))
        return [self._row_to_entity(row) for row in rows]

    def search_parameters(
        self, keyword: str, event_id: Optional[int] = None, template_id: Optional[int] = None
    ) -> List[ParameterEntity]:
        """
        搜索参数（支持参数名和中文名模糊搜索）

        Args:
            keyword: 搜索关键词
            event_id: 可选的事件ID过滤
            template_id: 可选的模板ID过滤

        Returns:
            ParameterEntity列表

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
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause}
            AND (ep.param_name LIKE ?)
            ORDER BY ep.id DESC
        """

        params.extend([keyword_pattern])
        rows = fetch_all_as_dict(query, tuple(params))
        return [self._row_to_entity(row) for row in rows]

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
        from backend.core.utils.converters import get_db_connection

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
    ) -> List[ParameterEntity]:
        """
        根据参数类型获取参数列表

        Args:
            template_id: 模板ID（参数类型）
            event_id: 可选的事件ID过滤

        Returns:
            ParameterEntity列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_parameters_by_type(1, event_id=1)
        """
        if event_id:
            query = """
                SELECT
                    ep.*,
                    le.game_gid
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                WHERE ep.template_id = ? AND ep.event_id = ? AND ep.is_active = 1
                ORDER BY ep.id
            """
            rows = fetch_all_as_dict(query, (template_id, event_id))
        else:
            query = """
                SELECT
                    ep.*,
                    le.game_gid
                FROM event_params ep
                JOIN log_events le ON ep.event_id = le.id
                WHERE ep.template_id = ? AND ep.is_active = 1
                ORDER BY ep.id DESC
            """
            rows = fetch_all_as_dict(query, (template_id,))

        return [self._row_to_entity(row) for row in rows]

    def update(self, param_id: int, data: Dict[str, Any]) -> Optional[ParameterEntity]:
        """
        根据参数ID更新参数

        Args:
            param_id: 参数ID
            data: 要更新的字段字典（支持Entity字段名或数据库字段名）

        Returns:
            更新后的ParameterEntity, 不存在返回None

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.update(1, {'name': 'Updated Name'})  # Entity字段名
            >>> param = repo.update(1, {'param_name': 'Updated Name'})  # 数据库字段名
        """
        if not data:
            return None

        # 映射Entity字段名到数据库字段名
        field_mapping = {
            'name': 'param_name',
            'description': 'param_description',
        }

        # 转换字段名
        db_data = {}
        for key, value in data.items():
            db_key = field_mapping.get(key, key)
            db_data[db_key] = value

        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in db_data.keys()])
        query = f"UPDATE event_params SET {set_clause} WHERE id = ?"
        values = list(db_data.values()) + [param_id]

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        # 返回更新后的参数
        return self.find_by_id(param_id)

    def delete(self, param_id: int) -> bool:
        """
        根据参数ID删除参数

        Args:
            param_id: 参数ID

        Returns:
            是否删除成功

        Example:
            >>> repo = ParameterRepository()
            >>> success = repo.delete(1)
        """
        query = "DELETE FROM event_params WHERE id = ?"

        from backend.core.utils.converters import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (param_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0

    # ========== Common Params Methods ==========

    def get_common_params_by_game(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取指定游戏的公共参数列表

        Args:
            game_gid: 游戏GID

        Returns:
            公共参数字典列表

        Example:
            >>> repo = ParameterRepository()
            >>> params = repo.get_common_params_by_game(10000147)
        """
        # First get game_id from game_gid
        game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return []

        game_id = game["id"]

        query = """
            SELECT
                id,
                game_gid,
                param_name,
                param_name_cn,
                param_type,
                table_name,
                status,
                created_at,
                updated_at
            FROM common_params
            WHERE game_gid = ?
            ORDER BY created_at DESC
        """
        return fetch_all_as_dict(query, (game_gid,))

    def find_common_param_by_name(self, game_gid: int, param_name: str) -> Optional[Dict[str, Any]]:
        """
        根据游戏GID和参数名查找公共参数

        Args:
            game_gid: 游戏GID
            param_name: 参数名称

        Returns:
            公共参数字典，不存在返回None

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.find_common_param_by_name(10000147, 'zone_id')
        """
        query = """
            SELECT * FROM common_params
            WHERE game_gid = ? AND param_name = ?
        """
        return fetch_one_as_dict(query, (game_gid, param_name))

    def create_common_param(self, param_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建公共参数

        Args:
            param_data: 公共参数数据

        Returns:
            创建的公共参数字典，失败返回None

        Example:
            >>> repo = ParameterRepository()
            >>> param = repo.create_common_param({
            ...     'game_id': 1,
            ...     'game_gid': 10000147,
            ...     'param_name': 'zone_id',
            ...     'param_name_cn': '区域ID',
            ...     'param_type': 'string',
            ...     'table_name': 'common'
            ... })
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO common_params (
                    game_id, game_gid, param_name, param_name_cn, param_type,
                    table_name, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'synced', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (
                param_data.get('game_id'),
                param_data.get('game_gid'),
                param_data.get('param_name'),
                param_data.get('param_name_cn'),
                param_data.get('param_type', 'string'),
                param_data.get('table_name', 'common')
            ))
            param_id = cursor.lastrowid
            conn.commit()

            return fetch_one_as_dict("SELECT * FROM common_params WHERE id = ?", (param_id,))

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_common_param(self, param_id: int) -> bool:
        """
        删除公共参数

        Args:
            param_id: 公共参数ID

        Returns:
            是否删除成功

        Example:
            >>> repo = ParameterRepository()
            >>> success = repo.delete_common_param(1)
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM common_params WHERE id = ?", (param_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    def delete_common_params_batch(self, param_ids: List[int]) -> int:
        """
        批量删除公共参数

        Args:
            param_ids: 公共参数ID列表

        Returns:
            删除的参数数量

        Example:
            >>> repo = ParameterRepository()
            >>> count = repo.delete_common_params_batch([1, 2, 3])
        """
        if not param_ids:
            return 0

        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            placeholders = ",".join(["?" for _ in param_ids])
            query = f"DELETE FROM common_params WHERE id IN ({placeholders})"
            cursor.execute(query, tuple(param_ids))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        finally:
            conn.close()

    def batch_find_by_event_ids(self, event_ids: List[int]) -> Dict[int, List[ParameterEntity]]:
        """
        批量查询事件参数（解决N+1查询问题）

        Args:
            event_ids: 事件ID列表

        Returns:
            {event_id: [ParameterEntity]} 字典,按event_id分组

        Example:
            >>> repo = ParameterRepository()
            >>> params_map = repo.batch_find_by_event_ids([1, 2, 3])
            >>> # params_map = {1: [ParameterEntity, ...], 2: [...], 3: [...]}
        """
        if not event_ids:
            return {}

        placeholders = ','.join(['?' for _ in event_ids])
        query = f"""
            SELECT
                ep.*,
                le.game_gid
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE ep.event_id IN ({placeholders})
            ORDER BY ep.event_id, ep.id
        """

        rows = fetch_all_as_dict(query, event_ids)

        # 按event_id分组
        result = {}
        for row in rows:
            entity = self._row_to_entity(row)
            event_id = row['event_id']
            if event_id not in result:
                result[event_id] = []
            result[event_id].append(entity)

        return result

    def batch_get_game_gids_by_param_ids(self, param_ids: List[int]) -> Dict[int, int]:
        """
        批量获取参数ID对应的游戏GID（解决N+1查询）

        Args:
            param_ids: 公共参数ID列表

        Returns:
            {param_id: game_gid} 字典

        Example:
            >>> repo = ParameterRepository()
            >>> game_gids = repo.batch_get_game_gids_by_param_ids([1, 2, 3])
            >>> # game_gids = {1: 10000147, 2: 10000147, 3: 10000148}
        """
        if not param_ids:
            return {}

        placeholders = ','.join(['?' for _ in param_ids])
        query = f"SELECT id, game_gid FROM common_params WHERE id IN ({placeholders})"

        rows = fetch_all_as_dict(query, param_ids)

        return {row['id']: row['game_gid'] for row in rows}

    # ========== Extended Methods (from parameter_service_extended.py) ==========

    def get_parameter_details(self, param_name: str, game_gid: int) -> Optional[Dict[str, Any]]:
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

    def get_common_params_with_event_count(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取公共参数列表（包含事件计数）

        Args:
            game_gid: 游戏GID

        Returns:
            公共参数列表，每个参数包含使用它的事件数量
        """
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

    def get_alter_table_sql(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取ALTER TABLE SQL语句

        Args:
            param_id: 公共参数ID

        Returns:
            包含参数信息和SQL的字典，不存在返回None
        """
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
        from backend.services.hql.manager import HQLManager

        manager = HQLManager()
        alter_sql = manager.generate_alter_table_hql(
            target_table=param["table_name"],
            param_name=param["param_name"],
            param_type=param["param_type"],
            param_name_cn=param["param_name_cn"],
        )

        return {"param": param, "alter_sql": alter_sql}

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

        return {"param_id": param_id, "library_id": library_id}
