import { useCallback } from 'react';
import { useReactFlow, Node, ReactFlowState } from 'reactflow';

export type NodeType = 'event' | 'custom' | 'union_all' | 'join' | 'output';

interface SmartPositionResult {
  x: number;
  y: number;
}

export function useSmartPosition() {
  const { getNodes, getViewport } = useReactFlow();

  const calculatePosition = useCallback((newNodeType: NodeType): SmartPositionResult => {
    const existingNodes = getNodes();
    const viewport = getViewport();

    const sameTypeNodes = existingNodes.filter((n: Node) => n.type === newNodeType);

    if (sameTypeNodes.length === 0) {
      return {
        x: (-viewport.x + viewport.width / 2) / viewport.zoom,
        y: (-viewport.y + viewport.height / 2) / viewport.zoom
      };
    }

    const centerX = sameTypeNodes.reduce((sum, n) => sum + n.position.x, 0) / sameTypeNodes.length;
    const centerY = sameTypeNodes.reduce((sum, n) => sum + n.position.y, 0) / sameTypeNodes.length;

    let nearestNode = sameTypeNodes[0];
    let minDistance = Infinity;

    sameTypeNodes.forEach(node => {
      const distance = Math.sqrt(
        Math.pow(node.position.x - centerX, 2) +
        Math.pow(node.position.y - centerY, 2)
      );
      if (distance < minDistance) {
        minDistance = distance;
        nearestNode = node;
      }
    });

    return {
      x: nearestNode.position.x + 150,
      y: nearestNode.position.y + 100
    };
  }, [getNodes, getViewport]);

  return { calculatePosition };
}
