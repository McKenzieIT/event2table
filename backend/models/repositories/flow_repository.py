# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Repository (流程/Canvas模板数据访问层 - 精简架构)

提供流程模板相关的数据访问方法
- 返回统一Entity模型 (FlowEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import Any, Dict, List, Optional

from backend.core.data_access import GenericRepository
from backend.core.utils import execute_write
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
from backend.core.utils.json_helpers import deserialize_json_field, serialize_json_field
from backend.models.entities import FlowEntity


class FlowRepository(GenericRepository):
    """
    流程模板仓储类 (精简架构)

    继承 GenericRepository 并添加流程特定的查询方法
    返回FlowEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化流程仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="flow_templates",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120,  # 2分钟缓存
        )

    def find_by_id(self, flow_id: int) -> Optional[FlowEntity]:
        """
        根据ID查找流程

        Args:
            flow_id: 流程ID

        Returns:
            FlowEntity, 不存在返回None

        Example:
            >>> repo = FlowRepository()
            >>> flow = repo.find_by_id(1)
            >>> print(flow.flow_name) if flow else None
        """
        query = f'SELECT * FROM "{self.table_name}" WHERE id = ?'
        row = fetch_one_as_dict(query, (flow_id,))

        if row:
            # 反序列化JSON字段
            row["flow_graph"] = deserialize_json_field(row.get("flow_graph"))
            row["variables"] = deserialize_json_field(row.get("variables"))

        return FlowEntity(**row) if row else None

    def find_by_game_gid(self, game_gid: int) -> List[FlowEntity]:
        """
        根据游戏GID查找所有流程

        Args:
            game_gid: 游戏GID

        Returns:
            FlowEntity列表

        Example:
            >>> repo = FlowRepository()
            >>> flows = repo.find_by_game_gid(10000147)
            >>> for flow in flows:
            ...     print(flow.flow_name)
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE game_gid = ? AND is_active = 1
            ORDER BY updated_at DESC
        '''
        rows = fetch_all_as_dict(query, (game_gid,))

        # 反序列化JSON字段并转换为Entity
        entities = []
        for row in rows:
            row["flow_graph"] = deserialize_json_field(row.get("flow_graph"))
            row["variables"] = deserialize_json_field(row.get("variables"))
            entities.append(FlowEntity(**row))

        return entities

    def find_all_active(self) -> List[FlowEntity]:
        """
        查询所有激活的流程

        Returns:
            FlowEntity列表
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE is_active = 1
            ORDER BY updated_at DESC
        '''
        rows = fetch_all_as_dict(query)

        entities = []
        for row in rows:
            row["flow_graph"] = deserialize_json_field(row.get("flow_graph"))
            row["variables"] = deserialize_json_field(row.get("variables"))
            entities.append(FlowEntity(**row))

        return entities

    def create(self, flow: FlowEntity) -> int:
        """
        创建新流程

        Args:
            flow: FlowEntity实例

        Returns:
            新创建的流程ID

        Example:
            >>> from backend.models.entities import FlowEntity
            >>> repo = FlowRepository()
            >>> flow = FlowEntity(
            ...     game_gid=10000147,
            ...     flow_name="Test Flow",
            ...     flow_graph={"nodes": [], "edges": []},
            ...     description="Test description"
            ... )
            >>> flow_id = repo.create(flow)
        """
        insert_sql = f'''
            INSERT INTO "{self.table_name}" (
                game_gid, flow_name, flow_graph, variables,
                description, created_by, is_active,
                created_at, updated_at, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 1)
        '''

        params = (
            flow.game_gid,
            flow.flow_name,
            serialize_json_field(flow.flow_graph),
            serialize_json_field(flow.variables),
            flow.description or "",
            flow.created_by or "",
            1 if flow.is_active else 0,
        )

        return execute_write(insert_sql, params, return_last_id=True)

    def update(self, flow_id: int, flow: FlowEntity) -> bool:
        """
        更新流程

        Args:
            flow_id: 流程ID
            flow: FlowEntity实例

        Returns:
            是否更新成功

        Example:
            >>> from backend.models.entities import FlowEntity
            >>> repo = FlowRepository()
            >>> flow = FlowEntity(
            ...     flow_name="Updated Flow Name",
            ...     description="Updated description"
            ... )
            >>> success = repo.update(1, flow)
        """
        update_parts = [
            "flow_name = ?",
            "flow_graph = ?",
            "variables = ?",
            "description = ?",
            "is_active = ?",
            "updated_at = datetime('now')",
        ]

        params = (
            flow.flow_name,
            serialize_json_field(flow.flow_graph),
            serialize_json_field(flow.variables),
            flow.description or "",
            1 if flow.is_active else 0,
            flow_id,
        )

        update_sql = f'''
            UPDATE "{self.table_name}" SET
            {", ".join(update_parts)}
            WHERE id = ?
        '''

        result = execute_write(update_sql, params)
        return result > 0

    def delete(self, flow_id: int) -> bool:
        """
        删除流程（软删除: 设置is_active=0）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Example:
            >>> repo = FlowRepository()
            >>> success = repo.delete(1)
        """
        update_sql = f'''
            UPDATE "{self.table_name}"
            SET is_active = 0, updated_at = datetime('now')
            WHERE id = ?
        '''

        result = execute_write(update_sql, (flow_id,))
        return result > 0

    def hard_delete(self, flow_id: int) -> bool:
        """
        硬删除流程（从数据库中彻底删除）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复, 请谨慎使用
        """
        delete_sql = f'DELETE FROM "{self.table_name}" WHERE id = ?'
        result = execute_write(delete_sql, (flow_id,))
        return result > 0

    def count_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的流程数量

        Args:
            game_gid: 游戏GID

        Returns:
            流程数量
        """
        query = f'''
            SELECT COUNT(*) as count
            FROM "{self.table_name}"
            WHERE game_gid = ? AND is_active = 1
        '''
        result = fetch_one_as_dict(query, (game_gid,))
        return result["count"] if result else 0

    def count_all(self) -> int:
        """
        统计所有流程数量

        Returns:
            流程数量
        """
        query = f'''
            SELECT COUNT(*) as count
            FROM "{self.table_name}"
            WHERE is_active = 1
        '''
        result = fetch_one_as_dict(query)
        return result["count"] if result else 0
