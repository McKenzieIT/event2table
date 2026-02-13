import { useCallback } from 'react';
import { useReactFlow } from 'reactflow';

/**
 * 智能定位 Hook
 * 计算新节点在画布上的最佳位置
 */
export function useSmartPosition() {
  const { getNodes, getViewport } = useReactFlow();

  /**
   * 计算新节点的位置
   * @param {string} newNodeType - 新节点类型
   * @returns {Object} {x, y} 位置坐标
   */
  const calculatePosition = useCallback((newNodeType) => {
    const existingNodes = getNodes();
    const viewport = getViewport();

    // 查找同类型节点
    const sameTypeNodes = existingNodes.filter(n => n.type === newNodeType);

    if (sameTypeNodes.length === 0) {
      // 画布为空 → 放在视口中心
      return {
        x: (-viewport.x + viewport.width / 2) / viewport.zoom,
        y: (-viewport.y + viewport.height / 2) / viewport.zoom
      };
    }

    // 计算同类型节点的中心点
    const centerX = sameTypeNodes.reduce((sum, n) => sum + n.position.x, 0) / sameTypeNodes.length;
    const centerY = sameTypeNodes.reduce((sum, n) => sum + n.position.y, 0) / sameTypeNodes.length;

    // 找到距离中心点最近的节点
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

    // 在最近节点右下方偏移
    return {
      x: nearestNode.position.x + 150,
      y: nearestNode.position.y + 100
    };
  }, [getNodes, getViewport]);

  return { calculatePosition };
}
