import React from 'react';

/**
 * FieldCanvasError - 错误状态组件
 * 使用 React.memo 优化性能
 */
const FieldCanvasError = React.memo(() => {
  return (
    <div className="field-canvas">
      <div className="panel-header">
        <h3>
          <i className="bi bi-grid-3x3" aria-hidden="true"></i>
          字段画布
        </h3>
      </div>
      <div className="panel-content">
        <div className="error-state">
          <i className="bi bi-exclamation-triangle" aria-hidden="true"></i>
          <p>加载参数失败</p>
        </div>
      </div>
    </div>
  );
});

FieldCanvasError.displayName = 'FieldCanvasError';

export default FieldCanvasError;
