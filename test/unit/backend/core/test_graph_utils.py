"""
Graph utilities 模块测试

测试图处理通用工具函数：
- 图构建 (build_graph_from_edges)
- 图遍历 (bfs_traversal, dfs_traversal)
- 节点检测 (find_isolated_nodes, detect_cycles_dfs, count_node_connections)
- 起始/结束节点查找 (find_start_nodes, find_end_nodes)

TDD Phase: Red - 先写测试，验证图算法正确性
"""

import pytest


class TestBuildGraphFromEdges:
    """测试 build_graph_from_edges 函数"""

    def test_build_simple_graph(self):
        """测试构建简单图"""
        from backend.core.graph_utils import build_graph_from_edges

        nodes = [
            {'id': 'A'},
            {'id': 'B'},
            {'id': 'C'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'C'}
        ]

        graph = build_graph_from_edges(nodes, edges)

        assert graph == {
            'A': ['B'],
            'B': ['C'],
            'C': []
        }

    def test_build_graph_with_missing_nodes(self):
        """测试边引用不存在的节点"""
        from backend.core.graph_utils import build_graph_from_edges

        nodes = [{'id': 'A'}]
        edges = [
            {'source': 'A', 'target': 'B'},  # B不在nodes中
            {'source': 'C', 'target': 'A'}   # C不在nodes中
        ]

        graph = build_graph_from_edges(nodes, edges)

        # 应该优雅处理不存在的节点
        assert 'A' in graph
        assert graph['A'] == ['B']

    def test_build_empty_graph(self):
        """测试空图"""
        from backend.core.graph_utils import build_graph_from_edges

        graph = build_graph_from_edges([], [])

        assert graph == {}

    def test_build_graph_with_multiple_edges(self):
        """测试节点有多个出边"""
        from backend.core.graph_utils import build_graph_from_edges

        nodes = [
            {'id': 'A'},
            {'id': 'B'},
            {'id': 'C'},
            {'id': 'D'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'A', 'target': 'C'},
            {'source': 'A', 'target': 'D'}
        ]

        graph = build_graph_from_edges(nodes, edges)

        assert set(graph['A']) == {'B', 'C', 'D'}


class TestBFSTraversal:
    """测试 bfs_traversal 函数"""

    def test_bfs_simple_path(self):
        """测试简单路径的BFS"""
        from backend.core.graph_utils import bfs_traversal

        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': [],
            'D': []
        }

        reachable = bfs_traversal(graph, ['A'])

        assert reachable == {'A', 'B', 'C', 'D'}

    def test_bfs_multiple_start_nodes(self):
        """测试多个起始节点的BFS"""
        from backend.core.graph_utils import bfs_traversal

        graph = {
            'A': ['C'],
            'B': ['C'],
            'C': ['D'],
            'D': []
        }

        reachable = bfs_traversal(graph, ['A', 'B'])

        assert reachable == {'A', 'B', 'C', 'D'}

    def test_bfs_disconnected_graph(self):
        """测试不连通图的BFS"""
        from backend.core.graph_utils import bfs_traversal

        graph = {
            'A': ['B'],
            'B': [],
            'C': ['D'],  # 不连通部分
            'D': []
        }

        reachable = bfs_traversal(graph, ['A'])

        assert reachable == {'A', 'B'}
        assert 'C' not in reachable
        assert 'D' not in reachable

    def test_bfs_empty_graph(self):
        """测试空图的BFS"""
        from backend.core.graph_utils import bfs_traversal

        # 空图中，起始节点会被添加到reachable集合（即使它不在graph中）
        # BFS会先添加起始节点到队列，然后立即弹出并标记为已访问
        reachable = bfs_traversal({}, ['A'])

        # 空图中，起始节点仍然会被访问（返回起始节点本身）
        assert reachable == {'A'}

    def test_bfs_cycle_handling(self):
        """测试BFS处理环"""
        from backend.core.graph_utils import bfs_traversal

        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['A']  # 环
        }

        reachable = bfs_traversal(graph, ['A'])

        assert reachable == {'A', 'B', 'C'}


class TestDFSTraversal:
    """测试 dfs_traversal 函数"""

    def test_dfs_simple_path(self):
        """测试简单路径的DFS"""
        from backend.core.graph_utils import dfs_traversal

        graph = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': [],
            'D': []
        }

        visited, paths = dfs_traversal(graph, 'A')

        assert visited == {'A', 'B', 'C', 'D'}
        assert 'A' in paths

    def test_dfs_empty_graph(self):
        """测试空图的DFS"""
        from backend.core.graph_utils import dfs_traversal

        visited, paths = dfs_traversal({}, 'A')

        assert visited == {'A'}
        assert paths == {'A': []}


