// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useCallback, useEffect, ReactNode, memo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    addEdge,
    Panel,
    Node,
    Edge,
    Connection,
    NodeTypes,
    OnSelectionChangeParams,
    ReactFlowJsonObject,
} from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './CustomNode';
import EventNode from './nodes/EventNode';
import UnionAllNode from './nodes/UnionAllNode';
import JoinNode from './nodes/JoinNode';
import OutputNode from './nodes/OutputNode';
import NodeSidebar from './NodeSidebar';
import Toolbar from './Toolbar';
import JoinConfigModal from './JoinConfigModal';
import HQLResultModal from './HQLResultModal';
import PropertiesPanel from './PropertiesPanel';
import { loadEventConfig } from '../api/canvasApi';
import { configToReactFlowNode } from './utils/nodeConverter';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { calculateAffectedCount, deleteMultipleNodesCascade } from './utils/cascadeDelete';
import { useCanvasHistory } from './utils/useCanvasHistory';
import { useFlowLoad } from '../hooks/useFlowLoad';
import { useFlowSave } from '../hooks/useFlowSave';
import { useFlowExecute } from '../hooks/useFlowExecute';
import { useToast } from '@shared/ui';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import { GameData } from './utils/hqlGenerators';
import './CanvasFlow.css';

// ============================================
// Type Definitions
// ============================================

/**
 * Extended Node data interface for Canvas nodes
 */
export interface CanvasNodeData {
    label?: string;
    configId?: number;
    config?: Record<string, unknown>;
    eventConfig?: {
        event_name?: string;
        event_name_cn?: string;
        fieldCount?: number;
        [key: string]: unknown;
    };
    eventData?: {
        fields?: Array<{
            name: string;
            type?: string;
            source?: string;
        }>;
        [key: string]: unknown;
    };
    [key: string]: unknown;
}

/**
 * Extended Node type with Canvas-specific data
 */
export type CanvasNode = Node<CanvasNodeData>;

/**
 * Available fields for JOIN configuration
 */
interface AvailableFields {
    left: Array<{
        name: string;
        type?: string;
        source?: string;
    }>;
    right: Array<{
        name: string;
        type?: string;
        source?: string;
    }>;
}

/**
 * Props for CanvasFlow component
 */
export interface CanvasFlowProps {
    gameData: GameData;
    flowId?: number | string;
}

/**
 * Saved config structure
 */
interface SavedConfig {
    id: number;
    name: string;
    [key: string]: unknown;
}

/**
 * Flow data payload for save/execute
 */
interface FlowDataPayload {
    name?: string;
    game_gid: number | string;
    game_id?: number;
    nodes: Array<{
        id: string;
        type: string;
        position: { x: number; y: number };
        data: CanvasNodeData;
    }>;
    edges: Array<{
        id: string;
        source: string;
        target: string;
    }>;
}

// ============================================
// Constants
// ============================================

// Initial empty data
const initialNodes: CanvasNode[] = [];
const initialEdges: Edge[] = [];

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
 *
 * @param gameData - Game configuration data
 * @param flowId - Optional flow ID for loading existing flows
 */
