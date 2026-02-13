/**
 * HQLHistoryV2 - HQL生成历史版本组件
 *
 * 功能：
 * - 显示历史HQL生成记录
 * - 版本对比功能
 * - 一键恢复历史版本
 * - 时间戳和元数据显示
 */

import React, { useState, useEffect } from 'react';
import './HQLHistoryV2.css';

export default function HQLHistoryV2({
  history = [],
  onRestore,
  onCompare,
  apiBaseUrl = '/hql-preview-v2'
}) {
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [showCompare, setShowCompare] = useState(false);
  const [expandedItems, setExpandedItems] = useState(new Set());

  // 选择/取消选择版本进行对比
  const toggleVersionSelection = (versionId) => {
    if (selectedVersions.includes(versionId)) {
      setSelectedVersions(selectedVersions.filter(id => id !== versionId));
    } else if (selectedVersions.length < 2) {
      setSelectedVersions([...selectedVersions, versionId]);
    }
  };

  // 展开/收起历史项详情
  const toggleExpand = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  // 恢复历史版本
  const handleRestore = async (item) => {
    if (onRestore) {
      onRestore(item);
    } else {
      // 默认实现：将HQL复制到剪贴板
      try {
        await navigator.clipboard.writeText(item.hql);
        alert('HQL已复制到剪贴板');
      } catch (err) {
        console.error('Failed to copy HQL:', err);
      }
    }
  };

  // 对比选中的版本
  const handleCompare = () => {
    if (selectedVersions.length !== 2) {
      alert('请选择2个版本进行对比');
      return;
    }

    const version1 = history.find(h => h.id === selectedVersions[0]);
    const version2 = history.find(h => h.id === selectedVersions[1]);

    if (onCompare) {
      onCompare(version1, version2);
    }

    setShowCompare(true);
  };

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;

    return date.toLocaleDateString('zh-CN');
  };

  // 获取性能分数颜色
  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981'; // green
    if (score >= 70) return '#f59e0b'; // yellow
    if (score >= 50) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  // 获取模式标签
  const getModeLabel = (mode) => {
    const labels = {
      'single': '单事件',
      'join': 'JOIN',
      'union': 'UNION'
    };
    return labels[mode] || mode;
  };

  return (
    <div className="hql-history-v2">
      {/* 头部 */}
      <div className="history-header">
        <h3>📜 HQL生成历史</h3>
        <div className="header-actions">
          {selectedVersions.length === 2 && (
            <button
              className="btn btn-sm btn-primary"
              onClick={handleCompare}
            >
              <i className="bi bi-arrows-collapse"></i> 对比版本
            </button>
          )}
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => setSelectedVersions([])}
          >
            清除选择
          </button>
        </div>
      </div>

      {/* 历史记录列表 */}
      <div className="history-list">
        {history.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-clock-history"></i>
            <p>暂无历史记录</p>
            <p className="text-muted">生成HQL后将在此显示历史版本</p>
          </div>
        ) : (
          history.map((item, index) => (
            <div
              key={item.id || index}
              className={`history-item ${expandedItems.has(item.id || index) ? 'expanded' : ''} ${
                selectedVersions.includes(item.id || index) ? 'selected' : ''
              }`}
            >
              {/* 基本信息 */}
              <div className="history-item-header">
                <div className="item-info">
                  <div className="item-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedVersions.includes(item.id || index)}
                      onChange={() => toggleVersionSelection(item.id || index)}
                    />
                  </div>
                  <div className="item-meta">
                    <div className="item-title">
                      <span className="version-number">
                        版本 #{history.length - index}
                      </span>
                      <span className={`mode-badge mode-${item.mode}`}>
                        {getModeLabel(item.mode)}
                      </span>
                      {item.performance && (
                        <span
                          className="score-badge"
                          style={{ backgroundColor: getScoreColor(item.performance.score) }}
                        >
                          {item.performance.score}分
                        </span>
                      )}
                    </div>
                    <div className="item-details">
                      <span className="timestamp">
                        <i className="bi bi-clock"></i>
                        {formatTimestamp(item.timestamp)}
                      </span>
                      <span className="event-count">
                        <i className="bi bi-box"></i>
                        {item.events?.length || 0}个事件
                      </span>
                      <span className="field-count">
                        <i className="bi bi-list"></i>
                        {item.fields?.length || 0}个字段
                      </span>
                    </div>
                  </div>
                </div>
                <div className="item-actions">
                  <button
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => toggleExpand(item.id || index)}
                    title="查看详情"
                  >
                    <i className={`bi bi-chevron-${expandedItems.has(item.id || index) ? 'up' : 'down'}`}></i>
                  </button>
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => handleRestore(item)}
                    title="恢复此版本"
                  >
                    <i className="bi bi-arrow-counterclockwise"></i> 恢复
                  </button>
                </div>
              </div>

              {/* 展开详情 */}
              {expandedItems.has(item.id || index) && (
                <div className="history-item-details">
                  {/* HQL预览 */}
                  <div className="hql-preview">
                    <h5>生成的HQL</h5>
                    <pre className="hql-code">{item.hql}</pre>
                  </div>

                  {/* 性能分析详情 */}
                  {item.performance && item.performance.issues && item.performance.issues.length > 0 && (
                    <div className="performance-details">
                      <h5>性能问题</h5>
                      <ul className="issues-list">
                        {item.performance.issues.map((issue, idx) => (
                          <li key={idx} className={`issue-item issue-${issue.type}`}>
                            <span className="issue-message">{issue.message}</span>
                            {issue.suggestion && (
                              <span className="issue-suggestion">
                                💡 {issue.suggestion}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 元数据 */}
                  <div className="metadata">
                    <h5>元数据</h5>
                    <div className="metadata-grid">
                      <div className="metadata-item">
                        <strong>生成时间:</strong>
                        <span>{new Date(item.timestamp).toLocaleString('zh-CN')}</span>
                      </div>
                      {item.events && (
                        <div className="metadata-item">
                          <strong>事件列表:</strong>
                          <span>{item.events.map(e => e.event_name || e.name).join(', ')}</span>
                        </div>
                      )}
                      {item.options && (
                        <div className="metadata-item">
                          <strong>生成选项:</strong>
                          <span>
                            {Object.entries(item.options)
                              .filter(([key, value]) => value !== undefined && value !== null)
                              .map(([key, value]) => `${key}=${value}`)
                              .join(', ')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* 版本对比弹窗 */}
      {showCompare && selectedVersions.length === 2 && (
        <div className="compare-modal">
          <div className="modal-backdrop" onClick={() => setShowCompare(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h4>🔍 版本对比</h4>
              <button
                className="btn btn-sm btn-outline-secondary"
                onClick={() => setShowCompare(false)}
              >
                <i className="bi bi-x"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="compare-grid">
                {selectedVersions.map((versionId, idx) => {
                  const item = history.find(h => h.id === versionId);
                  return (
                    <div key={versionId} className="compare-column">
                      <h5>版本 #{history.length - history.indexOf(item)}</h5>
                      <div className="compare-meta">
                        <span>{formatTimestamp(item.timestamp)}</span>
                        <span className={`mode-badge mode-${item.mode}`}>
                          {getModeLabel(item.mode)}
                        </span>
                      </div>
                      <pre className="compare-hql">{item.hql}</pre>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