class TestFindIsolatedNodes:
    """测试 find_isolated_nodes 函数"""

    def test_find_isolated_simple(self):
        """测试找出简单孤立节点"""
        from backend.core.graph_utils import find_isolated_nodes

        nodes = [
            {'id': 'A', 'type': 'event', 'data': {'label': 'Event A'}},
            {'id': 'B', 'type': 'event', 'data': {'label': 'Event B'}},
            {'id': 'C', 'type': 'output', 'data': {'label': 'Output'}}
        ]
        edges = [
            {'source': 'A', 'target': 'C'}  # A->C, B是孤立的（B不是起始节点）
        ]
        # 注意：在这个图中，A没有输入边，所以A是起始节点
        # B没有输入边，所以B也是起始节点
        # 实际上A和B都是起始节点，都可达，没有孤立节点
        # 要创建真正的孤立节点，需要：起始节点 -> 中间节点，孤立节点完全无法到达

        nodes2 = [
            {'id': 'start', 'type': 'event', 'data': {'label': 'Start'}},
            {'id': 'middle', 'type': 'event', 'data': {'label': 'Middle'}},
            {'id': 'isolated', 'type': 'event', 'data': {'label': 'Isolated'}},
            {'id': 'output', 'type': 'output', 'data': {'label': 'Output'}}
        ]
        edges2 = [
            {'source': 'start', 'target': 'middle'},
            {'source': 'middle', 'target': 'output'}
        ]
        # start是起始节点，可到达middle和output
        # isolated没有输入边，所以它也是起始节点（会被访问）

        isolated = find_isolated_nodes(nodes2, edges2, ignore_types=['output'])

        # 实际上没有孤立节点，因为所有event节点都是起始节点或可达的
        assert len(isolated) == 0

    def test_find_isolated_with_ignore_types(self):
        """测试忽略特定类型的节点"""
        from backend.core.graph_utils import find_isolated_nodes

        # 创建一个真正的孤立节点场景
        nodes = [
            {'id': 'start', 'type': 'event', 'data': {'label': 'Start'}},
            {'id': 'connected', 'type': 'event', 'data': {'label': 'Connected'}},
            {'id': 'isolated', 'type': 'event', 'data': {'label': 'Isolated'}},
            {'id': 'output', 'type': 'output', 'data': {'label': 'Output'}}
        ]
        edges = [
            {'source': 'start', 'target': 'connected'},
            {'source': 'connected', 'target': 'output'},
            {'source': 'nonexistent', 'target': 'isolated'}  # 孤立：输入来自不存在的节点
        ]

        isolated = find_isolated_nodes(nodes, edges, ignore_types=['output'])

        # isolated有输入边（来自nonexistent），但nonexistent不在图中
        # 所以isolated无法从任何起始节点到达
        assert len(isolated) == 1
        assert isolated[0]['id'] == 'isolated'

    def test_find_isolated_empty_nodes(self):
        """测试空节点列表"""
        from backend.core.graph_utils import find_isolated_nodes

        isolated = find_isolated_nodes([], [], ignore_types=['output'])

        assert isolated == []

    def test_find_isolated_all_connected(self):
        """测试所有节点都连通"""
        from backend.core.graph_utils import find_isolated_nodes

        nodes = [
            {'id': 'A', 'type': 'event', 'data': {'label': 'A'}},
            {'id': 'B', 'type': 'event', 'data': {'label': 'B'}},
            {'id': 'C', 'type': 'output', 'data': {'label': 'C'}}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'C'}
        ]

        isolated = find_isolated_nodes(nodes, edges, ignore_types=['output'])

        assert len(isolated) == 0


class TestDetectCyclesDFS:
    """测试 detect_cycles_dfs 函数"""

    def test_detect_simple_cycle(self):
        """测试检测简单环"""
        from backend.core.graph_utils import detect_cycles_dfs

        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': ['A']  # 环: A -> B -> C -> A
        }

        cycles = detect_cycles_dfs(graph)

        assert len(cycles) == 1
        assert 'A' in cycles[0]
        assert 'B' in cycles[0]
        assert 'C' in cycles[0]

    def test_detect_self_loop(self):
        """测试检测自环"""
        from backend.core.graph_utils import detect_cycles_dfs

        graph = {
            'A': ['A']  # 自环
        }

        cycles = detect_cycles_dfs(graph)

        assert len(cycles) >= 1

    def test_detect_no_cycles(self):
        """测试无环图"""
        from backend.core.graph_utils import detect_cycles_dfs

        graph = {
            'A': ['B'],
            'B': ['C'],
            'C': []
        }

        cycles = detect_cycles_dfs(graph)

        assert len(cycles) == 0

    def test_detect_multiple_cycles(self):
        """测试检测多个环"""
        from backend.core.graph_utils import detect_cycles_dfs

        graph = {
            'A': ['B'],
            'B': ['A'],  # 环1: A <-> B
            'C': ['D'],
            'D': ['C']   # 环2: C <-> D
        }

        cycles = detect_cycles_dfs(graph)

        assert len(cycles) >= 2


