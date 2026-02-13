"""
图处理通用工具函数模块

提供图遍历、节点检测等通用算法。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-09

功能分类:
- 图构建工具
- 图遍历算法（BFS/DFS）
- 节点检测（孤立节点、环检测）

使用示例:
    >>> from backend.core.graph_utils import (
    ...     build_graph_from_edges,
    ...     find_isolated_nodes,
    ...     detect_cycles_dfs
    ... )
    >>>
    >>> # 构建图
    >>> graph = build_graph_from_edges(nodes, edges)
    >>>
    >>> # 检测孤立节点
    >>> isolated = find_isolated_nodes(nodes, edges, ignore_types=['output'])
    >>>
    >>> # 检测环
    >>> cycles = detect_cycles_dfs(graph)
"""

from typing import Dict, List, Set, Tuple, Any
from collections import deque

# ============================================================================
# 图构建工具
# ============================================================================


def build_graph_from_edges(nodes: List[Dict], edges: List[Dict]) -> Dict[str, List[str]]:
    """
    从节点和边列表构建邻接表

    Args:
        nodes: 节点列表，每个节点至少包含 'id' 字段
        edges: 边列表，每条边包含 'source' 和 'target' 字段

    Returns:
        邻接表 {node_id: [neighbor_ids]}

    Example:
        >>> nodes = [{'id': 'A'}, {'id': 'B'}]
        >>> edges = [{'source': 'A', 'target': 'B'}]
        >>> graph = build_graph_from_edges(nodes, edges)
        >>> print(graph)
        {'A': ['B'], 'B': []}
    """
    graph = {node["id"]: [] for node in nodes}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            graph.setdefault(source, []).append(target)
    return graph


# ============================================================================
# 图遍历算法
# ============================================================================


