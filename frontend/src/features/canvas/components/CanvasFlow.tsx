// ⚡️ REACT PERF - Canvas: Refactored main component with extracted modules
// ✅ Performance optimization: All business logic extracted to useCanvasFlow hook
// ✅ Component size reduced from 648 to ~250 lines for better maintainability
// See: docs/reports/2026-03-06/FEATURES-OPTIMIZATION-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { memo, NodeTypes } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './CustomNode';
import EventNode from './nodes/EventNode';
import UnionAllNode from './nodes/UnionAllNode';
import JoinNode from './nodes/JoinNode';
import OutputNode from './nodes/OutputNode';
import NodeSidebar from './NodeSidebar';
import Toolbar from './Toolbar';
import PropertiesPanel from './PropertiesPanel';
import CanvasInfoPanel from './CanvasInfoPanel';
import CanvasModals from './CanvasModals';
import { useCanvasFlow } from './useCanvasFlow';
import { CanvasFlowProps } from './CanvasFlow.types';
import './CanvasFlow.css';

// ============================================
// Constants
// ============================================

// Define nodeTypes constant at module level to avoid TDZ errors
const CANVAS_NODE_TYPES: NodeTypes = {
    custom: CustomNode,
    event: EventNode,
    union_all: UnionAllNode,
    join: JoinNode,
    output: OutputNode,
};

// ============================================
// Component
// ============================================

/**
 * CanvasFlow Component
 *
 * Main canvas component for visual flow editing with drag-and-drop node support
 * Refactored to use extracted modules for better maintainability
 *
 * @param gameData - Game configuration data
 * @param flowId - Optional flow ID for loading existing flows
 */
const CanvasFlow: React.FC<CanvasFlowProps> = ({ gameData, flowId }) => {
    // Use custom hook for all business logic
    const canvasFlow = useCanvasFlow(gameData, flowId);

    // Destructure hook return values for cleaner JSX
    const {
        nodes,
        edges,
        savedConfigs,
        isLoading,
        showJoinConfig,
        selectedNode,
        availableFields,
        showHQLResult,
        generatedHQL,
        outputFields,
        flowName,
        showPropertiesPanel,
        selectedForProperties,
        onNodesChange,
        onEdgesChange,
        onConnect,
        onNodeDoubleClick,
        onNodeClick,
        handleSelectionChange,
        onDrop,
        onDragOver,
        updateNodeFromProperties,
        openConfigFromProperties,
        handleJoinConfigApply,
        setShowJoinConfig,
        setShowHQLResult,
        setShowPropertiesPanel,
        setSavedConfigs,
        ConfirmDialogComponent,
    } = canvasFlow;

    return (
        <div className="canvas-flow-container" data-testid="canvas-flow-container">
            <NodeSidebar
                gameData={gameData}
                savedConfigs={savedConfigs}
                onConfigsLoad={setSavedConfigs}
            />
            <div className="react-flow-wrapper" data-testid="react-flow-wrapper">
                <Toolbar gameData={gameData} />
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    onNodeClick={onNodeClick}
                    onNodeDoubleClick={onNodeDoubleClick}
                    onSelectionChange={handleSelectionChange}
                    nodeTypes={CANVAS_NODE_TYPES}
                    fitView
                    className="react-flow-canvas"
                    deleteKeyCode="Delete"
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                    <CanvasInfoPanel
                        nodeCount={nodes.length}
                        edgeCount={edges.length}
                        isLoading={isLoading}
                    />
                </ReactFlow>
            </div>

            {/* Modals - extracted to CanvasModals component */}
            <CanvasModals
                showJoinConfig={showJoinConfig}
                showHQLResult={showHQLResult}
                selectedNode={selectedNode}
                availableFields={availableFields}
                generatedHQL={generatedHQL}
                flowName={flowName}
                gameData={gameData}
                outputFields={outputFields}
                onCloseJoinConfig={() => setShowJoinConfig(false)}
                onJoinConfigApply={handleJoinConfigApply}
                onCloseHQLResult={() => setShowHQLResult(false)}
                onRegenerateHQL={canvasFlow.handleGenerateHQL}
            />

            {/* Properties panel */}
            {showPropertiesPanel && (
                <PropertiesPanel
                    selectedNode={selectedForProperties}
                    nodes={nodes}
                    edges={edges}
                    onUpdateNode={updateNodeFromProperties}
                    onConfigure={openConfigFromProperties}
                    onClose={() => setShowPropertiesPanel(false)}
                    data-testid="properties-panel"
                />
            )}

            {/* Promise-based confirm dialog */}
            <ConfirmDialogComponent />
        </div>
    );
};

// ✅ 添加 React.memo 优化渲染性能
const CanvasFlowMemo = memo(CanvasFlow);

export default CanvasFlowMemo;