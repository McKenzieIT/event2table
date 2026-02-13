import { useState, useCallback, useEffect, useRef } from "react";
import { useNodeConnections } from "./useNodeConnections";
import ToastNotification from "@shared/ui/ToastNotification";
import ConnectionPromptModal from "../components/ConnectionPromptModal";

/**
 * 自动连接 Hook
 * 管理节点的自动连接逻辑和提示
 *
 * @param {Array} nodes - 节点列表
 * @param {Array} edges - 边列表
 * @param {Function} onEdgesChange - 边变更回调
 * @param {Function} addEdge - 添加边的函数
 * @param {Object} options - 配置选项
 * @param {boolean} options.enabled - 是否启用自动连接
 * @param {boolean} options.showPrompt - 是否显示连接提示
 * @param {boolean} options.autoConnectNewNodes - 是否自动连接新节点
 *
 * @returns {Object} 自动连接相关的状态和函数
 *   - toast: Toast 通知配置
 *   - modal: 连接提示模态框配置
 *   - autoConnect: 自动连接函数
 *   - showConnectionPrompt: 显示连接提示
 *   - setAutoConnectEnabled: 设置自动连接开关
 *
 * @example
 * const { toast, modal, autoConnect, showConnectionPrompt } = useAutoConnect(
 *   nodes, edges, onEdgesChange, addEdge,
 *   { enabled: true, showPrompt: true, autoConnectNewNodes: false }
 * );
 */
