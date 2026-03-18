/**
 * Frontend Common Helper Utilities
 *
 * 此模块提供跨多个组件共享的工具函数,
 * 目标是消除重复代码,提高代码可维护性。
 *
 * 创建日期: 2026-03-17
 * 作者: Claude Code (Subagent 1: 代码重复消除专家)
 *
 * 主要功能:
 * 1. 日期时间处理
 * 2. 字符串清理和验证
 * 3. API调用封装
 * 4. 本地存储辅助函数
 * 5. 通用数据转换
 */

/**
 * 格式化日期为字符串
 *
 * @param date - 日期对象或日期字符串
 * @param format - 格式化字符串 (default: 'YYYY-MM-DD')
 * @returns 格式化后的日期字符串
 *
 * @example
 * formatDate(new Date(2026, 2, 17)) // '2026-03-17'
 * formatDate('2026-03-17') // '2026-03-17'
 */
export function formatDate(
  date: Date | string,
  format: string = 'YYYY-MM-DD'
): string {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return '';
  }

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day);
}

/**
 * 格式化日期时间为字符串
 *
 * @param date - 日期对象或日期字符串
 * @param includeTime - 是否包含时间 (default: true)
 * @returns 格式化后的日期时间字符串
 *
 * @example
 * formatDateTime(new Date(2026, 2, 17, 14, 30)) // '2026-03-17 14:30'
 */
export function formatDateTime(
  date: Date | string,
  includeTime: boolean = true
): string {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return '';
  }

  const datePart = formatDate(d);
  if (!includeTime) {
    return datePart;
  }

  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return `${datePart} ${hours}:${minutes}:${seconds}`;
}

/**
 * 解析日期字符串为Date对象
 *
 * @param dateStr - 日期字符串
 * @returns Date对象或null（解析失败）
 *
 * @example
 * parseDate('2026-03-17') // Date object
 * parseDate('invalid') // null
 */
export function parseDate(dateStr: string): Date | null {
  const date = new Date(dateStr);
  return isNaN(date.getTime()) ? null : date;
}

/**
 * 清理和验证用户输入
 *
 * @param input - 用户输入字符串
 * @returns 清理后的字符串
 *
 * @example
 * sanitizeInput('<script>alert("test")</script>') // '&lt;script&gt;...'
 * sanitizeInput('  hello  ') // 'hello'
 */
export function sanitizeInput(input: string): string {
  if (!input) {
    return '';
  }

  // 去除首尾空白
  let cleaned = input.trim();

  // HTML转义（防止XSS攻击）
  cleaned = cleaned
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');

  return cleaned;
}

/**
 * 验证字符串是否为空或仅包含空白
 *
 * @param str - 要验证的字符串
 * @returns 如果为空或仅空白返回true
 *
 * @example
 * isBlank('') // true
 * isBlank('  ') // true
 * isBlank('hello') // false
 */
export function isBlank(str: string | null | undefined): boolean {
  return !str || str.trim().length === 0;
}

/**
 * 标准化标识符（转换为下划线命名）
 *
 * @param identifier - 原始标识符
 * @returns 标准化后的标识符
 *
 * @example
 * normalizeIdentifier('EventName') // 'event_name'
 * normalizeIdentifier('event-name') // 'event_name'
 */
export function normalizeIdentifier(identifier: string): string {
  return identifier
    .toLowerCase()
    .replace(/[-\s]+/g, '_')
    .replace(/[^a-z0-9_]/g, '');
}

/**
 * 封装的API调用函数（带错误处理）
 *
 * @param endpoint - API端点路径
 * @param options - fetch选项
 * @returns Promise解析后的JSON响应
 * @throws Error当请求失败时
 *
 * @example
 * const data = await fetchAPI('/api/games')
 * const created = await fetchAPI('/api/games', {
 *   method: 'POST',
 *   body: JSON.stringify({ name: 'Test' })
 * })
 */
export async function fetchAPI<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(endpoint, { ...defaultOptions, ...options });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * 从本地存储获取数据（带类型安全）
 *
 * @param key - 存储键
 * @returns 存储的值或null
 *
 * @example
 * const token = getFromStorage<string>('auth_token')
 */
