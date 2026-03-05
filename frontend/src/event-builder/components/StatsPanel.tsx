// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * StatsPanel Component
 * 统计信息面板组件
 */
import React, { useMemo } from 'react';
import { ensureArray, safeFilter, safeLength } from '@shared/utils/componentUtils';

type FieldType = 'base' | 'param' | 'basic' | 'custom' | 'fixed';

interface Field {
  id: string;
  fieldType: FieldType;
  name: string;
  alias?: string;
  dataType: string;
}

interface WhereCondition {
  id: string;
  field: string;
  operator: string;
  value: unknown;
}

interface Stats {
  total: number;
  baseFields: number;
  paramFields: number;
  whereCount: number;
}

interface StatsPanelProps {
  fields?: Field[] | null;
  whereConditions?: WhereCondition[] | null;
}

export default function StatsPanel({ fields = [], whereConditions = [] }: StatsPanelProps) {
  const stats = useMemo<Stats>(() => {
    // ✅ 添加空值检查
    const safeFields = ensureArray<Field>(fields);
    const safeWhereConditions = ensureArray<WhereCondition>(whereConditions);

    const baseFields = safeFilter(safeFields, f => f.fieldType === 'base').length;
    const paramFields = safeFilter(safeFields, f => f.fieldType === 'param').length;
    const whereCount = safeLength(safeWhereConditions);

    return {
      total: safeLength(safeFields),
      baseFields,
      paramFields,
      whereCount,
    };
  }, [fields, whereConditions]);

  return (
    <div className="sidebar-section glass-card-dark stats-panel">
      <div className="section-header">
        <h3>
          <i className="bi bi-bar-chart"></i>
                   统计信息
        </h3>
      </div>
      <div className="section-content">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">总字段数</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.baseFields}</div>
            <div className="stat-label">基础字段</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.paramFields}</div>
            <div className="stat-label">参数字段</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.whereCount}</div>
            <div className="stat-label">WHERE条件</div>
          </div>
        </div>
      </div>
    </div>
  );
}
