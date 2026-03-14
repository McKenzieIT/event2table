# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Join Config Repository (Join配置数据访问层 - 精简架构)

提供Join Config相关的数据访问方法
- 返回统一Entity模型 (JoinConfigEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import List, Optional

from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
from backend.models.entities import JoinConfigEntity


class JoinConfigRepository(GenericRepository):
    """
    Join配置仓储类 (精简架构)

    继承 GenericRepository 并添加Join Config特定的查询方法
    返回JoinConfigEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化Join Config仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="join_configs",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120,  # 2分钟缓存
        )

    def find_by_id(self, config_id: int) -> Optional[JoinConfigEntity]:
        """
        根据数据库ID查询Join配置

        Args:
            config_id: 数据库自增ID

        Returns:
            JoinConfigEntity, 不存在返回None

        Example:
            >>> repo = JoinConfigRepository()
            >>> config = repo.find_by_id(1)
            >>> print(config.name) if config else None
        """
        import json

        query = "SELECT * FROM join_configs WHERE id = ?"
        row = fetch_one_as_dict(query, (config_id,))

        if row is None:
            return None

        # 映射数据库列名到Entity字段名
        # join_conditions (数据库) → join_config (Entity)
        # 同时需要反序列化JSON字符串
        if 'join_conditions' in row and row['join_conditions']:
            # 解析JSON字符串
            if isinstance(row['join_conditions'], str):
                try:
                    row['join_config'] = json.loads(row['join_conditions'])
                except json.JSONDecodeError:
                    row['join_config'] = {}
            else:
                row['join_config'] = row['join_conditions']
            del row['join_conditions']

        # 反序列化其他JSON字段
        json_fields = ['source_events', 'output_fields', 'where_conditions', 'field_mappings']
        for field in json_fields:
            if field in row and isinstance(row[field], str):
                try:
                    row[field] = json.loads(row[field])
                except (json.JSONDecodeError, ValueError):
                    row[field] = [] if field in ['source_events', 'output_fields'] else None

        return JoinConfigEntity(**row)

    def find_by_game_gid(
        self, game_gid: int, join_type: Optional[str] = None
    ) -> List[JoinConfigEntity]:
        """
        根据游戏GID查询Join配置列表

        Args:
            game_gid: 游戏业务GID
            join_type: 可选, 按join_type过滤

        Returns:
            JoinConfigEntity列表

        Example:
            >>> repo = JoinConfigRepository()
            >>> configs = repo.find_by_game_gid(10000147, join_type="join")
            >>> for config in configs:
            ...     print(config.name)
        """
        import json

        query = "SELECT * FROM join_configs WHERE game_gid = ?"
        params = [game_gid]

        if join_type:
            query += " AND join_type = ?"
            params.append(join_type)

        query += " ORDER BY created_at DESC"

        rows = fetch_all_as_dict(query, tuple(params))

        # 处理每一行: 字段映射和JSON反序列化
        entities = []
        for row in rows:
            # 映射 join_conditions → join_config
            if 'join_conditions' in row and row['join_conditions']:
                if isinstance(row['join_conditions'], str):
                    try:
                        row['join_config'] = json.loads(row['join_conditions'])
                    except json.JSONDecodeError:
                        row['join_config'] = {}
                else:
                    row['join_config'] = row['join_conditions']
                del row['join_conditions']

            # 反序列化其他JSON字段
            json_fields = ['source_events', 'output_fields', 'where_conditions', 'field_mappings']
            for field in json_fields:
                if field in row and isinstance(row[field], str):
                    try:
                        row[field] = json.loads(row[field])
                    except (json.JSONDecodeError, ValueError):
                        row[field] = [] if field in ['source_events', 'output_fields'] else None

            entities.append(JoinConfigEntity(**row))

        return entities

    def find_all(self) -> List[JoinConfigEntity]:
        """
        查询所有Join配置

        Returns:
            JoinConfigEntity列表
        """
        query = "SELECT * FROM join_configs ORDER BY created_at DESC"
        rows = fetch_all_as_dict(query)
        return [JoinConfigEntity(**row) for row in rows]

    def find_by_name(self, name: str) -> Optional[JoinConfigEntity]:
        """
        根据配置名称查询Join配置

        Args:
            name: 配置名称

        Returns:
            JoinConfigEntity, 不存在返回None
        """
        query = "SELECT * FROM join_configs WHERE name = ?"
        row = fetch_one_as_dict(query, (name,))
        return JoinConfigEntity(**row) if row else None

    def create(self, data: dict) -> Optional[JoinConfigEntity]:
        """
        创建Join配置

        注意: JSON字段会自动序列化为字符串

        Args:
            data: Join配置数据字典

        Returns:
            创建的JoinConfigEntity, 失败返回None

        Raises:
            Exception: 数据库操作失败
        """
        # 序列化JSON字段
        import json

        data_to_insert = data.copy()

        # 序列化JSON字段为字符串
        if 'source_events' in data_to_insert and isinstance(data_to_insert['source_events'], list):
            data_to_insert['source_events'] = json.dumps(data_to_insert['source_events'])

        # 注意: Entity字段名为 join_config, 数据库字段名为 join_conditions(复数)
        if 'join_config' in data_to_insert and isinstance(data_to_insert['join_config'], dict):
            data_to_insert['join_conditions'] = json.dumps(data_to_insert.pop('join_config'))

        if 'output_fields' in data_to_insert and isinstance(data_to_insert['output_fields'], list):
            data_to_insert['output_fields'] = json.dumps(data_to_insert['output_fields'])

        if 'where_conditions' in data_to_insert and isinstance(
            data_to_insert['where_conditions'], dict
        ):
            data_to_insert['where_conditions'] = json.dumps(data_to_insert['where_conditions'])

        if 'field_mappings' in data_to_insert and isinstance(
            data_to_insert['field_mappings'], dict
        ):
            data_to_insert['field_mappings'] = json.dumps(data_to_insert['field_mappings'])

        # 调用父类创建方法(返回字典而非ID)
        created_dict = super().create(data_to_insert)

        # 由于JoinConfigRepository重写了find_by_id()返回Entity, 
        # super().create()实际返回的是Entity对象而非字典
        if created_dict is not None:
            # 如果是Entity对象, 直接返回
            if hasattr(created_dict, 'id'):
                return created_dict
            # 如果是字典, 通过find_by_id获取Entity
            elif 'id' in created_dict:
                return self.find_by_id(created_dict['id'])

        return None

    def update(self, config_id: int, data: dict) -> bool:
        """
        更新Join配置

        注意: JSON字段会自动序列化为字符串

        Args:
            config_id: 配置ID
            data: 更新数据字典

        Returns:
            更新成功返回True, 失败返回False
        """
        # 序列化JSON字段
        import json

        data_to_update = data.copy()

        # 序列化JSON字段为字符串
        if 'source_events' in data_to_update and isinstance(data_to_update['source_events'], list):
            data_to_update['source_events'] = json.dumps(data_to_update['source_events'])

        # 注意: Entity字段名为 join_config, 数据库字段名为 join_conditions(复数)
        if 'join_config' in data_to_update and isinstance(data_to_update['join_config'], dict):
            data_to_update['join_conditions'] = json.dumps(data_to_update.pop('join_config'))

        if 'output_fields' in data_to_update and isinstance(data_to_update['output_fields'], list):
            data_to_update['output_fields'] = json.dumps(data_to_update['output_fields'])

        if 'where_conditions' in data_to_update and isinstance(
            data_to_update['where_conditions'], dict
        ):
            data_to_update['where_conditions'] = json.dumps(data_to_update['where_conditions'])

        if 'field_mappings' in data_to_update and isinstance(
            data_to_update['field_mappings'], dict
        ):
            data_to_update['field_mappings'] = json.dumps(data_to_update['field_mappings'])

        # 调用父类更新方法
        return super().update(config_id, data_to_update)

    def delete_by_game_gid(self, game_gid: int) -> int:
        """
        删除游戏的所有Join配置

        Args:
            game_gid: 游戏业务GID

        Returns:
            删除的配置数量
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM join_configs WHERE game_gid = ?", (game_gid,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count
