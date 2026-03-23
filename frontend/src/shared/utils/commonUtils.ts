/**
 * Common Utilities - 消除前端代码重复的共享工具函数
 *
 * 此模块提供跨多个组件共享的工具函数,
 * 目标是消除重复代码,提高代码可维护性。
 *
 * 创建日期: 2026-03-16
 * 作者: Claude Code (Subagent 1: 代码重复消除专家)
 *
 * 主要功能:
 * 1. 表单验证
 * 2. 日期时间格式化
 * 3. 字符串处理
 * 4. API响应处理
 * 5. Modal状态管理
 * 6. 通用React Hooks辅助函数
 */

// ============================================================================
// 表单验证工具
// ============================================================================

/**
 * 验证必填字段
 */
export const validateRequired = (value: any, fieldName: string): string | null => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return `${fieldName}不能为空`;
  }
  return null;
};

/**
 * 验证事件名称(英文) - 只允许小写字母和下划线
 */
export const validateEventName = (eventName: string): string | null => {
  if (!eventName) {
    return '事件名称（英文）不能为空';
  }
  if (!/^[a-z_]+$/.test(eventName)) {
    return '事件名称只能包含小写字母和下划线';
  }
  return null;
};

/**
 * 验证游戏GID格式
 */
export const validateGameGid = (gid: string | number): string | null => {
  const gidStr = String(gid).trim();
  if (!gidStr) {
    return '游戏GID不能为空';
  }
  const gidNum = parseInt(gidStr, 10);
  if (isNaN(gidNum) || gidNum <= 0) {
    return '游戏GID必须是正整数';
  }
  return null;
};

/**
 * 验证URL格式
 */
export const validateUrl = (url: string): string | null => {
  if (!url) {
    return null; // URL不是必填的
  }
  try {
    new URL(url);
    return null;
  } catch {
    return '请输入有效的URL';
  }
};

/**
 * 批量验证表单字段
 */
export const validateForm = <T extends Record<string, any>>(
  data: T,
  validators: Partial<Record<keyof T, (value: any) => string | null>>
): Record<string, string> => {
  const errors: Record<string, string> = {};

  for (const [field, validator] of Object.entries(validators)) {
    const error = validator(data[field]);
    if (error) {
      errors[field] = error;
    }
  }

  return errors;
};

// ============================================================================
// 日期时间格式化工具
// ============================================================================

/**
 * 格式化日期为 YYYY-MM-DD
 */
export const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * 格式化日期时间为 YYYY-MM-DD HH:mm:ss
 */
export const formatDateTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const datePart = formatDate(d);
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  return `${datePart} ${hours}:${minutes}:${seconds}`;
};

/**
 * 解析日期字符串
 */
export const parseDate = (dateStr: string): Date | null => {
  try {
    const date = new Date(dateStr);
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return null;
    }
    return date;
  } catch {
    return null;
  }
};

/**
 * 获取相对时间描述(如: "2小时前")
 */
export const getRelativeTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 30) return `${diffDays}天前`;
  return formatDate(d);
};

// ============================================================================
// 字符串处理工具
// ============================================================================

/**
 * 清理字符串(去除首尾空白,返回null如果为空)
 */
export const cleanString = (value: any): string | null => {
  if (value === null || value === undefined) {
    return null;
  }
  const str = String(value).trim();
  return str === '' ? null : str;
};

/**
 * 标准化标识符(转换为驼峰命名)
 */
export const toCamelCase = (str: string): string => {
  return str
    .replace(/[-_\s]+(.)?/g, (_, char) => (char ? char.toUpperCase() : ''))
    .replace(/^(.)/, (char) => char.toLowerCase());
};

/**
 * 标准化标识符(转换为下划线命名)
 */
export const toSnakeCase = (str: string): string => {
  return str
    .replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
    .replace(/^_/, '')
    .replace(/-+/g, '_');
};

/**
 * 截断文本并添加省略号
 */
export const truncate = (text: string, maxLength: number, suffix: string = '...'): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - suffix.length) + suffix;
};

/**
 * 高亮搜索关键词
 */
