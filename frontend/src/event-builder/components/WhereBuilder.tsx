// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * WhereBuilder Component
 * WHERE条件构建器组件
 */
import { ensureArray, safeLength } from '@shared/utils/componentUtils';
import { useState } from 'react';

// WHERE条件接口
export interface WhereCondition {
  id: string;
  field: string;
  operator: string;
  value: any;
  logicalOperator?: string;
  type?: 'condition' | 'group';
  conditions?: WhereCondition[];
}

// 组件Props接口
interface WhereBuilderProps {
  conditions?: WhereCondition[];
  onChange: (conditions: WhereCondition[]) => void;
  onOpenModal: () => void;
}

export default function WhereBuilder({
  conditions = [],
  onChange,
  onOpenModal
}: WhereBuilderProps) {
  const [isCollapsed, setIsCollapsed] = useState(true);

  // ✅ 添加空值保护
  const safeConditions = ensureArray(conditions);

  const generateWhereClause = (): string => {
    if (safeLength(safeConditions) === 0) {
      return '暂无WHERE条件';
    }

    const parts = safeConditions.map((condition, index) => {
      if (condition.type === 'group') {
        return `(${condition.conditions?.length || 0} 个条件)`;
      } else {
        const operator = condition.logicalOperator ? ` ${condition.logicalOperator} ` : '';
        return `${operator}${condition.field || '?'} ${condition.operator || '='} '${condition.value || ''}'`;
      }
    });

    return parts.join(' ');
  };

  return (
    <div className="sidebar-section glass-card-dark where-builder-section">
      <div
        className="section-header"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <h3>
          <i className="bi bi-funnel"></i>
                   WHERE条件
        </h3>
        {onOpenModal && (
          <button
            className="btn btn-sm btn-outline-primary"
            data-testid="open-where-builder"
            onClick={(e) => {
              e.stopPropagation();
              onOpenModal();
            }}
          >
            <i className="bi bi-gear"></i>
                     配置
          </button>
        )}
        <i className={`bi bi-chevron-${isCollapsed ? 'right' : 'down'} toggle-icon`}></i>
      </div>
      {!isCollapsed && (
        <div className="section-content">
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
            {generateWhereClause()}
          </pre>
          <p className="help-text">点击"配置"按钮编辑WHERE条件</p>
        </div>
      )}
    </div>
  );
}
