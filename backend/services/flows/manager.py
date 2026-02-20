#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Manager

流程管理器

提供流程的高级操作功能：
- 加载流程
- 生成HQL
- 验证流程
"""

import logging
from typing import Dict, Any, Optional
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.games import GameRepository

logger = logging.getLogger(__name__)


class FlowManager:
    """
    流程管理器

    提供流程的高级操作功能
    """

    def __init__(self):
        """初始化流程管理器"""
        self.flow_repo = FlowRepository()
        self.game_repo = GameRepository()

    def load_flow(self, flow_id: int) -> Dict[str, Any]:
        """
        加载流程数据

        Args:
            flow_id: 流程ID

        Returns:
            流程数据字典

        Raises:
            ValueError: 当流程不存在时
        """
        flow = self.flow_repo.find_by_id(flow_id)

        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 验证游戏是否存在
        if flow.get("game_gid"):
            game = self.game_repo.find_by_gid(flow["game_gid"])
            if not game:
                logger.warning(
                    f"Flow {flow_id} references non-existent game_gid {flow['game_gid']}"
                )
            else:
                flow["game_name"] = game.get("name", "")

        return flow

    def validate_flow(self, flow_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证流程数据

        Args:
            flow_data: 流程数据字典

        Returns:
            (是否有效, 错误消息) 元组
        """
        # 检查必需字段
        if "flow_graph" not in flow_data:
            return False, "Missing flow_graph field"

        flow_graph = flow_data["flow_graph"]

        # 检查flow_graph结构
        if not isinstance(flow_graph, dict):
            return False, "flow_graph must be a dictionary"

        # 检查nodes字段
        if "nodes" not in flow_graph:
            return False, "flow_graph missing nodes field"

        nodes = flow_graph["nodes"]
        if not isinstance(nodes, list):
            return False, "flow_graph.nodes must be a list"

        # 验证每个节点
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                return False, f"Node {i} must be a dictionary"

            if "id" not in node:
                return False, f"Node {i} missing id field"

            if "type" not in node:
                return False, f"Node {i} missing type field"

        # 检查edges字段（可选）
        if "edges" in flow_graph:
            edges = flow_graph["edges"]
            if not isinstance(edges, list):
                return False, "flow_graph.edges must be a list"

            # 验证每条边
            for i, edge in enumerate(edges):
                if not isinstance(edge, dict):
                    return False, f"Edge {i} must be a dictionary"

                if "source" not in edge:
                    return False, f"Edge {i} missing source field"

                if "target" not in edge:
                    return False, f"Edge {i} missing target field"

        return True, ""

    def clone_flow(self, flow_id: int, new_name: str) -> Optional[int]:
        """
        克隆流程

        Args:
            flow_id: 原流程ID
            new_name: 新流程名称

        Returns:
            新流程ID，失败返回None
        """
        try:
            # 加载原流程
            original_flow = self.load_flow(flow_id)

            # 创建新流程
            new_flow_data = {
                "game_gid": original_flow["game_gid"],
                "flow_name": new_name,
                "flow_graph": original_flow.get("flow_graph", {}),
                "variables": original_flow.get("variables", {}),
                "description": f"Cloned from {original_flow.get('flow_name', 'Unknown')}",
                "created_by": original_flow.get("created_by", ""),
                "is_active": True,
            }

            new_flow_id = self.flow_repo.create(new_flow_data)

            logger.info(f"Flow cloned: {flow_id} -> {new_flow_id} ({new_name})")

            return new_flow_id

        except Exception as e:
            logger.error(f"Failed to clone flow {flow_id}: {e}")
            return None

    def export_flow(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        导出流程数据（用于备份或迁移）

        Args:
            flow_id: 流程ID

        Returns:
            流程导出数据，失败返回None
        """
        try:
            flow = self.load_flow(flow_id)

            # 构造导出数据
            export_data = {
                "version": "1.0",
                "flow": flow,
                "exported_at": str(flow.get("updated_at")),
            }

            return export_data

        except Exception as e:
            logger.error(f"Failed to export flow {flow_id}: {e}")
            return None

    def get_flow_statistics(self, game_gid: int) -> Dict[str, Any]:
        """
        获取指定游戏的流程统计信息

        Args:
            game_gid: 游戏GID

        Returns:
            统计信息字典
        """
        flows = self.flow_repo.find_by_game_gid(game_gid)

        total_count = len(flows)
        active_count = sum(1 for f in flows if f.get("is_active", 0) == 1)

        # 统计节点类型
        node_types = {}
        for flow in flows:
            flow_graph = flow.get("flow_graph", {})
            nodes = flow_graph.get("nodes", [])
            for node in nodes:
                node_type = node.get("type", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1

        return {
            "total_count": total_count,
            "active_count": active_count,
            "inactive_count": total_count - active_count,
            "node_types": node_types,
        }


# 全局单例
flow_manager = FlowManager()
