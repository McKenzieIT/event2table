/**
 * API Error Handler Utility
 *
 * Provides standardized error handling for API calls with user-friendly
 * Chinese error messages and toast notification support.
 *
 * Features:
 * - Automatic error message translation
 * - Toast notification integration
 * - Loading state management
 * - Network error detection
 * - Validation error formatting
 */

import { FetchError } from './types';

// Re-export FetchError for convenience
export { FetchError };

// ==================== Error Message Mappings ====================

/**
 * Maps HTTP status codes to user-friendly Chinese messages
 */
const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误，请检查输入内容',
  401: '未授权访问，请先登录',
  403: '无权限执行此操作',
  404: '请求的资源不存在',
  409: '数据冲突，该记录可能已存在',
  500: '服务器内部错误，请稍后重试',
  502: '网关错误，请稍后重试',
  503: '服务暂时不可用，请稍后重试',
  504: '请求超时，请稍后重试',
};

/**
 * Maps common error codes/keys to detailed messages
 */
const SPECIFIC_ERROR_MESSAGES: Record<string, string> = {
  // Game errors
  'duplicate_game_gid': '游戏GID已存在，请使用其他GID',
  'game_not_found': '游戏不存在，请检查GID是否正确',
  'invalid_game_gid': '游戏GID格式不正确，必须为正整数（例如：10000147）',
  'game_has_events': '无法删除游戏：该游戏下仍有事件，请先删除所有事件',

  // Event errors
  'duplicate_event_name': '事件名称已存在，请使用其他名称',
  'event_not_found': '事件不存在',
  'invalid_event_name': '事件名称格式不正确，只能包含字母、数字和下划线',
  'event_has_parameters': '无法删除事件：该事件下仍有参数，请先删除所有参数',

  // Parameter errors
  'duplicate_param_name': '参数名称已存在，请使用其他名称',
  'param_not_found': '参数不存在',
  'invalid_param_name': '参数名称格式不正确，只能包含字母、数字和下划线',

  // HQL errors
  'hql_generation_failed': 'HQL生成失败，请检查字段配置',
  'invalid_hql_mode': '无效的HQL模式',

  // Validation errors
  'required_field': '必填字段不能为空',
  'invalid_format': '格式不正确',
  'invalid_json': 'JSON格式不正确',

  // Network errors
  'network_error': '网络连接失败，请检查网络连接',
  'timeout': '请求超时，请稍后重试',
  'abort': '请求被取消',
};

// ==================== Error Types ====================

export enum ErrorType {
  VALIDATION = 'validation_error',
  NOT_FOUND = 'not_found',
  CONFLICT = 'conflict',
  NETWORK = 'network_error',
  SERVER = 'server_error',
  UNKNOWN = 'unknown_error',
}

// ==================== Error Parsing ====================

/**
 * Extract error message from API response
 */
export function parseErrorMessage(error: unknown): string {
  // Network errors (no response)
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return SPECIFIC_ERROR_MESSAGES.network_error;
  }

  // AbortError (request cancelled)
  if (error instanceof DOMException && error.name === 'AbortError') {
    return SPECIFIC_ERROR_MESSAGES.abort;
  }

  // FetchError with response
  if (error instanceof FetchError) {
    // Try to parse error response body
    if (error.data?.error) {
      return error.data.error;
    }

    if (error.data?.message) {
      return error.data.message;
    }

    // Fallback to status code message
    if (error.status && HTTP_ERROR_MESSAGES[error.status]) {
      return HTTP_ERROR_MESSAGES[error.status];
    }
  }

  // Generic Error
  if (error instanceof Error) {
    return error.message;
  }

  // Unknown error
  return SPECIFIC_ERROR_MESSAGES.network_error;
}

/**
 * Extract error type from error object
 */
export function parseErrorType(error: unknown): ErrorType {
  if (error instanceof FetchError) {
    const status = error.status;

    if (status === 400 || status === 422) {
      return ErrorType.VALIDATION;
    }
    if (status === 404) {
      return ErrorType.NOT_FOUND;
    }
    if (status === 409) {
      return ErrorType.CONFLICT;
    }
    if (status >= 500) {
      return ErrorType.SERVER;
    }
  }

  if (error instanceof TypeError) {
    return ErrorType.NETWORK;
  }

  return ErrorType.UNKNOWN;
}

/**
 * Extract field-specific validation errors
 */
export function parseValidationErrors(error: unknown): Record<string, string> | null {
  if (error instanceof FetchError && error.data?.details) {
    return error.data.details as Record<string, string>;
  }

  // Try to parse error message for field errors
  const message = parseErrorMessage(error);

  // Pattern: "fieldName validation failed: reason"
  const fieldErrorMatch = message.match(/^(\w+)\s+验证失败\s*:\s*(.+)$/);
  if (fieldErrorMatch) {
    return {
      [fieldErrorMatch[1]]: fieldErrorMatch[2],
    };
  }

  return null;
}

// ==================== Error Display Helpers ====================

/**
 * Format error message for toast notification
 * Adds context-specific prefixes
 */
