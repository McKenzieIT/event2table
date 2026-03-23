import React from 'react';

interface DebugPanelProps {
  show: boolean;
  onClose: () => void;
}

export const DebugPanel = React.memo(function DebugPanel({ show, onClose }: DebugPanelProps): React.JSX.Element | null {
  if (!show) return null;

  return (
    <div className="panel-overlay" onClick={onClose}>
      <div className="panel-container debug-panel" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <h3>
            <i className="bi bi-bug"></i> 调试模式
          </h3>
          <button className="btn btn-sm btn-outline-secondary" onClick={onClose}>
            <i className="bi bi-x"></i> 关闭
          </button>
        </div>
        <div className="panel-body">
          <div className="panel-placeholder">
            <i className="bi bi-info-circle"></i>
            <p>调试信息将在HQL生成后显示</p>
            <small>请先选择事件并添加字段，然后生成HQL以查看调试信息</small>
          </div>
        </div>
      </div>
    </div>
  );
});

DebugPanel.displayName = 'DebugPanel';
