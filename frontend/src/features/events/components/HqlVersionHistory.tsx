/**
 * HqlVersionHistory Component
 *
 * Displays HQL version history as a list with version details
 *
 * @example
 * ```tsx
 * <HqlVersionHistory
 *   eventId={123}
 *   onSelectVersion={(version) => console.log(version)}
 *   onCompare={(v1, v2) => console.log('compare', v1, v2)}
 * />
 * ```
 */

import React, { useState, useCallback } from 'react';
import { useHqlVersionHistory } from '../hooks/useHqlVersionHistory';
import type { HqlVersion } from '../api/hqlVersionApi';
import { Spinner, EmptyState } from '@shared/ui';
import './HqlVersionHistory.css';

interface HqlVersionHistoryProps {
  eventId: number;
  selectedVersionId?: number;
  compareVersionId?: number;
  onSelectVersion?: (version: HqlVersion) => void;
  onCompare?: (version1: HqlVersion, version2: HqlVersion) => void;
}

const HqlVersionHistory: React.FC<HqlVersionHistoryProps> = ({
  eventId,
  selectedVersionId,
  compareVersionId,
  onSelectVersion,
  onCompare
}) => {
  const { data, isLoading, error, refetch } = useHqlVersionHistory(eventId);
  const [expandedVersionId, setExpandedVersionId] = useState<number | null>(null);

  const handleToggleExpand = useCallback((versionId: number) => {
    setExpandedVersionId(prev => prev === versionId ? null : versionId);
  }, []);

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
      <div className="hql-version-history loading">
        <Spinner size="sm" label="加载版本历史..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="hql-version-history error">
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
      <div className="hql-version-history empty">
        <EmptyState
          icon={<i className="bi bi-clock-history" style={{ fontSize: '32px' }} />}
          title="暂无版本历史"
          description="保存HQL后将显示版本历史"
        />
      </div>
    );
  }

  return (
    <div className="hql-version-history">
      <div className="version-history-header">
        <h6>版本历史 ({data.total})</h6>
      </div>
      <div className="version-list">
        {data.versions.map((version, index) => (
          <div
            key={version.id}
            className={`version-item ${selectedVersionId === version.id ? 'selected' : ''} ${compareVersionId === version.id ? 'comparing' : ''}`}
          >
            <div className="version-summary">
              <div className="version-info">
                <span className="version-number">v{version.version_number}</span>
                {version.is_current && (
                  <span className="badge badge-success ms-2">当前</span>
                )}
                <span className="version-date text-muted ms-2">
                  {formatDate(version.created_at)}
                </span>
              </div>
              <div className="version-actions">
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => handleToggleExpand(version.id)}
                  type="button"
                >
                  <i className={`bi ${expandedVersionId === version.id ? 'bi-chevron-up' : 'bi-chevron-down'}`}></i>
                </button>
                {onSelectVersion && (
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => onSelectVersion(version)}
                    type="button"
                    title="选择此版本"
                  >
                    <i className="bi bi-check-circle"></i>
                  </button>
                )}
                {onCompare && compareVersionId && compareVersionId !== version.id && (
                  <button
                    className="btn btn-sm btn-outline-info"
                    onClick={() => {
                      const compareWith = data.versions.find(v => v.id === compareVersionId);
                      if (compareWith) {
                        onCompare(compareWith, version);
                      }
                    }}
                    type="button"
                    title="与此版本对比"
                  >
                    <i className="bi bi-code-diff"></i>
                  </button>
                )}
              </div>
            </div>
            {version.change_description && (
              <div className="version-description">
                {version.change_description}
              </div>
            )}
            {expandedVersionId === version.id && (
              <div className="version-details">
                <pre className="hql-content">
                  <code>{version.hql_content}</code>
                </pre>
                {version.created_by && (
                  <div className="version-meta text-muted">
                    <i className="bi bi-person"></i>
                    {' '}{version.created_by}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default React.memo(HqlVersionHistory);