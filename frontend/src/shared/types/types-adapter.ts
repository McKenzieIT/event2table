// @ts-nocheck - TypeScript检查暂禁用
/**
 * 类型适配器 - 将共享类型与现有前端类型桥接
 *
 * 此文件提供向后兼容的适配层，允许逐步迁移到共享类型
 */

import {
  EventType as SharedEvent,
  Field as SharedField,
  Condition as SharedCondition,
  FieldType as SharedFieldType,
  Operator as SharedOperator,
  LogicalOperator as SharedLogicalOperator,
  GenerationMode,
  SQLMode
} from './hql-types';

// ========== 前端原有类型 (向后兼容) ==========

/**
 * 字段类型枚举 (原有)
 * @deprecated 使用 SharedFieldType 代替
 */
export enum FieldType {
  PARAMETER = 'parameter',  // 映射到 SharedFieldType.PARAM
  BASIC = 'basic',          // 映射到 SharedFieldType.BASE
  CUSTOM = 'custom',        // 映射到 SharedFieldType.CUSTOM
  FIXED = 'fixed'           // 映射到 SharedFieldType.FIXED
}

/**
 * 数据类型枚举 (原有)
 */
export enum DataType {
  STRING = 'string',
  INT = 'int',
  BIGINT = 'bigint',
  FLOAT = 'float',
  DECIMAL = 'decimal(10,2)',
  BOOLEAN = 'boolean'
}

/**
 * 事件接口 (原有 - 增强版)
 * 扩展自共享类型
 */
export interface Event extends SharedEvent {
  id: number;
  gid: number;
  description: string;
  category: string;
}

/**
 * 参数接口 (原有)
 */
export interface Parameter {
  id: number;
  name: string;
  alias: string;
  dataType: DataType;
  description: string;
  isRequired: boolean;
}

/**
 * 字段接口 (原有 - 增强版)
 * 扩展自共享类型
 */
export interface Field extends SharedField {
  id: string;
  sourceId?: number;
  dataType: DataType;
  isEditable: boolean;
}

/**
 * WHERE条件接口 (原有)
 * @deprecated 使用 SharedCondition 或 WhereCondition 代替
 */
export interface WhereCondition {
  id: string;
  field: string;
  operator: '=' | '!=' | '>' | '<' | '>=' | '<=' | 'LIKE' | 'IN' | 'NOT IN' | 'IS NULL' | 'IS NOT NULL';
  value?: string | number | boolean;
  logic?: 'AND' | 'OR';
  dataType?: string;
}

/**
 * 字段配置接口 (原有)
 */
export interface FieldConfig {
  id?: number;
  name: string;
  gameGid: number;
  eventId: number;
  fields: Field[];
  mode: SQLMode;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * HQL预览选项接口 (原有)
 */
export interface HQLPreviewOptions {
  fields: Field[];
  mode: SQLMode;
  event?: Event;
  gameId?: number;
}

/**
 * API响应接口 (原有)
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

/**
 * 分页参数接口 (原有)
 */
export interface PaginationParams {
  page: number;
  limit: number;
  search?: string;
}

/**
 * 分页响应接口 (原有)
 */
export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  timestamp: string;
}

// ========== 类型转换适配器 ==========

/**
 * 字段类型转换器: 前端 -> 共享类型
 */
export function toSharedFieldType(fieldType: FieldType): SharedFieldType {
  const mapping = {
    [FieldType.PARAMETER]: SharedFieldType.PARAM,
    [FieldType.BASIC]: SharedFieldType.BASE,
    [FieldType.CUSTOM]: SharedFieldType.CUSTOM,
    [FieldType.FIXED]: SharedFieldType.FIXED
  };
  return mapping[fieldType];
}

/**
 * 字段类型转换器: 共享类型 -> 前端
 */
export function fromSharedFieldType(fieldType: SharedFieldType): FieldType {
  const mapping = {
    [SharedFieldType.PARAM]: FieldType.PARAMETER,
    [SharedFieldType.BASE]: FieldType.BASIC,
    [SharedFieldType.CUSTOM]: FieldType.CUSTOM,
    [SharedFieldType.FIXED]: FieldType.FIXED
  };
  return mapping[fieldType];
}

/**
 * 字段转换器: 前端 -> 共享类型
 */
export function toSharedField(field: Field): SharedField {
  return {
    name: field.name,
    type: toSharedFieldType(field.type as FieldType),
    alias: field.alias,
    aggregate_func: field.aggregate_func,
    json_path: field.json_path,
    custom_expression: field.custom_expression,
    fixed_value: field.fixed_value
  };
}

/**
 * 字段转换器: 共享类型 -> 前端
 */
export function fromSharedField(sharedField: SharedField, id?: string): Field {
  return {
    id: id || crypto.randomUUID(),
    name: sharedField.name,
    type: fromSharedFieldType(sharedField.type) as any,
    alias: sharedField.alias,
    aggregate_func: sharedField.aggregate_func,
    json_path: sharedField.json_path,
    custom_expression: sharedField.custom_expression,
    fixed_value: sharedField.fixed_value,
    dataType: DataType.STRING,  // 默认值
    isEditable: true            // 默认值
  };
}

/**
 * WHERE条件转换器: 前端 -> 共享类型
 */
export function toSharedCondition(condition: WhereCondition): SharedCondition {
  return {
    field: condition.field,
    operator: condition.operator as any,
    value: condition.value,
    logical_op: condition.logic as any
  };
}

/**
 * WHERE条件转换器: 共享类型 -> 前端
 */
export function fromSharedCondition(shared: SharedCondition): WhereCondition {
  return {
    id: crypto.randomUUID(),
    field: shared.field,
    operator: shared.operator as any,
    value: shared.value,
    logic: shared.logical_op
  };
}

// ========== 类型守卫 ==========

/**
 * 检查是否为共享类型字段
 */
export function isSharedField(field: any): field is SharedField {
  return field && typeof field.name === 'string' && typeof field.type === 'string';
}

/**
 * 检查是否为前端类型字段
 */
export function isFrontendField(field: any): field is Field {
  return field && typeof field.id === 'string' && field.dataType !== undefined;
}

// ========== 导出所有类型 ==========

export * from './hql-types';  // 重新导出所有共享类型
export * from './eventNodes';  // 保留原有事件节点类型
export * from './whereBuilder'; // 保留原有WHERE构建器类型