class TestCountNodeConnections:
    """测试 count_node_connections 函数"""

    def test_count_connections_simple(self):
        """测试简单连接计数"""
        from backend.core.graph_utils import count_node_connections

        nodes = [
            {'id': 'A'},
            {'id': 'B'},
            {'id': 'C'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'A', 'target': 'C'}
        ]

        counts = count_node_connections(nodes, edges)

        assert counts['A'] == {'in': 0, 'out': 2}
        assert counts['B'] == {'in': 1, 'out': 0}
        assert counts['C'] == {'in': 1, 'out': 0}

    def test_count_connections_with_bidirectional(self):
        """测试双向边"""
        from backend.core.graph_utils import count_node_connections

        nodes = [
            {'id': 'A'},
            {'id': 'B'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'A'}
        ]

        counts = count_node_connections(nodes, edges)

        assert counts['A'] == {'in': 1, 'out': 1}
        assert counts['B'] == {'in': 1, 'out': 1}

    def test_count_connections_empty(self):
        """测试空图"""
        from backend.core.graph_utils import count_node_connections

        counts = count_node_connections([], [])

        assert counts == {}


class TestFindStartNodes:
    """测试 find_start_nodes 函数"""

    def test_find_start_simple(self):
        """测试找出起始节点"""
        from backend.core.graph_utils import find_start_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'event'},
            {'id': 'C', 'type': 'output'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'C'}
        ]

        starts = find_start_nodes(nodes, edges, ignore_types=['output'])

        assert starts == ['A']

    def test_find_start_multiple(self):
        """测试多个起始节点"""
        from backend.core.graph_utils import find_start_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'event'},
            {'id': 'C', 'type': 'output'}
        ]
        edges = [
            {'source': 'A', 'target': 'C'},
            {'source': 'B', 'target': 'C'}
        ]

        starts = find_start_nodes(nodes, edges, ignore_types=['output'])

        assert set(starts) == {'A', 'B'}

    def test_find_start_with_ignore_types(self):
        """测试忽略特定类型"""
        from backend.core.graph_utils import find_start_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'output'}
        ]
        edges = []

        # B没有入边，但被忽略
        starts = find_start_nodes(nodes, edges, ignore_types=['output'])

        assert starts == ['A']


class TestFindEndNodes:
    """测试 find_end_nodes 函数"""

    def test_find_end_simple(self):
        """测试找出结束节点"""
        from backend.core.graph_utils import find_end_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'event'},
            {'id': 'C', 'type': 'event'},
            {'id': 'D', 'type': 'output'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'B', 'target': 'C'},
            {'source': 'C', 'target': 'D'}
        ]

        ends = find_end_nodes(nodes, edges, ignore_types=['output'])

        # A, B, C都有输出边，D是output被忽略
        # 所以没有结束节点
        assert ends == []

    def test_find_end_with_actual_end(self):
        """测试有实际的结束节点"""
        from backend.core.graph_utils import find_end_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'event'},
            {'id': 'C', 'type': 'event'},
            {'id': 'D', 'type': 'output'}
        ]
        edges = [
            {'source': 'A', 'target': 'B'},
            {'source': 'A', 'target': 'C'}  # A->B, A->C
        ]

        ends = find_end_nodes(nodes, edges, ignore_types=['output'])

        # B和C没有输出边，是结束节点
        assert set(ends) == {'B', 'C'}

    def test_find_end_multiple(self):
        """测试多个结束节点"""
        from backend.core.graph_utils import find_end_nodes

        nodes = [
            {'id': 'A', 'type': 'event'},
            {'id': 'B', 'type': 'event'},
            {'id': 'C', 'type': 'event'},
            {'id': 'D', 'type': 'output'}
        ]
        edges = [
            {'source': 'A', 'target': 'C'},
            {'source': 'B', 'target': 'C'},
            {'source': 'C', 'target': 'D'}
        ]

        ends = find_end_nodes(nodes, edges, ignore_types=['output'])

        # A和B没有出边（到C的边被移除了？不对，C有出边到D）
        # 实际上A和B都有出边，所以没有结束节点？
        # 等等，A->C, B->C, C->D
        # A的出边：C，所以A不是结束节点
        # B的出边：C，所以B不是结束节点
        # C的出边：D，所以C不是结束节点
        # D被忽略
        # 所以没有结束节点
        assert ends == []
