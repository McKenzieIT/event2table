import React from 'react';

interface PerformancePanelProps {
  show: boolean;
  onClose: () => void;
}

export const PerformancePanel = React.memo(function PerformancePanel({ show, onClose }: PerformancePanelProps): React.JSX.Element {
  if (!show) return null;

  return (
    <div className="panel-overlay" onClick={onClose}>
      <div className="panel-container performance-panel" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <h3>
            <i className="bi bi-speedometer2"></i> 性能分析
          </h3>
          <button className="btn btn-sm btn-outline-secondary" onClick={onClose}>
            <i className="bi bi-x"></i> 关闭
          </button>
        </div>
        <div className="panel-body">
          <div className="panel-placeholder">
            <i className="bi bi-info-circle"></i>
            <p>性能数据将在HQL生成后显示</p>
            <small>请先选择事件并添加字段，然后生成HQL以查看性能分析</small>
          </div>
        </div>
      </div>
    </div>
  );
});

PerformancePanel.displayName = 'PerformancePanel';
