/**
 * WhereBuilder Component
 * WHERE条件构建器组件
 */
import { useState } from 'react';
import PropTypes from 'prop-types';
import { ensureArray, safeLength } from '@shared/utils/componentUtils';

export default function WhereBuilder({ conditions, onChange, onOpenModal }) {
  const [isCollapsed, setIsCollapsed] = useState(true);

  // ✅ 添加空值保护
  const safeConditions = ensureArray(conditions);

  const generateWhereClause = () => {
    if (safeLength(safeConditions) === 0) {
      return '<span class="text-muted">暂无WHERE条件</span>';
    }

    const parts = safeConditions.map((condition, index) => {
      if (condition.type === 'group') {
        return `<span class="where-group">(${condition.conditions?.length || 0} 个条件)</span>`;
      } else {
        const operator = condition.logicalOperator ? ` ${condition.logicalOperator} ` : '';
        return `${operator}<span class="where-condition">${condition.field || '?'} ${condition.operator || '='} '${condition.value || ''}'</span>`;
      }
    });

    return '<code>' + parts.join(' ') + '</code>';
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
          <div
            className="where-summary"
            dangerouslySetInnerHTML={{ __html: generateWhereClause() }}
          />
          <p className="help-text">点击"配置"按钮编辑WHERE条件</p>
        </div>
      )}
    </div>
  );
}

WhereBuilder.propTypes = {
  conditions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
      operator: PropTypes.string.isRequired,
      value: PropTypes.any,
      logicalOperator: PropTypes.string,
      type: PropTypes.oneOf(['condition', 'group'])
    })
  ),
  onChange: PropTypes.func.isRequired,
  onOpenModal: PropTypes.func.isRequired
};

WhereBuilder.defaultProps = {
  conditions: []
};
