import React from "react";
import "./NodeDetailModal.css";

/**
 * 节点详情模态框
 * 显示节点的完整信息，包括事件配置、字段列表等
 */
export default function NodeDetailModal({ isOpen, node, onClose }) {
  if (!isOpen || !node) return null;

  const { data } = node;
  const isEventNode = node.type === "event";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="node-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="node-icon">{data.icon || "⚙️"}</span>
          <h2>{data.label}</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          {isEventNode && data.eventConfig ? (
            <>
              {/* 节点类型 */}
              <div className="detail-section">
                <h3>节点类型</h3>
                <p>事件节点</p>
              </div>

              {/* 事件信息 */}
              <div className="detail-section">
                <h3>事件信息</h3>
                <div className="detail-row">
                  <span className="detail-label">事件名称:</span>
                  <span className="detail-value">
                    {data.eventConfig.event_name_cn}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">事件标识:</span>
                  <span className="detail-value code">
                    {data.eventConfig.event_name}
                  </span>
                </div>
                {data.eventConfig.description && (
                  <div className="detail-row">
                    <span className="detail-label">描述:</span>
                    <span className="detail-value">
                      {data.eventConfig.description}
                    </span>
                  </div>
                )}
              </div>

              {/* 字段列表 */}
              <div className="detail-section">
                <h3>字段列表 (共{data.fieldCount || 0}个)</h3>
                <div className="field-list">
                  {(data.baseFields || []).slice(0, 5).map((field, idx) => (
                    <div key={idx} className="field-item">
                      <span className="field-name">
                        {field.alias || field.field_name}
                      </span>
                      <span className="field-type">
                        {field.field_type === "param" ? "参数" : "基础"}
                      </span>
                    </div>
                  ))}
                  {(data.baseFields || []).length > 5 && (
                    <div className="field-more">
                      ... 还有 {data.baseFields.length - 5} 个字段
                    </div>
                  )}
                </div>
              </div>

              {/* 配置信息 */}
              <div className="detail-section">
                <h3>配置信息</h3>
                <div className="detail-row">
                  <span className="detail-label">配置ID:</span>
                  <span className="detail-value code">{data.configId}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">中文名称:</span>
                  <span className="detail-value">{data.nameCn || "-"}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="detail-section">
              <h3>节点信息</h3>
              <p>{data.label}</p>
              {data.description && <p>{data.description}</p>}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            关闭
          </button>
          {isEventNode && data.configId && (
            <button
              className="btn btn-primary"
              onClick={() => {
                window.open(
                  `/event_node_builder?game_gid=${window.gameData?.gid}&config_id=${data.configId}`,
                  "_blank",
                );
                onClose();
              }}
            >
              编辑配置
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
