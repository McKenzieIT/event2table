import React from "react";
import type { EventNodeStats } from "@shared/types/eventNodes";

/**
 * 统计卡片组件 - 使用metric-card系统
 * 展示事件节点的关键统计数据
 */
function StatisticsCards({ stats }: { stats: EventNodeStats | null }) {
  if (!stats) {
    return (
      <div className="stats-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="metric-card skeleton-card">
            <div className="skeleton-icon"></div>
            <div className="skeleton-content">
              <div className="skeleton-number"></div>
              <div className="skeleton-text"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="stats-grid">
      {/* 总节点数 */}
      <div className="metric-card metric-card--cyan">
        <div className="metric-card__icon metric-card__icon--cyan">
          <i className="bi bi-diagram-3-fill"></i>
        </div>
        <div className="metric-card__value">{stats.total_nodes}</div>
        <div className="metric-card__label">事件节点总数</div>
      </div>

      {/* 关联事件数 */}
      <div className="metric-card metric-card--violet">
        <div className="metric-card__icon metric-card__icon--violet">
          <i className="bi bi-box-seam-fill"></i>
        </div>
        <div className="metric-card__value">{stats.unique_events}</div>
        <div className="metric-card__label">关联事件数</div>
      </div>

      {/* 平均字段数 */}
      <div className="metric-card metric-card--warning">
        <div className="metric-card__icon metric-card__icon--warning">
          <i className="bi bi-list-ul"></i>
        </div>
        <div className="metric-card__value">{stats.avg_fields.toFixed(1)}</div>
        <div className="metric-card__label">平均字段数</div>
      </div>

      {/* 今日修改 */}
      <div className="metric-card metric-card--success">
        <div className="metric-card__icon metric-card__icon--success">
          <i className="bi bi-clock-history"></i>
        </div>
        <div className="metric-card__value">{stats.today_modified || 0}</div>
        <div className="metric-card__label">今日修改</div>
      </div>
    </div>
  );
}

export default React.memo(StatisticsCards);
