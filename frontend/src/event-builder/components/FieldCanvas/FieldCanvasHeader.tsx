import React from 'react';
import { CanvasStatsDisplay } from './CanvasStatsDisplay';

interface FieldCanvasHeaderProps {
  stats: {
    total: number;
    baseFields: number;
    paramFields: number;
    whereCount: number;
  };
}

/**
 * FieldCanvasHeader - 画布头部组件
 * 包含标题和统计信息
 * 使用 React.memo 优化性能
 */
const FieldCanvasHeader = React.memo<FieldCanvasHeaderProps>(({ stats }) => {
  return (
    <div className="panel-header compact">
      <h3>
        <i className="bi bi-grid-3x3" aria-hidden="true"></i>
        字段画布
      </h3>

      {/* Statistics Display - 紧凑型统计信息 */}
      <CanvasStatsDisplay stats={stats} />
    </div>
  );
});

FieldCanvasHeader.displayName = 'FieldCanvasHeader';

export default FieldCanvasHeader;
