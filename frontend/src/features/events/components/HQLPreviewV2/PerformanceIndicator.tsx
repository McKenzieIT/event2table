/**
 * PerformanceIndicator组件
 *
 * 显示HQL性能指标和建议
 */

import React from 'react';
import './PerformanceIndicator.css';

interface PerformanceIssue {
  type: 'warning' | 'error' | 'info';
  message: string;
  suggestion?: string;
}

interface PerformanceReport {
  score: number;
  issues: PerformanceIssue[];
  metrics: {
    hasPartitionFilter: boolean;
    hasSelectStar: boolean;
    joinCount: number;
    complexity: 'low' | 'medium' | 'high';
  };
}

interface PerformanceIndicatorProps {
  report: PerformanceReport;
}

export const PerformanceIndicator: React.FC<PerformanceIndicatorProps> = ({ report }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="performance-indicator">
      <div className="performance-header">
        <h4>Performance Analysis</h4>
        <div className="score-badge" style={{ backgroundColor: getScoreColor(report.score) }}>
          {report.score}/100 - {getScoreLabel(report.score)}
        </div>
      </div>

      {/* Metrics */}
      <div className="metrics-grid">
        <div className="metric-item">
          <span className="metric-label">Partition Filter:</span>
          <span className={`metric-value ${report.metrics.hasPartitionFilter ? 'good' : 'bad'}`}>
            {report.metrics.hasPartitionFilter ? '✓ Present' : '✗ Missing'}
          </span>
        </div>

        <div className="metric-item">
          <span className="metric-label">SELECT *:</span>
          <span className={`metric-value ${!report.metrics.hasSelectStar ? 'good' : 'bad'}`}>
            {report.metrics.hasSelectStar ? '⚠ Found' : '✓ Not Found'}
          </span>
        </div>

        <div className="metric-item">
          <span className="metric-label">JOINs:</span>
          <span className="metric-value">{report.metrics.joinCount}</span>
        </div>

        <div className="metric-item">
          <span className="metric-label">Complexity:</span>
          <span className="metric-value">{report.metrics.complexity}</span>
        </div>
      </div>

      {/* Issues */}
      {report.issues.length > 0 && (
        <div className="issues-list">
          <h5>Issues & Suggestions</h5>
          {report.issues.map((issue, index) => (
            <div key={index} className={`issue-item issue-${issue.type}`}>
              <div className="issue-header">
                <span className="issue-icon">
                  {issue.type === 'error' && '❌'}
                  {issue.type === 'warning' && '⚠️'}
                  {issue.type === 'info' && 'ℹ️'}
                </span>
                <span className="issue-message">{issue.message}</span>
              </div>
              {issue.suggestion && (
                <div className="issue-suggestion">
                  <strong>Suggestion:</strong> {issue.suggestion}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PerformanceIndicator;