export function formatToastError(
  error: unknown,
  context?: string
): string {
  const message = parseErrorMessage(error);

  if (context) {
    return `${context}失败：${message}`;
  }

  return message;
}

/**
 * Get detailed error info for debugging
 * (Only use in development or error logging)
 */
export function getErrorDetails(error: unknown): {
  message: string;
  type: ErrorType;
  status?: number;
  details?: Record<string, string>;
} {
  return {
    message: parseErrorMessage(error),
    type: parseErrorType(error),
    status: error instanceof FetchError ? error.status : undefined,
    details: parseValidationErrors(error) ?? undefined,
  };
}

// ==================== API Error Handler ====================

export interface ErrorHandlerOptions {
  /** Operation context (e.g., "创建游戏", "更新事件") */
  context?: string;
  /** Whether to show error in toast notification */
  showToast?: boolean;
  /** Custom error message override */
  customMessage?: string;
  /** Callback for handling specific error types */
  onError?: (error: unknown, details: ReturnType<typeof getErrorDetails>) => void;
}

/**
 * Handle API errors with toast notifications
 *
 * @example
 * ```tsx
 * try {
 *   const response = await fetch('/api/games', { method: 'POST', body: ... });
 *   if (!response.ok) throw await FetchError.fromResponse(response);
 *   return await response.json();
 * } catch (error) {
 *   handleApiError(error, { context: '创建游戏' });
 *   throw error; // Re-throw if needed
 * }
 * ```
 */
export function handleApiError(
  error: unknown,
  options: ErrorHandlerOptions = {}
): void {
  const { context, showToast = true, customMessage, onError } = options;

  // Get error details
  const details = getErrorDetails(error);

  // Call custom error handler if provided
  if (onError) {
    onError(error, details);
  }

  // Show toast notification (if enabled and toast hook is available)
  if (showToast) {
    const message = customMessage || formatToastError(error, context);
    // Note: This will be called from components with useToast hook
    // We'll store the message to be displayed by the component
    console.error('[API Error]', message, details);
  }

  // Log error details in development
  if (import.meta.env.DEV) {
    console.group('🔴 API Error Details');
    console.error('Message:', details.message);
    console.error('Type:', details.type);
    console.error('Status:', details.status);
    console.error('Validation Errors:', details.details);
    console.error('Original Error:', error);
    console.groupEnd();
  }
}

// ==================== React Hook Integration ====================

/**
 * Hook-like function to handle API errors with toast notifications
 * Call this from components that have access to useToast hook
 *
 * @example
 * ```tsx
 * const { error: showError } = useToast();
 *
 * try {
 *   await createGame(data);
 * } catch (err) {
 *   handleErrorWithToast(err, showError, { context: '创建游戏' });
 * }
 * ```
 */
export function handleErrorWithToast(
  error: unknown,
  showError: (message: string, duration?: number) => void,
  options: ErrorHandlerOptions = {}
): void {
  const message = options.customMessage || formatToastError(error, options.context);

  // Log error
  handleApiError(error, { ...options, showToast: false });

  // Show toast
  showError(message, 5000); // Errors stay longer (5s)

  // Handle field-specific errors
  const validationErrors = parseValidationErrors(error);
  if (validationErrors) {
    // Could show multiple toasts or pass to form state
    Object.entries(validationErrors).forEach(([field, msg]) => {
      console.warn(`[Validation Error] ${field}: ${msg}`);
    });
  }
}

// ==================== Loading State Management ====================

/**
 * Wraps an async API call with loading state management
 *
 * @example
 * ```tsx
 * const [loading, setLoading] = useState(false);
 * const { success, error } = useToast();
 *
 * const handleCreate = async (data) => {
 *   const result = await withLoading(
 *     () => createGame(data),
 *     setLoading,
 *     { onSuccess: () => success('创建成功'), onError: (err) => handleErrorWithToast(err, error, { context: '创建游戏' }) }
 *   );
 *   return result;
 * };
 * ```
 */
export async function withLoading<T>(
  asyncFn: () => Promise<T>,
  setLoading: (loading: boolean) => void,
  options: {
    onSuccess?: (data: T) => void;
    onError?: (error: unknown) => void;
    finally?: () => void;
  } = {}
): Promise<T> {
  setLoading(true);
  try {
    const result = await asyncFn();
    options.onSuccess?.(result);
    return result;
  } catch (error) {
    options.onError?.(error);
    throw error;
  } finally {
    setLoading(false);
    options.finally?.();
  }
}

// ==================== Fetch Error Class ====================

/**
 * Custom FetchError class for better error handling
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /**
   * Create ApiError from fetch Response
   */
  static async fromResponse(response: Response): Promise<ApiError> {
    let data: unknown = null;

    try {
      data = await response.json();
    } catch {
      // Response body is not JSON
    }

    const message = data?.error || data?.message || HTTP_ERROR_MESSAGES[response.status] || 'Unknown error';

    return new ApiError(message, response.status, data);
  }

  /**
   * Check if error is of specific type
   */
  isType(errorType: ErrorType): boolean {
    return parseErrorType(this) === errorType;
  }
}

