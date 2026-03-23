// ⚡️ REACT PERF - Canvas: Custom hook for canvas flow logic
// Extracted from CanvasFlow.tsx for better testability and reusability

import { useState, useCallback, useEffect } from 'react';
import { useNodesState, useEdgesState, addEdge, Connection, Edge, OnSelectionChangeParams } from 'reactflow';
import { useToast } from '@shared/ui';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import { loadEventConfig } from '../api/canvasApi';
import { configToReactFlowNode } from './utils/nodeConverter';
import { calculateAffectedCount, deleteMultipleNodesCascade } from './utils/cascadeDelete';
import { useCanvasHistory } from './utils/useCanvasHistory';
import { useFlowLoad } from '../hooks/useFlowLoad';
import { useFlowSave } from '../hooks/useFlowSave';
import { useFlowExecute } from '../hooks/useFlowExecute';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import type { GameData } from '@/shared/types/game-types';
import {
    CanvasNode,
    CanvasNodeData,
    AvailableFields,
    SavedConfig,
    FlowDataPayload,
} from './CanvasFlow.types';

/**
 * useCanvasFlow Hook
 *
 * Encapsulates all business logic for the CanvasFlow component
 * Handles state management, node operations, and API interactions
 */
export const useCanvasFlow = (gameData: GameData, flowId?: number | string) => {
    const { warning: toastWarning, success: toastSuccess, info: toastInfo, error: toastError } = useToast();
    const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

    // Node and edge state
    const [nodes, setNodes, onNodesChange] = useNodesState<CanvasNodeData>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [savedConfigs, setSavedConfigs] = useState<SavedConfig[]>([]);

    // Load flow data using React Query
    const { data: flowData, isLoading: isLoadingFlow, error: flowError } = useFlowLoad(
        flowId ? Number(flowId) : undefined
    );

    // Save and execute mutations
    const { mutate: saveFlowMutation, isLoading: isSaving } = useFlowSave();
    const { mutate: executeFlowMutation, isLoading: isExecuting } = useFlowExecute();

    // Modal states
    const [showJoinConfig, setShowJoinConfig] = useState<boolean>(false);
    const [selectedNode, setSelectedNode] = useState<CanvasNode | null>(null);
    const [availableFields, setAvailableFields] = useState<AvailableFields>({ left: [], right: [] });
    const [showHQLResult, setShowHQLResult] = useState<boolean>(false);
    const [generatedHQL, setGeneratedHQL] = useState<string>('');
    const [outputFields, setOutputFields] = useState<unknown[]>([]);
    const [flowName, setFlowName] = useState<string>('flow');

    // Properties panel state
    const [showPropertiesPanel, setShowPropertiesPanel] = useState<boolean>(false);
    const [selectedForProperties, setSelectedForProperties] = useState<CanvasNode | null>(null);

    // History management
    const {
        pushHistory,
        undo,
        redo,
        canUndo,
        canRedo
    } = useCanvasHistory((state: { nodes: CanvasNode[]; edges: Edge[] }) => {
        setNodes(state.nodes);
        setEdges(state.edges);
    });

    // Load flow data when it changes
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
    const getAvailableFields = useCallback((
        joinNode: CanvasNode,
        nodesList: CanvasNode[],
        edgesList: Edge[]
    ): AvailableFields => {
        const inputEdges = edgesList.filter(e => e.target === joinNode.id);

        if (inputEdges.length !== 2) {
            return { left: [], right: [] };
        }

        const leftNodeId = inputEdges[0].source;
        const rightNodeId = inputEdges[1].source;

        const leftNode = nodesList.find(n => n.id === leftNodeId);
        const rightNode = nodesList.find(n => n.id === rightNodeId);

        const extractFields = (node: CanvasNode | undefined): AvailableFields['left'] => {
            if (!node || !node.data) return [];

            if (node.data.config?.fieldList) {
                return node.data.config.fieldList as AvailableFields['left'];
            }

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

    // Node double-click handler
    const onNodeDoubleClick = useCallback((event: React.MouseEvent, node: CanvasNode) => {
        if (node.type === 'join') {
            setSelectedNode(node);
            const fields = getAvailableFields(node, nodes, edges);
            setAvailableFields(fields);

            if (fields.left.length > 0 && fields.right.length > 0) {
                setShowJoinConfig(true);
            } else {
                toastWarning('请先连接两个事件节点到JOIN节点');
            }
        } else if (node.type === 'event' || node.type === 'custom') {
            if (node.data.configId) {
                const editUrl = `/event-node-builder?game_gid=${gameData.gid}&config_id=${node.data.configId}`;
                window.open(editUrl, '_blank');
            } else {
                toastWarning('此节点没有关联的配置ID');
            }
        }
    }, [gameData.gid, nodes, edges, toastWarning, getAvailableFields]);

    // Node click handler
    const onNodeClick = useCallback((event: React.MouseEvent, node: CanvasNode) => {
        setSelectedForProperties(node);
        setShowPropertiesPanel(true);
    }, []);

    // Selection change handler
    const handleSelectionChange = useCallback((params: OnSelectionChangeParams) => {
        if (params.nodes.length === 1) {
            const selectedNode = nodes.find(n => n.id === params.nodes[0]);
            if (selectedNode) {
                setSelectedForProperties(selectedNode);
                setShowPropertiesPanel(true);
            }
        }
    }, [nodes]);

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
        if (node.type === 'join') {
            setSelectedNode(node);
            const fields = getAvailableFields(node, nodes, edges);
            setAvailableFields(fields);

            if (fields.left.length > 0 && fields.right.length > 0) {
                setShowJoinConfig(true);
                setShowPropertiesPanel(false);
            } else {
                toastWarning('请先连接两个事件节点到JOIN节点');
            }
        } else if (node.type === 'event' || node.type === 'custom') {
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

    // Delete selected nodes
    const deleteSelected = useCallback(async () => {
        const selectedNodes = nodes.filter((n) => n.selected);
        if (selectedNodes.length === 0) {
            toastWarning('请先选择要删除的节点');
            return;
        }

        const selectedIds = selectedNodes.map((n) => n.id);
        const affected = calculateAffectedCount(selectedIds, nodes, edges);

        const message = `确定要删除 ${selectedNodes.length} 个节点吗？

影响范围：
• 删除节点：${affected.nodes} 个
• 删除连接：${affected.edges} 条
• 级联删除：${affected.cascading} 个孤立节点

⚠️ 此操作不可撤销！`;

        if (await confirm(message)) {
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
            game_gid: gameData.gid,
            game_id: typeof gameData.id === 'number' ? gameData.id : Number(gameData.gid),
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

    return {
        // State
        nodes,
        edges,
        savedConfigs,
        isLoading: isLoadingFlow || isSaving || isExecuting,
        
        // Modal states
        showJoinConfig,
        selectedNode,
        availableFields,
        showHQLResult,
        generatedHQL,
        outputFields,
        flowName,
        
        // Properties panel states
        showPropertiesPanel,
        selectedForProperties,
        
        // History states
        canUndo,
        canRedo,
        
        // Event handlers
        onNodesChange,
        onEdgesChange,
        onConnect,
        onNodeDoubleClick,
        onNodeClick,
        handleSelectionChange,
        onDrop,
        onDragOver,
        
        // Action handlers
        updateNodeFromProperties,
        openConfigFromProperties,
        handleJoinConfigApply,
        setShowJoinConfig,
        setShowHQLResult,
        setShowPropertiesPanel,
        setSavedConfigs,
        
        // History handlers
        handleUndo,
        handleRedo,
        
        // Keyboard shortcuts handlers
        deleteSelected,
        clearCanvas,
        handleSaveFlow,
        handleGenerateHQL,
        
        // Confirm dialog
        ConfirmDialogComponent,
    };
};
