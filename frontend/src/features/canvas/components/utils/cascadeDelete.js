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

/**
 * Delete a node with cascading effects
 * @param {string} nodeId - Node ID to delete
 * @param {Array} nodes - Current all nodes
 * @param {Array} edges - Current all edges
 * @returns {Object} { nodes, edges, affected } - Updated nodes, edges, and affected count
 */
export function deleteNodeCascade(nodeId, nodes, edges) {
  // Step 1: Find related edges (connected to this node)
  const relatedEdges = edges.filter(
    e => e.source === nodeId || e.target === nodeId
  );

  // Step 2: Remove the target node
  const remainingNodes = nodes.filter(n => n.id !== nodeId);

  // Step 3: Remove related edges
  const remainingEdges = edges.filter(
    e => e.source !== nodeId && e.target !== nodeId
  );

  // Step 4: Find orphan output nodes (output nodes with no inputs)
  const orphanOutputs = findOrphanOutputNodes(remainingNodes, remainingEdges);

  // Step 5: Recursively delete orphan nodes
  let finalNodes = [...remainingNodes];
  let finalEdges = [...remainingEdges];
  let totalAffected = 1 + relatedEdges.length + orphanOutputs.length; // node + edges + orphans

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
 * @param {Array} selectedNodeIds - Array of node IDs to delete
 * @param {Array} nodes - Current all nodes
 * @param {Array} edges - Current all edges
 * @returns {Object} { nodes, edges, summary } - Updated nodes, edges, and deletion summary
 */
export function deleteMultipleNodesCascade(selectedNodeIds, nodes, edges) {
  let newNodes = [...nodes];
  let newEdges = [...edges];
  let deletedNodes = 0;
  let deletedEdges = 0;
  let cascadedNodes = 0;

  // Delete each selected node (cascade effects handled internally)
  selectedNodeIds.forEach(nodeId => {
    const result = deleteNodeCascade(nodeId, newNodes, newEdges);
    newNodes = result.nodes;
    newEdges = result.edges;

    // Count affected items
    const nodeCount = nodes.length - newNodes.length;
    const edgeCount = edges.length - newEdges.length;

    deletedNodes += 1; // The selected node itself
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
 * Find orphan output nodes (output nodes with no input connections)
 * @param {Array} nodes - Current nodes
 * @param {Array} edges - Current edges
 * @returns {Array} Array of orphan output node IDs
 */
function findOrphanOutputNodes(nodes, edges) {
  const outputNodes = nodes.filter(n => n.type === 'output');

  return outputNodes
    .filter(output => {
      // Check if there's any input connection to this output node
      const hasInput = edges.some(e => e.target === output.id);
      return !hasInput;
    })
    .map(n => n.id);
}

/**
 * Calculate affected count before deletion (for confirmation dialog)
 * @param {Array} selectedNodeIds - Node IDs to be deleted
 * @param {Array} nodes - Current nodes
 * @param {Array} edges - Current edges
 * @returns {Object} { nodes, edges, cascading } - Estimated affected count
 */
export function calculateAffectedCount(selectedNodeIds, nodes, edges) {
  let affectedNodes = selectedNodeIds.length;
  let affectedEdges = 0;
  let cascadingNodes = 0;

  // Simulate deletion to calculate affected count
  let tempNodes = [...nodes];
  let tempEdges = [...edges];

  selectedNodeIds.forEach(nodeId => {
    // Count related edges
    const relatedEdges = tempEdges.filter(
      e => e.source === nodeId || e.target === nodeId
    );
    affectedEdges += relatedEdges.length;

    // Remove node and edges
    tempNodes = tempNodes.filter(n => n.id !== nodeId);
    tempEdges = tempEdges.filter(
      e => e.source !== nodeId && e.target !== nodeId
    );

    // Count orphan outputs
    const orphanOutputs = findOrphanOutputNodes(tempNodes, tempEdges);
    cascadingNodes += orphanOutputs.length;

    // Remove orphans from temp arrays
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
