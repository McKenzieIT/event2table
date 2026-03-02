// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * FieldSelector Component
 * 字段选择下拉框（支持增强版：显示事件所有参数）
 */
import React from 'react';
import { useEventAllParams } from '../../hooks/useEventAllParams';
import { FieldSelectorProps } from './types';
import './FieldSelector.css';

const FieldSelector: React.FC<FieldSelectorProps> = ({
  value,
  onChange,
  canvasFields = [],
  selectedEvent
}) => {
  // 如果有选择事件，使用增强版hook获取所有参数
  const { fields: allFields, isLoading } = useEventAllParams(selectedEvent, canvasFields);

  // 如果没有选择事件，使用原有逻辑（向后兼容）
  if (!selectedEvent) {
    const options = [
      ...canvasFields.map(field => ({
        value: field.fieldName || field.name || '',
        label: `${field.displayName || field.fieldName || field.name || ''} (${field.fieldName || field.name || ''})`
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

  // 增强版：显示所有事件参数 + 基础字段，并分组
  return (
    <select
      className="field-selector"
      value={value}
      disabled={isLoading}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">选择字段</option>

      {/* 参数字段分组 */}
      <optgroup label="📦 参数字段">
        {allFields
          .filter(f => f.group === 'parameter')
          .map(field => (
            <option
              key={field.fieldName}
              value={field.fieldName}
              className={field.isFromCanvas ? 'field-from-canvas' : ''}
            >
              {field.isFromCanvas ? '✓ ' : ''}{field.displayName} ({field.fieldName})
            </option>
          ))}
      </optgroup>

      {/* 基础字段分组 */}
      <optgroup label="📊 基础字段">
        {allFields
          .filter(f => f.group === 'base')
          .map(field => (
            <option
              key={field.fieldName}
              value={field.fieldName}
              className={field.isFromCanvas ? 'field-from-canvas' : ''}
            >
              {field.isFromCanvas ? '✓ ' : ''}{field.displayName}
            </option>
          ))}
      </optgroup>
    </select>
  );
};

export default FieldSelector;
