/**
 * Field Builder Types
 *
 * Type definitions for the field builder module
 * These types extend the base types with field-builder-specific properties
 */

import { Event as BaseEvent } from './event-types';
import { Field as BaseField, FieldType as BaseFieldType } from './hql-types';
import { Parameter as BaseParameter } from './parameter-types';

// 字段类型枚举
export enum FieldType {
  PARAMETER = 'param',
  BASIC = 'base',
  CUSTOM = 'custom',
  FIXED = 'fixed'
}

// 数据类型枚举
export enum DataType {
  STRING = 'string',
  INT = 'int',
  BIGINT = 'bigint',
  FLOAT = 'float',
  DECIMAL = 'decimal(10,2)',
  BOOLEAN = 'boolean'
}

// 事件接口 - Extends base Event with field-builder-specific properties
export interface Event extends BaseEvent {
  parameters: Parameter[];
  category?: string;
}

// 参数接口 - Extends base Parameter with field-builder-specific properties
export interface Parameter extends BaseParameter {
  alias?: string;
  dataType: DataType;
  isRequired?: boolean;
}

// 字段接口 - Extends base Field with field-builder-specific properties
export interface Field extends Omit<BaseField, 'type'> {
  id: string; // UUID
  type: FieldType;
  sourceId?: number; // 参数ID（如果是参数类型）
  dataType: DataType;
  fixedValue?: string; // 固定值
  mapping?: string; // 映射表达式
  isEditable: boolean;
}

// 配置接口
export interface FieldConfig {
  id?: number;
  name: string;
  gameGid: number;
  eventId: number;
  fields: Field[];
  mode: 'view' | 'procedure';
  createdAt?: string;
  updatedAt?: string;
}

// SQL输出模式
export type SQLMode = 'view' | 'procedure' | 'custom';

// WHERE条件接口 - Import from whereBuilder to avoid duplication
export type { WhereCondition } from './whereBuilder';

// HQL预览选项接口
export interface HQLPreviewOptions {
  fields: Field[];
  mode: SQLMode;
  event?: Event;
  gameId?: number;
}

// API响应接口
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

// 分页参数接口
export interface PaginationParams {
  page: number;
  limit: number;
  search?: string;
}

// 分页响应接口
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

// Toast通知类型
export type ToastType = 'success' | 'error' | 'warning' | 'info';

// Toast接口
export interface Toast {
  show: (message: string, type?: ToastType) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
}

// 扩展Window接口以包含toast
declare global {
  interface Window {
    toast?: Toast;
  }
}
