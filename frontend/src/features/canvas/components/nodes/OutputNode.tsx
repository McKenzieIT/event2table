// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { memo, useMemo } from 'react';
import { Handle, Position } from 'reactflow';
import './OutputNode.css';

/**
 * Output configuration structure
 */
interface OutputConfig {
  view_name?: string;
}

/**
 * OutputNode data structure
 */
interface OutputNodeData {
  label?: string;
  config?: OutputConfig;
  [key: string]: unknown;
}

/**
 * OutputNode component props
 */
interface OutputNodeProps {
  data: OutputNodeData;
}

/**
 * OutputNode component
 *
 * Displays the final output node in the canvas flow.
 * Represents the generated HQL view output.
 *
 * Features:
 * - Single input port
 * - Displays the target view name
 * - No output ports (terminal node)
 */
function OutputNode({ data }: OutputNodeProps): React.ReactElement {
  // ⚡ PERF: 使用 useMemo 缓存视图名称
  const viewName = useMemo(() => data.config?.view_name || '未命名', [data.config?.view_name]);

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

// ⚡ PERF: 使用 React.memo 优化渲染性能
const OutputNodeMemo = memo(OutputNode);
export default OutputNodeMemo;
export type { OutputNodeData, OutputNodeProps };
