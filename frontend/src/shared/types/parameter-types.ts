/**
 * Parameter Types - 统一参数类型定义
 * Unified Parameter Type Definitions
 *
 * ⚠️ IMPORTANT: This is the ONLY place where the Parameter interface should be defined
 * All other files should import from here
 */

/**
 * Parameter data type enum
 */
export type ParameterType = 'string' | 'int' | 'float' | 'boolean' | 'json';

/**
 * EventParam - Legacy alias for Parameter (for backward compatibility)
 * @deprecated Use Parameter instead
 */
export type EventParam = Parameter;

/**
 * Parameter - 参数实体
 * Unified Parameter interface used across the entire application
 */
export interface Parameter {
  /** Database ID */
  id: number;

  /** Parameter unique code/name */
  paramName: string;
  param_name?: string; // Deprecated: use paramName

  /** Parameter Chinese name */
  paramNameCn: string;
  param_name_cn?: string; // Deprecated: use paramNameCn

  /** Parameter data type */
  paramType: ParameterType;
  param_type?: string; // Deprecated: use paramType

  /** Game business GID (null means public parameter) */
  gameGid: number | null;
  game_gid?: number | null; // Deprecated: use gameGid

  /** Parameter description */
  description?: string;
  param_description?: string; // Deprecated: use description

  /** Default value */
  defaultValue?: unknown;
  default_value?: unknown; // Deprecated: use defaultValue

  /** Template ID reference */
  templateId?: number;
  template_id?: number; // Deprecated: use templateId

  /** Is parameter active */
  isActive?: boolean;
  is_active?: boolean; // Deprecated: use isActive

  /** Version number */
  version?: number;

  /** Creation timestamp */
  createdAt?: string;
  created_at?: string; // Deprecated: use createdAt

  /** Update timestamp */
  updatedAt?: string;
  updated_at?: string; // Deprecated: use updatedAt

  /** Parameter type (derived from paramType for UI compatibility) */
  type?: ParameterType;

  /** Event count (number of events using this parameter) */
  eventCount?: number;
}

/**
 * Parameter creation request
 */
export interface ParameterCreateRequest {
  paramName: string;
  paramNameCn: string;
  paramType: ParameterType;
  gameGid: number | null;
  description?: string;
  defaultValue?: unknown;
}

/**
 * Parameter update request
 */
export interface ParameterUpdateRequest {
  id: number;
  paramName?: string;
  paramNameCn?: string;
  paramType?: ParameterType;
  description?: string;
  defaultValue?: unknown;
  isActive?: boolean;
}

/**
 * Parameter usage in events
 */
export interface ParameterUsage {
  eventId: number;
  event_id?: number; // Deprecated: use eventId
  eventName: string;
  event_name?: string; // Deprecated: use eventName
  eventDisplayName: string;
  event_display_name?: string; // Deprecated: use eventDisplayName
  usageCount: number;
  usage_count?: number; // Deprecated: use usageCount
}

/**
 * Parameter details with usage information
 */
export interface ParameterDetails {
  parameter: Parameter;
  usageInEvents: ParameterUsage[];
  usage_in_events?: ParameterUsage[]; // Deprecated: use usageInEvents
  isPublic: boolean;
  is_public?: boolean; // Deprecated: use isPublic
  totalUsage: number;
  total_usage?: number; // Deprecated: use totalUsage
}

/**
 * Parameter list query options
 */
export interface ParameterListOptions {
  gameGid?: number;
  page?: number;
  limit?: number;
  search?: string;
  type?: ParameterType;
}

/**
 * Parameter list response
 */
export interface ParameterListResponse {
  success: boolean;
  data: {
    parameters: Parameter[];
    hasMore?: boolean;
    page?: number;
  };
  total?: number;
  page?: number;
  pageSize?: number;
}

/**
 * Parameter details response
 */
export interface ParameterDetailsResponse {
  success: boolean;
  data: ParameterDetails;
}
