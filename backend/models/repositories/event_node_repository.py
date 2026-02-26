#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Node Repository (事件节点数据访问层 - 精简架构)

提供事件节点相关的数据访问方法
- 返回统一Entity模型 (EventNodeEntity)
- 移除DDD抽象
- 保持GenericRepository继承
"""

from typing import List, Dict, Optional
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.utils import execute_write
from backend.models.entities import EventNodeEntity
from backend.core.utils.json_helpers import serialize_json_field, deserialize_json_field


class EventNodeRepository(GenericRepository):
    """
    事件节点仓储类 (精简架构)

    继承 GenericRepository 并添加事件节点特定的查询方法
    返回EventNodeEntity而非字典,确保类型安全
    """

    def __init__(self):
        """
        初始化事件节点仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_nodes",
            primary_key="id",
            enable_cache=True,
            cache_timeout=120  # 2分钟缓存
        )

    def find_by_id(self, node_id: int) -> Optional[EventNodeEntity]:
        """
        根据ID查找事件节点

        Args:
            node_id: 节点ID

        Returns:
            EventNodeEntity, 不存在返回None

        Example:
            >>> repo = EventNodeRepository()
            >>> node = repo.find_by_id(1)
            >>> print(node.name) if node else None
        """
        query = f'SELECT * FROM "{self.table_name}" WHERE id = ? AND is_active = 1'
        row = fetch_one_as_dict(query, (node_id,))

        if row:
            # 反序列化JSON字段
            row["config_json"] = deserialize_json_field(row.get("config_json"))

        return EventNodeEntity(**row) if row else None

    def find_by_game_gid(self, game_gid: int) -> List[EventNodeEntity]:
        """
        根据游戏GID查找所有事件节点

        Args:
            game_gid: 游戏GID

        Returns:
            EventNodeEntity列表

        Example:
            >>> repo = EventNodeRepository()
            >>> nodes = repo.find_by_game_gid(10000147)
            >>> for node in nodes:
            ...     print(node.name)
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
            row["config_json"] = deserialize_json_field(row.get("config_json"))
            entities.append(EventNodeEntity(**row))

        return entities

    def find_by_event_id(self, event_id: int) -> List[EventNodeEntity]:
        """
        根据事件ID查找所有事件节点

        Args:
            event_id: 事件ID

        Returns:
            EventNodeEntity列表
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE event_id = ? AND is_active = 1
            ORDER BY updated_at DESC
        '''
        rows = fetch_all_as_dict(query, (event_id,))

        # 反序列化JSON字段并转换为Entity
        entities = []
        for row in rows:
            row["config_json"] = deserialize_json_field(row.get("config_json"))
            entities.append(EventNodeEntity(**row))

        return entities

    def create(self, node: EventNodeEntity) -> int:
        """
        创建新事件节点

        Args:
            node: EventNodeEntity实例

        Returns:
            新创建的节点ID

        Example:
            >>> from backend.models.entities import EventNodeEntity
            >>> repo = EventNodeRepository()
            >>> node = EventNodeEntity(
            ...     game_gid=10000147,
            ...     name="Test Node",
            ...     event_id=1,
            ...     config_json={"fields": [], "mode": "single"}
            ... )
            >>> node_id = repo.create(node)
        """
        insert_sql = f'''
            INSERT INTO "{self.table_name}" (
                game_gid, name, event_id, config_json, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        '''

        params = (
            node.game_gid,
            node.name,
            node.event_id,
            serialize_json_field(node.config_json),
            1 if node.is_active else 0,
        )

        return execute_write(insert_sql, params, return_last_id=True)

    def update(self, node_id: int, node: EventNodeEntity) -> bool:
        """
        更新事件节点

        Args:
            node_id: 节点ID
            node: EventNodeEntity实例

        Returns:
            是否更新成功

        Example:
            >>> from backend.models.entities import EventNodeEntity
            >>> repo = EventNodeRepository()
            >>> node = EventNodeEntity(
            ...     name="Updated Node Name",
            ...     config_json={"fields": ["role_id"]}
            ... )
            >>> success = repo.update(1, node)
        """
        update_parts = [
            "name = ?",
            "event_id = ?",
            "config_json = ?",
            "is_active = ?",
            "updated_at = datetime('now')",
        ]

        params = (
            node.name,
            node.event_id,
            serialize_json_field(node.config_json),
            1 if node.is_active else 0,
            node_id,
        )

        update_sql = f'''
            UPDATE "{self.table_name}" SET
            {", ".join(update_parts)}
            WHERE id = ?
        '''

        result = execute_write(update_sql, params)
        return result > 0

    def delete(self, node_id: int) -> bool:
        """
        删除事件节点（软删除：设置is_active=0）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Example:
            >>> repo = EventNodeRepository()
            >>> success = repo.delete(1)
        """
        update_sql = f'''
            UPDATE "{self.table_name}"
            SET is_active = 0, updated_at = datetime('now')
            WHERE id = ?
        '''

        result = execute_write(update_sql, (node_id,))
        return result > 0

    def hard_delete(self, node_id: int) -> bool:
        """
        硬删除事件节点（从数据库中彻底删除）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        delete_sql = f'DELETE FROM "{self.table_name}" WHERE id = ?'
        result = execute_write(delete_sql, (node_id,))
        return result > 0

    def count_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的事件节点数量

        Args:
            game_gid: 游戏GID

        Returns:
            节点数量
        """
        query = f'''
            SELECT COUNT(*) as count
            FROM "{self.table_name}"
            WHERE game_gid = ? AND is_active = 1
        '''
        result = fetch_one_as_dict(query, (game_gid,))
        return result["count"] if result else 0
