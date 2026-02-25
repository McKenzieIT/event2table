/**
 * ReactFlow节点执行引擎
 * 负责DAG构建、拓扑排序、节点执行
 */

import { HQLGenerators, GameData, EventConfig, JoinConfig, FilterConfig, AggregateConfig, OutputConfig, InputSource } from "./hqlGenerators";

export interface NodeData {
  eventConfig?: EventConfig;
  config?: JoinConfig | FilterConfig | AggregateConfig | OutputConfig;
  label?: string;
  [key: string]: unknown;
}

export interface ReactFlowNode {
  id: string;
  type: string;
  data: NodeData;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
}

interface GraphNode {
  dependencies: string[];
  dependents: string[];
  node: ReactFlowNode;
}

interface Graph {
  [nodeId: string]: GraphNode;
}

interface CycleDetectionResult {
  hasCycle: boolean;
  cycle?: string[];
}

interface CycleCheckResult {
  hasCycles: boolean;
  cycles: string[][];
}

interface ExecutionResult {
  success: boolean;
  output?: {
    type: string;
    [key: string]: unknown;
  };
  error?: string;
}

interface PipelineResult {
  success: boolean;
  executionOrder: string[];
  nodeOutputs: Record<string, { type: string; hql: string }>;
  final_hql?: string;
  errors: { nodeId: string; error: string }[];
  cycles?: string[][];
  error?: string;
  stack?: string;
}

export class ReactNodeExecutor {
  static buildDependencyGraph(nodes: ReactFlowNode[], edges: ReactFlowEdge[]): Graph {
    const graph: Graph = {};
    nodes.forEach((node) => {
      graph[node.id] = {
        dependencies: [],
        dependents: [],
        node,
      };
    });
    edges.forEach((edge) => {
      const { source, target } = edge;
      if (graph[source] && graph[target]) {
        graph[target].dependencies.push(source);
        graph[source].dependents.push(target);
      }
    });
    return graph;
  }

  static detectCycles(graph: Graph): CycleCheckResult {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const cycles: string[][] = [];

    const dfs = (nodeId: string, path: string[]): CycleDetectionResult => {
      visited.add(nodeId);
      recursionStack.add(nodeId);
      path.push(nodeId);

      const nodeGraph = graph[nodeId];
      if (nodeGraph && nodeGraph.dependencies) {
        for (const depId of nodeGraph.dependencies) {
          if (!visited.has(depId)) {
            const result = dfs(depId, [...path]);
            if (result.hasCycle) return result;
          } else if (recursionStack.has(depId)) {
            const cycleStart = path.indexOf(depId);
            const cycle = [...path.slice(cycleStart), depId];
            return { hasCycle: true, cycle };
          }
        }
      }

      recursionStack.delete(nodeId);
      return { hasCycle: false };
    };

    for (const nodeId of Object.keys(graph)) {
      if (!visited.has(nodeId)) {
        const result = dfs(nodeId);
        if (result.hasCycle && result.cycle) {
          cycles.push(result.cycle);
        }
      }
    }
    return { hasCycles: cycles.length > 0, cycles };
  }

