// ⚡️ REACT PERF - Canvas: Info panel component with React.memo optimization
// Extracted from CanvasFlow.tsx for better maintainability

import React, { memo } from 'react';
import { Panel } from 'reactflow';

import { CanvasInfoPanelProps } from './CanvasFlow.types';

/**
 * CanvasInfoPanel Component
 *
 * Displays canvas statistics (node count, edge count, loading status)
 * Optimized with React.memo to prevent unnecessary re-renders
 */
const CanvasInfoPanel: React.FC<CanvasInfoPanelProps> = memo(({ 
    nodeCount, 
    edgeCount, 
    isLoading 
}) => {
    return (
        <Panel position="top-right" className="info-panel" data-testid="canvas-info-panel">
            <div>节点: {nodeCount}</div>
            <div>连接: {edgeCount}</div>
            {isLoading && <div className="loading-indicator">加载中...</div>}
        </Panel>
    );
});

CanvasInfoPanel.displayName = 'CanvasInfoPanel';

export default CanvasInfoPanel;
