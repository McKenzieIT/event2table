import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    addEdge,
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
import './CanvasFlow.css';

// 初始空数据
const initialNodes = [];
const initialEdges = [];

// 定义nodeTypes常量，避免在组件内部初始化导致的TDZ错误
// 将其移到模块级别，确保在组件函数之前定义
const CANVAS_NODE_TYPES = {
    custom: CustomNode,
    event: EventNode,
    union_all: UnionAllNode,
    join: JoinNode,
    output: OutputNode,
};

export default function CanvasFlow({ gameData, flowId }) {
    // 直接使用模块级常量，避免运行时初始化
    const nodeTypes = CANVAS_NODE_TYPES;

    const { warning: toastWarning, success: toastSuccess, info: toastInfo, error: toastError } = useToast();

    // Promise-based confirm dialog
    const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [savedConfigs, setSavedConfigs] = useState([]);

    // Load flow data using React Query
    const { data: flowData, isLoading: isLoadingFlow, error: flowError } = useFlowLoad(flowId);

    // Save flow mutation
    const { mutate: saveFlowMutation, isLoading: isSaving } = useFlowSave();

    // Execute flow mutation
    const { mutate: executeFlowMutation, isLoading: isExecuting } = useFlowExecute();

    // JOIN配置模态框状态
    const [showJoinConfig, setShowJoinConfig] = useState(false);
    const [selectedNode, setSelectedNode] = useState(null);
    const [availableFields, setAvailableFields] = useState({ left: [], right: [] });

    // HQL结果模态框状态
    const [showHQLResult, setShowHQLResult] = useState(false);
    const [generatedHQL, setGeneratedHQL] = useState('');
    const [outputFields, setOutputFields] = useState([]);
    const [flowName, setFlowName] = useState('flow');

    // 属性面板状态
    const [showPropertiesPanel, setShowPropertiesPanel] = useState(false);
    const [selectedForProperties, setSelectedForProperties] = useState(null);

    // 历史记录（Undo/Redo）
    const {
        pushHistory,
        undo,
        redo,
        canUndo,
        canRedo
    } = useCanvasHistory(({ nodes, edges }) => {
        // Restore callback
        setNodes(nodes);
        setEdges(edges);
    });

    // Load flow data when it changes (React Query handles caching)
    useEffect(() => {
        if (flowError) {
            console.error('[CanvasFlow] Failed to load flow:', flowError);
            toastWarning(`加载流程失败: ${flowError.message}`);
        }

        if (flowData?.flow_graph || flowData?.nodes) {
            const data = flowData.flow_graph || flowData;
            if (data.nodes) {
                setNodes(data.nodes);
            }
            if (data.edges) {
                setEdges(data.edges || []);
            }
        }
    }, [flowData, flowError, flowId, setNodes, setEdges, toastWarning]);

    // 获取JOIN节点的可用字段
    // Moved this function before onNodeDoubleClick to avoid initialization error
    const getAvailableFields = useCallback((joinNode, nodes, edges) => {
        // 找到连接到JOIN节点的两个输入节点
        const inputEdges = edges.filter(e => e.target === joinNode.id);

        if (inputEdges.length !== 2) {
            return { left: [], right: [] };
        }

        const leftNodeId = inputEdges[0].source;
        const rightNodeId = inputEdges[1].source;

        const leftNode = nodes.find(n => n.id === leftNodeId);
        const rightNode = nodes.find(n => n.id === rightNodeId);

        // 从节点配置中提取字段
        const extractFields = (node) => {
            if (!node || !node.data) return [];

            // 如果有fieldList（来自EventNodeBuilder）
            if (node.data.config?.fieldList) {
                return node.data.config.fieldList;
            }

            // 默认从eventData中提取字段名称
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

    // 连接节点
    const onConnect = useCallback((params) => {
        setEdges((eds) => addEdge(params, eds));
    }, []);

    // 节点双击 - 编辑配置
    const onNodeDoubleClick = useCallback((event, node) => {
        // 处理JOIN节点双击
        if (node.type === 'join') {
            setSelectedNode(node);
            // 获取可用字段
            const fields = getAvailableFields(node, nodes, edges);
            setAvailableFields(fields);

            if (fields.left.length > 0 && fields.right.length > 0) {
                setShowJoinConfig(true);
            } else {
                toastWarning('请先连接两个事件节点到JOIN节点');
            }
        }
        // 处理事件节点双击 - 跳转到EventNodeBuilder
        else if (node.type === 'event' || node.type === 'custom') {
            if (node.data.configId) {
                const editUrl = `/event-node-builder?game_gid=${gameData.gid}&config_id=${node.data.configId}`;
                window.open(editUrl, '_blank');
            } else {
                toastWarning('此节点没有关联的配置ID');
            }
        }
    }, [gameData.gid, nodes, edges, toastWarning]);

    // 节点点击 - 显示属性面板
    const onNodeClick = useCallback((event, node) => {
        setSelectedForProperties(node);
        setShowPropertiesPanel(true);
    }, []);

    // 从属性面板更新节点
    const updateNodeFromProperties = useCallback((nodeId, updates) => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === nodeId
                    ? { ...node, data: { ...node.data, ...updates } }
                    : node
            )
        );
    }, [setNodes]);

    // 从属性面板打开配置
    const openConfigFromProperties = useCallback((node) => {
        // 处理JOIN节点
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
        // 处理事件节点
        else if (node.type === 'event' || node.type === 'custom') {
            if (node.data.configId) {
                const editUrl = `/event-node-builder?game_gid=${gameData.gid}&config_id=${node.data.configId}`;
                window.open(editUrl, '_blank');
            } else {
                toastWarning('此节点没有关联的配置ID');
            }
        }
    }, [gameData.gid, nodes, edges, toastWarning]);

    // 应用JOIN配置
    const handleJoinConfigApply = useCallback((config) => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === selectedNode.id
                    ? { ...node, data: { ...node.data, config } }
                    : node
            )
        );
    }, [selectedNode, setNodes]);

    // 删除选中节点（带级联删除）
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
            setNodes(result.nodes);
            setEdges(result.edges);

            toastSuccess(`已删除 ${result.summary.deletedNodes} 个节点和 ${result.summary.deletedEdges} 条连接`);
        }
    }, [nodes, edges, setNodes, setEdges, toastWarning, toastSuccess, confirm]);

    // 清空画布
    const clearCanvas = useCallback(async () => {
        if (await confirm('确定要清空画布吗？此操作不可撤销。')) {
            pushHistory({ nodes, edges });
            setNodes([]);
            setEdges([]);
        }
    }, [setNodes, setEdges, nodes, edges, pushHistory, confirm]);

    // 撤销操作
    const handleUndo = useCallback(() => {
        const previousState = undo();
        if (previousState) {
            setNodes(previousState.nodes);
            setEdges(previousState.edges);
            toastInfo('已撤销');
        }
    }, [undo, setNodes, setEdges, toastInfo]);

    // 重做操作
    const handleRedo = useCallback(() => {
        const nextState = redo();
        if (nextState) {
            setNodes(nextState.nodes);
            setEdges(nextState.edges);
            toastInfo('已重做');
        }
    }, [redo, setNodes, setEdges, toastInfo]);

    // 监听节点和连接变化，自动保存历史
    useEffect(() => {
        // Push history after a short delay to avoid excessive history entries
        const timer = setTimeout(() => {
            pushHistory({ nodes, edges });
        }, 500);

        return () => clearTimeout(timer);
    }, [nodes, edges, pushHistory]);

    // 保存流程
    const handleSaveFlow = useCallback(() => {
        if (nodes.length === 0) {
            toastWarning('画布为空，无法保存');
            return;
        }
        const flowNameInput = prompt('请输入流程名称：');
        if (!flowNameInput) return;

        const flowDataPayload = {
            name: flowNameInput,
            game_gid: gameData.gid,  // 主键
            game_id: gameData.id,    // 保留向后兼容
            nodes: nodes.map((n) => ({ id: n.id, type: n.type, position: n.position, data: n.data })),
            edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target }))
        };

        saveFlowMutation(flowDataPayload, {
            onSuccess: () => {
                toastSuccess(`流程 "${flowNameInput}" 保存成功！`);
            },
            onError: (error) => {
                console.error('Save flow error:', error);
                toastError(`保存失败: ${error.message}`);
            }
        });
    }, [nodes, edges, gameData.gid, gameData.id, saveFlowMutation, toastWarning, toastSuccess, toastError]);

    // 生成HQL
    const handleGenerateHQL = useCallback(() => {
        if (nodes.length === 0) {
            toastWarning('画布为空，无法生成HQL');
            return;
        }

        const flowDataPayload = {
            nodes: nodes.map((n) => ({ id: n.id, type: n.type, position: n.position, data: n.data })),
            edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target }))
        };

        executeFlowMutation({ flow_id: 1, flowData: flowDataPayload }, {
            onSuccess: (data) => {
                setGeneratedHQL(data.hql || '');
                setOutputFields(data.output_fields || []);
                setShowHQLResult(true);
                toastSuccess('HQL生成成功');
            },
            onError: (error) => {
                console.error('Generate HQL error:', error);
                toastError(`生成失败: ${error.message}`);
            }
        });
    }, [nodes, edges, executeFlowMutation, toastWarning, toastSuccess, toastError]);

    // 键盘快捷键
    useKeyboardShortcuts({
        onDelete: deleteSelected,
        onClear: clearCanvas,
        onSave: handleSaveFlow,
        onGenerate: handleGenerateHQL,
        onUndo: handleUndo,
        onRedo: handleRedo
    });

    // 拖拽结束
    const onDrop = useCallback(async (event) => {
        event.preventDefault();
        try {
            const dragData = JSON.parse(event.dataTransfer.getData('application/reactflow'));
            if (!dragData) return;

            const reactFlowBounds = event.target.getBoundingClientRect();
            const position = { x: event.clientX - reactFlowBounds.left, y: event.clientY - reactFlowBounds.top };

            if (dragData.type === 'saved-config' && dragData.configId) {
                try {
                    const result = await loadEventConfig(dragData.configId, gameData.gid);

                    // 显式验证：确保result存在且成功
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

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    return (
        <div className="canvas-flow-container" data-testid="canvas-flow-container">
            <NodeSidebar gameData={gameData} savedConfigs={savedConfigs} onConfigsLoad={setSavedConfigs} />
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
                    onSelectionChange={(params) => {
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

            {/* JOIN配置模态框 */}
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

            {/* HQL结果模态框 */}
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

            {/* 属性面板 */}
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
}
