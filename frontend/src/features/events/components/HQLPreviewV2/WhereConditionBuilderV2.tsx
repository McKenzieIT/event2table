/**
 * WHERE条件构建器 V2
 *
 * 用于构建复杂的WHERE条件
 */

import React, { useState } from 'react';
import './WhereConditionBuilderV2.css';

interface Condition {
  id: string;
  field: string;
  operator: string;
  value?: any;
  logicalOp: 'AND' | 'OR';
}

interface WhereConditionBuilderV2Props {
  conditions: Condition[];
  onConditionsChange: (conditions: Condition[]) => void;
  availableFields?: string[];
}

export const WhereConditionBuilderV2: React.FC<WhereConditionBuilderV2Props> = ({
  conditions,
  onConditionsChange,
  availableFields = []
}) => {
  const [newCondition, setNewCondition] = useState<Partial<Condition>>({
    field: '',
    operator: '=',
    value: '',
    logicalOp: 'AND'
  });

  // 添加条件
  const addCondition = () => {
    if (!newCondition.field) {
      return;
    }

    const condition: Condition = {
      id: Date.now().toString(),
      field: newCondition.field || '',
      operator: newCondition.operator || '=',
      value: newCondition.value,
      logicalOp: newCondition.logicalOp || 'AND'
    };

    onConditionsChange([...conditions, condition]);
    setNewCondition({
      field: '',
      operator: '=',
      value: '',
      logicalOp: 'AND'
    });
  };

  // 删除条件
  const removeCondition = (id: string) => {
    onConditionsChange(conditions.filter(c => c.id !== id));
  };

  // 更新条件
  const updateCondition = (id: string, updates: Partial<Condition>) => {
    onConditionsChange(
      conditions.map(c => (c.id === id ? { ...c, ...updates } : c))
    );
  };

  // 操作符选项
  const operators = [
    { value: '=', label: '=' },
    { value: '!=', label: '!=' },
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '>=', label: '>=' },
    { value: '<=', label: '<=' },
    { value: 'LIKE', label: 'LIKE' },
    { value: 'IN', label: 'IN' },
    { value: 'NOT IN', label: 'NOT IN' },
    { value: 'IS NULL', label: 'IS NULL' },
    { value: 'IS NOT NULL', label: 'IS NOT NULL' }
  ];

  return (
    <div className="where-condition-builder-v2">
      <div className="builder-header">
        <h4>WHERE Conditions</h4>
        <span className="condition-count">{conditions.length} conditions</span>
      </div>

      {/* 条件列表 */}
      <div className="conditions-list">
        {conditions.map((condition, index) => (
          <div key={condition.id} className="condition-item">
            {/* Logical Operator (except first) */}
            {index > 0 && (
              <select
                value={condition.logicalOp}
                onChange={(e) =>
                  updateCondition(condition.id, {
                    logicalOp: e.target.value as 'AND' | 'OR'
                  })
                }
                className="logical-op-select"
              >
                <option value="AND">AND</option>
                <option value="OR">OR</option>
              </select>
            )}

            {/* Field */}
            <input
              type="text"
              value={condition.field}
              onChange={(e) => updateCondition(condition.id, { field: e.target.value })}
              placeholder="Field name"
              className="field-input"
            />

            {/* Operator */}
            <select
              value={condition.operator}
              onChange={(e) => updateCondition(condition.id, { operator: e.target.value })}
              className="operator-select"
            >
              {operators.map(op => (
                <option key={op.value} value={op.value}>
                  {op.label}
                </option>
              ))}
            </select>

            {/* Value (not for IS NULL/IS NOT NULL) */}
            {!condition.operator.includes('IS NULL') && (
              <input
                type="text"
                value={condition.value || ''}
                onChange={(e) => updateCondition(condition.id, { value: e.target.value })}
                placeholder="Value"
                className="value-input"
              />
            )}

            {/* Delete Button */}
            <button
              onClick={() => removeCondition(condition.id)}
              className="delete-btn"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Add New Condition */}
      <div className="add-condition">
        <input
          type="text"
          list="available-fields"
          value={newCondition.field}
          onChange={(e) => setNewCondition({ ...newCondition, field: e.target.value })}
          placeholder="Field name"
          className="field-input"
        />
        {availableFields.length > 0 && (
          <datalist id="available-fields">
            {availableFields.map(field => (
              <option key={field} value={field} />
            ))}
          </datalist>
        )}

        <select
          value={newCondition.operator}
          onChange={(e) => setNewCondition({ ...newCondition, operator: e.target.value })}
          className="operator-select"
        >
          {operators.map(op => (
            <option key={op.value} value={op.value}>
              {op.label}
            </option>
          ))}
        </select>

        {!newCondition.operator?.includes('IS NULL') && (
          <input
            type="text"
            value={newCondition.value}
            onChange={(e) => setNewCondition({ ...newCondition, value: e.target.value })}
            placeholder="Value"
            className="value-input"
          />
        )}

        <button onClick={addCondition} className="add-btn">
          + Add Condition
        </button>
      </div>
    </div>
  );
};

export default WhereConditionBuilderV2;
