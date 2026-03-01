/**
 * WhereBuilder Type Definitions
 */

import { ReactNode } from 'react';

/** WHERE条件类型 */
export type WhereConditionType = 'condition' | 'group';

/** 逻辑操作符类型 */
export type LogicalOperator = 'AND' | 'OR';

/** WHERE操作符类型 */
export type WhereOperator =
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
  | 'NOT BETWEEN'
  | 'IS NULL'
  | 'IS NOT NULL';

/** 字段分组类型 */
export type FieldGroup = 'parameter' | 'base';

/** 单个WHERE条件 */
export interface WhereCondition {
  id: string;
  type: WhereConditionType;
  field?: string;
  operator?: WhereOperator;
  value?: string | string[] | null;
  logicalOp?: LogicalOperator;
}

/** WHERE条件分组 */
export interface WhereGroup extends WhereCondition {
  type: 'group';
  children: WhereCondition[];
  isCollapsed?: boolean;
}

/** 画布字段定义 */
export interface CanvasField {
  fieldName?: string;
  name?: string;
  displayName?: string;
}

/** 带状态的字段定义 */
export interface FieldWithStatus {
  fieldName: string;
  displayName: string;
  isFromCanvas: boolean;
  group: FieldGroup;
}

/** 选中的事件定义 */
export interface SelectedEvent {
  id: number;
  name?: string;
  [key: string]: any;
}

/** 操作符定义 */
export interface OperatorDefinition {
  value: WhereOperator;
  label: string;
  description: string;
}

/** 字段选择器Props */
export interface FieldSelectorProps {
  value?: string;
  onChange: (value: string) => void;
  canvasFields?: CanvasField[];
  selectedEvent?: SelectedEvent | null;
}

/** 增强版字段选择器Props */
export interface FieldSelectorEnhancedProps extends FieldSelectorProps {
  canvasFields: CanvasField[];
  selectedEvent: SelectedEvent | null;
}

/** 操作符选择器Props */
export interface OperatorSelectorProps {
  value?: WhereOperator;
  onChange: (value: WhereOperator) => void;
  field?: string;
}

/** 值输入组件Props */
export interface ValueInputProps {
  value?: string | string[] | null;
  onChange: (value: string | string[] | null) => void;
  operator?: WhereOperator;
  field?: string;
}

/** 条件更新回调 */
export type ConditionUpdateCallback = (id: string, updates: Partial<WhereCondition>) => void;

/** 条件删除回调 */
export type ConditionDeleteCallback = (id: string) => void;

/** 条件列表更新回调 */
export type ConditionsUpdateCallback = (conditions: WhereCondition[]) => void;

/** WHERE条件项Props */
export interface WhereConditionItemProps {
  condition: WhereCondition;
  index: number;
  isFirst: boolean;
  canvasFields?: CanvasField[];
  selectedEvent?: SelectedEvent | null;
  onUpdate: ConditionUpdateCallback;
  onDelete: ConditionDeleteCallback;
}

/** WHERE条件画布Props */
export interface WhereBuilderCanvasProps {
  conditions: WhereCondition[];
  canvasFields?: CanvasField[];
  selectedEvent?: SelectedEvent | null;
  onUpdate: ConditionsUpdateCallback;
}

/** WHERE构建器Props */
export interface WhereBuilderProps {
  conditions: WhereCondition[];
  canvasFields?: CanvasField[];
  selectedEvent?: SelectedEvent | null;
  onUpdate: ConditionsUpdateCallback;
  onConditionsChange?: (conditions: WhereCondition[]) => void;
}

/** WHERE构建器模态框Props */
export interface WhereBuilderModalProps extends WhereBuilderProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
}
