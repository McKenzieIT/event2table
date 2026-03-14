/**
 * Events Module Types
 *
 * Type definitions for event-related data structures
 *
 * ⚠️ IMPORTANT: Event interface is now imported from @/shared/types/event-types
 * Do not define Event interface here - use the unified definition
 */

// Re-export Event from shared types for convenience
export type { Event } from '@/shared/types/event-types';

/**
 * HQL field type enum
 */
export type HqlFieldType = 'base' | 'param' | 'custom' | 'fixed';

/**
 * HQL field structure
 */
export interface HqlField {
  fieldName: string;
  fieldType: HqlFieldType;
  alias?: string;
  jsonPath?: string;
  customExpression?: string;
  fixedValue?: unknown;
  aggregateFunc?: string;
}

/**
 * HQL where condition operator
 */
export type WhereOperator =
  | '='
  | '!='
  | '>'
  | '<'
  | '>='
  | '<='
  | 'LIKE'
  | 'IN'
  | 'NOT IN'
  | 'IS NULL'
  | 'IS NOT NULL';

/**
 * HQL where condition
 */
export interface WhereCondition {
  field: string;
  operator: WhereOperator;
  value?: unknown;
  logicalOp?: 'AND' | 'OR';
}

/**
 * HQL generation mode
 */
export type HqlMode = 'single' | 'join' | 'union';

/**
 * HQL SQL mode
 */
export type SqlMode = 'VIEW' | 'PROCEDURE' | 'CUSTOM';

/**
 * HQL generation options
 */
export interface HqlOptions {
  mode?: HqlMode;
  sql_mode?: SqlMode;
  include_comments?: boolean;
  include_performance?: boolean;
}

/**
 * HQL generation request
 */
export interface HqlGenerateRequest {
  events: Array<{
    game_gid: number;
    event_id: number;
  }>;
  fields: HqlField[];
  where_conditions?: WhereCondition[];
  options?: HqlOptions;
  debug?: boolean;
}

/**
 * HQL generation response
 */
export interface HqlGenerateResponse {
  hql: string;
  generated_at: string;
  performance?: unknown;
}

/**
 * Debug trace step
 */
export interface DebugStep {
  step: string;
  result: unknown;
  count?: number;
}

/**
 * Debug trace response
 */
export interface DebugTraceResponse {
  hql: string;
  steps: DebugStep[];
  events: Array<{
    game_gid: number;
    event_id: number;
  }>;
  fields: HqlField[];
  performance?: unknown;
}

/**
 * Field recommendation
 */
export interface FieldRecommendation {
  name: string;
  type: string;
  description: string;
}

/**
 * Field recommendations response
 */
export interface FieldRecommendationsResponse {
  suggestions: FieldRecommendation[];
  count: number;
}

/**
 * Cache statistics
 */
export interface CacheStats {
  cache_size: number;
  cache_maxsize: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate: number;
}
