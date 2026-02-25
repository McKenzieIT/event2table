/**
 * 节点数据转换工具
 * 将Flask API返回的配置转换为ReactFlow节点格式
 */

// ============================================
// Type Definitions
// ============================================

export interface Position {
  x: number;
  y: number;
}

export interface FieldConfig {
  field_name: string;
  display_name: string;
  data_type: string;
  is_required: boolean;
}

export interface EventConfig {
  id: number;
  game_gid: number;
  event_id: number;
  name_en: string;
  name_cn: string;
  event_name?: string;
  event_name_cn?: string;
  description?: string;
  base_fields?: FieldConfig[];
  filter_conditions?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface NodeData {
  label: string;
  configId: number;
  eventId: number;
  eventName: string;
  eventCnName: string;
  nameEn: string;
  nameCn: string;
  fieldCount: number;
  baseFields: FieldConfig[];
  filterConditions: Record<string, unknown>;
  description: string;
  eventConfig: EventConfig;
}

export interface ReactFlowNode {
  id: string;
  type: string;
  position: Position;
  data: NodeData;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string | null;
  targetHandle?: string | null;
}

export interface Connection {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface FlowData {
  nodes: ReactFlowNode[];
  connections: Connection[];
}

// ============================================
// Converter Functions
// ============================================

/**
 * 将事件节点配置转换为ReactFlow节点
 * @param config - 事件节点配置
 * @param position - 节点位置 {x, y}
 * @returns ReactFlow节点
 */
export function configToReactFlowNode(
  config: EventConfig,
  position: Position
): ReactFlowNode {
  const node: ReactFlowNode = {
    id: `node_${config.id}_${Date.now()}`,
    type: "event",
    position,
    data: {
      label: config.name_cn || config.event_name_cn || "事件节点",
      configId: config.id,
      eventId: config.event_id,
      eventName: config.event_name || "",
      eventCnName: config.event_name_cn || "",
      nameEn: config.name_en || "",
      nameCn: config.name_cn || "",
      fieldCount: config.base_fields ? config.base_fields.length : 0,
      baseFields: config.base_fields || [],
      filterConditions: config.filter_conditions || {},
      description: config.description || "",
      eventConfig: config,
    },
  };
  return node;
}

/**
 * 将ReactFlow节点列表转换为流程保存格式
 * @param nodes - ReactFlow节点
 * @param edges - ReactFlow边
 * @returns 流程数据
 */
export function reactFlowToFlowData(
  nodes: ReactFlowNode[],
  edges: ReactFlowEdge[]
): FlowData {
  return {
    nodes: nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: node.data,
    })),
    connections: edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle,
      targetHandle: edge.targetHandle,
    })),
  };
}

/**
 * 将流程数据转换为ReactFlow格式
 * @param flowData - 流程数据
 * @returns {nodes, edges}
 */
export function flowDataToReactFlow(flowData: FlowData): {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
} {
  return {
    nodes: (flowData.nodes || []) as ReactFlowNode[],
    edges: (flowData.connections || []) as ReactFlowEdge[],
  };
}
