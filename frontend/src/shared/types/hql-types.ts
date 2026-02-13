/**
 * HQL类型定义 - 自动生成
 *
 * 版本: 2.1
 * 生成时间: 2026-02-07
 * 源文件: hql-types.schema.yaml
 *
 * ⚠️  请勿手动编辑此文件
 * 所有修改应在schema文件中进行
 */

// ========== 枚举类型 ==========

/** 字段类型枚举 */
export enum FieldType {
  /** 基础字段（直接来自表） */
  BASE = 'base',
  /** 参数字段（从JSON提取） */
  PARAM = 'param',
  /** 自定义表达式字段 */
  CUSTOM = 'custom',
  /** 固定常量值字段 */
  FIXED = 'fixed',
}

/** 聚合函数枚举 */
export enum AggregateFunction {
  /** 计数 */
  COUNT = 'COUNT',
  /** 求和 */
  SUM = 'SUM',
  /** 平均值 */
  AVG = 'AVG',
  /** 最小值 */
  MIN = 'MIN',
  /** 最大值 */
  MAX = 'MAX',
  /** 去重计数 */
  DISTINCT = 'DISTINCT',
}

/** 操作符枚举 */
export enum Operator {
  /** 等于 */
  EQUAL = '=',
  /** 不等于 */
  NOT_EQUAL = '!=',
  /** 大于 */
  GREATER_THAN = '>',
  /** 小于 */
  LESS_THAN = '<',
  /** 大于等于 */
  GREATER_EQUAL = '>=',
  /** 小于等于 */
  LESS_EQUAL = '<=',
  /** 模糊匹配 */
  LIKE = 'LIKE',
  /** 在列表中 */
  IN = 'IN',
  /** 不在列表中 */
  NOT_IN = 'NOT IN',
  /** 为空 */
  IS_NULL = 'IS NULL',
  /** 不为空 */
  IS_NOT_NULL = 'IS NOT NULL',
}

/** 逻辑操作符枚举 */
export enum LogicalOperator {
  /** 逻辑与 */
  AND = 'AND',
  /** 逻辑或 */
  OR = 'OR',
}

/** HQL生成模式 */
export enum GenerationMode {
  /** 单事件模式 */
  SINGLE = 'single',
  /** 多事件JOIN模式 */
  JOIN = 'join',
  /** 多事件UNION模式 */
  UNION = 'union',
}

/** SQL模式 */
export enum SQLMode {
  /** 视图模式 */
  VIEW = 'VIEW',
  /** 存储过程模式 */
  PROCEDURE = 'PROCEDURE',
  /** 自定义模式 */
  CUSTOM = 'CUSTOM',
}

// ========== 数据模型 ==========

/** 事件模型 */
export interface Event {
  name: string
  table_name: string
  partition_field?: string; // default: ds
}

/** 字段模型 */
export interface Field {
  name: string
  type: FieldType
  alias?: string
  aggregate_func?: AggregateFunction
  json_path?: string
  custom_expression?: string
  fixed_value?: any
}

/** WHERE条件模型 */
export interface Condition {
  field: string
  operator: Operator
  value?: any
  logical_op?: LogicalOperator; // default: AND
}

/** JOIN配置模型 */
export interface JoinConfig {
  join_type: string
  join_condition: string
  left_event: Event
  right_event: Event
}

/** HQL生成选项 */
export interface GenerationOptions {
  mode?: GenerationMode; // default: single
  sql_mode?: SQLMode; // default: VIEW
  include_comments?: boolean; // default: True
}

/** HQL生成上下文 */
export interface HQLContext {
  event?: Event
  partition_value?: string; // default: ${ds}
}

// ========== API类型 ==========

/** HQL生成请求 */
export interface GenerateRequest {
  events: Event[]
  fields: Field[]
  where_conditions?: Condition[]
  options?: GenerationOptions
  debug?: boolean; // default: False
}

/** HQL生成响应 */
export interface GenerateResponse {
  success: boolean
  data: Record<string, any>
}

/** 调试跟踪信息 */
export interface DebugTrace {
  hql: string
  steps: DebugStep[]
  events: Event[]
  fields: Field[]
}

/** 调试步骤 */
export interface DebugStep {
  step: string
  result: any
  count?: number
}

// ========== 性能分析类型 ==========

/** 性能问题 */
export interface PerformanceIssue {
  type: string
  message: string
  suggestion?: string
}

/** 性能指标 */
export interface PerformanceMetrics {
  has_partition_filter: boolean
  has_select_star: boolean
  join_count: number
  cross_join_count: number
  subquery_count: number
  udf_count: number
  complexity: string
}

/** 性能报告 */
export interface PerformanceReport {
  score: number
  issues: PerformanceIssue[]
  metrics: PerformanceMetrics
}
