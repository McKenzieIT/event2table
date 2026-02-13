import React from 'react';
import { Handle, Position } from 'reactflow';
import './JoinNode.css';

export default function JoinNode({ data }) {
  const joinType = data.config?.join_type || 'INNER';

  return (
    <div className="custom-node join-node">
      {/* 输入端口1 */}
      <Handle
        type="target"
        position={Position.Left}
        id="input-left"
        style={{ top: '30%' }}
        className="node-port input-port"
      />

      {/* 输入端口2 */}
      <Handle
        type="target"
        position={Position.Left}
        id="input-right"
        style={{ top: '70%' }}
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
        <span className="node-icon">🔀</span>
        <span className="node-title">JOIN</span>
        <span className="join-type-badge">{joinType}</span>
      </div>

      {/* 节点内容 */}
      <div className="node-body">
        <div className="node-description">
          连接两个事件数据
        </div>
      </div>
    </div>
  );
}