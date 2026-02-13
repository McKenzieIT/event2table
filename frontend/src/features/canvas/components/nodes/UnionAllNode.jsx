import React from 'react';
import { Handle, Position } from 'reactflow';
import './UnionAllNode.css';

export default function UnionAllNode({ data }) {
  return (
    <div className="custom-node union-all-node">
      {/* 输入端口 */}
      <Handle
        type="target"
        position={Position.Left}
        className="node-port input-port"
      />

      {/* 输出端口 */}
      <Handle
        type="source"
        position={Position.Right}
        className="node-port output-port"
      />

      {/* 节点头部 */}
      <div className="node-header">
        <span className="node-icon">🔗</span>
        <span className="node-title">UNION ALL</span>
      </div>

      {/* 节点内容 */}
      <div className="node-body">
        <div className="node-description">
          合并多个事件数据
        </div>
      </div>
    </div>
  );
}