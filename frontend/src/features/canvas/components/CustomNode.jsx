import React from "react";
import { Handle, Position } from "reactflow";
import "./CustomNode.css";

export default function CustomNode({ data, selected }) {
  return (
    <div
      className={`react-flow__node custom-node ${selected ? "selected" : ""}`}
    >
      <div className="custom-node">
        <Handle
          type="target"
          position={Position.Top}
          className="custom-node-handle"
        />

        <div className="custom-node-header">
          <span className="custom-node-icon">⚙️</span>
          <span className="custom-node-title">{data.label}</span>
        </div>

        <div className="custom-node-body">
          {data.eventCnName && (
            <div className="node-info-row">
              <span className="node-info-label">事件:</span>
              <span className="node-info-value">{data.eventCnName}</span>
            </div>
          )}
          {data.eventName && (
            <div className="node-info-row">
              <span className="node-info-label">名称:</span>
              <span className="node-info-value node-info-monospace">
                {data.eventName}
              </span>
            </div>
          )}
          {data.fieldCount !== undefined && (
            <div className="node-info-row">
              <span className="node-info-label">字段数:</span>
              <span className="node-info-value">{data.fieldCount}</span>
            </div>
          )}
          {data.description && (
            <div className="node-info-row">
              <span className="node-info-label">描述:</span>
              <span className="node-info-value node-info-description">
                {data.description}
              </span>
            </div>
          )}
          {/* 显示字段列表（最多5个） */}
          {data.baseFields && data.baseFields.length > 0 && (
            <div className="node-fields-section">
              <div className="node-fields-title">
                字段 (共{data.baseFields.length}个)
              </div>
              <div className="node-fields-list">
                {data.baseFields.slice(0, 5).map((field, idx) => (
                  <div key={idx} className="node-field-item">
                    <span className="field-name">
                      {field.alias || field.field_name}
                    </span>
                    <span className="field-type">
                      {field.field_type === "param" ? "参数" : "基础"}
                    </span>
                  </div>
                ))}
                {data.baseFields.length > 5 && (
                  <div className="node-field-more">
                    ... 还有 {data.baseFields.length - 5} 个字段
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <Handle
          type="source"
          position={Position.Bottom}
          className="custom-node-handle"
        />
      </div>
    </div>
  );
}
