/**
 * 节点数据转换工具
 * 将Flask API返回的配置转换为ReactFlow节点格式
 */

/**
 * 将事件节点配置转换为ReactFlow节点
 * @param {Object} config - 事件节点配置
 * @param {Object} position - 节点位置 {x, y}
 * @returns {Object} ReactFlow节点
 */
export function configToReactFlowNode(config, position) {
  console.log(
    "[nodeConverter] Creating node with type: event, configId:",
    config.id,
  );
  const node = {
    id: `node_${config.id}_${Date.now()}`,
    type: "event", // Use 'event' type to match EventNode component
    position,
    data: {
      label: config.name_cn || config.event_name_cn || "事件节点",
      configId: config.id,
      eventId: config.event_id,
      eventName: config.event_name,
      eventCnName: config.event_name_cn,
      nameEn: config.name_en,
      nameCn: config.name_cn,
      fieldCount: config.base_fields ? config.base_fields.length : 0,
      baseFields: config.base_fields || [],
      filterConditions: config.filter_conditions || {},
      description: config.description || "",
      // Add eventConfig for ReactNodeExecutor compatibility
      eventConfig: config,
    },
  };
  console.log("[nodeConverter] Created node:", node.id, "type:", node.type);
  return node;
}

/**
 * 将ReactFlow节点列表转换为流程保存格式
 * @param {Array} nodes - ReactFlow节点
 * @param {Array} edges - ReactFlow边
 * @returns {Object} 流程数据
 */
export function reactFlowToFlowData(nodes, edges) {
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
 * @param {Object} flowData - 流程数据
 * @returns {Object} {nodes, edges}
 */
export function flowDataToReactFlow(flowData) {
  return {
    nodes: flowData.nodes || [],
    edges: flowData.connections || [],
  };
}
