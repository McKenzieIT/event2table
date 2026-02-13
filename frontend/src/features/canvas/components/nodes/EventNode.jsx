import React from 'react';
import { Handle, Position } from 'reactflow';
import './EventNode.css';

/**
 * 事件节点组件
 * 显示从事件节点构建器加载的事件配置
 */
export default function EventNode({ data }) {
  return (
    <div className="custom-node event-node">
      {/* 输出端口 */}
      <Handle
        type="source"
        position={Position.Right}
        className="node-port output-port"
      />

      {/* 节点头部 */}
      <div className="node-header">
        <span className="node-icon">⚙️</span>
        <span className="node-title">{data.label || '事件节点'}</span>
      </div>

      {/* 节点内容 */}
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