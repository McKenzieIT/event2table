/**
 * Parameters Module Types
 *
 * Type definitions for parameter-related data structures
 */

/**
 * Parameter type enum
 */
export type ParameterType = 'string' | 'int' | 'float' | 'boolean' | 'json';

/**
 * Parameter structure
 */
export interface Parameter {
  id: number;
  param_name: string;
  param_name_cn: string;
  param_type: ParameterType;
  game_gid: number | null; // null means public parameter
  description?: string;
  default_value?: unknown;
  created_at?: string;
  updated_at?: string;
}

/**
 * Parameter usage in events
 */
export interface ParameterUsage {
  event_id: number;
  event_name: string;
  event_display_name: string;
  usage_count: number;
}

/**
 * Parameter details with usage information
 */
export interface ParameterDetails {
  parameter: Parameter;
  usage_in_events: ParameterUsage[];
  is_public: boolean;
  total_usage: number;
}

/**
 * API response wrapper for parameters list
 */
export interface ParametersListResponse {
  success: boolean;
  data: {
    parameters: Parameter[];
    has_more?: boolean;
    page?: number;
  };
  message?: string;
  total?: number;
  page?: number;
  page_size?: number;
}

/**
 * API response wrapper for parameter details
 */
export interface ParameterDetailsResponse {
  success: boolean;
  data: ParameterDetails;
  message?: string;
}

/**
 * Query options for fetching parameters
 */
export interface FetchParametersOptions {
  page?: number;
  limit?: number;
  search?: string;
  type?: string;
}