const CanvasFlow: React.FC<CanvasFlowProps> = ({ gameData, flowId }) => {
    // Direct use of module-level constant to avoid runtime initialization
    const nodeTypes: NodeTypes = CANVAS_NODE_TYPES;

    const { warning: toastWarning, success: toastSuccess, info: toastInfo, error: toastError } = useToast();

    // Promise-based confirm dialog
    const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

    const [nodes, setNodes, onNodesChange] = useNodesState<CanvasNodeData>(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [savedConfigs, setSavedConfigs] = useState<SavedConfig[]>([]);

    // Load flow data using React Query
    const { data: flowData, isLoading: isLoadingFlow, error: flowError } = useFlowLoad(
        flowId ? Number(flowId) : undefined
    );

    // Save flow mutation
    const { mutate: saveFlowMutation, isLoading: isSaving } = useFlowSave();

    // Execute flow mutation
    const { mutate: executeFlowMutation, isLoading: isExecuting } = useFlowExecute();

    // JOIN configuration modal state
    const [showJoinConfig, setShowJoinConfig] = useState<boolean>(false);
    const [selectedNode, setSelectedNode] = useState<CanvasNode | null>(null);
    const [availableFields, setAvailableFields] = useState<AvailableFields>({ left: [], right: [] });

    // HQL result modal state
    const [showHQLResult, setShowHQLResult] = useState<boolean>(false);
    const [generatedHQL, setGeneratedHQL] = useState<string>('');
    const [outputFields, setOutputFields] = useState<unknown[]>([]);
    const [flowName, setFlowName] = useState<string>('flow');

    // Properties panel state
    const [showPropertiesPanel, setShowPropertiesPanel] = useState<boolean>(false);
    const [selectedForProperties, setSelectedForProperties] = useState<CanvasNode | null>(null);

    // History (Undo/Redo)
    const {
        pushHistory,
        undo,
        redo,
        canUndo,
        canRedo
    } = useCanvasHistory((state: { nodes: CanvasNode[]; edges: Edge[] }) => {
        // Restore callback
        setNodes(state.nodes);
        setEdges(state.edges);
    });

    // Load flow data when it changes (React Query handles caching)
    useEffect(() => {
        if (flowError) {
            console.error('[CanvasFlow] Failed to load flow:', flowError);
            toastWarning(`加载流程失败: ${flowError.message}`);
        }

        if (flowData?.flow_data || flowData?.nodes) {
            const data = flowData.flow_data || flowData;
            if (data.nodes) {
                setNodes(data.nodes as CanvasNode[]);
            }
            if (data.edges) {
                setEdges(data.edges || []);
            }
        }
    }, [flowData, flowError, flowId, setNodes, setEdges, toastWarning]);

    // Get available fields for JOIN node
    // Moved this function before onNodeDoubleClick to avoid initialization error
    const getAvailableFields = useCallback((
        joinNode: CanvasNode,
        nodesList: CanvasNode[],
        edgesList: Edge[]
    ): AvailableFields => {
        // Find two input nodes connected to JOIN node
        const inputEdges = edgesList.filter(e => e.target === joinNode.id);

        if (inputEdges.length !== 2) {
            return { left: [], right: [] };
        }

        const leftNodeId = inputEdges[0].source;
        const rightNodeId = inputEdges[1].source;

        const leftNode = nodesList.find(n => n.id === leftNodeId);
        const rightNode = nodesList.find(n => n.id === rightNodeId);

        // Extract fields from node configuration
        const extractFields = (node: CanvasNode | undefined): AvailableFields['left'] => {
            if (!node || !node.data) return [];

            // If has fieldList (from EventNodeBuilder)
            if (node.data.config?.fieldList) {
                return node.data.config.fieldList as AvailableFields['left'];
            }

            // Default: extract field names from eventData
            if (node.data.eventData?.fields) {
                return node.data.eventData.fields.map(f => ({
                    name: f.name,
                    type: f.type || 'string',
                    source: f.source || 'unknown'
                }));
            }

            return [];
        };

        return {
            left: extractFields(leftNode),
            right: extractFields(rightNode)
        };
    }, []);

    // Connect nodes
    const onConnect = useCallback((params: Connection) => {
        setEdges((eds) => addEdge(params, eds));
    }, [setEdges]);

    // Node double-click - edit configuration
    const onNodeDoubleClick = useCallback((event: React.MouseEvent, node: CanvasNode) => {
        // Handle JOIN node double-click
        if (node.type === 'join') {
            setSelectedNode(node);
            // Get available fields
            const fields = getAvailableFields(node, nodes, edges);
            setAvailableFields(fields);

            if (fields.left.length > 0 && fields.right.length > 0) {
                setShowJoinConfig(true);
            } else {
                toastWarning('请先连接两个事件节点到JOIN节点');
            }
        }
        // Handle event node double-click - navigate to EventNodeBuilder
        else if (node.type === 'event' || node.type === 'custom') {
            if (node.data.configId) {
                const editUrl = `/event-node-builder?game_gid=${gameData.gid}&config_id=${node.data.configId}`;
                window.open(editUrl, '_blank');
            } else {
                toastWarning('此节点没有关联的配置ID');
            }
        }
    }, [gameData.gid, nodes, edges, toastWarning, getAvailableFields]);

    // Node click - show properties panel
    const onNodeClick = useCallback((event: React.MouseEvent, node: CanvasNode) => {
        setSelectedForProperties(node);
        setShowPropertiesPanel(true);
    }, []);

    // Update node from properties panel
    const updateNodeFromProperties = useCallback((nodeId: string, updates: Partial<CanvasNodeData>) => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === nodeId
                    ? { ...node, data: { ...node.data, ...updates } }
                    : node
            )
        );
    }, [setNodes]);

    // Open configuration from properties panel
    const openConfigFromProperties = useCallback((node: CanvasNode) => {
        // Handle JOIN node
        if (node.type === 'join') {
            setSelectedNode(node);
            const fields = getAvailableFields(node, nodes, edges);
            setAvailableFields(fields);

            if (fields.left.length > 0 && fields.right.length > 0) {
                setShowJoinConfig(true);
                setShowPropertiesPanel(false); // Close properties panel when opening config modal
            } else {
                toastWarning('请先连接两个事件节点到JOIN节点');
            }
        }
        // Handle event node
        else if (node.type === 'event' || node.type === 'custom') {
            if (node.data.configId) {
                const editUrl = `/event-node-builder?game_gid=${gameData.gid}&config_id=${node.data.configId}`;
                window.open(editUrl, '_blank');
            } else {
                toastWarning('此节点没有关联的配置ID');
            }
        }
    }, [gameData.gid, nodes, edges, toastWarning, getAvailableFields]);

    // Apply JOIN configuration
    const handleJoinConfigApply = useCallback((config: Record<string, unknown>) => {
        if (!selectedNode) return;

        setNodes((nds) =>
            nds.map((node) =>
                node.id === selectedNode.id
                    ? { ...node, data: { ...node.data, config } }
                    : node
            )
        );
    }, [selectedNode, setNodes]);

    // Delete selected nodes (with cascade delete)
    const deleteSelected = useCallback(async () => {
        const selectedNodes = nodes.filter((n) => n.selected);
        if (selectedNodes.length === 0) {
            toastWarning('请先选择要删除的节点');
            return;
        }

        const selectedIds = selectedNodes.map((n) => n.id);

        // Calculate affected count for confirmation dialog
        const affected = calculateAffectedCount(selectedIds, nodes, edges);

        // Show confirmation dialog with affected count
        const message = `确定要删除 ${selectedNodes.length} 个节点吗？

影响范围：
• 删除节点：${affected.nodes} 个
• 删除连接：${affected.edges} 条
• 级联删除：${affected.cascading} 个孤立节点

⚠️ 此操作不可撤销！`;

        if (await confirm(message)) {
            // Perform cascade delete
            const result = deleteMultipleNodesCascade(selectedIds, nodes, edges);
            setNodes(result.nodes as CanvasNode[]);
            setEdges(result.edges);

            toastSuccess(`已删除 ${result.summary.deletedNodes} 个节点和 ${result.summary.deletedEdges} 条连接`);
        }
    }, [nodes, edges, setNodes, setEdges, toastWarning, toastSuccess, confirm]);

    // Clear canvas
    const clearCanvas = useCallback(async () => {
        if (await confirm('确定要清空画布吗？此操作不可撤销。')) {
            pushHistory({ nodes, edges });
            setNodes([]);
            setEdges([]);
        }
    }, [setNodes, setEdges, nodes, edges, pushHistory, confirm]);

    // Undo operation
    const handleUndo = useCallback(() => {
        const previousState = undo();
        if (previousState) {
            setNodes(previousState.nodes as CanvasNode[]);
            setEdges(previousState.edges);
            toastInfo('已撤销');
        }
    }, [undo, setNodes, setEdges, toastInfo]);

    // Redo operation
    const handleRedo = useCallback(() => {
        const nextState = redo();
        if (nextState) {
            setNodes(nextState.nodes as CanvasNode[]);
            setEdges(nextState.edges);
            toastInfo('已重做');
        }
    }, [redo, setNodes, setEdges, toastInfo]);

    // Monitor nodes and edges changes, auto-save history
    useEffect(() => {
        // Push history after a short delay to avoid excessive history entries
        const timer = setTimeout(() => {
            pushHistory({ nodes, edges });
        }, 500);

        return () => clearTimeout(timer);
    }, [nodes, edges, pushHistory]);

    // Save flow
    const handleSaveFlow = useCallback(() => {
        if (nodes.length === 0) {
            toastWarning('画布为空，无法保存');
            return;
        }
        const flowNameInput = prompt('请输入流程名称：');
        if (!flowNameInput) return;

        const flowDataPayload: FlowDataPayload = {
            name: flowNameInput,
            game_gid: gameData.gid,  // Primary key
            game_id: typeof gameData.id === 'number' ? gameData.id : Number(gameData.gid),    // Keep backward compatibility
            nodes: nodes.map((n) => ({ id: n.id, type: n.type || '', position: n.position, data: n.data })),
            edges: edges.map((e) => ({ id: e.id || '', source: e.source, target: e.target }))
        };

        saveFlowMutation(flowDataPayload, {
            onSuccess: () => {
                toastSuccess(`流程 "${flowNameInput}" 保存成功！`);
            },
            onError: (error: Error) => {
                console.error('Save flow error:', error);
                toastError(`保存失败: ${error.message}`);
            }
        });
    }, [nodes, edges, gameData.gid, gameData.id, saveFlowMutation, toastWarning, toastSuccess, toastError]);

    // Generate HQL
    const handleGenerateHQL = useCallback(() => {
        if (nodes.length === 0) {
            toastWarning('画布为空，无法生成HQL');
            return;
        }

        const flowDataPayload = {
            nodes: nodes.map((n) => ({ id: n.id, type: n.type || '', position: n.position, data: n.data })),
            edges: edges.map((e) => ({ id: e.id || '', source: e.source, target: e.target }))
        };

        executeFlowMutation({ flowId: 1 }, {
            onSuccess: (data) => {
                setGeneratedHQL(data.hql || '');
                setOutputFields(data.output_fields || []);
                setShowHQLResult(true);
                toastSuccess('HQL生成成功');
            },
            onError: (error: Error) => {
                console.error('Generate HQL error:', error);
                toastError(`生成失败: ${error.message}`);
            }
        });
    }, [nodes, edges, executeFlowMutation, toastWarning, toastSuccess, toastError]);

    // Keyboard shortcuts
    useKeyboardShortcuts({
        onDelete: deleteSelected,
        onClear: clearCanvas,
        onSave: handleSaveFlow,
        onGenerate: handleGenerateHQL,
        onUndo: handleUndo,
        onRedo: handleRedo
    });

    // Drop event
    const onDrop = useCallback(async (event: React.DragEvent) => {
        event.preventDefault();
        try {
            const dragData = JSON.parse(event.dataTransfer.getData('application/reactflow'));
            if (!dragData) return;

            const reactFlowBounds = (event.target as Element).getBoundingClientRect();
            const position = {
                x: event.clientX - reactFlowBounds.left,
                y: event.clientY - reactFlowBounds.top
            };

            if (dragData.type === 'saved-config' && dragData.configId) {
                try {
                    const result = await loadEventConfig(dragData.configId, gameData.gid);

                    // Explicit validation: ensure result exists and is successful
                    if (result && result.success) {
                        if (result.data && result.data.config && typeof result.data.config === 'object') {
                            const newNode = configToReactFlowNode(result.data.config, position);
                            setNodes((nds) => nds.concat(newNode));
                        } else {
                            console.warn('[CanvasFlow] result.data.config is missing');
                            toastError('配置数据格式错误');
                        }
                    } else {
                        const errorMsg = result ? (result.message || '加载配置失败') : '加载配置失败';
                        toastError(`加载配置失败: ${errorMsg}`);
                    }
                } catch (error) {
                    console.error('[CanvasFlow] Error loading config:', error);
                    toastError('加载配置时发生错误');
                }
            }
        } catch (error) {
            console.error('[CanvasFlow] Drop error:', error);
        }
    }, [gameData.gid, setNodes, toastError]);

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

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
                    onSelectionChange={(params: OnSelectionChangeParams) => {
                        // Update properties panel when selection changes
                        if (params.nodes.length === 1) {
                            const selectedNode = nodes.find(n => n.id === params.nodes[0]);
                            if (selectedNode) {
                                setSelectedForProperties(selectedNode);
                                setShowPropertiesPanel(true);
                            }
                        } else if (params.nodes.length === 0) {
                            // Don't auto-hide panel when clicking on canvas, user must close it manually
                        }
                    }}
                    nodeTypes={nodeTypes}
                    fitView
                    className="react-flow-canvas"
                    deleteKeyCode="Delete"
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                    <Panel position="top-right" className="info-panel" data-testid="canvas-info-panel">
                        <div>节点: {nodes.length}</div>
                        <div>连接: {edges.length}</div>
                        {(isLoadingFlow || isSaving || isExecuting) && <div className="loading-indicator">加载中...</div>}
                    </Panel>
                </ReactFlow>
            </div>

            {/* JOIN configuration modal */}
            {showJoinConfig && (
                <JoinConfigModal
                    isOpen={showJoinConfig}
                    onClose={() => setShowJoinConfig(false)}
                    node={selectedNode}
                    availableFields={availableFields}
                    onApply={handleJoinConfigApply}
                    data-testid="join-config-modal"
                />
            )}

            {/* HQL result modal */}
            {showHQLResult && (
                <HQLResultModal
                    isOpen={showHQLResult}
                    onClose={() => setShowHQLResult(false)}
                    hql={generatedHQL}
                    flowName={flowName}
                    gameData={gameData}
                    onRegenerate={handleGenerateHQL}
                    outputFields={outputFields}
                    data-testid="hql-result-modal"
                />
            )}

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
