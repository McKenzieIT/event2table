// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from 'react';
import { Handle, Position, Node } from 'reactflow';
import './EventNode.css';

/**
 * Event configuration data structure
 */
interface EventConfigData {
    event_name?: string;
    event_name_cn?: string;
    fieldCount?: number;
    [key: string]: unknown;
}

/**
 * Event Node data structure
 */
interface EventNodeData {
    label?: string;
    eventConfig?: EventConfigData;
    configId?: string;
    [key: string]: unknown;
}

/**
 * Event Node Props
 *
 * Extends ReactFlow's Node type with EventNodeData
 */
interface EventNodeProps extends Node<EventNodeData> {
    data: EventNodeData;
}

/**
 * EventNode Component
 *
 * Displays event configuration loaded from Event Node Builder
 *
 * @param data - Node data containing event configuration
 *
 * @example
 * ```tsx
 * <EventNode
 *   data={{
 *     label: 'Login Event',
 *     eventConfig: {
 *       event_name: 'login',
 *       event_name_cn: '登录',
 *       fieldCount: 5
 *     }
 *   }}
 * />
 * ```
 */
export default function EventNode({ data }: EventNodeProps): React.ReactElement {
    return (
        <div className="custom-node event-node">
            {/* Output port */}
            <Handle
                type="source"
                position={Position.Right}
                className="node-port output-port"
            />

            {/* Node header */}
            <div className="node-header">
                <span className="node-icon">⚙️</span>
                <span className="node-title">{data.label || '事件节点'}</span>
            </div>

            {/* Node body */}
            <div className="node-body">
                {data.eventConfig ? (
                    <>
                        <div className="node-info">
                            <div className="event-name-cn">{data.eventConfig.event_name_cn || '-'}</div>
                            {data.eventConfig.event_name && (
                                <div className="event-name-en">{data.eventConfig.event_name}</div>
                            )}
                        </div>
                        <div className="node-stats">
                            字段数: {data.eventConfig.fieldCount || 0}
                        </div>
                    </>
                ) : (
                    <div className="node-placeholder">
                        双击配置事件
                    </div>
                )}
            </div>
        </div>
    );
}

export type { EventNodeData, EventNodeProps };
