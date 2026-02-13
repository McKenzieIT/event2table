import React from 'react';
import { Handle, Position } from 'reactflow';
import './OutputNode.css';

export default function OutputNode({ data }) {
  const viewName = data.config?.view_name || '未命名';

  return (
    <div className="custom-node output-node">
      {/* 输入端口 */}
      <Handle
        type="target"
        position={Position.Left}
        className="node-port input-port"
      />

      {/* 节点头部 */}
      <div className="node-header">
        <span className="node-icon">📤</span>
        <span className="node-title">输出</span>
      </div>

      {/* 节点内容 */}
      <div className="node-body">
        <div className="view-name">
          {viewName}
        </div>
      </div>
    </div>
  );
}