// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * ValueInput Component
 * 值输入组件（支持多种类型）
 */
import React, { useState, useEffect, ChangeEvent } from 'react';
import './ValueInput.css';

/**
 * 支持的操作符类型
 */
type OperatorType =
  | '='
  | '!='
  | '>'
  | '>='
  | '<'
  | '<='
  | 'LIKE'
  | 'NOT LIKE'
  | 'IN'
  | 'NOT IN'
  | 'BETWEEN'
  | 'NOT BETWEEN'
  | 'IS NULL'
  | 'IS NOT NULL';

/**
 * 字段定义接口
 */
interface Field {
  name: string;
  type?: string;
  [key: string]: any;
}

/**
 * ValueInput 组件 Props
 */
interface ValueInputProps {
  /** 当前值（可以是字符串、字符串数组或null） */
  value: string | string[] | null;
  /** 值变化回调 */
  onChange: (value: string | string[] | null) => void;
  /** 操作符 */
  operator: OperatorType;
  /** 字段定义 */
  field: Field;
}

/**
 * ValueInput 组件
 *
 * 根据操作符类型渲染不同的输入控件：
 * - IS NULL / IS NOT NULL: 显示占位符
 * - IN / NOT IN: 显示逗号分隔的文本输入
 * - BETWEEN / NOT BETWEEN: 显示范围输入（最小值 至 最大值）
 * - 其他: 显示普通文本输入
 */
export default function ValueInput({ value, onChange, operator }: ValueInputProps) {
  const [inputValue, setInputValue] = useState<string>(value || '');

  // 根据操作符决定输入类型
  const needsArray: boolean = ['IN', 'NOT IN'].includes(operator);
  const needsRange: boolean = ['BETWEEN', 'NOT BETWEEN'].includes(operator);
  const needsNothing: boolean = ['IS NULL', 'IS NOT NULL'].includes(operator);

  const handleChange = (newValue: string | string[]): void => {
    if (typeof newValue === 'string') {
      setInputValue(newValue);
    }
    onChange(newValue);
  };

  // 如果操作符需要null值
  useEffect(() => {
    if (needsNothing) {
      onChange(null);
    }
  }, [operator, onChange]);

  // IS NULL / IS NOT NULL: 不显示输入框
  if (needsNothing) {
    return <span className="text-muted">-</span>;
  }

  // IN / NOT IN: 显示逗号分隔的数组输入
  if (needsArray) {
    return (
      <input
        type="text"
        className="value-input"
        placeholder="值1, 值2, 值3"
        value={Array.isArray(value) ? value.join(', ') : (value || '')}
        onChange={(e: ChangeEvent<HTMLInputElement>) => {
          const arr: string[] = e.target.value.split(',').map(s => s.trim());
          handleChange(arr);
        }}
      />
    );
  }

  // BETWEEN / NOT BETWEEN: 显示范围输入（两个输入框）
  if (needsRange) {
    return (
      <div className="value-range-input">
        <input
          type="text"
          className="value-input"
          placeholder="最小值"
          value={Array.isArray(value) ? (value[0] || '') : ''}
          onChange={(e: ChangeEvent<HTMLInputElement>) => {
            const arr: string[] = Array.isArray(value) ? [...value] : [];
            arr[0] = e.target.value;
            handleChange(arr);
          }}
        />
        <span>至</span>
        <input
          type="text"
          className="value-input"
          placeholder="最大值"
          value={Array.isArray(value) ? (value[1] || '') : ''}
          onChange={(e: ChangeEvent<HTMLInputElement>) => {
            const arr: string[] = Array.isArray(value) ? [...value] : [];
            arr[1] = e.target.value;
            handleChange(arr);
          }}
        />
      </div>
    );
  }

  // 默认: 显示普通文本输入
  return (
    <input
      type="text"
      className="value-input"
      placeholder="值"
      value={inputValue}
      onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(e.target.value)}
    />
  );
}
