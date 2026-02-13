/**
 * Component Utilities
 * 组件工具函数 - 提供空值检查和类型安全保护
 *
 * 功能:
 * - ensureArray: 确保值是数组
 * - safeLength: 安全地获取数组长度
 * - safeFilter: 安全地过滤数组
 * - safeMap: 安全地映射数组
 *
 * @module componentUtils
 */

/**
 * 确保值是数组
 * @param {any} value - 要检查的值
 * @param {Array} [defaultValue=[]] - 默认值
 * @returns {Array}
 * @example
 * ensureArray(undefined) // []
 * ensureArray([1, 2, 3]) // [1, 2, 3]
 * ensureArray(null, ['default']) // ['default']
 */
export function ensureArray(value, defaultValue = []) {
  return Array.isArray(value) ? value : defaultValue;
}

/**
 * 安全地获取数组长度
 * @param {any} value - 要检查的值
 * @returns {number}
 * @example
 * safeLength([1, 2, 3]) // 3
 * safeLength(undefined) // 0
 * safeLength(null) // 0
 */
export function safeLength(value) {
  return Array.isArray(value) ? value.length : 0;
}

/**
 * 安全地过滤数组
 * @param {any} value - 要过滤的值
 * @param {Function} predicate - 过滤函数
 * @returns {Array}
 * @example
 * safeFilter([1, 2, 3], x => x > 1) // [2, 3]
 * safeFilter(undefined, x => x > 1) // []
 */
export function safeFilter(value, predicate) {
  return Array.isArray(value) ? value.filter(predicate) : [];
}

/**
 * 安全地映射数组
 * @param {any} value - 要映射的值
 * @param {Function} mapper - 映射函数
 * @returns {Array}
 * @example
 * safeMap([1, 2, 3], x => x * 2) // [2, 4, 6]
 * safeMap(undefined, x => x * 2) // []
 */
export function safeMap(value, mapper) {
  return Array.isArray(value) ? value.map(mapper) : [];
}

/**
 * 安全地检查数组是否为空
 * @param {any} value - 要检查的值
 * @returns {boolean}
 * @example
 * safeIsEmpty([]) // true
 * safeIsEmpty([1, 2]) // false
 * safeIsEmpty(undefined) // true
 */
export function safeIsEmpty(value) {
  return !Array.isArray(value) || value.length === 0;
}
