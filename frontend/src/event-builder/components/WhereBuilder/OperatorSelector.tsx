// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * OperatorSelector Component
 * 操作符选择器
 *
 * Features:
 * - Select dropdown for SQL operators
 * - Operator descriptions as tooltips
 * - Support for common comparison and logical operators
 *
 * @component OperatorSelector
 */
import React from 'react';
import './OperatorSelector.css';

/**
 * Operator type definition
 * 支持的SQL操作符类型
 */
export type OperatorType =
  | '='
  | '!='
  | '>'
  | '<'
  | '>='
  | '<='
  | 'IN'
  | 'NOT IN'
  | 'LIKE'
  | 'NOT LIKE'
  | 'BETWEEN'
  | 'IS NULL'
  | 'IS NOT NULL';

/**
 * Operator option interface
 * 操作符选项接口
 */
interface OperatorOption {
  value: OperatorType;
  label: string;
  description: string;
}

/**
 * Available operators
 * 可用的操作符列表
 */
const OPERATORS: OperatorOption[] = [
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

/**
 * Component props interface
 * 组件属性接口
 */
interface OperatorSelectorProps {
  /**
   * Current selected operator value
   * 当前选中的操作符值
   */
  value: OperatorType | '';

  /**
   * Change handler for operator selection
   * 操作符选择变更处理函数
   */
  onChange: (operator: OperatorType) => void;

  /**
   * Field name (optional, for future enhancements)
   * 字段名称（可选，用于未来扩展）
   */
  field?: string;
}

/**
 * OperatorSelector Component
 *
 * A dropdown selector for SQL operators with descriptions.
 *
 * @param props - Component props
 * @returns React component
 *
 * @example
 * ```tsx
 * <OperatorSelector
 *   value="="
 *   onChange={(operator) => setOperator(operator)}
 * />
 * ```
 */
export default function OperatorSelector({ value, onChange }: OperatorSelectorProps): React.ReactElement {
  return (
    <select
      className="operator-selector"
      value={value}
      onChange={(e) => onChange(e.target.value as OperatorType)}
    >
      <option value="">选择操作符</option>
      {OPERATORS.map((op) => (
        <option key={op.value} value={op.value} title={op.description}>
          {op.label}
        </option>
      ))}
    </select>
  );
}
