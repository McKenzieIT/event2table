/**
 * StatsPanel Component
 * 统计信息面板组件
 */
import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { ensureArray, safeFilter, safeLength } from '@shared/utils/componentUtils';

export default function StatsPanel({ fields, whereConditions }) {
  const stats = useMemo(() => {
    // ✅ 添加空值检查
    const safeFields = ensureArray(fields);
    const safeWhereConditions = ensureArray(whereConditions);

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

StatsPanel.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      fieldType: PropTypes.oneOf(['base', 'param', 'basic', 'custom', 'fixed']).isRequired,
      name: PropTypes.string.isRequired,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired
    })
  ),
  whereConditions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
      operator: PropTypes.string.isRequired,
      value: PropTypes.any
    })
  )
};

StatsPanel.defaultProps = {
  fields: [],
  whereConditions: []
};
