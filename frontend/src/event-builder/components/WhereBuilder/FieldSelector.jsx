/**
 * FieldSelector Component
 * 字段选择下拉框
 */
import React from 'react';
import './FieldSelector.css';

export default function FieldSelector({ value, onChange, canvasFields = [] }) {
  const options = [
    ...canvasFields.map(field => ({
      value: field.fieldName,
      label: `${field.displayName} (${field.fieldName})`
    })),
    // 常用字段
    { value: 'ds', label: 'ds (分区)' },
    { value: 'role_id', label: 'role_id (角色ID)' },
    { value: 'account_id', label: 'account_id (账号ID)' },
    { value: 'utdid', label: 'utdid (设备ID)' },
    { value: 'tm', label: 'tm (上报时间)' },
    { value: 'ts', label: 'ts (时间戳)' },
  ];

  return (
    <select
      className="field-selector"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">选择字段</option>
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