export const highlightKeyword = (text: string, keyword: string): string => {
  if (!keyword) return text;
  const regex = new RegExp(`(${keyword})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

// ============================================================================
// API响应处理工具
// ============================================================================

/**
 * 处理API错误的统一方法
 */
export const handleApiError = (error: any): string => {
  if (error?.message) {
    return error.message;
  }
  if (error?.errors?.[0]) {
    // Handle both string and object formats
    const firstError = error.errors[0];
    return typeof firstError === 'string' ? firstError : firstError.message || String(firstError);
  }
  if (typeof error === 'string') {
    return error;
  }
  return '操作失败,请稍后重试';
};

/**
 * 检查GraphQL响应是否成功
 */
export const isGraphQLSuccess = (response: any): boolean => {
  return response?.ok === true || response?.data?.ok === true;
};

/**
 * 从GraphQL响应中提取错误消息
 */
export const getGraphQLErrors = (response: any): string[] => {
  if (response?.errors) {
    return response.errors.map((e: any) => e.message || String(e));
  }
  if (response?.data?.errors) {
    return response.data.errors.map((e: any) => e.message || String(e));
  }
  return [];
};

// ============================================================================
// Modal状态管理工具
// ============================================================================

/**
 * 创建Modal状态的通用Hook参数
 */
export interface ModalState<T = any> {
  isOpen: boolean;
  data?: T;
  mode: 'create' | 'edit' | 'view';
}

/**
 * 创建初始Modal状态
 */
export const createInitialModalState = <T = any>(): ModalState<T> => ({
  isOpen: false,
  mode: 'create',
});

/**
 * 打开Modal(创建模式)
 */
export const openCreateModal = <T = any>(setState: (state: ModalState<T>) => void) => {
  setState({
    isOpen: true,
    mode: 'create',
  });
};

/**
 * 打开Modal(编辑模式)
 */
export const openEditModal = <T = any>(setState: (state: ModalState<T>) => void, data: T) => {
  setState({
    isOpen: true,
    data,
    mode: 'edit',
  });
};

/**
 * 打开Modal(查看模式)
 */
export const openViewModal = <T = any>(setState: (state: ModalState<T>) => void, data: T) => {
  setState({
    isOpen: true,
    data,
    mode: 'view',
  });
};

/**
 * 关闭Modal
 */
export const closeModal = <T = any>(setState: (state: ModalState<T>) => void) => {
  setState({
    isOpen: false,
    mode: 'create',
  });
};

// ============================================================================
// React Hooks辅助函数
// ============================================================================

/**
 * 创建表单状态管理Hook
 */
export const useFormState = <T extends Record<string, any>>(
  initialValues: T
): [
  T,
  (field: keyof T, value: any) => void,
  (values: Partial<T>) => void,
  () => void
] => {
  const [values, setValues] = React.useState<T>(initialValues);

  const handleChange = (field: keyof T, value: any) => {
    setValues((prev) => ({ ...prev, [field]: value }));
  };

  const setMultipleValues = (newValues: Partial<T>) => {
    setValues((prev) => ({ ...prev, ...newValues }));
  };

  const resetValues = () => {
    setValues(initialValues);
  };

  return [values, handleChange, setMultipleValues, resetValues];
};

/**
 * 创建加载状态管理Hook
 */
export const useLoadingState = (): [
  boolean,
  (loading: boolean) => void,
  () => Promise<void>,
  (asyncFn: () => Promise<any>) => Promise<any>
] => {
  const [loading, setLoading] = React.useState(false);

  const withLoading = async (asyncFn: () => Promise<any>): Promise<any> => {
    setLoading(true);
    try {
      return await asyncFn();
    } finally {
      setLoading(false);
    }
  };

  const executeAsync = async (asyncFn: () => Promise<any>): Promise<any> => {
    return withLoading(asyncFn);
  };

  return [loading, setLoading, executeAsync, withLoading];
};

// ============================================================================
// 分页工具
// ============================================================================

/**
 * 分页参数接口
 */
export interface PaginationParams {
  page: number;
  perPage: number;
  total?: number;
}

/**
 * 默认分页参数
 */
export const DEFAULT_PAGINATION: PaginationParams = {
  page: 1,
  perPage: 20,
};

/**
 * 计算分页信息
 */
export const calculatePagination = (total: number, page: number, perPage: number) => {
  const totalPages = Math.ceil(total / perPage);
  const hasNext = page < totalPages;
  const hasPrev = page > 1;
  const offset = (page - 1) * perPage;

  return {
    totalPages,
    hasNext,
    hasPrev,
    offset,
  };
};

/**
 * 构建分页查询参数
 */
export const buildPaginationParams = (page: number, perPage: number) => {
  return {
    page: Math.max(1, page),
    per_page: Math.min(100, Math.max(1, perPage)),
  };
};

// ============================================================================
// 类型守卫
// ============================================================================

/**
 * 检查值是否为空(null/undefined/空字符串/空数组)
 */
export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) {
    return true;
  }
  if (typeof value === 'string' && value.trim() === '') {
    return true;
  }
  if (Array.isArray(value) && value.length === 0) {
    return true;
  }
  if (typeof value === 'object' && Object.keys(value).length === 0) {
    return true;
  }
  return false;
};

/**
 * 安全地访问嵌套对象属性
 */
export const safeGet = <T = any>(obj: any, path: string, defaultValue?: T): T => {
  const keys = path.split('.');
  let result = obj;

  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue as T;
    }
    result = result[key];
  }

  return result !== undefined ? result : (defaultValue as T);
};

// ============================================================================
// 数组工具
// ============================================================================

/**
 * 数组去重
 */
export const unique = <T>(arr: T[], key?: keyof T): T[] => {
  if (!key) {
    return Array.from(new Set(arr));
  }

  const seen = new Set<any>();
  return arr.filter((item) => {
    const k = item[key];
    if (seen.has(k)) {
      return false;
    }
    seen.add(k);
    return true;
  });
};

/**
 * 数组分组
 */
export const groupBy = <T>(arr: T[], key: keyof T): Record<string, T[]> => {
  return arr.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

/**
 * 数组排序(支持嵌套属性)
 */
export const sortBy = <T>(arr: T[], key: keyof T | string, order: 'asc' | 'desc' = 'asc'): T[] => {
  return [...arr].sort((a, b) => {
    const aVal = safeGet(a, key as string, '');
    const bVal = safeGet(b, key as string, '');

    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
};

// ============================================================================
// 导出列表
// ============================================================================

export default {
  // 表单验证
  validateRequired,
  validateEventName,
  validateGameGid,
  validateUrl,
  validateForm,
  // 日期时间
  formatDate,
  formatDateTime,
  parseDate,
  getRelativeTime,
  // 字符串处理
  cleanString,
  toCamelCase,
  toSnakeCase,
  truncate,
  highlightKeyword,
  // API响应
  handleApiError,
  isGraphQLSuccess,
  getGraphQLErrors,
  // Modal状态
  createInitialModalState,
  openCreateModal,
  openEditModal,
  openViewModal,
  closeModal,
  // React Hooks
  useFormState,
  useLoadingState,
  // 分页
  DEFAULT_PAGINATION,
  calculatePagination,
  buildPaginationParams,
  // 类型守卫
  isEmpty,
  safeGet,
  // 数组工具
  unique,
  groupBy,
  sortBy,
};

// 需要导入React
import React from 'react';
