/**
 * HqlVersionTimeline Component
 *
 * Displays HQL version history as a vertical timeline
 *
 * @example
 * ```tsx
 * <HqlVersionTimeline
 *   eventId={123}
 *   onSelectVersion={(version) => console.log(version)}
 * />
 * ```
 */

import React, { useCallback } from 'react';
import { useHqlVersionHistory } from '../hooks/useHqlVersionHistory';
import type { HqlVersion } from '../api/hqlVersionApi';
import { Spinner, EmptyState } from '@shared/ui';
import './HqlVersionTimeline.css';

interface HqlVersionTimelineProps {
  eventId: number;
  selectedVersionId?: number;
  onSelectVersion?: (version: HqlVersion) => void;
}

const HqlVersionTimeline: React.FC<HqlVersionTimelineProps> = ({
  eventId,
  selectedVersionId,
  onSelectVersion
}) => {
  const { data, isLoading, error, refetch } = useHqlVersionHistory(eventId);

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, []);

  if (isLoading) {
    return (
      <div className="hql-version-timeline loading">
        <Spinner size="sm" label="加载版本历史..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="hql-version-timeline error">
        <div className="alert alert-danger">
          <i className="bi bi-exclamation-triangle"></i>
          {' '}加载版本历史失败: {error.message}
          <button className="btn btn-sm btn-outline-primary ms-2" onClick={() => refetch()}>
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!data || data.versions.length === 0) {
    return (
      <div className="hql-version-timeline empty">
        <EmptyState
          icon={<i className="bi bi-clock-history" style={{ fontSize: '32px' }} />}
          title="暂无版本历史"
          description="保存HQL后将显示版本时间线"
        />
      </div>
    );
  }

  return (
    <div className="hql-version-timeline">
      <div className="timeline-header">
        <h6>版本时间线</h6>
      </div>
      <div className="timeline-container">
        <div className="timeline-line" />
        <div className="timeline-items">
          {data.versions.map((version, index) => (
            <div
              key={version.id}
              className={`timeline-item ${selectedVersionId === version.id ? 'selected' : ''}`}
              onClick={() => onSelectVersion?.(version)}
            >
              <div className="timeline-marker">
                {version.is_current && <span className="current-dot" />}
              </div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="version-number">v{version.version_number}</span>
                  {version.is_current && (
                    <span className="badge badge-success ms-2">当前</span>
                  )}
                  <span className="version-date text-muted">
                    {formatDate(version.created_at)}
                  </span>
                </div>
                {version.change_description && (
                  <div className="timeline-description">
                    {version.change_description}
                  </div>
                )}
                {version.created_by && (
                  <div className="timeline-meta text-muted">
                    <i className="bi bi-person"></i>
                    {' '}{version.created_by}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default React.memo(HqlVersionTimeline);