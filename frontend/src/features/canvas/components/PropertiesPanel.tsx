// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { useState, useEffect, useMemo, ChangeEvent } from 'react';
import { Button, Input, EmptyState } from '@shared/ui';
import { FlowNode, FlowEdge } from '../types';
import './PropertiesPanel.css';

/**
 * Node data structure for event nodes
 */
interface EventNodeData {
  label?: string;
  eventConfig?: {
    event_name?: string;
    event_name_cn?: string;
    fieldCount?: number;
  };
  configId?: string;
}

/**
 * Node data structure for JOIN nodes
 */
interface JoinNodeData {
  label?: string;
  config?: {
    join_type?: string;
    conditions?: Array<{
      leftField: string;
      operator: string;
      rightField: string;
    }>;
  };
}

/**
 * Properties Panel Component Props
 */
interface PropertiesPanelProps {
  /**
   * The currently selected node
   */
  selectedNode: FlowNode | null;

  /**
   * All nodes in the canvas
   */
  nodes: FlowNode[];

  /**
   * All edges in the canvas
   */
  edges: FlowEdge[];

  /**
   * Callback when node is updated
   * @param nodeId - The ID of the node to update
   * @param updates - The updates to apply to the node
   */
  onUpdateNode: (nodeId: string, updates: Partial<FlowNode['data']>) => void;

  /**
   * Callback to open configuration modal
   * @param node - The node to configure
   */
  onConfigure?: (node: FlowNode) => void;

  /**
   * Callback to close the panel
   */
  onClose: () => void;
}

/**
 * Connected node information
 */
interface ConnectedNode {
  id: string;
  label: string;
  type: string;
}

/**
 * Connections information
 */
interface Connections {
  inputs: ConnectedNode[];
  outputs: ConnectedNode[];
}

/**
 * Properties Panel Component
 *
 * Displays and allows editing of node properties
 *
 * @example
 * ```tsx
 * <PropertiesPanel
 *   selectedNode={selectedNode}
 *   nodes={nodes}
 *   edges={edges}
 *   onUpdateNode={handleUpdateNode}
 *   onConfigure={handleConfigure}
 *   onClose={handleClose}
 * />
 * ```
 */
