/**
 * ReactFlow节点执行引擎
 * 负责DAG构建、拓扑排序、节点执行
 */
import { HQLGenerators } from "./hqlGenerators.js";

export class ReactNodeExecutor {
  /**
   * 构建依赖图（DAG）
   */
  static buildDependencyGraph(nodes, edges) {
    const graph = {};
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

  /**
   * 检测循环依赖
   */
  static detectCycles(graph) {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];
    const dfs = (nodeId, path = []) => {
      visited.add(nodeId);
      recursionStack.add(nodeId);
      path.push(nodeId);
      for (const depId of graph[nodeId].dependencies) {
        if (!visited.has(depId)) {
          const result = dfs(depId, [...path]);
          if (result.hasCycle) return result;
        } else if (recursionStack.has(depId)) {
          const cycleStart = path.indexOf(depId);
          const cycle = [...path.slice(cycleStart), depId];
          return { hasCycle: true, cycle };
        }
      }
      recursionStack.delete(nodeId);
      return { hasCycle: false };
    };
    for (const nodeId of Object.keys(graph)) {
      if (!visited.has(nodeId)) {
        const result = dfs(nodeId);
        if (result.hasCycle) cycles.push(result.cycle);
      }
    }
    return { hasCycles: cycles.length > 0, cycles };
  }

  /**
   * 拓扑排序（Kahn算法）
   */
  static topologicalSort(graph) {
    const inDegree = {};
    const queue = [];
    const result = [];
    Object.keys(graph).forEach((nodeId) => {
      inDegree[nodeId] = graph[nodeId].dependencies.length;
      if (inDegree[nodeId] === 0) queue.push(nodeId);
    });
    while (queue.length > 0) {
      const nodeId = queue.shift();
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

  /**
   * 执行单个节点
   * @param {Object} node - ReactFlow节点
   * @param {Object} nodeOutputs - 已执行节点的输出
   * @param {Object} graph - 依赖图
   * @param {Object} gameData - 游戏数据
   * @returns {Object} {success: boolean, output?: Object, error?: string}
   */
  static executeNode(node, nodeOutputs, graph, gameData) {
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
        error: error.message,
      };
    }
  }

  /**
   * 获取节点的输入值
   * @param {Object} node - 节点
   * @param {Object} nodeOutputs - 节点输出
   * @param {Object} graph - 依赖图
   * @returns {Object} 输入值映射
   */
  static getInputValues(node, nodeOutputs, graph) {
    const inputs = {};
    if (graph[node.id] && graph[node.id].dependencies) {
      graph[node.id].dependencies.forEach((depId) => {
        if (nodeOutputs[depId]) {
          inputs[depId] = nodeOutputs[depId];
        }
      });
    }
    return inputs;
  }

  /**
   * 执行事件节点
   */
  static executeEventNode(node, gameData) {
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
        event_id: data.eventConfig.event_id,
        event_name: data.eventConfig.event_name,
        hql: hql,
      },
    };
  }

  /**
   * 执行UNION ALL节点
   */
  static executeUnionAll(node, nodeOutputs, graph) {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSources = Object.values(inputs);

    if (inputSources.length < 2) {
      return {
        success: false,
        error: "UNION ALL节点至少需要2个输入",
      };
    }

    const hql = HQLGenerators.generateUnionAllHQL(inputSources);

    return {
      success: true,
      output: {
        type: "union_all",
        input_count: inputSources.length,
        hql: hql,
      },
    };
  }

  /**
   * 执行JOIN节点
   */
  static executeJoin(node, nodeOutputs, graph) {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputList = Object.values(inputs);

    if (inputList.length !== 2) {
      return {
        success: false,
        error: "JOIN节点需要恰好2个输入",
      };
    }

    const config = node.data.config || {};
    if (!config.conditions || config.conditions.length === 0) {
      return {
        success: false,
        error: "JOIN节点缺少连接条件",
      };
    }

    const hql = HQLGenerators.generateJoinHQL(
      config,
      inputList[0],
      inputList[1],
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

  /**
   * 执行过滤节点
   */
  static executeFilter(node, nodeOutputs, graph) {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "过滤节点需要1个输入",
      };
    }

    const config = node.data.config || {};
    const hql = HQLGenerators.generateFilterHQL(config, inputSource);

    return {
      success: true,
      output: {
        type: "filter",
        hql: hql,
      },
    };
  }

  /**
   * 执行聚合节点
   */
  static executeAggregate(node, nodeOutputs, graph) {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "聚合节点需要1个输入",
      };
    }

    const config = node.data.config || {};
    const hql = HQLGenerators.generateAggregateHQL(config, inputSource);

    return {
      success: true,
      output: {
        type: "aggregate",
        hql: hql,
      },
    };
  }

  /**
   * 执行输出节点
   */
  static executeOutput(node, nodeOutputs, graph, gameData) {
    const inputs = this.getInputValues(node, nodeOutputs, graph);
    const inputSource = Object.values(inputs)[0];

    if (!inputSource) {
      return {
        success: false,
        error: "输出节点需要1个输入",
      };
    }

    const config = node.data.config || {};
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

  /**
   * 执行完整的节点流程
   * @param {Array} nodes - ReactFlow节点数组
   * @param {Array} edges - ReactFlow边数组
   * @param {Object} gameData - 游戏数据
   * @returns {Object} 执行结果
   */
  static executePipeline(nodes, edges, gameData) {
    try {
      // 1. 构建依赖图
      const graph = this.buildDependencyGraph(nodes, edges);

      // 2. 检测循环依赖
      const cycleCheck = this.detectCycles(graph);
      if (cycleCheck.hasCycles) {
        return {
          success: false,
          error: "检测到循环依赖",
          cycles: cycleCheck.cycles,
        };
      }

      // 3. 拓扑排序
      const executionOrder = this.topologicalSort(graph);

      // 4. 按序执行节点
      const nodeOutputs = {};
      const errors = [];

      for (const nodeId of executionOrder) {
        const node = nodes.find((n) => n.id === nodeId);
        const result = this.executeNode(node, nodeOutputs, graph, gameData);

        if (result.success) {
          nodeOutputs[nodeId] = result.output;
        } else {
          errors.push({ nodeId, error: result.error });
        }
      }

      // 5. 生成最终HQL
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
        error: error.message,
        stack: error.stack,
      };
    }
  }
}