def bfs_traversal(graph: Dict[str, List[str]], start_nodes: List[str]) -> Set[str]:
    """
    广度优先搜索（BFS）遍历图

    Args:
        graph: 邻接表 {node_id: [neighbor_ids]}
        start_nodes: 起始节点列表

    Returns:
        可达节点集合

    Example:
        >>> graph = {'A': ['B', 'C'], 'B': ['D'], 'C': [], 'D': []}
        >>> reachable = bfs_traversal(graph, ['A'])
        >>> print(reachable)
        {'A', 'B', 'C', 'D'}
    """
    queue = deque(start_nodes)
    visited = set()
    reachable = set()

    while queue:
        current_id = queue.popleft()
        if current_id in visited:
            continue

        visited.add(current_id)
        reachable.add(current_id)

        for neighbor in graph.get(current_id, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return reachable


def dfs_traversal(
    graph: Dict[str, List[str]], start_node: str, visited: Optional[Set[str]] = None
) -> Tuple[Set[str], Dict[str, List[str]]]:
    """
    深度优先搜索（DFS）遍历图

    Args:
        graph: 邻接表
        start_node: 起始节点
        visited: 已访问节点集合（用于递归）

    Returns:
        Tuple[visited_nodes, paths]

    Example:
        >>> graph = {'A': ['B', 'C'], 'B': ['D'], 'C': [], 'D': []}
        >>> visited, paths = dfs_traversal(graph, 'A')
        >>> print(visited)
        {'A', 'B', 'C', 'D'}
    """
    if visited is None:
        visited = set()

    visited.add(start_node)
    paths = {start_node: []}

    for neighbor in graph.get(start_node, []):
        if neighbor not in visited:
            child_visited, child_paths = dfs_traversal(graph, neighbor, visited)
            visited.update(child_visited)
            paths.update(child_paths)
            paths[start_node].append(neighbor)

    return visited, paths


# ============================================================================
# 节点检测工具
# ============================================================================


def find_isolated_nodes(
    nodes: List[Dict], edges: List[Dict], ignore_types: Optional[List[str]] = None
) -> List[Dict]:
    """
    找出孤立节点（无法从起始节点到达的节点）

    Args:
        nodes: 节点列表
        edges: 边列表
        ignore_types: 忽略的节点类型列表（如['output']）

    Returns:
        孤立节点列表，每个节点包含 id, type, label

    Example:
        >>> isolated = find_isolated_nodes(nodes, edges, ignore_types=['output'])
        >>> print(isolated)
        [{'id': 'node-3', 'type': 'event', 'label': 'Login'}]
    """
    if not nodes:
        return []

    ignore_types = ignore_types or []

    # 构建图
    graph = build_graph_from_edges(nodes, edges)

    # 找出起始节点（没有输入的节点，除ignore_types外）
    start_nodes = [
        node["id"]
        for node in nodes
        if node.get("type") not in ignore_types
        and not any(e.get("target") == node["id"] for e in edges)
    ]

    # 如果没有起始节点，使用第一个节点
    if not start_nodes:
        start_nodes = [nodes[0]["id"]]

    # BFS遍历找出可达节点
    reachable = bfs_traversal(graph, start_nodes)

    # 找出孤立节点
    isolated = []
    for node in nodes:
        node_id = node["id"]
        if node_id not in reachable and node.get("type") not in ignore_types:
            isolated.append(
                {
                    "id": node_id,
                    "type": node.get("type"),
                    "label": node.get("data", {}).get("label", "Unknown"),
                }
            )

    return isolated


def detect_cycles_dfs(graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    使用DFS检测图中的环

    Args:
        graph: 邻接表 {node_id: [neighbor_ids]}

    Returns:
        环路径列表，每个环是一组节点ID

    Example:
        >>> graph = {'A': ['B'], 'B': ['C'], 'C': ['A']}
        >>> cycles = detect_cycles_dfs(graph)
        >>> print(cycles)
        [['A', 'B', 'C']]
    """
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node_id: str, path: List[str]) -> None:
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)

        for neighbor in graph.get(node_id, []):
            if neighbor not in visited:
                dfs(neighbor, path.copy())
            elif neighbor in rec_stack:
                # 找到环
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        rec_stack.remove(node_id)

    for node_id in graph:
        if node_id not in visited:
            dfs(node_id, [])

    return cycles


def count_node_connections(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Dict[str, int]]:
    """
    统计每个节点的连接数

    Args:
        nodes: 节点列表
        edges: 边列表

    Returns:
        {node_id: {'in': incoming_count, 'out': outgoing_count}}

    Example:
        >>> counts = count_node_connections(nodes, edges)
        >>> print(counts['node-1'])
        {'in': 1, 'out': 2}
    """
    connection_counts = {node["id"]: {"in": 0, "out": 0} for node in nodes}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            if source in connection_counts:
                connection_counts[source]["out"] += 1
            if target in connection_counts:
                connection_counts[target]["in"] += 1

    return connection_counts


def find_start_nodes(
    nodes: List[Dict], edges: List[Dict], ignore_types: Optional[List[str]] = None
) -> List[str]:
    """
    找出起始节点（没有输入边的节点）

    Args:
        nodes: 节点列表
        edges: 边列表
        ignore_types: 忽略的节点类型

    Returns:
        起始节点ID列表

    Example:
        >>> starts = find_start_nodes(nodes, edges, ignore_types=['output'])
        >>> print(starts)
        ['node-1', 'node-2']
    """
    ignore_types = ignore_types or []

    return [
        node["id"]
        for node in nodes
        if node.get("type") not in ignore_types
        and not any(e.get("target") == node["id"] for e in edges)
    ]


def find_end_nodes(
    nodes: List[Dict], edges: List[Dict], ignore_types: Optional[List[str]] = None
) -> List[str]:
    """
    找出结束节点（没有输出边的节点）

    Args:
        nodes: 节点列表
        edges: 边列表
        ignore_types: 忽略的节点类型

    Returns:
        结束节点ID列表

    Example:
        >>> ends = find_end_nodes(nodes, edges, ignore_types=['output'])
        >>> print(ends)
        ['node-3', 'node-4']
    """
    ignore_types = ignore_types or []

    # 找出所有有输出的节点
    nodes_with_output = {edge.get("source") for edge in edges if edge.get("source")}

    return [
        node["id"]
        for node in nodes
        if node.get("type") not in ignore_types and node["id"] not in nodes_with_output
    ]


# 导出列表
__all__ = [
    # 图构建
    "build_graph_from_edges",
    # 图遍历
    "bfs_traversal",
    "dfs_traversal",
    # 节点检测
    "find_isolated_nodes",
    "detect_cycles_dfs",
    "count_node_connections",
    "find_start_nodes",
    "find_end_nodes",
]