  static topologicalSort(graph: Graph): string[] {
    const inDegree: Record<string, number> = {};
    const queue: string[] = [];
    const result: string[] = [];

    Object.keys(graph).forEach((nodeId) => {
      inDegree[nodeId] = graph[nodeId].dependencies.length;
      if (inDegree[nodeId] === 0) queue.push(nodeId);
    });

    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      result.push(nodeId);

      graph[nodeId].dependents.forEach((dependentId) => {
        inDegree[dependentId]--;
        if (inDegree[dependentId] === 0) {
          queue.push(dependentId);
        }
      });
    }
    return result;
  }

  static executeNode(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph,
    gameData: GameData
  ): ExecutionResult {
    const { type, data } = node;

    try {
      switch (type) {
        case "event":
          return this.executeEventNode(node, gameData);

        case "union_all":
          return this.executeUnionAll(node, nodeOutputs, graph);

        case "join":
          return this.executeJoin(node, nodeOutputs, graph);

        case "filter":
          return this.executeFilter(node, nodeOutputs, graph);

        case "aggregate":
          return this.executeAggregate(node, nodeOutputs, graph);

        case "output":
          return this.executeOutput(node, nodeOutputs, graph, gameData);

        default:
          return {
            success: false,
            error: `未知节点类型: ${type}`,
          };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  static getInputValues(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph
  ): Record<string, { type: string; hql: string }> {
    const inputs: Record<string, { type: string; hql: string }> = {};
    if (graph[node.id] && graph[node.id].dependencies) {
      graph[node.id].dependencies.forEach((depId) => {
        if (nodeOutputs[depId]) {
          inputs[depId] = nodeOutputs[depId];
        }
      });
    }
    return inputs;
  }

  static executeEventNode(node: ReactFlowNode, gameData: GameData): ExecutionResult {
    const { data } = node;

    if (!data.eventConfig) {
      return {
        success: false,
        error: "事件节点缺少eventConfig",
      };
    }

    const hql = HQLGenerators.generateEventHQL(data.eventConfig, gameData);

    return {
      success: true,
      output: {
        type: "event",
        event_id: data.eventConfig.event_name,
        event_name: data.eventConfig.event_name,
        hql: hql,
      },
    };
  }

  static executeUnionAll(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph
  ): ExecutionResult {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSources = Object.values(inputs);

    if (inputSources.length < 2) {
      return {
        success: false,
        error: "UNION ALL节点至少需要2个输入",
      };
    }

    const hql = HQLGenerators.generateUnionAllHQL(inputSources as InputSource[]);

    return {
      success: true,
      output: {
        type: "union_all",
        input_count: inputSources.length,
        hql: hql,
      },
    };
  }

  static executeJoin(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph
  ): ExecutionResult {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputList = Object.values(inputs);

    if (inputList.length !== 2) {
      return {
        success: false,
        error: "JOIN节点需要恰好2个输入",
      };
    }

    const config = (node.data.config || {}) as JoinConfig;
    if (!config.conditions || config.conditions.length === 0) {
      return {
        success: false,
        error: "JOIN节点缺少连接条件",
      };
    }

    const hql = HQLGenerators.generateJoinHQL(
      config,
      inputList[0],
      inputList[1]
    );

    return {
      success: true,
      output: {
        type: "join",
        join_type: config.join_type || "INNER",
        hql: hql,
      },
    };
  }

  static executeFilter(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph
  ): ExecutionResult {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "过滤节点需要1个输入",
      };
    }

    const config = (node.data.config || {}) as FilterConfig;
    const hql = HQLGenerators.generateFilterHQL(config, inputSource);

    return {
      success: true,
      output: {
        type: "filter",
        hql: hql,
      },
    };
  }

  static executeAggregate(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph
  ): ExecutionResult {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "聚合节点需要1个输入",
      };
    }

    const config = (node.data.config || {}) as AggregateConfig;
    const hql = HQLGenerators.generateAggregateHQL(config, inputSource);

    return {
      success: true,
      output: {
        type: "aggregate",
        hql: hql,
      },
    };
  }

  static executeOutput(
    node: ReactFlowNode,
    nodeOutputs: Record<string, { type: string; hql: string }>,
    graph: Graph,
    gameData: GameData
  ): ExecutionResult {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "输出节点需要1个输入",
      };
    }

    const config = (node.data.config || {}) as OutputConfig;
    if (!config.view_name) {
      return {
        success: false,
        error: "输出节点缺少view_name",
      };
    }

    const hql = HQLGenerators.generateOutputHQL(config, inputSource, gameData);

    return {
      success: true,
      output: {
        type: "output",
        view_name: config.view_name,
        hql: hql,
      },
    };
  }

  static executePipeline(
    nodes: ReactFlowNode[],
    edges: ReactFlowEdge[],
    gameData: GameData
  ): PipelineResult {
    try {
      const graph = this.buildDependencyGraph(nodes, edges);

      const cycleCheck = this.detectCycles(graph);
      if (cycleCheck.hasCycles) {
        return {
          success: false,
          error: "检测到循环依赖",
          cycles: cycleCheck.cycles,
          executionOrder: [],
          nodeOutputs: {},
          errors: [],
        };
      }

      const executionOrder = this.topologicalSort(graph);

      const nodeOutputs: Record<string, { type: string; hql: string }> = {};
      const errors: { nodeId: string; error: string }[] = [];

      for (const nodeId of executionOrder) {
        const node = nodes.find((n) => n.id === nodeId);
        if (!node) continue;

        const result = this.executeNode(node, nodeOutputs, graph, gameData);

        if (result.success && result.output) {
          nodeOutputs[nodeId] = result.output as { type: string; hql: string };
        } else if (result.error) {
          errors.push({ nodeId, error: result.error });
        }
      }

      const finalOutput = executionOrder[executionOrder.length - 1];
      const finalHQL = nodeOutputs[finalOutput]?.hql;

      return {
        success: errors.length === 0,
        executionOrder,
        nodeOutputs,
        final_hql: finalHQL,
        errors,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        executionOrder: [],
        nodeOutputs: {},
        errors: [],
      };
    }
  }
}
