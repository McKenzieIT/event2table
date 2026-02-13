/**
 * Canvas Module Types
 *
 * Type definitions for canvas-related data structures
 */

/**
 * Flow node structure
 */
export interface FlowNode {
  id: string;
  type: string;
  x: number;
  y: number;
  data: Record<string, unknown>;
}

/**
 * Flow edge structure
 */
export interface FlowEdge {
  id: string;
  source: string;
  target: string;
}

/**
 * Complete flow data structure
 */
export interface FlowData {
  nodes: FlowNode[];
  edges: FlowEdge[];
}

/**
 * Saved flow structure
 */
export interface SavedFlow {
  id: number;
  game_id: number;
  name: string;
  flow_data: FlowData;
  created_at: string;
  updated_at: string;
}

/**
 * Event configuration structure
 */
export interface EventConfig {
  id: number;
  game_gid: number;
  event_id: number;
  name: string;
  name_cn?: string;
  fields: Field[];
  config_json?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Field structure within event config
 */
export interface Field {
  field_name: string;
  field_type: string;
  alias?: string;
  json_path?: string;
  custom_expression?: string;
  fixed_value?: unknown;
  aggregate_func?: string;
}

/**
 * HQL execution result
 */
export interface ExecutionResult {
  success: boolean;
  hql: string;
  metadata?: Record<string, unknown>;
  error?: string;
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  healthy: boolean;
  version: string;
  timestamp: string;
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

/**
 * Query options for fetching event configs
 */
export interface EventConfigQueryOptions {
  gameGid: number;
  configId?: number;
}

/**
 * Save flow options
 */
export interface SaveFlowOptions {
  gameId: number;
  flowData: FlowData;
}
