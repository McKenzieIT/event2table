import { useState, useCallback, useEffect, useRef } from "react";
import { Node, Edge, OnEdgesChange } from "reactflow";
import { useNodeConnections, CanvasNodeType } from "./useNodeConnections";

export type ToastType = "info" | "success" | "warning" | "error";

interface AutoConnectOptions {
  enabled?: boolean;
  showPrompt?: boolean;
  autoConnectNewNodes?: boolean;
}

interface TargetOption {
  id: string;
  data: { label: string };
  type: string;
}

interface ToastConfig {
  show: boolean;
  message: string;
  type: ToastType;
  onClose: () => void;
}

interface ModalConfig {
  show: boolean;
  sourceNode: Node | null;
  targetOptions: TargetOption[];
  onClose: () => void;
  onConnect: (modalSourceId: string, selectedTargetId: string) => void;
  onSkip: (sourceId: string) => void;
}

interface AutoConnectResult {
  toast: ToastConfig;
  modal: ModalConfig;
  autoConnect: (newNodeId: string) => boolean;
  showConnectionPrompt: (node: Node) => void;
  setAutoConnectEnabled: (enabled: boolean) => void;
  skipNodeConnection: (nodeId: string) => void;
}

export function useAutoConnect(
  nodes: Node[],
  edges: Edge[],
  onEdgesChange: OnEdgesChange,
  addEdge: (edge: Edge, edges: Edge[]) => Edge | import("reactflow").Connection,
  options: AutoConnectOptions = {},
): AutoConnectResult {
  const {
    enabled = true,
    showPrompt = true,
    autoConnectNewNodes = false,
  } = options;

  const [autoConnectEnabled, setAutoConnectEnabled] = useState(enabled);
  const [lastAddedNode, setLastAddedNode] = useState<Node | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<ToastType>("info");
  const [showModal, setShowModal] = useState(false);
  const [targetOptions, setTargetOptions] = useState<TargetOption[]>([]);
  const [skipNodes, setSkipNodes] = useState<Set<string>>(new Set());

  const prevNodesLengthRef = useRef(nodes.length);
  const nodesRef = useRef<Node[]>(nodes);

  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  const {
    canConnect,
    validateConnection,
    suggestConnections,
    createConnection,
  } = useNodeConnections({
    nodes,
    edges,
    onEdgesChange,
    addEdge,
  });

  const showToastNotification = useCallback(
    (message: string, type: ToastType = "info", duration: number = 3000) => {
      setToastMessage(message);
      setToastType(type);
      setShowToast(true);

      setTimeout(() => {
        setShowToast(false);
      }, duration);
    },
    [],
  );

  const showConnectionPrompt = useCallback(
    (node: Node) => {
      if (!showPrompt || !autoConnectEnabled) return;

      const suggestions = suggestConnections(node.id);
      if (suggestions.length > 0) {
        setLastAddedNode(node);
        setTargetOptions(
          suggestions.map((conn) => ({
            id: conn.source,
            data: { label: conn.sourceLabel },
            type: conn.type,
          })),
        );
        setShowModal(true);
      } else {
        showToastNotification("无可连接的节点", "info", 2000);
      }
    },
    [suggestConnections, showPrompt, autoConnectEnabled, showToastNotification],
  );

  const skipNodeConnection = useCallback((nodeId: string) => {
    setSkipNodes((prev) => new Set(prev).add(nodeId));
  }, []);

  const autoConnect = useCallback(
    (newNodeId: string): boolean => {
      if (!autoConnectEnabled) return false;

      const currentNodes = nodesRef.current;
      const newNode = currentNodes.find((n) => n.id === newNodeId);

      if (!newNode) {
        return false;
      }

      if (skipNodes.has(newNodeId)) return false;

      if (newNode.type === "event" || newNode.type === "custom") {
        return false;
      }

      let possibleConnections: {
        sourceId: string;
        targetId: string;
        sourceNode: Node;
        targetNode: Node;
      }[] = [];

      if (newNode.type === "union_all" || newNode.type === "join") {
        currentNodes.forEach((sourceNode) => {
          if (sourceNode.id === newNodeId) return;
          if (skipNodes.has(sourceNode.id)) return;
          if (
            sourceNode.type !== "event" &&
            sourceNode.type !== "custom"
          )
            return;
          if (canConnect(sourceNode, newNode)) {
            possibleConnections.push({
              sourceId: sourceNode.id,
              targetId: newNodeId,
              sourceNode: sourceNode,
              targetNode: newNode,
            });
          }
        });
      } else if (newNode.type === "output") {
        currentNodes.forEach((sourceNode) => {
          if (sourceNode.id === newNodeId) return;
          if (skipNodes.has(sourceNode.id)) return;
          if (sourceNode.type !== "union_all" && sourceNode.type !== "join")
            return;
          if (canConnect(sourceNode, newNode)) {
            possibleConnections.push({
              sourceId: sourceNode.id,
              targetId: newNodeId,
              sourceNode: sourceNode,
              targetNode: newNode,
            });
          }
        });
      } else {
        return false;
      }

      if (possibleConnections.length === 0) {
        return false;
      }

      if (possibleConnections.length === 1 && autoConnectNewNodes) {
        try {
          const conn = possibleConnections[0];
          createConnection(conn.sourceId, conn.targetId);
          showToastNotification(
            `已自动连接 ${conn.sourceNode.data.label} → ${conn.targetNode.data.label}`,
            "success",
            2000,
          );
          return true;
        } catch (error) {
          showToastNotification(
            `连接失败: ${(error as Error).message}`,
            "error",
            3000,
          );
          return false;
        }
      }

      if (showPrompt && possibleConnections.length > 0) {
        const targetOptions = possibleConnections.map((conn) => ({
          id: conn.sourceId,
          data: { label: conn.sourceNode.data.label },
          type: conn.sourceNode.type,
        }));

        setLastAddedNode(newNode);
        setTargetOptions(targetOptions);
        setShowModal(true);
      }

      return true;
    },
    [
      nodesRef,
      canConnect,
      autoConnectEnabled,
      skipNodes,
      autoConnectNewNodes,
      showPrompt,
      showToastNotification,
      createConnection,
    ],
  );

  const handleConnect = useCallback(
    (modalSourceId: string, selectedTargetId: string) => {
      try {
        const modalSourceNode = nodes.find((n) => n.id === modalSourceId);
        if (
          modalSourceNode &&
          (modalSourceNode.type === "union_all" ||
            modalSourceNode.type === "join" ||
            modalSourceNode.type === "output")
        ) {
          const newEdge = {
            id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            source: selectedTargetId,
            target: modalSourceId,
            animated: true,
            style: { stroke: "#5a67d8", strokeWidth: 3 },
            label: "",
          };
          onEdgesChange([
            {
              type: "add",
              item: newEdge,
            },
          ]);
          const sourceLabel = nodes.find((n) => n.id === selectedTargetId)
            ?.data.label;
          showToastNotification(
            `连接成功: ${sourceLabel} → ${modalSourceNode.data.label}`,
            "success",
            2000,
          );
        } else {
          const newEdge = {
            id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            source: modalSourceId,
            target: selectedTargetId,
            animated: true,
            style: { stroke: "#5a67d8", strokeWidth: 3 },
            label: "",
          };
          onEdgesChange([
            {
              type: "add",
              item: newEdge,
            },
          ]);
          showToastNotification("连接成功！", "success", 2000);
        }
        setShowModal(false);
      } catch (error) {
        console.error("[useAutoConnect] Connection error:", error);
        showToastNotification(
          `连接失败: ${(error as Error).message}`,
          "error",
          3000,
        );
      }
    },
    [nodes, onEdgesChange, showToastNotification],
  );

  const handleSkip = useCallback(
    (sourceId: string) => {
      skipNodeConnection(sourceId);
      setShowModal(false);
      showToastNotification("已跳过连接", "info", 2000);
    },
    [skipNodeConnection, showToastNotification],
  );

  useEffect(() => {
    if (!autoConnectEnabled || !autoConnectNewNodes) return;

    if (nodes.length === prevNodesLengthRef.current) return;

    const newNodes = nodes.filter((node) => {
      return !edges.some(
        (edge) => edge.source === node.id || edge.target === node.id,
      );
    });

    newNodes.forEach((node) => {
      if (!skipNodes.has(node.id)) {
        autoConnect(node.id);
      }
    });

    prevNodesLengthRef.current = nodes.length;
  }, [
    nodes.length,
    edges,
    autoConnectEnabled,
    autoConnectNewNodes,
    skipNodes,
    autoConnect,
  ]);

  useEffect(() => {
    setAutoConnectEnabled(enabled);
  }, [enabled]);

  return {
    toast: {
      show: showToast,
      message: toastMessage,
      type: toastType,
      onClose: () => setShowToast(false),
    },
    modal: {
      show: showModal,
      sourceNode: lastAddedNode,
      targetOptions: targetOptions,
      onClose: () => setShowModal(false),
      onConnect: handleConnect,
      onSkip: handleSkip,
    },
    autoConnect,
    showConnectionPrompt,
    setAutoConnectEnabled,
    skipNodeConnection,
  };
}
