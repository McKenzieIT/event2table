import React, { useState, useEffect, useMemo } from 'react';
import { Button, Input } from '@shared/ui';
import './PropertiesPanel.css';

/**
 * Properties Panel Component
 * Displays and allows editing of node properties
 *
 * @param {Object} selectedNode - The currently selected node
 * @param {Array} nodes - All nodes in the canvas
 * @param {Array} edges - All edges in the canvas
 * @param {Function} onUpdateNode - Callback when node is updated
 * @param {Function} onConfigure - Callback to open configuration modal
 * @param {Function} onClose - Callback to close the panel
 */
export default function PropertiesPanel({
    selectedNode,
    nodes,
    edges,
    onUpdateNode,
    onConfigure,
    onClose
}) {
    const [editedLabel, setEditedLabel] = useState('');
    const [hasChanges, setHasChanges] = useState(false);

    // Update edited label when selected node changes
    useEffect(() => {
        if (selectedNode) {
            setEditedLabel(selectedNode.data.label || '');
            setHasChanges(false);
        }
    }, [selectedNode]);

    // Get connected nodes information
    const connectedNodes = useMemo(() => {
        if (!selectedNode || !edges.length) return { inputs: [], outputs: [] };

        const inputEdges = edges.filter(e => e.target === selectedNode.id);
        const outputEdges = edges.filter(e => e.source === selectedNode.id);

        const inputs = inputEdges.map(edge => {
            const node = nodes.find(n => n.id === edge.source);
            return node ? { id: node.id, label: node.data.label, type: node.type } : null;
        }).filter(Boolean);

        const outputs = outputEdges.map(edge => {
            const node = nodes.find(n => n.id === edge.target);
            return node ? { id: node.id, label: node.data.label, type: node.type } : null;
        }).filter(Boolean);

        return { inputs, outputs };
    }, [selectedNode, edges, nodes]);

    // Handle label change
    const handleLabelChange = (value) => {
        setEditedLabel(value);
        setHasChanges(value !== (selectedNode?.data.label || ''));
    };

    // Handle save changes
    const handleSave = () => {
        if (selectedNode && hasChanges) {
            onUpdateNode(selectedNode.id, { label: editedLabel });
            setHasChanges(false);
        }
    };

    // Handle cancel changes
    const handleCancel = () => {
        setEditedLabel(selectedNode?.data.label || '');
        setHasChanges(false);
    };

    // Handle open configuration
    const handleOpenConfig = () => {
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
            return (
                <div className="properties-section">
                    <h4 className="section-title">事件信息</h4>
                    {data.eventConfig ? (
                        <>
                            <div className="property-row">
                                <span className="property-label">事件名称:</span>
                                <span className="property-value">
                                    {data.eventConfig.event_name_cn || '-'}
                                </span>
                            </div>
                            {data.eventConfig.event_name && (
                                <div className="property-row">
                                    <span className="property-label">事件代码:</span>
                                    <span className="property-value code">
                                        {data.eventConfig.event_name}
                                    </span>
                                </div>
                            )}
                            <div className="property-row">
                                <span className="property-label">字段数量:</span>
                                <span className="property-value">
                                    {data.eventConfig.fieldCount || 0}
                                </span>
                            </div>
                            {data.configId && (
                                <div className="property-row">
                                    <span className="property-label">配置ID:</span>
                                    <span className="property-value code small">
                                        {data.configId}
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
            const config = data.config || {};
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
                <div className="empty-state">
                    <div className="empty-icon">📋</div>
                    <div className="empty-title">未选择节点</div>
                    <div className="empty-description">
                        点击画布上的节点查看属性
                    </div>
                </div>
            </div>
        );
    }

    const nodeTypeIcons = {
        event: '⚙️',
        custom: '⚙️',
        join: '🔀',
        union_all: '🔗',
        output: '📤'
    };

    const nodeTypeLabels = {
        event: '事件节点',
        custom: '事件节点',
        join: 'JOIN节点',
        union_all: 'UNION节点',
        output: '输出节点'
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
                            onChange={(e) => handleLabelChange(e.target.value)}
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
