/**
 * Shared Types - 统一类型导出
 * Centralized Type Exports
 *
 * This file provides unified type exports with progressive migration support
 *
 * @version 3.0
 * @updated 2026-03-10
 *
 * Migration Guide:
 * 1. New components: import from '@/shared/types/event-types', '@/shared/types/game-types', etc.
 * 2. Existing components: import from '@/shared/types' (auto-adapted)
 * 3. Gradually migrate to unified types
 */

// ========== Core Entity Types - 统一实体类型 ==========
export type {
  Event,
  EventCreateRequest,
  EventUpdateRequest,
  EventListOptions,
  EventListResponse,
  EventDetailsResponse
} from './event-types';

export type {
  Game,
  GameCreateRequest,
  GameUpdateRequest,
  GameListOptions,
  GameListResponse,
  GameDetailsResponse,
  GameContext,
  GameStatus
} from './game-types';

export type {
  Parameter,
  ParameterCreateRequest,
  ParameterUpdateRequest,
  ParameterListOptions,
  ParameterListResponse,
  ParameterDetailsResponse,
  ParameterUsage,
  ParameterDetails,
  ParameterType
} from './parameter-types';

// ========== HQL Types - HQL类型 ==========
export type {
  Event as HqlEvent,
  Field,
  FieldConfig,
  Condition,
  JoinConfig,
  GenerationOptions,
  HQLContext,
  GenerateRequest,
  GenerateResponse,
  DebugTrace,
  DebugStep,
  PerformanceIssue,
  PerformanceMetrics,
  PerformanceReport,
} from './hql-types';

// Export enums as values
export {
  FieldType,
  AggregateFunction,
  Operator,
  LogicalOperator,
  GenerationMode,
  SQLMode,
} from './hql-types';

// ========== API Types - API通用类型 ==========
export type {
  ApiResponse,
  Pagination,
  PaginatedResponse,
  ConditionValue,
  HQLGenerateData,
  HQLGenerateResponse,
  EventParam,
  ApiError
} from './api-types';

// ========== Type Adapters - 类型适配器 (向后兼容) ==========
export {
  isSharedField,
  isFrontendField,
  adaptFieldToFrontend,
  adaptFieldFromFrontend,
} from './types-adapter';

// ========== Frontend Specific Types - 前端特定类型 ==========
export * from './eventNodes';
export * from './fieldBuilder';
export * from './whereBuilder';

// ========== API Client Types - API客户端类型 ==========
export type { GenerateRequest as ApiGenerateRequest, GenerateResponse as ApiGenerateResponse, DebugTraceResponse } from '../api/hqlApi';

