// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from "react";
import { Handle, Position } from "reactflow";
import "./CustomNode.css";
import type { CustomNodeProps, CustomNodeData, Field } from "./types";

export default function CustomNode({ data, selected }: CustomNodeProps): React.JSX.Element {
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
          {(data as any).eventCnName && (
            <div className="node-info-row">
              <span className="node-info-label">事件:</span>
              <span className="node-info-value">{(data as any).eventCnName}</span>
            </div>
          )}
          {(data as any).eventName && (
            <div className="node-info-row">
              <span className="node-info-label">名称:</span>
              <span className="node-info-value node-info-monospace">
                {(data as any).eventName}
              </span>
            </div>
          )}
          {data.fieldCount !== undefined && (
            <div className="node-info-row">
              <span className="node-info-label">字段数:</span>
              <span className="node-info-value">{data.fieldCount}</span>
            </div>
          )}
          {(data as any).description && (
            <div className="node-info-row">
              <span className="node-info-label">描述:</span>
              <span className="node-info-value node-info-description">
                {(data as any).description}
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
                {data.baseFields.slice(0, 5).map((field, idx) => {
                  const typedField = field as Field;
                  return (
                    <div key={idx} className="node-field-item">
                      <span className="field-name">
                        {typedField.alias || typedField.name}
                      </span>
                      <span className="field-type">
                        {typedField.type === "param" ? "参数" : "基础"}
                      </span>
                    </div>
                  );
                })}
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
