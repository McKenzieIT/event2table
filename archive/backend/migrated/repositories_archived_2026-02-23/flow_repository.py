#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Repository (流程/Canvas模板数据访问层)

提供流程模板相关的数据访问方法
"""

from typing import List, Dict, Optional, Any
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.database.database import get_db
import json


class FlowRepository:
    """
    流程模板仓储类

    提供流程模板的CRUD操作
    """

    def __init__(self):
        """初始化流程仓储"""
        self.table_name = "flow_templates"

    def find_by_id(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查找流程

        Args:
            flow_id: 流程ID

        Returns:
            流程字典，不存在返回None

        Example:
            >>> repo = FlowRepository()
            >>> flow = repo.find_by_id(1)
            >>> print(flow['flow_name']) if flow else None
        """
        query = f'SELECT * FROM "{self.table_name}" WHERE id = ?'
        flow = fetch_one_as_dict(query, (flow_id,))

        if flow and flow.get("flow_graph"):
            try:
                flow["flow_graph"] = json.loads(flow["flow_graph"])
            except (json.JSONDecodeError, TypeError):
                flow["flow_graph"] = {}

        if flow and flow.get("variables"):
            try:
                flow["variables"] = json.loads(flow["variables"])
            except (json.JSONDecodeError, TypeError):
                flow["variables"] = {}

        return flow

    def find_by_game_gid(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        根据游戏GID查找所有流程

        Args:
            game_gid: 游戏GID

        Returns:
            流程列表

        Example:
            >>> repo = FlowRepository()
            >>> flows = repo.find_by_game_gid(10000147)
            >>> for flow in flows:
            ...     print(flow['flow_name'])
        """
        query = f'''
            SELECT * FROM "{self.table_name}"
            WHERE game_gid = ? AND is_active = 1
            ORDER BY updated_at DESC
        '''
        flows = fetch_all_as_dict(query, (game_gid,))

        # 解析JSON字段
        for flow in flows:
            if flow.get("flow_graph"):
                try:
                    flow["flow_graph"] = json.loads(flow["flow_graph"])
                except (json.JSONDecodeError, TypeError):
                    flow["flow_graph"] = {}

            if flow.get("variables"):
                try:
                    flow["variables"] = json.loads(flow["variables"])
                except (json.JSONDecodeError, TypeError):
                    flow["variables"] = {}

        return flows

    def create(self, data: Dict[str, Any]) -> int:
        """
        创建新流程

        Args:
            data: 流程数据字典

        Returns:
            新创建的流程ID

        Example:
            >>> repo = FlowRepository()
            >>> flow_id = repo.create({
            ...     'game_gid': 10000147,
            ...     'flow_name': 'Test Flow',
            ...     'flow_graph': {'nodes': [], 'edges': []},
            ...     'description': 'Test description'
            ... })
        """
        with get_db() as db:
            cursor = db.cursor()

            insert_sql = f'''
                INSERT INTO "{self.table_name}" (
                    game_gid, flow_name, flow_graph, variables,
                    description, created_by, is_active,
                    created_at, updated_at, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 1)
            '''

            cursor.execute(
                insert_sql,
                (
                    data["game_gid"],
                    data["flow_name"],
                    json.dumps(data.get("flow_graph", {})),
                    json.dumps(data.get("variables", {})),
                    data.get("description", ""),
                    data.get("created_by", ""),
                    data.get("is_active", 1),
                ),
            )

            db.commit()
            return cursor.lastrowid

    def update(self, flow_id: int, data: Dict[str, Any]) -> bool:
        """
        更新流程

        Args:
            flow_id: 流程ID
            data: 更新数据字典

        Returns:
            是否更新成功

        Example:
            >>> repo = FlowRepository()
            >>> success = repo.update(1, {
            ...     'flow_name': 'Updated Flow Name',
            ...     'description': 'Updated description'
            ... })
        """
        with get_db() as db:
            cursor = db.cursor()

            update_parts = []
            params = []

            if "flow_name" in data:
                update_parts.append("flow_name = ?")
                params.append(data["flow_name"])

            if "description" in data:
                update_parts.append("description = ?")
                params.append(data["description"])

            if "flow_graph" in data:
                update_parts.append("flow_graph = ?")
                params.append(json.dumps(data["flow_graph"]))

            if "variables" in data:
                update_parts.append("variables = ?")
                params.append(json.dumps(data["variables"]))

            if "is_active" in data:
                update_parts.append("is_active = ?")
                params.append(data["is_active"])

            if update_parts:
                update_parts.append('updated_at = datetime("now")')
                params.append(flow_id)

                update_sql = f'''
                    UPDATE "{self.table_name}" SET
                    {", ".join(update_parts)}
                    WHERE id = ?
                '''

                cursor.execute(update_sql, params)
                db.commit()
                return cursor.rowcount > 0

            return False

    def delete(self, flow_id: int) -> bool:
        """
        删除流程（软删除：设置is_active=0）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Example:
            >>> repo = FlowRepository()
            >>> success = repo.delete(1)
        """
        with get_db() as db:
            cursor = db.cursor()

            # 软删除：设置is_active=0
            delete_sql = f'''
                UPDATE "{self.table_name}"
                SET is_active = 0, updated_at = datetime('now')
                WHERE id = ?
            '''
            cursor.execute(delete_sql, (flow_id,))
            db.commit()

            return cursor.rowcount > 0

    def hard_delete(self, flow_id: int) -> bool:
        """
        硬删除流程（从数据库中彻底删除）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        with get_db() as db:
            cursor = db.cursor()

            delete_sql = f'DELETE FROM "{self.table_name}" WHERE id = ?'
            cursor.execute(delete_sql, (flow_id,))
            db.commit()

            return cursor.rowcount > 0

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
