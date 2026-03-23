// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * PerformanceMonitor - 性能监控组件
 *
 * 监控GraphQL查询性能、缓存命中率等指标
 */

import { useApolloClient } from '@apollo/client/react';
import { Card, Button, Badge } from '@shared/ui';
import React, { useState, useEffect } from 'react';
import './PerformanceMonitor.css';

interface QueryPerformance {
  queryName: string;
  duration: number;
  timestamp: Date;
}

interface PerformanceMetrics {
  cacheHits: number;
  cacheMisses: number;
  totalQueries: number;
  avgQueryTime: number;
  slowQueries: QueryPerformance[];
}

interface PerformanceMonitorProps {
  isOpen: boolean;
  onClose: () => void;
}

const PerformanceMonitor = ({ isOpen, onClose }: PerformanceMonitorProps): React.JSX.Element | null => {
  const client = useApolloClient();
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    cacheHits: 0,
    cacheMisses: 0,
    totalQueries: 0,
    avgQueryTime: 0,
    slowQueries: [],
  });

  useEffect(() => {
    if (!isOpen) return;

    // TODO: 监听GraphQL查询 (需要实际的GraphQL subscription)
    // 这里是示例代码，实际使用时需要替换为真实的subscription

    const timer = setInterval(() => {
      // 模拟查询数据
    }, 5000);

    return () => clearInterval(timer);
  }, [client, isOpen]);

  // 计算缓存命中率
  const cacheHitRatio = metrics.totalQueries > 0
    ? ((metrics.cacheHits / metrics.totalQueries) * 100).toFixed(2)
    : '0.00';

  // 清空缓存
  const handleClearCache = (): void => {
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
                  <Badge variant={Number(cacheHitRatio) > 80 ? 'success' : Number(cacheHitRatio) > 50 ? 'warning' : 'danger'}>
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
