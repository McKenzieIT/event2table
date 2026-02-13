import React, { useState, useCallback } from "react";
import { Button, Checkbox } from "@shared/ui";
import "./ConnectionPromptModal.css";

/**
 * 连接提示模态框组件
 * 当新节点添加时，提示用户是否自动连接相关节点
 *
 * @param {Object} props - 组件属性
 * @param {boolean} props.isOpen - 模态框是否打开
 * @param {Function} props.onClose - 关闭回调
 * @param {Object} props.sourceNode - 源节点信息
 * @param {Array} props.targetOptions - 可选目标节点列表
 * @param {Function} props.onConnect - 连接回调
 * @param {Function} props.onSkip - 跳过回调
 *
 * @example
 * <ConnectionPromptModal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   sourceNode={sourceNode}
 *   targetOptions={targetNodes}
 *   onConnect={handleConnect}
 *   onSkip={handleSkip}
 * />
 */
export default function ConnectionPromptModal({
  isOpen,
  onClose,
  sourceNode,
  targetOptions = [],
  onConnect,
  onSkip,
}) {
  // 🔧 v1.0.23: 支持多选 - 使用Set存储选中的节点ID
  const [selectedTargets, setSelectedTargets] = useState(new Set());
  const [autoConnectEnabled, setAutoConnectEnabled] = useState(true);

  const handleConnect = useCallback(() => {
    if (autoConnectEnabled && onConnect && selectedTargets.size > 0) {
      // 🔧 v1.0.23: 连接所有选中的节点
      // 注意：对于union_all/join节点，参数是反的
      const modalSourceNode = sourceNode;
      const isConnectionNode =
        modalSourceNode.type === "union_all" ||
        modalSourceNode.type === "join" ||
        modalSourceNode.type === "output";

      selectedTargets.forEach((targetId) => {
        if (isConnectionNode) {
          // 对于连接节点：targetId是源（事件节点），modalSourceNode.id是目标（UNION ALL）
          onConnect(targetId, modalSourceNode.id);
        } else {
          // 正常情况：modalSourceNode是源，targetId是目标
          onConnect(modalSourceNode.id, targetId);
        }
      });

      // 🔧 v1.0.24 fix: 延迟关闭，确保所有连接都已创建并渲染
      setTimeout(() => {
        onClose();
      }, 100);
    } else {
      // 如果没有启用自动连接或没有选中节点，直接关闭
      onClose();
    }
  }, [selectedTargets, autoConnectEnabled, sourceNode, onConnect, onClose]);

  const handleSkip = useCallback(() => {
    if (onSkip) {
      onSkip(sourceNode.id);
    }
    onClose();
  }, [sourceNode, onSkip, onClose]);

  const handleToggleAutoConnect = useCallback(() => {
    setAutoConnectEnabled(!autoConnectEnabled);
  }, [autoConnectEnabled]);

  // 🔧 v1.0.23: Toggle选择节点
  const handleToggleTarget = useCallback((targetId) => {
    setSelectedTargets((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(targetId)) {
        newSet.delete(targetId);
      } else {
        newSet.add(targetId);
      }
      return newSet;
    });
  }, []);

  // 生成节点类型的图标
  const getNodeIcon = (nodeType) => {
    const icons = {
      event: "🎮",
      union_all: "🔀",
      join: "🔗",
      output: "📤",
    };
    return icons[nodeType] || "📦";
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content connection-prompt"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>自动连接提示</h3>
          <Button variant="ghost" size="sm" className="close-btn" onClick={onClose} title="关闭">
            ×
          </Button>
        </div>

        <div className="modal-body">
          <div className="source-info">
            <div className="node-badge">
              <span className="node-icon">{getNodeIcon(sourceNode.type)}</span>
              <span className="node-label">{sourceNode.data.label}</span>
            </div>
            <p>已添加到画布</p>
          </div>

          <div className="divider"></div>

          <div className="target-options">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "12px",
              }}
            >
              <h4 style={{ margin: 0 }}>选择要连接的节点：</h4>
              {selectedTargets.size > 0 && (
                <span className="selection-count">
                  已选择 <strong>{selectedTargets.size}</strong> 个节点
                </span>
              )}
            </div>
            {targetOptions.length === 0 ? (
              <p className="no-options">无可连接的节点</p>
            ) : (
              <div className="target-list">
                {targetOptions.map((target) => (
                  <div
                    key={target.id}
                    className={`target-option ${selectedTargets.has(target.id) ? "selected" : ""}`}
                    onClick={() => handleToggleTarget(target.id)}
                  >
                    <span className="node-icon">
                      {getNodeIcon(target.type)}
                    </span>
                    <span className="node-label">{target.data.label}</span>
                    <span className="node-type">({target.type})</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="auto-connect-option">
            <Checkbox
              checked={autoConnectEnabled}
              onChange={handleToggleAutoConnect}
              label="下次自动连接"
            />
          </div>
        </div>

        <div className="modal-footer">
          <Button
            variant="secondary"
            onClick={handleSkip}
            disabled={!autoConnectEnabled}
          >
            跳过连接
          </Button>
          <Button
            variant="primary"
            onClick={handleConnect}
            disabled={selectedTargets.size === 0 && !autoConnectEnabled}
          >
            {autoConnectEnabled ? "立即连接" : "稍后手动连接"}
          </Button>
        </div>
      </div>
    </div>
  );
}
