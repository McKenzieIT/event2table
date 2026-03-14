/**
 * Parameters Module Types
 *
 * Type definitions for parameter-related data structures
 *
 * ⚠️ IMPORTANT: Parameter interface is now imported from @/shared/types/parameter-types
 * Do not define Parameter interface here - use the unified definition
 */

// Import Parameter type from shared types
import type { Parameter, ParameterType } from '@/shared/types/parameter-types';

// Re-export for convenience
export type { Parameter, ParameterType } from '@/shared/types/parameter-types';

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