export function getFromStorage<T = any>(key: string): T | null {
  try {
    const item = localStorage.getItem(key);
    return item ? (JSON.parse(item) as T) : null;
  } catch (error) {
    console.error(`Failed to get from storage: ${key}`, error);
    return null;
  }
}

/**
 * 保存数据到本地存储
 *
 * @param key - 存储键
 * @param value - 要存储的值
 *
 * @example
 * saveToStorage('auth_token', 'abc123')
 * saveToStorage('user', { name: 'John' })
 */
export function saveToStorage<T = any>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Failed to save to storage: ${key}`, error);
  }
}

/**
 * 从本地存储删除数据
 *
 * @param key - 存储键
 *
 * @example
 * removeFromStorage('auth_token')
 */
export function removeFromStorage(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove from storage: ${key}`, error);
  }
}

/**
 * 深度克隆对象
 *
 * @param obj - 要克隆的对象
 * @returns 克隆后的新对象
 *
 * @example
 * const original = { a: 1, b: { c: 2 } };
 * const cloned = deepClone(original);
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }

  const cloned = {} as T;
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      (cloned as any)[key] = deepClone((obj as any)[key]);
    }
  }

  return cloned;
}

/**
 * 合并多个对象（浅合并）
 *
 * @param target - 目标对象
 * @param sources - 源对象
 * @returns 合并后的对象
 *
 * @example
 * const merged = mergeObjects({ a: 1 }, { b: 2 }); // { a: 1, b: 2 }
 */
export function mergeObjects<T extends Record<string, any>>(
  target: T,
  ...sources: Partial<T>[]
): T {
  const result = { ...target };

  for (const source of sources) {
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        (result as any)[key] = source[key];
      }
    }
  }

  return result;
}

/**
 * 防抖函数
 *
 * @param func - 要防抖的函数
 * @param delay - 延迟时间（毫秒）
 * @returns 防抖后的函数
 *
 * @example
 * const debouncedSearch = debounce((query: string) => {
 *   console.log('Searching:', query);
 * }, 300);
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * 节流函数
 *
 * @param func - 要节流的函数
 * @param limit - 时间限制（毫秒）
 * @returns 节流后的函数
 *
 * @example
 * const throttledScroll = throttle(() => {
 *   console.log('Scrolling...');
 * }, 100);
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * 生成唯一ID
 *
 * @param prefix - ID前缀（可选）
 * @returns 唯一ID字符串
 *
 * @example
 * generateId() // '550e8400-e29b-41d4-a716-446655440000'
 * generateId('user') // 'user-550e8400-e29b-41d4-a716-446655440000'
 */
export function generateId(prefix: string = ''): string {
  const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });

  return prefix ? `${prefix}-${uuid}` : uuid;
}

/**
 * 格式化文件大小
 *
 * @param bytes - 字节数
 * @returns 格式化后的文件大小字符串
 *
 * @example
 * formatFileSize(1024) // '1 KB'
 * formatFileSize(1048576) // '1 MB'
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 截断文本到指定长度
 *
 * @param text - 原始文本
 * @param maxLength - 最大长度
 * @param suffix - 后缀（默认为'...'）
 * @returns 截断后的文本
 *
 * @example
 * truncateText('Very long text...', 10) // 'Very long...'
 */
export function truncateText(
  text: string,
  maxLength: number,
  suffix: string = '...'
): string {
  if (text.length <= maxLength) {
    return text;
  }

  return text.slice(0, maxLength - suffix.length) + suffix;
}

/**
 * 导出所有工具函数
 */
export const helpers = {
  // 日期时间
  formatDate,
  formatDateTime,
  parseDate,
  // 字符串处理
  sanitizeInput,
  isBlank,
  normalizeIdentifier,
  // API调用
  fetchAPI,
  // 本地存储
  getFromStorage,
  saveToStorage,
  removeFromStorage,
  // 数据操作
  deepClone,
  mergeObjects,
  // 函数工具
  debounce,
  throttle,
  // 其他工具
  generateId,
  formatFileSize,
  truncateText,
};

export default helpers;
