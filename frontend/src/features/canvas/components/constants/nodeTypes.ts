/**
 * 节点类型常量定义
 */

export const NODE_TYPES = {
  EVENT: "event",
  UNION_ALL: "union_all",
  JOIN: "join",
  OUTPUT: "output",
  FILTER: "filter",
  AGGREGATE: "aggregate",
} as const;

export type NodeTypeKey = keyof typeof NODE_TYPES;
export type NodeTypeValue = typeof NODE_TYPES[NodeTypeKey];

interface NodeConfig {
  icon: string;
  label: string;
  color: string;
  hasInput: boolean;
  hasOutput: boolean;
  minInputs?: number;
  maxInputs?: number;
  editable?: boolean;
  draggable?: boolean;
  required?: boolean;
  description: string;
}

export const NODE_CONFIG: Record<string, NodeConfig> = {
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

export function getNodeConfig(nodeType: string): NodeConfig | null {
  return NODE_CONFIG[nodeType] || null;
}