export default function PropertiesPanel({
    selectedNode,
    nodes,
    edges,
    onUpdateNode,
    onConfigure,
    onClose
}: PropertiesPanelProps) {
    const [editedLabel, setEditedLabel] = useState<string>('');
    const [hasChanges, setHasChanges] = useState<boolean>(false);

    // Update edited label when selected node changes
    useEffect(() => {
        if (selectedNode) {
            setEditedLabel(selectedNode.data.label as string || '');
            setHasChanges(false);
        }
    }, [selectedNode]);

    // Get connected nodes information
    const connectedNodes = useMemo((): Connections => {
        if (!selectedNode || !edges.length) return { inputs: [], outputs: [] };

        const inputEdges = edges.filter(e => e.target === selectedNode.id);
        const outputEdges = edges.filter(e => e.source === selectedNode.id);

        const inputs: ConnectedNode[] = inputEdges
            .map(edge => {
                const node = nodes.find(n => n.id === edge.source);
                return node ? { id: node.id, label: node.data.label as string, type: node.type } : null;
            })
            .filter((node): node is ConnectedNode => node !== null);

        const outputs: ConnectedNode[] = outputEdges
            .map(edge => {
                const node = nodes.find(n => n.id === edge.target);
                return node ? { id: node.id, label: node.data.label as string, type: node.type } : null;
            })
            .filter((node): node is ConnectedNode => node !== null);

        return { inputs, outputs };
    }, [selectedNode, edges, nodes]);

    // Handle label change
    const handleLabelChange = (value: string): void => {
        setEditedLabel(value);
        setHasChanges(value !== (selectedNode?.data.label as string || ''));
    };

    // Handle save changes
    const handleSave = (): void => {
        if (selectedNode && hasChanges) {
            onUpdateNode(selectedNode.id, { label: editedLabel });
            setHasChanges(false);
        }
    };

    // Handle cancel changes
    const handleCancel = (): void => {
        setEditedLabel(selectedNode?.data.label as string || '');
        setHasChanges(false);
    };

    // Handle open configuration
    const handleOpenConfig = (): void => {
        if (onConfigure && selectedNode) {
            onConfigure(selectedNode);
        }
    };

    // Render node-specific content
    const renderNodeContent = () => {
        if (!selectedNode) return null;

        const nodeType = selectedNode.type;
        const data = selectedNode.data;

        // Event Node
        if (nodeType === 'event' || nodeType === 'custom') {
            const eventData = data as EventNodeData;
            return (
                <div className="properties-section">
                    <h4 className="section-title">事件信息</h4>
                    {eventData.eventConfig ? (
                        <>
                            <div className="property-row">
                                <span className="property-label">事件名称:</span>
                                <span className="property-value">
                                    {eventData.eventConfig.event_name_cn || '-'}
                                </span>
                            </div>
                            {eventData.eventConfig.event_name && (
                                <div className="property-row">
                                    <span className="property-label">事件代码:</span>
                                    <span className="property-value code">
                                        {eventData.eventConfig.event_name}
                                    </span>
                                </div>
                            )}
                            <div className="property-row">
                                <span className="property-label">字段数量:</span>
                                <span className="property-value">
                                    {eventData.eventConfig.fieldCount || 0}
                                </span>
                            </div>
                            {eventData.configId && (
                                <div className="property-row">
                                    <span className="property-label">配置ID:</span>
                                    <span className="property-value code small">
                                        {eventData.configId}
                                    </span>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="no-config-message">
                            此节点尚未配置
                        </div>
                    )}
                </div>
            );
        }

        // JOIN Node
        if (nodeType === 'join') {
            const joinData = data as JoinNodeData;
            const config = joinData.config || {};
            return (
                <div className="properties-section">
                    <h4 className="section-title">JOIN配置</h4>
                    <div className="property-row">
                        <span className="property-label">JOIN类型:</span>
                        <span className="property-value join-type">
                            {config.join_type || 'INNER'}
                        </span>
                    </div>
                    {config.conditions && config.conditions.length > 0 && (
                        <div className="property-row-block">
                            <span className="property-label">连接条件:</span>
                            <div className="conditions-list">
                                {config.conditions.map((cond, idx) => (
                                    <div key={idx} className="condition-item">
                                        <code>{cond.leftField}</code>
                                        <span className="operator">{cond.operator}</span>
                                        <code>{cond.rightField}</code>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {!config.conditions || config.conditions.length === 0 && (
                        <div className="no-config-message">
                            此JOIN节点尚未配置
                        </div>
                    )}
                </div>
            );
        }

        // UNION ALL Node
        if (nodeType === 'union_all') {
            return (
                <div className="properties-section">
                    <h4 className="section-title">UNION ALL配置</h4>
                    <div className="property-row">
                        <span className="property-label">操作:</span>
                        <span className="property-value">
                            合并多个事件数据
                        </span>
                    </div>
                </div>
            );
        }

        // Output Node
        if (nodeType === 'output') {
            return (
                <div className="properties-section">
                    <h4 className="section-title">输出配置</h4>
                    <div className="property-row">
                        <span className="property-label">目标:</span>
                        <span className="property-value">
                            DWD视图输出
                        </span>
                    </div>
                </div>
            );
        }

        return null;
    };

    // Render connections section
    const renderConnections = () => {
        if (connectedNodes.inputs.length === 0 && connectedNodes.outputs.length === 0) {
            return (
                <div className="properties-section">
                    <h4 className="section-title">连接</h4>
                    <div className="no-connections-message">
                        此节点未连接到其他节点
                    </div>
                </div>
            );
        }

        return (
            <div className="properties-section">
                <h4 className="section-title">连接</h4>
                {connectedNodes.inputs.length > 0 && (
                    <div className="connections-group">
                        <div className="connections-label">输入:</div>
                        {connectedNodes.inputs.map(node => (
                            <div key={node.id} className="connection-item">
                                <span className="connection-type-badge">{node.type}</span>
                                <span className="connection-label">{node.label}</span>
                            </div>
                        ))}
                    </div>
                )}
                {connectedNodes.outputs.length > 0 && (
                    <div className="connections-group">
                        <div className="connections-label">输出:</div>
                        {connectedNodes.outputs.map(node => (
                            <div key={node.id} className="connection-item">
                                <span className="connection-type-badge">{node.type}</span>
                                <span className="connection-label">{node.label}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    // If no node selected, show empty state
    if (!selectedNode) {
        return (
            <div className="properties-panel empty">
                <EmptyState
                    icon={<span style={{ fontSize: '48px' }}>📋</span>}
                    title="未选择节点"
                    description="点击画布上的节点查看属性"
                />
            </div>
        );
    }

    const nodeTypeIcons: Record<string, string> = {
        event: '⚙️',
        custom: '⚙️',
        join: '🔀',
        union_all: '🔗',
        output: '📤'
    };

    const nodeTypeLabels: Record<string, string> = {
        event: '事件节点',
        custom: '事件节点',
        join: 'JOIN节点',
        union_all: 'UNION节点',
        output: '输出节点'
    };

    const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
        handleLabelChange(e.target.value);
    };

    return (
        <div className="properties-panel">
            {/* Header */}
            <div className="properties-header">
                <h3 className="panel-title">属性面板</h3>
                <button
                    className="close-button"
                    onClick={onClose}
                    aria-label="Close panel"
                    type="button"
                >
                    ✕
                </button>
            </div>

            {/* Content */}
            <div className="properties-content">
                {/* Node Type Badge */}
                <div className="node-type-badge-large">
                    <span className="type-icon">{nodeTypeIcons[selectedNode.type] || '📦'}</span>
                    <span className="type-label">{nodeTypeLabels[selectedNode.type] || selectedNode.type}</span>
                </div>

                {/* Label Editor */}
                <div className="properties-section">
                    <h4 className="section-title">基本信息</h4>
                    <div className="property-row">
                        <Input
                            type="text"
                            value={editedLabel}
                            onChange={handleInputChange}
                            className="label-input"
                            placeholder="输入节点标签"
                        />
                        {hasChanges && (
                                <div className="change-actions">
                                    <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={handleSave}
                                        title="保存更改"
                                    >
                                        ✓
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={handleCancel}
                                        title="取消更改"
                                    >
                                        ✕
                                    </Button>
                                </div>
                            )}
                        </div>
                    <div className="property-row">
                        <span className="property-label">节点ID:</span>
                        <span className="property-value code small">
                            {selectedNode.id}
                        </span>
                    </div>
                </div>

                {/* Node-specific content */}
                {renderNodeContent()}

                {/* Connections */}
                {renderConnections()}

                {/* Configure Button (if applicable) */}
                {(selectedNode.type === 'join' || selectedNode.type === 'event' || selectedNode.type === 'custom') && (
                    <div className="properties-section">
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={handleOpenConfig}
                        >
                            ⚙️ 打开配置
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}

export type { PropertiesPanelProps };
