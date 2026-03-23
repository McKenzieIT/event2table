/**
 * HqlVersionCompare Component
 *
 * Displays comparison between two HQL versions with diff highlighting
 *
 * @example
 * ```tsx
 * <HqlVersionCompare
 *   version1={v1}
 *   version2={v2}
 *   diff={diffData}
 *   onClose={() => {}}
 * />
 * ```
 */

import { Modal } from '@shared/ui';
import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

import type { HqlVersion, VersionDiff } from '../api/hqlVersionApi';
import './HqlVersionCompare.css';

interface HqlVersionCompareProps {
  isOpen: boolean;
  version1: HqlVersion;
  version2: HqlVersion;
  diff?: VersionDiff;
  onClose: () => void;
}

const HqlVersionCompare: React.FC<HqlVersionCompareProps> = ({
  isOpen,
  version1,
  version2,
  diff,
  onClose
}) => {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="HQL版本对比"
      size="xl"
    >
      <div className="hql-version-compare">
        {/* Version Info Header */}
        <div className="compare-header">
          <div className="version-info-card">
            <h6>版本 {version1.version_number}</h6>
            <div className="version-meta">
              <span className="text-muted">
                <i className="bi bi-clock"></i>
                {' '}{formatDate(version1.created_at)}
              </span>
              {version1.created_by && (
                <span className="text-muted ms-3">
                  <i className="bi bi-person"></i>
                  {' '}{version1.created_by}
                </span>
              )}
            </div>
            {version1.change_description && (
              <div className="version-description mt-2">
                {version1.change_description}
              </div>
            )}
          </div>
          <div className="vs-divider">
            <i className="bi bi-arrow-left-right"></i>
          </div>
          <div className="version-info-card">
            <h6>版本 {version2.version_number}</h6>
            <div className="version-meta">
              <span className="text-muted">
                <i className="bi bi-clock"></i>
                {' '}{formatDate(version2.created_at)}
              </span>
              {version2.created_by && (
                <span className="text-muted ms-3">
                  <i className="bi bi-person"></i>
                  {' '}{version2.created_by}
                </span>
              )}
            </div>
            {version2.change_description && (
              <div className="version-description mt-2">
                {version2.change_description}
              </div>
            )}
          </div>
        </div>

        {/* Diff Summary */}
        {diff && (
          <div className="diff-summary">
            <div className="summary-stats">
              <span className="stat-item additions">
                <i className="bi bi-plus-circle"></i>
                {' '}新增 {diff.summary.additions}
              </span>
              <span className="stat-item deletions">
                <i className="bi bi-dash-circle"></i>
                {' '}删除 {diff.summary.deletions}
              </span>
              <span className="stat-item changes">
                <i className="bi bi-pencil-square"></i>
                {' '}修改 {diff.summary.changes}
              </span>
            </div>
          </div>
        )}

        {/* Diff Content */}
        <div className="diff-content">
          {diff && diff.diff ? (
            <SyntaxHighlighter
              language="diff"
              style={vscDarkPlus}
              showLineNumbers
              customStyle={{
                margin: 0,
                borderRadius: '8px',
                fontSize: '0.875rem',
                maxHeight: '60vh',
                overflow: 'auto'
              }}
            >
              {diff.diff}
            </SyntaxHighlighter>
          ) : (
            <div className="alert alert-info">
              <i className="bi bi-info-circle"></i>
              {' '}无法生成差异对比
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} type="button">
            关闭
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default React.memo(HqlVersionCompare);