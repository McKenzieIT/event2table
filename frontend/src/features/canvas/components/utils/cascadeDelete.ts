/**
 * Cascade Delete Utility
 * Handles cascading deletion of nodes and their connections
 *
 * Features:
 * - Delete node and all related edges
 * - Cascade delete orphan output nodes
 * - Calculate affected count for confirmation
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

// ============================================
// Type Definitions
// ============================================

export interface CanvasNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface CanvasEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string | null;
  targetHandle?: string | null;
  [key: string]: unknown;
}

export interface DeleteResult {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  affected: number;
}

export interface DeleteMultipleResult {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  summary: {
    deletedNodes: number;
    deletedEdges: number;
    cascadedNodes: number;
    totalAffected: number;
  };
}

export interface AffectedCount {
  nodes: number;
  edges: number;
  cascading: number;
}

// ============================================
// Helper Functions
// ============================================

/**
 * Find orphan output nodes (output nodes with no input connections)
 * @param nodes - Current nodes
 * @param edges - Current edges
 * @returns Array of orphan output node IDs
 */
function findOrphanOutputNodes(nodes: CanvasNode[], edges: CanvasEdge[]): string[] {
  const outputNodes = nodes.filter(n => n.type === 'output');

  return outputNodes
    .filter(output => {
      const hasInput = edges.some(e => e.target === output.id);
      return !hasInput;
    })
    .map(n => n.id);
}

// ============================================
// Main Functions
// ============================================

/**
 * Delete a node with cascading effects
 * @param nodeId - Node ID to delete
 * @param nodes - Current all nodes
 * @param edges - Current all edges
 * @returns {nodes, edges, affected} - Updated nodes, edges, and affected count
 */
export function deleteNodeCascade(
  nodeId: string,
  nodes: CanvasNode[],
  edges: CanvasEdge[]
): DeleteResult {
  const relatedEdges = edges.filter(
    e => e.source === nodeId || e.target === nodeId
  );

  const remainingNodes = nodes.filter(n => n.id !== nodeId);
  const remainingEdges = edges.filter(
    e => e.source !== nodeId && e.target !== nodeId
  );

  const orphanOutputs = findOrphanOutputNodes(remainingNodes, remainingEdges);

  let finalNodes = [...remainingNodes];
  let finalEdges = [...remainingEdges];
  let totalAffected = 1 + relatedEdges.length + orphanOutputs.length;

  orphanOutputs.forEach(orphanId => {
    const result = deleteNodeCascade(orphanId, finalNodes, finalEdges);
    finalNodes = result.nodes;
    finalEdges = result.edges;
    totalAffected += result.affected;
  });

  return {
    nodes: finalNodes,
    edges: finalEdges,
    affected: totalAffected
  };
}

/**
 * Delete multiple selected nodes with cascading effects
 * @param selectedNodeIds - Array of node IDs to delete
 * @param nodes - Current all nodes
 * @param edges - Current all edges
 * @returns {nodes, edges, summary} - Updated nodes, edges, and deletion summary
 */
export function deleteMultipleNodesCascade(
  selectedNodeIds: string[],
  nodes: CanvasNode[],
  edges: CanvasEdge[]
): DeleteMultipleResult {
  let newNodes = [...nodes];
  let newEdges = [...edges];
  let deletedNodes = 0;
  let deletedEdges = 0;
  let cascadedNodes = 0;

  selectedNodeIds.forEach(nodeId => {
    const result = deleteNodeCascade(nodeId, newNodes, newEdges);
    newNodes = result.nodes;
    newEdges = result.edges;

    const nodeCount = nodes.length - newNodes.length;
    const edgeCount = edges.length - newEdges.length;

    deletedNodes += 1;
    deletedEdges += (edgeCount - deletedEdges);
    cascadedNodes += (nodeCount - deletedNodes - cascadedNodes);
  });

  return {
    nodes: newNodes,
    edges: newEdges,
    summary: {
      deletedNodes,
      deletedEdges,
      cascadedNodes,
      totalAffected: deletedNodes + deletedEdges + cascadedNodes
    }
  };
}

/**
 * Calculate affected count before deletion (for confirmation dialog)
 * @param selectedNodeIds - Node IDs to be deleted
 * @param nodes - Current nodes
 * @param edges - Current edges
 * @returns {nodes, edges, cascading} - Estimated affected count
 */
export function calculateAffectedCount(
  selectedNodeIds: string[],
  nodes: CanvasNode[],
  edges: CanvasEdge[]
): AffectedCount {
  let affectedNodes = selectedNodeIds.length;
  let affectedEdges = 0;
  let cascadingNodes = 0;

  let tempNodes = [...nodes];
  let tempEdges = [...edges];

  selectedNodeIds.forEach(nodeId => {
    const relatedEdges = tempEdges.filter(
      e => e.source === nodeId || e.target === nodeId
    );
    affectedEdges += relatedEdges.length;

    tempNodes = tempNodes.filter(n => n.id !== nodeId);
    tempEdges = tempEdges.filter(
      e => e.source !== nodeId && e.target !== nodeId
    );

    const orphanOutputs = findOrphanOutputNodes(tempNodes, tempEdges);
    cascadingNodes += orphanOutputs.length;

    orphanOutputs.forEach(orphanId => {
      tempNodes = tempNodes.filter(n => n.id !== orphanId);
      const orphanRelatedEdges = tempEdges.filter(
        e => e.source === orphanId || e.target === orphanId
      );
      tempEdges = tempEdges.filter(
        e => e.source !== orphanId && e.target !== orphanId
      );
      affectedEdges += orphanRelatedEdges.length;
    });
  });

  return {
    nodes: affectedNodes,
    edges: affectedEdges,
    cascading: cascadingNodes
  };
}
