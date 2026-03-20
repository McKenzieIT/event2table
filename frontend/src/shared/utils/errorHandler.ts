/**
 * Unified Error Handler Utility
 *
 * 统一错误处理工具，提供错误分类、消息格式化和错误上报功能
 *
 * 功能：
 * 1. 错误分类（网络错误、API错误、业务错误）
 * 2. 错误消息格式化
 * 3. 错误上报（可选）
 *
 * 创建日期: 2026-03-20
 */

// ============================================================================
// 错误类型定义
// ============================================================================

/**
 * 错误类型枚举
 */
export enum ErrorType {
  /** 网络错误 */
  NETWORK = 'network_error',
  /** API错误 */
  API = 'api_error',
  /** 业务错误 */
  BUSINESS = 'business_error',
  /** 验证错误 */
  VALIDATION = 'validation_error',
  /** 未知错误 */
  UNKNOWN = 'unknown_error',
}

/**
 * 错误级别枚举
 */
export enum ErrorLevel {
  /** 信息 */
  INFO = 'info',
  /** 警告 */
  WARNING = 'warning',
  /** 错误 */
  ERROR = 'error',
  /** 致命错误 */
  FATAL = 'fatal',
}

/**
 * 统一错误接口
 */
export interface AppError {
  /** 错误类型 */
  type: ErrorType;
  /** 错误级别 */
  level: ErrorLevel;
  /** 错误消息 */
  message: string;
  /** 原始错误对象 */
  originalError?: unknown;
  /** 错误代码 */
  code?: string;
  /** 错误详情 */
  details?: Record<string, unknown>;
  /** 时间戳 */
  timestamp: number;
}

/**
 * 错误上报配置
 */
export interface ErrorReportConfig {
  /** 是否启用错误上报 */
  enabled: boolean;
  /** 上报URL */
  reportUrl?: string;
  /** 上报前回调 */
  beforeSend?: (error: AppError) => AppError | null;
  /** 上报后回调 */
  afterSend?: (error: AppError, success: boolean) => void;
}

// ============================================================================
// 错误分类
// ============================================================================

/**
 * 判断是否为网络错误
 */
function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    // 检查常见的网络错误消息
    const networkErrorMessages = [
      'Failed to fetch',
      'NetworkError',
      'Network request failed',
      'fetch failed',
    ];
    return networkErrorMessages.some(msg => error.message.includes(msg));
  }
  
  // 检查是否为AbortError
  if (error instanceof DOMException && error.name === 'AbortError') {
    return true;
  }
  
  return false;
}

/**
 * 判断是否为API错误
 */
function isApiError(error: unknown): boolean {
  // 检查是否有status属性（HTTP响应错误）
  if (error && typeof error === 'object') {
    return 'status' in error || 'statusCode' in error;
  }
  
  return false;
}

/**
 * 判断是否为业务错误
 */
function isBusinessError(error: unknown): boolean {
  // 检查是否有业务错误标识
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    return (
      'code' in err ||
      'errorCode' in err ||
      (typeof err.message === 'string' && 
       (err.message.includes('业务') || err.message.includes('验证')))
    );
  }
  
  return false;
}

/**
 * 分类错误
 */
export function classifyError(error: unknown): ErrorType {
  if (isNetworkError(error)) {
    return ErrorType.NETWORK;
  }
  
  if (isApiError(error)) {
    return ErrorType.API;
  }
  
  if (isBusinessError(error)) {
    return ErrorType.BUSINESS;
  }
  
  return ErrorType.UNKNOWN;
}

/**
 * 确定错误级别
 */
export function determineErrorLevel(error: unknown, errorType: ErrorType): ErrorLevel {
  // 网络错误通常是警告级别
  if (errorType === ErrorType.NETWORK) {
    return ErrorLevel.WARNING;
  }
  
  // API错误根据状态码确定级别
  if (errorType === ErrorType.API && error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    const status = err.status || err.statusCode;
    
    if (typeof status === 'number') {
      if (status >= 500) {
        return ErrorLevel.FATAL;
      }
      if (status >= 400) {
        return ErrorLevel.ERROR;
      }
    }
  }
  
  // 默认为错误级别
  return ErrorLevel.ERROR;
}

// ============================================================================
// 错误消息格式化
// ============================================================================

/**
 * HTTP状态码错误消息映射
 */
const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '未授权，请先登录',
  403: '无权限访问',
  404: '请求的资源不存在',
  409: '数据冲突',
  422: '验证失败',
  429: '请求过于频繁',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '请求超时',
};

/**
 * 业务错误代码消息映射
 */
const BUSINESS_ERROR_MESSAGES: Record<string, string> = {
  'duplicate_game_gid': '游戏GID已存在',
  'game_not_found': '游戏不存在',
  'invalid_game_gid': '游戏GID格式不正确',
  'duplicate_event_name': '事件名称已存在',
  'event_not_found': '事件不存在',
  'invalid_event_name': '事件名称格式不正确',
  'required_field': '必填字段不能为空',
  'invalid_format': '格式不正确',
};

/**
 * 提取错误消息
 */
function extractErrorMessage(error: unknown): string {
  // 从Error对象中提取
  if (error instanceof Error) {
    return error.message;
  }
  
  // 从对象中提取
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    
    // 优先使用message字段
    if (typeof err.message === 'string') {
      return err.message;
    }
    
    // 使用error字段
    if (typeof err.error === 'string') {
      return err.error;
    }
    
    // 尝试从错误代码映射
    if (typeof err.code === 'string' && BUSINESS_ERROR_MESSAGES[err.code]) {
      return BUSINESS_ERROR_MESSAGES[err.code];
    }
    
    // 尝试从HTTP状态码映射
    const status = err.status || err.statusCode;
    if (typeof status === 'number' && HTTP_ERROR_MESSAGES[status]) {
      return HTTP_ERROR_MESSAGES[status];
    }
  }
  
  // 字符串错误
  if (typeof error === 'string') {
    return error;
  }
  
  return '发生未知错误';
}

