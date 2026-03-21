import React from 'react';

/**
 * Props for CanvasStatsDisplay component
 */
export interface CanvasStatsDisplayProps {
  /** Statistics data */
  stats: {
    total: number;
    baseFields: number;
    paramFields: number;
    whereCount: number;
  };
}

/**
 * CanvasStatsDisplay Component
 */
export const CanvasStatsDisplay: React.FC<CanvasStatsDisplayProps> = ({ stats }) => {
  return (
    <div className="canvas-stats">
      <span className="stat-item">
        <i className="bi bi-grid-3x3"></i>
        {stats.total}
      </span>
      {stats.baseFields > 0 && (
        <span className="stat-item" title="基础字段">
          <i className="bi bi-type"></i>
          {stats.baseFields}
        </span>
      )}
      {stats.paramFields > 0 && (
        <span className="stat-item" title="参数字段">
          <i className="bi bi-link"></i>
          {stats.paramFields}
        </span>
      )}
      {stats.whereCount > 0 && (
        <span className="stat-item" title="WHERE条件">
          <i className="bi bi-funnel"></i>
          {stats.whereCount}
        </span>
      )}
    </div>
  );
};

CanvasStatsDisplay.displayName = 'CanvasStatsDisplay';
