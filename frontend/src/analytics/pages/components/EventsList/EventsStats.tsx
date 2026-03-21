import React from 'react';
import { EventsStatsProps } from './types';

/**
 * EventsStats 组件
 * 统计卡片，显示事件总数、已分类数、未分类数
 */
const EventsStats: React.FC<EventsStatsProps> = React.memo(({
  total,
  categorizedCount,
  uncategorizedCount
}) => {
  return (
    <div className="stats-container">
      <div className="stat-card">
        <div className="stat-value">{total}</div>
        <div className="stat-label">
          <span>总事件数</span>
        </div>
      </div>
      <div className="stat-card purple">
        <div className="stat-value">{categorizedCount}</div>
        <div className="stat-label">
          <span>已分类</span>
        </div>
      </div>
      <div className="stat-card orange">
        <div className="stat-value">{uncategorizedCount}</div>
        <div className="stat-label">
          <span>未分类</span>
        </div>
      </div>
    </div>
  );
});

EventsStats.displayName = 'EventsStats';

export default EventsStats;