export function useAutoConnect(
  nodes,
  edges,
  onEdgesChange,
  addEdge,
  options = {},
) {
  const {
    enabled = true,
    showPrompt = true,
    autoConnectNewNodes = false,
  } = options;

  const [autoConnectEnabled, setAutoConnectEnabled] = useState(enabled);
  const [lastAddedNode, setLastAddedNode] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("info");
  const [showModal, setShowModal] = useState(false);
  const [targetOptions, setTargetOptions] = useState([]);
  const [skipNodes, setSkipNodes] = useState(new Set());

  // Use ref to track previous nodes length for detecting new nodes
  const prevNodesLengthRef = useRef(nodes.length);

  // 🔧 v1.0.22: 使用ref存储最新nodes，避免闭包陷阱
  const nodesRef = useRef(nodes);

  // 每次nodes更新时同步到ref
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  // 使用节点连接管理 Hook
  const {
    canConnect,
    validateConnection,
    suggestConnections,
    createConnection,
  } = useNodeConnections(nodes, edges, onEdgesChange, addEdge);

  // 显示 Toast 通知
  const showToastNotification = useCallback(
    (message, type = "info", duration = 3000) => {
      setToastMessage(message);
      setToastType(type);
      setShowToast(true);

      setTimeout(() => {
        setShowToast(false);
      }, duration);
    },
    [],
  );

  // 显示连接提示
  const showConnectionPrompt = useCallback(
    (node) => {
      if (!showPrompt || !autoConnectEnabled) return;

      const suggestions = suggestConnections(node.id);
      if (suggestions.length > 0) {
        setLastAddedNode(node);
        setTargetOptions(suggestions);
        setShowModal(true);
      } else {
        showToastNotification("无可连接的节点", "info", 2000);
      }
    },
    [suggestConnections, showPrompt, autoConnectEnabled, showToastNotification],
  );

  // 跳过某个节点的连接
  const skipNodeConnection = useCallback((nodeId) => {
    setSkipNodes((prev) => new Set(prev).add(nodeId));
  }, []);

  // 执行自动连接
  const autoConnect = useCallback(
    (newNodeId) => {
      console.log(
        "[useAutoConnect] autoConnect called with nodeId:",
        newNodeId,
        "enabled:",
        autoConnectEnabled,
      );

      if (!autoConnectEnabled) return false;

      // 🔧 v1.0.22: 使用ref获取最新nodes，而不是闭包中的nodes参数
      const currentNodes = nodesRef.current;
      const newNode = currentNodes.find((n) => n.id === newNodeId);

      if (!newNode) {
        console.log(
          "[useAutoConnect] Node not found:",
          newNodeId,
          "currentNodes.length:",
          currentNodes.length,
        );
        return false;
      }

      console.log(
        "[useAutoConnect] Node found:",
        newNode.id,
        "type:",
        newNode.type,
      );

      // 检查是否跳过
      if (skipNodes.has(newNodeId)) return false;

      // 🔧 v1.0.17: 只有连接节点才触发自动连接询问
      // 事件节点不触发自动连接
      if (newNode.type === "event" || newNode.type === "custom") {
        return false;
      }

      // 根据新节点类型，决定查找方向
      // - 连接节点（union_all/join）：查找哪些节点可以连接到它
      // - 输出节点：查找哪些连接节点可以连接到它
      let possibleConnections = [];

      if (newNode.type === "union_all" || newNode.type === "join") {
        // 🔧 v1.0.22: 使用currentNodes而不是nodes
        currentNodes.forEach((sourceNode) => {
          if (sourceNode.id === newNodeId) return;
          if (skipNodes.has(sourceNode.id)) return;
          // 只查找事件节点
          if (sourceNode.type !== "event" && sourceNode.type !== "custom")
            return;
          // 检查 sourceNode → newNode 是否有效
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
        // 🔧 v1.0.22: 使用currentNodes而不是nodes
        // 输出节点：查找连接节点作为源
        currentNodes.forEach((sourceNode) => {
          if (sourceNode.id === newNodeId) return;
          if (skipNodes.has(sourceNode.id)) return;
          // 只查找连接节点
          if (sourceNode.type !== "union_all" && sourceNode.type !== "join")
            return;
          // 检查 sourceNode → newNode 是否有效
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
        // 其他节点类型：不触发自动连接
        return false;
      }

      console.log(
        "[useAutoConnect] possibleConnections:",
        possibleConnections.length,
      );

      if (possibleConnections.length === 0) {
        console.log("[useAutoConnect] No possible connections found");
        return false;
      }

      // 如果只有一个可能连接且自动连接已启用，执行连接
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
          showToastNotification(`连接失败: ${error.message}`, "error", 3000);
          return false;
        }
      }

      // 如果有多个可能连接，显示提示
      if (showPrompt && possibleConnections.length > 0) {
        console.log(
          "[useAutoConnect] Showing connection modal with",
          possibleConnections.length,
          "options",
        );
        // 对于连接节点（union_all/join）和输出节点，我们需要显示可以作为源的节点
        // Modal会显示sourceNode（新节点）和targetOptions（可选择的源节点）
        // 当用户选择时，会调用 onConnect(sourceNode.id, selectedTarget)
        // 但这对union_all是反的 - 我们需要 event → union_all
        // 所以targetOptions应该是事件节点，selectedTarget是事件节点ID
        // 而sourceNode虽然叫这个名字，但在这里应该是目标节点（union_all）
        // 我们需要特殊处理：modal的onConnect会被传入(selectedEventId, unionAllId)
        // 但modal内部的逻辑是 onConnect(sourceNode.id, selectedTarget)
        // 所以我们需要把union_all作为sourceNode传入（虽然它是目标），而targetOptions是事件节点
        const targetOptions = possibleConnections.map((conn) => {
          // 对于union_all/join/output，conn.sourceNode是事件节点，conn.targetNode是新节点
          // 我们要显示事件节点作为选项
          return {
            id: conn.sourceId,
            data: { label: conn.sourceNode.data.label },
            type: conn.sourceNode.type,
          };
        });

        // 设置模态框状态
        // 注意：对于union_all节点，sourceNode实际上是目标节点，modal的文案可能会混淆
        setLastAddedNode(newNode);
        setTargetOptions(targetOptions);
        setShowModal(true);
      }

      return true;
    },
    [
      nodesRef, // 🔧 v1.0.22: 使用ref而不是nodes
      canConnect,
      autoConnectEnabled,
      skipNodes,
      autoConnectNewNodes,
      showPrompt,
      showToastNotification,
    ],
  );

  // 处理连接选择
  const handleConnect = useCallback(
    (modalSourceId, selectedTargetId) => {
      try {
        // modalSourceId是modal传入的sourceNode.id（对于union_all，这是新节点ID）
        // selectedTargetId是用户选择的target（对于union_all，这是事件节点ID）
        // 但我们需要创建 event → union_all，所以需要交换
        // 判断modalSourceId是否是连接节点或输出节点（目标节点）
        const modalSourceNode = nodes.find((n) => n.id === modalSourceId);
        if (
          modalSourceNode &&
          (modalSourceNode.type === "union_all" ||
            modalSourceNode.type === "join" ||
            modalSourceNode.type === "output")
        ) {
          // 🔧 v1.0.25.1: 使用onEdgesChange触发状态更新，确保ReactFlow渲染连接线
          // 对于连接/输出节点，参数是反的：modalSourceId是目标，selectedTargetId是源
          const newEdge = {
            id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            source: selectedTargetId,
            target: modalSourceId,
            // 🔧 v1.0.25.2: 使用默认边类型（贝塞尔曲线），与手动连接保持一致
            animated: true,
            style: { stroke: "#5a67d8", strokeWidth: 3 },
            label: "",
          };
          // 使用onEdgesChange触发ReactFlow状态更新
          onEdgesChange([
            {
              type: "add",
              item: newEdge,
            },
          ]);
          const sourceLabel = nodes.find((n) => n.id === selectedTargetId)?.data
            .label;
          showToastNotification(
            `连接成功: ${sourceLabel} → ${modalSourceNode.data.label}`,
            "success",
            2000,
          );
          console.log("[useAutoConnect] Created edge:", newEdge);
        } else {
          // 正常情况：modalSourceId是源，selectedTargetId是目标
          const newEdge = {
            id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            source: modalSourceId,
            target: selectedTargetId,
            // 🔧 v1.0.25.2: 使用默认边类型（贝塞尔曲线），与手动连接保持一致
            animated: true,
            style: { stroke: "#5a67d8", strokeWidth: 3 },
            label: "",
          };
          // 使用onEdgesChange触发ReactFlow状态更新
          onEdgesChange([
            {
              type: "add",
              item: newEdge,
            },
          ]);
          showToastNotification("连接成功！", "success", 2000);
          console.log("[useAutoConnect] Created edge:", newEdge);
        }
        setShowModal(false);
      } catch (error) {
        console.error("[useAutoConnect] Connection error:", error);
        showToastNotification(`连接失败: ${error.message}`, "error", 3000);
      }
    },
    [nodes, onEdgesChange, showToastNotification],
  );

  // 处理跳过连接
  const handleSkip = useCallback(
    (sourceId) => {
      skipNodeConnection(sourceId);
      setShowModal(false);
      showToastNotification("已跳过连接", "info", 2000);
    },
    [skipNodeConnection, showToastNotification],
  );

  // 当节点添加时触发自动连接
  useEffect(() => {
    if (!autoConnectEnabled || !autoConnectNewNodes) return;

    // Only run when nodes length changes
    if (nodes.length === prevNodesLengthRef.current) return;

    // Find newly added nodes (nodes that weren't in previous state)
    const currentIds = new Set(nodes.map((n) => n.id));
    const prevIds = new Set();
    // We can't track previous nodes directly, so use edge-based detection
    const newNodes = nodes.filter((node) => {
      // Check if node has no connections yet (likely newly added)
      return !edges.some(
        (edge) => edge.source === node.id || edge.target === node.id,
      );
    });

    // Try to auto-connect new nodes
    newNodes.forEach((node) => {
      if (!skipNodes.has(node.id)) {
        autoConnect(node.id);
      }
    });

    // Update ref
    prevNodesLengthRef.current = nodes.length;
  }, [
    nodes.length,
    edges,
    autoConnectEnabled,
    autoConnectNewNodes,
    skipNodes,
    autoConnect,
  ]);

  // 当配置改变时更新状态
  useEffect(() => {
    setAutoConnectEnabled(enabled);
  }, [enabled]);

  return {
    // Toast 通知
    toast: {
      show: showToast,
      message: toastMessage,
      type: toastType,
      onClose: () => setShowToast(false),
    },

    // 连接提示模态框
    modal: {
      show: showModal,
      sourceNode: lastAddedNode,
      targetOptions: targetOptions,
      onClose: () => setShowModal(false),
      onConnect: handleConnect,
      onSkip: handleSkip,
    },

    // 自动连接
    autoConnect,
    showConnectionPrompt,
    setAutoConnectEnabled,
    skipNodeConnection,
  };
}
