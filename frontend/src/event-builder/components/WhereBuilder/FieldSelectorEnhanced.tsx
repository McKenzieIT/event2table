// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * FieldSelectorEnhanced Component
 * 增强版字段选择器，支持事件的所有参数字段 + 已在画布标记
 *
 * @usage
 * <FieldSelectorEnhanced
 *   value={condition.field}
 *   onChange={(value) => handleChange('field', value)}
 *   selectedEvent={selectedEvent}
 *   canvasFields={canvasFields}
 * />
 */
import React from 'react';

import { useEventAllParams } from '../../hooks/useEventAllParams';

import { FieldSelectorEnhancedProps } from './types';
import './FieldSelectorEnhanced.css';

const FieldSelectorEnhanced: React.FC<FieldSelectorEnhancedProps> = ({
  value,
  onChange,
  selectedEvent,
  canvasFields = []
}) => {
  // 获取所有字段（包含画布状态）
  const { fields, isLoading, paramCount, baseCount } = useEventAllParams(
    selectedEvent,
    canvasFields
  );

  // 分组字段
  const paramFields = fields.filter(f => f.group === 'parameter');
  const baseFields = fields.filter(f => f.group === 'base');

  // 处理字段选择
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  // 加载状态
  if (isLoading) {
    return (
      <select className="field-selector-enhanced" disabled>
        <option>加载中...</option>
      </select>
    );
  }

  // 无事件选择
  if (!selectedEvent) {
    return (
      <select className="field-selector-enhanced" disabled>
        <option>请先选择事件</option>
      </select>
    );
  }

  return (
    <select
      className="field-selector-enhanced"
      value={value}
      onChange={handleChange}
      aria-label="选择字段"
    >
      <option value="">选择字段</option>

      {/* 参数字段分组 */}
      {paramFields.length > 0 && (
        <optgroup label={`📦 参数字段 (${paramCount})`}>
          {paramFields.map(field => (
            <option
              key={field.fieldName}
              value={field.fieldName}
              className={field.isFromCanvas ? 'field-in-canvas' : ''}
            >
              {field.isFromCanvas ? '✓ ' : ''}{field.displayName} ({field.fieldName})
            </option>
          ))}
        </optgroup>
      )}

      {/* 基础字段分组 */}
      {baseFields.length > 0 && (
        <optgroup label={`📊 基础字段 (${baseCount})`}>
          {baseFields.map(field => (
            <option
              key={field.fieldName}
              value={field.fieldName}
              className={field.isFromCanvas ? 'field-in-canvas' : ''}
            >
              {field.isFromCanvas ? '✓ ' : ''}{field.displayName}
            </option>
          ))}
        </optgroup>
      )}
    </select>
  );
};

export default FieldSelectorEnhanced;
