/**
 * PerformanceIndicator - V2 API性能分析展示组件
 *
 * 功能：
 * - 显示性能分数（0-100分，颜色编码）
 * - 列出检测到的问题
 * - 提供优化建议
 */

import React from 'react';
import './PerformanceIndicator.css';

export default function PerformanceIndicator({ performance }) {
  if (!performance) {
    return null;
  }

  const { score, issues = [] } = performance;

  // 根据分数确定颜色和级别
  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981'; // green
    if (score >= 70) return '#f59e0b'; // yellow
    if (score >= 50) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return '优秀';
    if (score >= 70) return '良好';
    if (score >= 50) return '一般';
    return '需要优化';
  };

  const getScoreLevel = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const scoreColor = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);
  const scoreLevel = getScoreLevel(score);

  // 问题类型图标
  const getIssueIcon = (type) => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '•';
    }
  };

  return (
    <div className="performance-indicator">
      <div className="performance-header">
        <h3>📊 性能分析</h3>
        <div className="score-badge" style={{ backgroundColor: scoreColor }}>
          <span className="score-value">{score}</span>
          <span className="score-level">{scoreLevel}</span>
        </div>
      </div>

      <div className="score-summary">
        <p className="score-label">性能评级: <strong style={{ color: scoreColor }}>{scoreLabel}</strong></p>

        {/* 进度条 */}
        <div className="score-progress">
          <div
            className="score-progress-bar"
            style={{
              width: `${score}%`,
              backgroundColor: scoreColor
            }}
          />
        </div>
      </div>

      {/* 问题列表 */}
      {issues.length > 0 && (
        <div className="issues-list">
          <h4>检测到的问题 ({issues.length})</h4>
          {issues.map((issue, index) => (
            <div key={index} className={`issue-item issue-${issue.type}`}>
              <div className="issue-header">
                <span className="issue-icon">{getIssueIcon(issue.type)}</span>
                <span className="issue-title">{issue.message}</span>
              </div>

              {issue.suggestion && (
                <div className="issue-suggestion">
                  <strong>💡 建议：</strong> {issue.suggestion}
                </div>
              )}

              {issue.location && (
                <div className="issue-location">
                  📍 位置: {issue.location}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 无问题提示 */}
      {issues.length === 0 && (
        <div className="no-issues">
          <span className="success-icon">✅</span>
          <p>未检测到性能问题，HQL质量良好！</p>
        </div>
      )}

      {/* 优化建议 */}
      {score < 90 && (
        <div className="optimization-tips">
          <h4>🚀 优化建议</h4>
          <ul>
            {score < 60 && <li>添加分区过滤 (WHERE ds = '${ds}')</li>}
            {issues.some(i => i.message.includes('SELECT *')) && (
              <li>避免使用 SELECT *，明确指定所需字段</li>
            )}
            {issues.some(i => i.message.includes('JOIN')) && (
              <li>优化JOIN条件，确保JOIN字段有索引</li>
            )}
            {score >= 60 && score < 90 && (
              <li>当前HQL性能良好，可进一步优化索引</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
