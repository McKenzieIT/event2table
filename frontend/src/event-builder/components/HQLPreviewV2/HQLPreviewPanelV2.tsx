/**
 * HQL预览面板 V2
 *
 * 使用新的HQL V2 API生成HQL
 * 完全独立，可复用的React组件
 */
// @ts-nocheck - TypeScript检查暂禁用

import React, { useState, useEffect } from 'react';
import { hqlApiV2 } from '../../../shared/api/hqlApiV2';
import type { GenerateRequest } from '../../../shared/types';
import type { HQLGenerateResponse } from '@shared/types/api-types';
import { HQL_PREVIEW_DEBOUNCE } from '@shared/constants/timeouts';
import { DebugViewer } from './DebugViewer';
import { PerformanceIndicator } from './PerformanceIndicator';
import { WhereConditionBuilderV2 } from './WhereConditionBuilderV2';
import './HQLPreviewPanelV2.css';

// 从共享API类型导入类型定义
type ApiEvent = GenerateRequest['events'][0];
type ApiField = GenerateRequest['fields'][0];
type ApiCondition = NonNullable<GenerateRequest['where_conditions']>[number];

interface HQLPreviewPanelV2Props {
  events: ApiEvent[];
  fields: ApiField[];
  conditions?: ApiCondition[];
  mode?: 'single' | 'join' | 'union';
  apiBaseUrl?: string;
  enableCache?: boolean;
  enableHistory?: boolean;
  debugMode?: boolean;
  onHQLGenerated?: (hql: string) => void;
  onError?: (error: string) => void;
}

interface GenerateResponse {
  result: string;
  generated_at: string;
}

interface DebugTrace {
  result: string;
  steps: Array<{
    step: string;
    result: any;
    count?: number;
  }>;
  events: ApiEvent[];
  fields: ApiField[];
}

interface PerformanceReport {
  score: number;
  issues: string[];
  suggestions: string[];
}

export const HQLPreviewPanelV2: React.FC<HQLPreviewPanelV2Props> = ({
  events,
  fields,
  conditions = [],
  mode = 'single',
  apiBaseUrl = '/hql-preview-v2',
  enableCache = true,
  enableHistory = true,
  debugMode = false,
  onHQLGenerated,
  onError
}) => {
  // State
  const [hql, setHql] = useState<string>('');
  const [debugTrace, setDebugTrace] = useState<DebugTrace | null>(null);
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null);

  // 生成HQL
  const generateHQL = async () => {
    setLoading(true);
    setError('');
    setPerformanceReport(null);  // 清空旧的性能报告

    try {
      const requestData = {
        events,
        fields,
        where_conditions: conditions,
        options: {
          mode,
          sql_mode: 'VIEW',
          include_comments: true,
          include_performance: true  // 启用性能分析
        },
        debug: debugMode
      };

      if (debugMode) {
        // 调试模式：使用generate-debug端点
        const response = await hqlApiV2.generateDebug(requestData, apiBaseUrl);
        setDebugTrace(response.data);
        setHql(response.data.hql);

        // 调试模式也可能包含性能数据
        if (response.data.performance) {
          setPerformanceReport(response.data.performance);
        }

        if (onHQLGenerated) {
          onHQLGenerated(response.data.hql);
        }
      } else {
        // 普通模式：使用generate端点
        const response = await hqlApiV2.generate(requestData, apiBaseUrl);
        setHql(response.data.hql);

        // 提取性能报告
        if (response.data.performance) {
          setPerformanceReport(response.data.performance);
        }

        if (onHQLGenerated) {
          onHQLGenerated(response.data.hql);
        }
      }

      setLastGenerated(new Date());
    } catch (err: Error) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to generate HQL';
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  // 自动生成（当依赖变化时）
  useEffect(() => {
    const timer = setTimeout(() => {
      if (events.length > 0 && fields.length > 0) {
        generateHQL();
      }
    }, HQL_PREVIEW_DEBOUNCE);

    return () => clearTimeout(timer);
  }, [events, fields, conditions, mode, debugMode]);

  // 复制HQL到剪贴板
  const copyToClipboard = () => {
    navigator.clipboard.writeText(hql);
  };

  return (
    <div className="hql-preview-panel-v2">
      {/* Header */}
      <div className="hql-preview-header">
        <h3>HQL Preview (V2)</h3>
        <div className="header-actions">
          <button
            onClick={generateHQL}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Generating...' : 'Regenerate HQL'}
          </button>
          {hql && (
            <button
              onClick={copyToClipboard}
              className="btn-secondary"
            >
              Copy HQL
            </button>
          )}
          <label className="debug-toggle">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => setDebugMode(e.target.checked)}
            />
            Debug Mode
          </label>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Debug Mode Viewer */}
      {debugMode && debugTrace && (
        <DebugViewer trace={debugTrace} />
      )}

      {/* Performance Indicator */}
      {performanceReport && (
        <PerformanceIndicator report={performanceReport} />
      )}

      {/* HQL Display */}
      <div className="hql-display">
        {hql ? (
          <pre className="hql-content">{hql}</pre>
        ) : (
          <div className="placeholder">
            {loading ? 'Generating HQL...' : 'Add events and fields to generate HQL'}
          </div>
        )}
      </div>

      {/* Metadata */}
      {lastGenerated && (
        <div className="hql-metadata">
          <span>Last generated: {lastGenerated.toLocaleTimeString()}</span>
          <span>Events: {events.length}</span>
          <span>Fields: {fields.length}</span>
          <span>Conditions: {conditions.length}</span>
        </div>
      )}
    </div>
  );
};

export default HQLPreviewPanelV2;