/**
 * 格式化错误消息
 */
export function formatErrorMessage(
  error: unknown,
  context?: string
): string {
  const message = extractErrorMessage(error);
  
  if (context) {
    return `${context}：${message}`;
  }
  
  return message;
}

/**
 * 创建统一错误对象
 */
export function createAppError(
  error: unknown,
  context?: string
): AppError {
  const errorType = classifyError(error);
  const errorLevel = determineErrorLevel(error, errorType);
  const message = formatErrorMessage(error, context);
  
  // 提取错误代码
  let code: string | undefined;
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    code = (err.code || err.errorCode) as string | undefined;
  }
  
  // 提取错误详情
  let details: Record<string, unknown> | undefined;
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    if (err.details && typeof err.details === 'object') {
      details = err.details as Record<string, unknown>;
    }
  }
  
  return {
    type: errorType,
    level: errorLevel,
    message,
    originalError: error,
    code,
    details,
    timestamp: Date.now(),
  };
}

// ============================================================================
// 错误上报
// ============================================================================

/**
 * 默认错误上报配置
 */
const defaultReportConfig: ErrorReportConfig = {
  enabled: false,
};

let reportConfig: ErrorReportConfig = { ...defaultReportConfig };

/**
 * 配置错误上报
 */
export function configureErrorReporting(config: Partial<ErrorReportConfig>): void {
  reportConfig = { ...defaultReportConfig, ...config };
}

/**
 * 上报错误
 */
async function reportError(error: AppError): Promise<boolean> {
  if (!reportConfig.enabled) {
    return false;
  }
  
  // 调用beforeSend回调
  let errorToReport = error;
  if (reportConfig.beforeSend) {
    const result = reportConfig.beforeSend(error);
    if (result === null) {
      return false; // 取消上报
    }
    errorToReport = result;
  }
  
  try {
    if (reportConfig.reportUrl) {
      await fetch(reportConfig.reportUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorToReport),
      });
    }
    
    // 调用afterSend回调
    if (reportConfig.afterSend) {
      reportConfig.afterSend(errorToReport, true);
    }
    
    return true;
  } catch (e) {
    console.error('Failed to report error:', e);
    
    if (reportConfig.afterSend) {
      reportConfig.afterSend(errorToReport, false);
    }
    
    return false;
  }
}

// ============================================================================
// 错误处理主函数
// ============================================================================

/**
 * 处理错误
 */
export async function handleError(
  error: unknown,
  options: {
    /** 错误上下文 */
    context?: string;
    /** 是否上报错误 */
    report?: boolean;
    /** 自定义处理函数 */
    handler?: (appError: AppError) => void;
  } = {}
): Promise<AppError> {
  const { context, report = true, handler } = options;
  
  // 创建统一错误对象
  const appError = createAppError(error, context);
  
  // 记录错误到控制台
  console.group(`[${appError.level.toUpperCase()}] ${appError.type}`);
  console.error('Message:', appError.message);
  console.error('Timestamp:', new Date(appError.timestamp).toISOString());
  if (appError.code) {
    console.error('Code:', appError.code);
  }
  if (appError.details) {
    console.error('Details:', appError.details);
  }
  console.error('Original Error:', appError.originalError);
  console.groupEnd();
  
  // 上报错误
  if (report) {
    await reportError(appError);
  }
  
  // 调用自定义处理函数
  if (handler) {
    handler(appError);
  }
  
  return appError;
}

/**
 * 处理网络错误
 */
export async function handleNetworkError(
  error: unknown,
  context?: string
): Promise<AppError> {
  return handleError(error, {
    context: context || '网络请求',
    report: true,
  });
}

/**
 * 处理API错误
 */
export async function handleApiError(
  error: unknown,
  context?: string
): Promise<AppError> {
  return handleError(error, {
    context: context || 'API调用',
    report: true,
  });
}

/**
 * 处理业务错误
 */
export async function handleBusinessError(
  error: unknown,
  context?: string
): Promise<AppError> {
  return handleError(error, {
    context: context || '业务操作',
    report: true,
  });
}

// ============================================================================
// 辅助函数
// ============================================================================

/**
 * 判断是否应该重试
 */
export function shouldRetry(error: AppError): boolean {
  // 网络错误可以重试
  if (error.type === ErrorType.NETWORK) {
    return true;
  }
  
  // 5xx错误可以重试
  if (error.type === ErrorType.API) {
    const status = (error.originalError as Record<string, unknown>)?.status;
    if (typeof status === 'number' && status >= 500) {
      return true;
    }
  }
  
  return false;
}

/**
 * 获取用户友好的错误提示
 */
export function getUserFriendlyMessage(error: AppError): string {
  switch (error.type) {
    case ErrorType.NETWORK:
      return '网络连接失败，请检查网络设置后重试';
    case ErrorType.API:
      if (error.level === ErrorLevel.FATAL) {
        return '服务暂时不可用，请稍后重试';
      }
      return error.message;
    case ErrorType.BUSINESS:
      return error.message;
    default:
      return '操作失败，请稍后重试';
  }
}

// ============================================================================
// 导出
// ============================================================================

export default {
  classifyError,
  determineErrorLevel,
  formatErrorMessage,
  createAppError,
  handleError,
  handleNetworkError,
  handleApiError,
  handleBusinessError,
  configureErrorReporting,
  shouldRetry,
  getUserFriendlyMessage,
  ErrorType,
  ErrorLevel,
};
