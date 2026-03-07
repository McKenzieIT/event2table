// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import './JoinNode.css';

/**
 * Join configuration structure
 */
interface JoinConfig {
  join_type?: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL' | 'CROSS';
}

/**
 * JoinNode data structure
 */
interface JoinNodeData {
  label?: string;
  config?: JoinConfig;
  [key: string]: unknown;
}

/**
 * JoinNode component props
 */
interface JoinNodeProps {
  data: JoinNodeData;
}

/**
 * JoinNode component
 *
 * Displays a JOIN operation node in the canvas flow.
 * Joins two event data sources with specified join type.
 *
 * Features:
 * - Two input ports (left and right)
 * - One output port
 * - Displays join type badge (INNER, LEFT, RIGHT, FULL, CROSS)
 */
function JoinNode({ data }: JoinNodeProps): React.ReactElement {
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

// ⚡ PERF: 使用 React.memo 优化渲染性能
const JoinNodeMemo = memo(JoinNode);
export default JoinNodeMemo;
