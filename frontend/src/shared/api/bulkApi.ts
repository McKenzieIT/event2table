/**
 * Bulk Operations API Client
 * 批量操作API客户端
 *
 * @module bulkApi
 */

// ============================================
// Type Definitions
// ============================================

export interface BulkDeleteEventsRequest {
  event_ids: number[];
}

export interface BulkDeleteEventsResponse {
  success: boolean;
  message: string;
  data?: {
    deleted_count: number;
    event_ids: number[];
  };
}

export interface BulkUpdateCategoryRequest {
  event_ids: number[];
  category_id: number;
}

export interface BulkUpdateCategoryResponse {
  success: boolean;
  message: string;
  data?: {
    updated_count: number;
    category_id: number;
    event_ids: number[];
  };
}

export interface BulkToggleCommonParamsRequest {
  event_ids: number[];
  include: 0 | 1;
}

export interface BulkToggleCommonParamsResponse {
  success: boolean;
  message: string;
  data?: {
    updated_count: number;
    include: number;
    event_ids: number[];
  };
}

export interface BulkExportEventsRequest {
  event_ids: number[];
  format?: 'json';
}

export interface EventParameter {
  param_name: string;
  param_name_cn: string;
  template_id: number;
  param_type: string;
  description: string;
  is_active: number;
}

export interface BulkExportedEvent {
  id: number;
  game_gid: number;
  event_name: string;
  event_name_cn: string;
  category_id: number;
  category_name: string;
  source_table: string;
  target_table: string;
  include_in_common_params: number;
  parameters: EventParameter[];
}

export interface BulkExportEventsResponse {
  success: boolean;
  message: string;
  data?: {
    events: BulkExportedEvent[];
    count: number;
    format: string;
  };
}

export interface BulkValidateParametersRequest {
  event_ids: number[];
}

export interface ValidationResult {
  event_id: number;
  event_name: string;
  event_name_cn: string;
  is_valid: boolean;
  param_count: number;
  errors: string[];
  warnings: string[];
}

export interface BulkValidateParametersResponse {
  success: boolean;
  message: string;
  data?: {
    results: ValidationResult[];
    total_events: number;
    valid_events: number;
    invalid_events: number;
  };
}

// ============================================
// API Functions
// ============================================

/**
 * 批量删除事件
 *
 * @param data - 请求数据
 * @returns 删除结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await bulkDeleteEvents({ event_ids: [1, 2, 3] });
 * console.log(`Deleted ${response.data.deleted_count} events`);
 */
export const bulkDeleteEvents = async (
  data: BulkDeleteEventsRequest
): Promise<BulkDeleteEventsResponse> => {
  try {
    const response = await fetch('/bulk-delete-events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to bulk delete events: ${response.statusText}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Bulk delete events request failed');
    }

    return result;
  } catch (error) {
    console.error('[bulkApi] Failed to bulk delete events:', error);
    throw error;
  }
};

/**
 * 批量更新事件分类
 *
 * @param data - 请求数据
 * @returns 更新结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await bulkUpdateCategory({
 *   event_ids: [1, 2, 3],
 *   category_id: 5
 * });
 */
export const bulkUpdateCategory = async (
  data: BulkUpdateCategoryRequest
): Promise<BulkUpdateCategoryResponse> => {
  try {
    const response = await fetch('/bulk-update-category', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to bulk update category: ${response.statusText}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Bulk update category request failed');
    }

    return result;
  } catch (error) {
    console.error('[bulkApi] Failed to bulk update category:', error);
    throw error;
  }
};

/**
 * 批量切换通用参数包含状态
 *
 * @param data - 请求数据
 * @returns 更新结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await bulkToggleCommonParams({
 *   event_ids: [1, 2, 3],
 *   include: 1
 * });
 */
export const bulkToggleCommonParams = async (
  data: BulkToggleCommonParamsRequest
): Promise<BulkToggleCommonParamsResponse> => {
  try {
    const response = await fetch('/bulk-toggle-common-params', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to bulk toggle common params: ${response.statusText}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Bulk toggle common params request failed');
    }

    return result;
  } catch (error) {
    console.error('[bulkApi] Failed to bulk toggle common params:', error);
    throw error;
  }
};

/**
 * 批量导出事件配置
 *
 * @param data - 请求数据
 * @returns 导出结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await bulkExportEvents({
 *   event_ids: [1, 2, 3],
 *   format: 'json'
 * });
 * console.log(`Exported ${response.data.count} events`);
 */
export const bulkExportEvents = async (
  data: BulkExportEventsRequest
): Promise<BulkExportEventsResponse> => {
  try {
    const response = await fetch('/bulk-export-events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to bulk export events: ${response.statusText}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Bulk export events request failed');
    }

    return result;
  } catch (error) {
    console.error('[bulkApi] Failed to bulk export events:', error);
    throw error;
  }
};

/**
 * 批量验证事件参数
 *
 * @param data - 请求数据
 * @returns 验证结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await bulkValidateParameters({ event_ids: [1, 2, 3] });
 * console.log(`Valid: ${response.data.valid_events}, Invalid: ${response.data.invalid_events}`);
 */
export const bulkValidateParameters = async (
  data: BulkValidateParametersRequest
): Promise<BulkValidateParametersResponse> => {
  try {
    const response = await fetch('/bulk-validate-parameters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to bulk validate parameters: ${response.statusText}`);
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.message || 'Bulk validate parameters request failed');
    }

    return result;
  } catch (error) {
    console.error('[bulkApi] Failed to bulk validate parameters:', error);
    throw error;
  }
};

// ============================================
// Export Types
// ============================================

export type {
  BulkDeleteEventsRequest,
  BulkDeleteEventsResponse,
  BulkUpdateCategoryRequest,
  BulkUpdateCategoryResponse,
  BulkToggleCommonParamsRequest,
  BulkToggleCommonParamsResponse,
  BulkExportEventsRequest,
  BulkExportEventsResponse,
  BulkValidateParametersRequest,
  BulkValidateParametersResponse,
  EventParameter,
  BulkExportedEvent,
  ValidationResult,
};
