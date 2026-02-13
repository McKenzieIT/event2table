/**
 * OperatorSelector Component
 * 操作符选择器
 */
import React from 'react';
import './OperatorSelector.css';

const OPERATORS = [
  { value: '=', label: '=', description: '等于' },
  { value: '!=', label: '!=', description: '不等于' },
  { value: '>', label: '>', description: '大于' },
  { value: '<', label: '<', description: '小于' },
  { value: '>=', label: '>=', description: '大于等于' },
  { value: '<=', label: '<=', description: '小于等于' },
  { value: 'IN', label: 'IN', description: '包含于' },
  { value: 'NOT IN', label: 'NOT IN', description: '不包含于' },
  { value: 'LIKE', label: 'LIKE', description: '模糊匹配' },
  { value: 'NOT LIKE', label: 'NOT LIKE', description: '不匹配' },
  { value: 'BETWEEN', label: 'BETWEEN', description: '介于' },
  { value: 'IS NULL', label: 'IS NULL', description: '为空' },
  { value: 'IS NOT NULL', label: 'IS NOT NULL', description: '不为空' },
];

export default function OperatorSelector({ value, onChange, field }) {
  return (
    <select
      className="operator-selector"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">选择操作符</option>
      {OPERATORS.map(op => (
        <option key={op.value} value={op.value} title={op.description}>
          {op.label}
        </option>
      ))}
    </select>
  );
}
