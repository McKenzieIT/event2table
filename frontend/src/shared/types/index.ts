/**
 * 前端类型定义 - 统一导出
 *
 * 此文件提供统一的类型导出，支持渐进式迁移到共享类型
 *
 * @version 2.2
 * @updated 2026-02-17
 *
 * 迁移指南:
 * 1. 新组件使用 'from @shared/types/hql-types' (共享类型)
 * 2. 现有组件使用 'from @shared/types' (自动适配)
 * 3. 逐步替换为共享类型
 */

// ========== 共享类型 (HQL生成相关) - 按需导出避免冲突 ==========
export {
  FieldType,
  AggregateFunction,
  Operator,
  LogicalOperator,
  GenerationMode,
  SQLMode,
  Event,
  Field,
  Condition,
  JoinConfig,
  GenerationOptions,
  HQLContext,
  GenerateRequest,
  GenerateResponse,
} from './hql-types';

// ========== 类型适配器 (向后兼容) - 仅导出独有类型 ==========
export {
  isSharedField,
  isFrontendField,
  adaptFieldToFrontend,
  adaptFieldFromFrontend,
} from './types-adapter';

// ========== 前端原有类型 (保留) ==========
export * from './eventNodes';
export * from './fieldBuilder';
export * from './whereBuilder';

// ========== API类型 (从API客户端导出) ==========
export type { GenerateRequest, GenerateResponse, DebugTraceResponse } from '../api/hqlApiV2';

// ========== API通用类型 ==========
export type { 
  ApiResponse, 
  Pagination, 
  PaginatedResponse, 
  ConditionValue,
  HQLGenerateData,
  HQLGenerateResponse,
  Event as ApiEvent,
  Field as ApiField,
  EventParam,
  Game,
  ApiError
} from './api-types';

