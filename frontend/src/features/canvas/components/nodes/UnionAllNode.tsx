// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import './UnionAllNode.css';

/**
 * UnionAllNode data structure
 */
interface UnionAllNodeData {
  label?: string;
  [key: string]: unknown;
}

/**
 * UnionAllNode component props
 */
interface UnionAllNodeProps {
  data: UnionAllNodeData;
}

/**
 * UnionAllNode component
 *
 * Displays a UNION ALL operation node in the canvas flow.
 * Combines multiple event data sources with UNION ALL.
 *
 * Features:
 * - Single input port
 * - Single output port
 * - No configuration needed (simple pass-through)
 */
function UnionAllNode({ data }: UnionAllNodeProps): React.ReactElement {
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

// ⚡ PERF: 使用 React.memo 优化渲染性能
const UnionAllNodeMemo = memo(UnionAllNode);
export default UnionAllNodeMemo;
export type { UnionAllNodeData, UnionAllNodeProps };
