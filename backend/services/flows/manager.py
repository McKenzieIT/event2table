#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Manager

流程管理器

提供流程的高级操作功能: 
- 加载流程
- 生成HQL
- 验证流程
"""

import logging
from typing import Any, Dict, Optional

from backend.models.entities import FlowEntity
from backend.services.flows.flow_service import FlowService

logger = logging.getLogger(__name__)


class FlowManager:
    """
    流程管理器 (精简架构)

    提供流程的高级操作功能, 使用FlowService处理业务逻辑
    """

    def __init__(self):
        """初始化流程管理器"""
        self.flow_service = FlowService()

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
        flow = self.flow_service.get_flow_by_id(flow_id)

        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 转换为字典(兼容旧代码)
        flow_dict = flow.model_dump()

        # 添加游戏名称(如果有)
        if flow.game_gid:
            game = self.flow_service.game_repo.find_by_gid(flow.game_gid)
            if game:
                flow_dict["game_name"] = game.name
            else:
                logger.warning(f"Flow {flow_id} references non-existent game_gid {flow.game_gid}")

        return flow_dict

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

        # 检查edges字段(可选)
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
            新流程ID, 失败返回None
        """
        try:
            # 加载原流程
            original_flow = self.flow_service.get_flow_by_id(flow_id)
            if not original_flow:
                raise ValueError(f"Flow {flow_id} not found")

            # 创建新流程
            new_flow = FlowEntity(
                game_gid=original_flow.game_gid,
                flow_name=new_name,
                flow_graph=original_flow.flow_graph,
                variables=original_flow.variables,
                description=f"Cloned from {original_flow.flow_name}",
                created_by=original_flow.created_by,
                is_active=True,
            )

            created_flow = self.flow_service.create_flow(new_flow)

            logger.info(f"Flow cloned: {flow_id} -> {created_flow.id} ({new_name})")

            return created_flow.id

        except Exception as e:
            logger.error(f"Failed to clone flow {flow_id}: {e}")
            return None

    def export_flow(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        导出流程数据（用于备份或迁移）

        Args:
            flow_id: 流程ID

        Returns:
            流程导出数据, 失败返回None
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
        flows = self.flow_service.get_flows_by_game_gid(game_gid)

        total_count = len(flows)
        active_count = sum(1 for f in flows if f.is_active)

        # 统计节点类型
        node_types = {}
        for flow in flows:
            nodes = flow.flow_graph.get("nodes", [])
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
