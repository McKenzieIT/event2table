/**
 * 缓存统计指示器组件
 *
 * 显示HQL V2 API缓存统计信息
 */

import React, { useState, useEffect, useCallback } from 'react';
import { hqlApiV2 } from '../../../shared/api/hqlApiV2';
import type { CacheStatsResponse } from '../../../shared/types';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import './CacheIndicator.css';

interface CacheIndicatorProps {
  /** 自动刷新间隔（毫秒），0表示不自动刷新 */
  refreshInterval?: number;
  /** 是否显示详细信息 */
  showDetails?: boolean;
  /** 是否紧凑模式 */
  compact?: boolean;
  /** 自定义API基础URL */
  apiBaseUrl?: string;
}

/**
 * 缓存指示器组件
 */
export const CacheIndicator: React.FC<CacheIndicatorProps> = ({
  refreshInterval = 30000,
  showDetails = true,
  compact = false,
  apiBaseUrl = '/hql-preview-v2'
}) => {
  const [stats, setStats] = useState<CacheStatsResponse['data'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [confirmState, setConfirmState] = useState({ open: false, title: '清空缓存', message: '确定要清空缓存吗？' });

  // 获取缓存统计
  const fetchStats = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await hqlApiV2.getCacheStats(apiBaseUrl);
      setStats(response.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch cache stats';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 清空缓存
  const clearCache = async () => {
    setConfirmState({ open: true, title: '清空缓存', message: '确定要清空缓存吗？' });
  };

  const handleConfirmClear = useCallback(async () => {
    setConfirmState(prev => ({ ...prev, open: false }));
    setLoading(true);
    try {
      await hqlApiV2.clearCache(apiBaseUrl);
      await fetchStats();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to clear cache';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [apiBaseUrl]);

  const handleCancelClear = useCallback(() => {
    setConfirmState(prev => ({ ...prev, open: false }));
  }, []);

  useEffect(() => {
    fetchStats();

    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const getHitRateColor = (rate: number) => {
    if (rate >= 0.7) return '#52c41a';
    if (rate >= 0.4) return '#faad14';
    return '#ff4d4f';
  };

  // Compact mode
  if (compact && stats) {
    return (
      <div className="cache-indicator-compact">
        <span>Cache:</span>
        <span style={{ color: getHitRateColor(stats.hit_rate) }}>
          {(stats.hit_rate * 100).toFixed(0)}%
        </span>
        <span>{stats.cache_size}/{stats.cache_maxsize}</span>
      </div>
    );
  }

  return (
    <>
      <div className="cache-indicator">
        <div className="cache-header">
          <h4>缓存统计</h4>
          <div className="cache-actions">
            <button onClick={fetchStats} disabled={loading} className="btn-sm">
              刷新
            </button>
            <button onClick={clearCache} disabled={loading} className="btn-sm btn-danger">
              清空
            </button>
          </div>
        </div>

        {error && <div className="cache-error">{error}</div>}

        {stats && (
          <>
            <div className="cache-hitrate">
              <span>命中率: {(stats.hit_rate * 100).toFixed(1)}%</span>
              <span style={{
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: getHitRateColor(stats.hit_rate),
                color: 'white'
              }}>
                {stats.hit_rate >= 0.7 ? '优秀' : stats.hit_rate >= 0.4 ? '良好' : '较低'}
              </span>
            </div>

            {showDetails && (
              <div className="cache-metrics">
                <div>大小: {stats.cache_size} / {stats.cache_maxsize}</div>
                <div>命中: {stats.cache_hits}</div>
                <div>未命中: {stats.cache_misses}</div>
              </div>
            )}
          </>
        )}
      </div>

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="清空"
        cancelText="取消"
        variant="danger"
        onConfirm={handleConfirmClear}
        onCancel={handleCancelClear}
      />
    </>
  );
};

export default CacheIndicator;