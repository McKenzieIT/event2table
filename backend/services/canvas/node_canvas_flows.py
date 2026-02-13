#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点画布流程管理模块 - Node Canvas Flow Management

提供节点画布的流程管理功能，包括：
- 依赖图构建
- 循环依赖检测
- 拓扑排序
- HQL生成验证
"""

import json
from backend.core.logging import get_logger
from backend.core.utils import success_response, error_response

logger = get_logger(__name__)


def build_dependency_graph(nodes, connections):
    """
    构建节点依赖图

    Args:
        nodes (list): 节点列表 [{'id': 'n1', 'type': 'event_source', ...}, ...]
        connections (list): 连接列表 [{'source': 'n1', 'target': 'n2'}, ...]

    Returns:
        dict: 依赖图 {node_id: {dependencies: [], dependents: [], node: {}}}
    """
    graph = {}

    # 初始化所有节点
    for node in nodes:
        graph[node["id"]] = {
            "dependencies": [],  # 依赖的节点（输入）
            "dependents": [],  # 依赖此节点的节点（输出）
            "node": node,
        }

    # 根据连接构建依赖关系
    for conn in connections:
        source = conn.get("source")
        target = conn.get("target")

        if source in graph and target in graph:
            # target 依赖 source
            graph[target]["dependencies"].append(source)
            # source 被 target 依赖
            graph[source]["dependents"].append(target)

    logger.debug(f"Dependency graph built: {len(graph)} nodes, {len(connections)} connections")
    return graph


def detect_cycles(graph):
    """
    检测循环依赖（DFS算法）

    Args:
        graph (dict): 依赖图

    Returns:
        dict: {hasCycles: bool, cycles: [[...]]}
    """
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node_id, path=[]):
        visited.add(node_id)
        recursion_stack.add(node_id)
        path = path + [node_id]

        for dep_id in graph[node_id]["dependencies"]:
            if dep_id not in visited:
                result = dfs(dep_id, path)
                if result and len(result) > 0:
                    return result
            elif dep_id in recursion_stack:
                # 发现循环
                cycle_start = path.index(dep_id)
                cycle = path[cycle_start:] + [dep_id]
                return cycle

        recursion_stack.remove(node_id)
        return None

    for node_id in graph:
        if node_id not in visited:
            cycle = dfs(node_id)
            if cycle:
                cycles.append(cycle)

    has_cycles = len(cycles) > 0

    if has_cycles:
        logger.warning(f"Cycles detected: {len(cycles)} cycles")
        for i, cycle in enumerate(cycles):
            logger.warning(f'  Cycle {i+1}: {" -> ".join(cycle)}')
    else:
        logger.debug("No cycles detected")

    return {"hasCycles": has_cycles, "cycles": cycles}


def topological_sort(graph):
    """
    拓扑排序（Kahn算法）

    Args:
        graph (dict): 依赖图

    Returns:
        list: 拓扑排序后的节点ID列表

    Raises:
        ValueError: 如果图中存在循环
    """
    in_degree = {}
    queue = []
    result = []

    # 计算入度
    for node_id in graph:
        in_degree[node_id] = len(graph[node_id]["dependencies"])
        if in_degree[node_id] == 0:
            queue.append(node_id)

    # 处理队列
    while queue:
        node_id = queue.pop(0)
        result.append(node_id)

        for dependent_id in graph[node_id]["dependents"]:
            in_degree[dependent_id] -= 1
            if in_degree[dependent_id] == 0:
                queue.append(dependent_id)

    if len(result) != len(graph):
        raise ValueError("Graph has a cycle, topological sort failed")

    logger.debug(f'Topological sort: {" -> ".join(result)}')
    return result


def validate_flow_graph(graph_data):
    """
    验证流程图结构

    Args:
        graph_data (dict): 流程图数据
            {
                'nodes': [...],
                'connections': [...]
            }

    Returns:
        dict: {
            'valid': bool,
            'execution_order': list or None,
            'errors': list or None
        }
    """
    nodes = graph_data.get("nodes", [])
    connections = graph_data.get("connections", [])

    # 基本验证
    if not nodes:
        return {"valid": False, "execution_order": None, "errors": ["Flow graph has no nodes"]}

    # 检查是否有输出节点
    output_nodes = [n for n in nodes if n.get("type") == "output"]
    if not output_nodes:
        return {
            "valid": False,
            "execution_order": None,
            "errors": ["Flow must have at least one output node"],
        }

    # 构建依赖图
    graph = build_dependency_graph(nodes, connections)

    # 检测循环依赖
    cycle_result = detect_cycles(graph)
    if cycle_result["hasCycles"]:
        cycle_strs = [" -> ".join(cycle) for cycle in cycle_result["cycles"]]
        return {
            "valid": False,
            "execution_order": None,
            "errors": [f"Cycle detected: {cycle_str}" for cycle_str in cycle_strs],
        }

    # 拓扑排序
    try:
        execution_order = topological_sort(graph)
    except ValueError as e:
        return {"valid": False, "execution_order": None, "errors": [str(e)]}

    logger.info(f"Flow validation successful: {len(execution_order)} nodes in order")

    return {"valid": True, "execution_order": execution_order, "errors": None}


def prepare_flow_for_generation(graph_data):
    """
    准备流程图用于HQL生成

    Args:
        graph_data (dict): 流程图数据

    Returns:
        dict: 生成结果 {
            'success': bool,
            'execution_order': list,
            'node_count': int,
            'connection_count': int,
            'error': str or None
        }
    """
    try:
        # 验证流程图
        validation = validate_flow_graph(graph_data)

        if not validation["valid"]:
            return {
                "success": False,
                "execution_order": None,
                "node_count": 0,
                "connection_count": 0,
                "error": "; ".join(validation["errors"]),
            }

        nodes = graph_data.get("nodes", [])
        connections = graph_data.get("connections", [])

        return {
            "success": True,
            "execution_order": validation["execution_order"],
            "node_count": len(nodes),
            "connection_count": len(connections),
            "error": None,
        }

    except Exception as e:
        logger.exception(f"Error preparing flow for generation: {e}")
        return {
            "success": False,
            "execution_order": None,
            "node_count": 0,
            "connection_count": 0,
            "error": str(e),
        }


logger.info("Node canvas flow management module loaded")
