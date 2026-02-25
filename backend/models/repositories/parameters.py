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
from backend.models.entities import ParameterEntity


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
