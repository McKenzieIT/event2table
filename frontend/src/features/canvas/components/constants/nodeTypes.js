/**
 * 节点类型常量定义
 * @constant
 */

export const NODE_TYPES = {
  EVENT: "event", // 事件节点 (原process改名)
  UNION_ALL: "union_all", // UNION ALL连接节点
  JOIN: "join", // JOIN连接节点
  OUTPUT: "output", // 输出节点
  FILTER: "filter", // 过滤节点
  AGGREGATE: "aggregate", // 聚合节点
};

/**
 * 节点类型配置
 * 使用字符串字面量避免TDZ错误
 */
export const NODE_CONFIG = {
  event: {
    icon: "⚙️",
    label: "事件节点",
    color: "#667eea",
    hasInput: false,
    hasOutput: true,
    editable: true,
    draggable: true,
    description: "从事件节点构建器加载的事件配置",
  },
  union_all: {
    icon: "🔗",
    label: "UNION ALL",
    color: "#f59e0b",
    hasInput: true,
    hasOutput: true,
    minInputs: 2,
    maxInputs: 10,
    description: "合并多个事件数据",
  },
  join: {
    icon: "🔀",
    label: "JOIN",
    color: "#10b981",
    hasInput: true,
    hasOutput: true,
    minInputs: 2,
    maxInputs: 2,
    description: "连接两个事件数据",
  },
  output: {
    icon: "📤",
    label: "输出",
    color: "#ef4444",
    hasInput: true,
    hasOutput: false,
    required: true,
    description: "HQL生成的终点",
  },
  filter: {
    icon: "🔍",
    label: "过滤",
    color: "#8b5cf6",
    hasInput: true,
    hasOutput: true,
    description: "根据条件过滤数据",
  },
  aggregate: {
    icon: "📊",
    label: "聚合",
    color: "#ec4899",
    hasInput: true,
    hasOutput: true,
    description: "聚合统计数据",
  },
};

/**
 * 获取单个节点配置
 * @param {string} nodeType - 节点类型
 * @returns {Object|null} 节点配置
 */
export function getNodeConfig(nodeType) {
  return NODE_CONFIG[nodeType] || null;
}
