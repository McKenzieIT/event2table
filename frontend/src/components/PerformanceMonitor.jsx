/**
 * PerformanceMonitor - 性能监控组件
 *
 * 监控GraphQL查询性能、缓存命中率等指标
 */

import React, { useState, useEffect } from 'react';
import { useApolloClient } from '@apollo/client/react';
import { Card, Button, Badge } from '@shared/ui';
import './PerformanceMonitor.css';

const PerformanceMonitor = ({ isOpen, onClose }) => {
  const client = useApolloClient();
  const [metrics, setMetrics] = useState({
    cacheHits: 0,
    cacheMisses: 0,
    totalQueries: 0,
    avgQueryTime: 0,
    slowQueries: [],
  });

  useEffect(() => {
    if (!isOpen) return;

    // 监听GraphQL查询
    const subscription = client.subscribe({
      query: gql`
        subscription onQueryPerformance {
          queryPerformance {
            queryName
            duration
            cacheHit
            timestamp
          }
        }
      `,
    }).subscribe({
      next: (data) => {
        const { queryName, duration, cacheHit } = data.data.queryPerformance;
        
        setMetrics(prev => {
          const newMetrics = {
            ...prev,
            totalQueries: prev.totalQueries + 1,
            avgQueryTime: (prev.avgQueryTime * prev.totalQueries + duration) / (prev.totalQueries + 1),
          };

          if (cacheHit) {
            newMetrics.cacheHits = prev.cacheHits + 1;
          } else {
            newMetrics.cacheMisses = prev.cacheMisses + 1;
          }

          // 记录慢查询（> 100ms）
          if (duration > 100) {
            newMetrics.slowQueries = [
              ...prev.slowQueries.slice(-9),
              { queryName, duration, timestamp: new Date() }
            ];
          }

          return newMetrics;
        });
      },
    });

    return () => subscription.unsubscribe();
  }, [client, isOpen]);

  // 计算缓存命中率
  const cacheHitRatio = metrics.totalQueries > 0
    ? ((metrics.cacheHits / metrics.totalQueries) * 100).toFixed(2)
    : 0;

  // 清空缓存
  const handleClearCache = () => {
    client.clearStore();
    setMetrics({
      cacheHits: 0,
      cacheMisses: 0,
      totalQueries: 0,
      avgQueryTime: 0,
      slowQueries: [],
    });
  };

  if (!isOpen) return null;

  return (
    <div className="performance-monitor-overlay">
      <Card className="performance-monitor">
        <div className="monitor-header">
          <h3>性能监控</h3>
          <Button onClick={onClose} variant="text" size="sm">
            ✕
          </Button>
        </div>

        <div className="monitor-content">
          {/* 缓存统计 */}
          <div className="metric-section">
            <h4>缓存统计</h4>
            <div className="metric-grid">
              <div className="metric-item">
                <span className="metric-label">缓存命中率</span>
                <span className="metric-value">
                  <Badge variant={cacheHitRatio > 80 ? 'success' : cacheHitRatio > 50 ? 'warning' : 'danger'}>
                    {cacheHitRatio}%
                  </Badge>
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">缓存命中</span>
                <span className="metric-value">{metrics.cacheHits}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">缓存未命中</span>
                <span className="metric-value">{metrics.cacheMisses}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">总查询数</span>
                <span className="metric-value">{metrics.totalQueries}</span>
              </div>
            </div>
          </div>

          {/* 查询性能 */}
          <div className="metric-section">
            <h4>查询性能</h4>
            <div className="metric-grid">
              <div className="metric-item">
                <span className="metric-label">平均查询时间</span>
                <span className="metric-value">
                  <Badge variant={metrics.avgQueryTime < 50 ? 'success' : metrics.avgQueryTime < 100 ? 'warning' : 'danger'}>
                    {metrics.avgQueryTime.toFixed(2)}ms
                  </Badge>
                </span>
              </div>
              <div className="metric-item">
                <span className="metric-label">慢查询数量</span>
                <span className="metric-value">
                  <Badge variant={metrics.slowQueries.length === 0 ? 'success' : 'warning'}>
                    {metrics.slowQueries.length}
                  </Badge>
                </span>
              </div>
            </div>
          </div>

          {/* 慢查询列表 */}
          {metrics.slowQueries.length > 0 && (
            <div className="metric-section">
              <h4>慢查询列表</h4>
              <div className="slow-queries-list">
                {metrics.slowQueries.map((query, index) => (
                  <div key={index} className="slow-query-item">
                    <span className="query-name">{query.queryName}</span>
                    <span className="query-duration">{query.duration}ms</span>
                    <span className="query-time">{query.timestamp.toLocaleTimeString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="monitor-actions">
            <Button onClick={handleClearCache} variant="danger" size="sm">
              清空缓存
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PerformanceMonitor;
