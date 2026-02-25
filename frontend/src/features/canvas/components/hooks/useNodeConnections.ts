import { useState, useCallback } from "react";
import { Node, Edge, Connection, OnEdgesChange, addEdge as rfAddEdge } from "reactflow";

export type CanvasNodeType = 'event' | 'custom' | 'union_all' | 'join' | 'output';

interface NodeConnection {
  source: string;
  target: string;
}

interface ValidationResult {
  valid: boolean;
  error?: string;
}

interface ConnectionSuggestion {
  source: string;
  target: string;
  sourceLabel: string;
  targetLabel: string;
  type: string;
}

interface NodeConnectionsResult {
  incoming: Edge[];
  outgoing: Edge[];
  inDegree: number;
  outDegree: number;
}

interface UseNodeConnectionsParams {
  nodes: Node[];
  edges: Edge[];
  onEdgesChange?: OnEdgesChange;
  addEdge: (edge: Edge, edges: Edge[]) => Edge | Connection;
}

export function useNodeConnections({
  nodes,
  edges,
  onEdgesChange,
  addEdge,
}: UseNodeConnectionsParams) {
  const [connections, setConnections] = useState<NodeConnection[]>([]);

  const canConnect = useCallback(
    (sourceNode: Node | null, targetNode: Node | null): boolean => {
      if (!sourceNode || !targetNode) return false;
      if (sourceNode.id === targetNode.id) return false;

      const existingConnection = edges.find(
        (edge) =>
          edge.source === sourceNode.id && edge.target === targetNode.id,
      );
      if (existingConnection) return false;

      const typeRules: Record<CanvasNodeType, CanvasNodeType[]> = {
        event: ["union_all", "join", "output"],
        union_all: ["join", "output"],
        join: ["output"],
        output: [],
        custom: ["union_all", "join", "output"],
      };

      const allowedTypes = typeRules[sourceNode.type as CanvasNodeType] || [];
      return allowedTypes.includes(targetNode.type as CanvasNodeType);
    },
    [edges],
  );

  const validateConnection = useCallback(
    (connection: Connection): ValidationResult => {
      const sourceNode = nodes.find((n) => n.id === connection.source);
      const targetNode = nodes.find((n) => n.id === connection.target);

      if (!sourceNode || !targetNode) {
        return { valid: false, error: "节点不存在" };
      }

      if (!canConnect(sourceNode, targetNode)) {
        return { valid: false, error: "连接规则不允许" };
      }

      return { valid: true };
    },
    [nodes, canConnect],
  );

  const suggestConnections = useCallback(
    (nodeId: string): ConnectionSuggestion[] => {
      const suggestions: ConnectionSuggestion[] = [];
      const node = nodes.find((n) => n.id === nodeId);

      if (!node) return suggestions;

      nodes.forEach((targetNode) => {
        if (targetNode.id !== nodeId && canConnect(node, targetNode)) {
          suggestions.push({
            source: node.id,
            target: targetNode.id,
            sourceLabel: node.data?.label || '',
            targetLabel: targetNode.data?.label || '',
            type: targetNode.type || '',
          });
        }
      });

      return suggestions;
    },
    [nodes, canConnect],
  );

  const findSourceNodes = useCallback(
    (targetId: string): Node[] => {
      return nodes.filter((node) => {
        if (node.id === targetId) return false;
        const targetNode = nodes.find((n) => n.id === targetId);
        return targetNode ? canConnect(node, targetNode) : false;
      });
    },
    [nodes, canConnect],
  );

  const findTargetNodes = useCallback(
    (sourceId: string): Node[] => {
      return nodes.filter((node) => {
        if (node.id === sourceId) return false;
        const sourceNode = nodes.find((n) => n.id === sourceId);
        return sourceNode ? canConnect(sourceNode, node) : false;
      });
    },
    [nodes, canConnect],
  );

  const createConnection = useCallback(
    (sourceId: string, targetId: string): Edge => {
      const connection: Connection = { source: sourceId, target: targetId };
      const validation = validateConnection(connection);

      if (!validation.valid) {
        throw new Error(validation.error);
      }

      const newEdge: Edge = {
        id: `edge_${Date.now()}`,
        source: sourceId,
        target: targetId,
        type: "smoothstep",
        animated: true,
        style: { stroke: "#667eea", strokeWidth: 2 },
        label: "",
      };

      addEdge(newEdge, edges);
      return newEdge;
    },
    [validateConnection, addEdge, edges],
  );

  const removeConnection = useCallback(
    (edgeId: string): void => {
      const edgeToRemove = edges.find((edge) => edge.id === edgeId);
      if (edgeToRemove && onEdgesChange) {
        onEdgesChange([{ type: "remove", id: edgeId }]);
      }
    },
    [edges, onEdgesChange],
  );

  const getNodeInDegree = useCallback(
    (nodeId: string): number => {
      return edges.filter((edge) => edge.target === nodeId).length;
    },
    [edges],
  );

  const getNodeOutDegree = useCallback(
    (nodeId: string): number => {
      return edges.filter((edge) => edge.source === nodeId).length;
    },
    [edges],
  );

  const getNodeConnections = useCallback(
    (nodeId: string): NodeConnectionsResult => {
      return {
        incoming: edges.filter((edge) => edge.target === nodeId),
        outgoing: edges.filter((edge) => edge.source === nodeId),
        inDegree: getNodeInDegree(nodeId),
        outDegree: getNodeOutDegree(nodeId),
      };
    },
    [edges, getNodeInDegree, getNodeOutDegree],
  );

  const isSourceNode = useCallback(
    (nodeId: string): boolean => {
      const connections = getNodeConnections(nodeId);
      return (
        connections.incoming.length === 0 && connections.outgoing.length > 0
      );
    },
    [getNodeConnections],
  );

  const isIntermediateNode = useCallback(
    (nodeId: string): boolean => {
      const connections = getNodeConnections(nodeId);
      return connections.incoming.length > 0 && connections.outgoing.length > 0;
    },
    [getNodeConnections],
  );

  const isTerminalNode = useCallback(
    (nodeId: string): boolean => {
      const connections = getNodeConnections(nodeId);
      return (
        connections.incoming.length > 0 && connections.outgoing.length === 0
      );
    },
    [getNodeConnections],
  );

  return {
    connections,
    canConnect,
    validateConnection,
    suggestConnections,
    findSourceNodes,
    findTargetNodes,
    createConnection,
    removeConnection,
    getNodeConnections,
    getNodeInDegree,
    getNodeOutDegree,
    isSourceNode,
    isIntermediateNode,
    isTerminalNode,
  };
}
