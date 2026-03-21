import React from 'react';

/**
 * FieldCanvasLoading - 加载状态组件
 * 使用 React.memo 优化性能
 */
const FieldCanvasLoading = React.memo(() => {
  return (
    <div className="field-canvas">
      <div className="panel-header">
        <h3>
          <i className="bi bi-grid-3x3" aria-hidden="true"></i>
          字段画布
        </h3>
      </div>
      <div className="panel-content">
        <div className="loading-state">
          <i className="bi bi-arrow-repeat spin" aria-hidden="true"></i>
          <p>加载参数中...</p>
        </div>
      </div>
    </div>
  );
});

FieldCanvasLoading.displayName = 'FieldCanvasLoading';

export default FieldCanvasLoading;
