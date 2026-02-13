/**
 * 轻量级API验证器
 *
 * 零依赖，清晰错误消息
 * 用于替代可选链操作符 (?.) 进行显式验证
 *
 * @module apiValidator
 */

/**
 * 验证API响应结构
 *
 * @param {unknown} data - 响应数据
 * @param {string} [apiName='API'] - API名称（用于错误消息）
 * @returns {{ success: boolean; data?: unknown; error?: string }}
 *
 * @example
 * const validated = validateApiResponse(response, 'Events API');
 * if (validated.success) {
 *   console.log(validated.data); // 安全访问data
 * } else {
 *   console.error(validated.error); // 清晰的错误消息
 * }
 */
export function validateApiResponse(data, apiName = 'API') {
  if (!data || typeof data !== 'object') {
    return {
      success: false,
      error: `${apiName} response is not an object`
    };
  }

  if (!('success' in data)) {
    return {
      success: false,
      error: `${apiName} response missing 'success' field`
    };
  }

  if (data.success === false) {
    return {
      success: false,
      error: data.message || `${apiName} request failed`
    };
  }

  if (!('data' in data)) {
    return {
      success: false,
      error: `${apiName} response missing 'data' field`
    };
  }

  return { success: true, data: data.data };
}

/**
 * 验证数组响应
 *
 * @param {unknown} data - 响应数据
 * @param {string} [apiName='API'] - API名称
 * @returns {{ success: boolean; data?: unknown[]; error?: string }}
 *
 * @example
 * const validated = validateArrayResponse(data, 'Events API');
 * if (validated.success) {
 *   console.log(validated.data.length); // 安全访问数组
 * }
 */
export function validateArrayResponse(data, apiName = 'API') {
  const validated = validateApiResponse(data, apiName);

  if (!validated.success) {
    return validated;
  }

  if (!Array.isArray(validated.data)) {
    return {
      success: false,
      error: `${apiName} response data is not an array`
    };
  }

  return { success: true, data: validated.data };
}

/**
 * 抛出式验证（简化错误处理）
 * 验证失败时抛出错误
 *
 * @param {unknown} data - 响应数据
 * @param {string} [apiName='API'] - API名称
 * @returns {unknown} 验证后的数据
 * @throws {Error} 验证失败时抛出
 *
 * @example
 * try {
 *   const data = assertApiResponse(response, 'Events API');
 *   console.log(data); // 安全访问，无需额外检查
 * } catch (error) {
 *   console.error(error.message); // 清晰的错误消息
 * }
 */
export function assertApiResponse(data, apiName = 'API') {
  const validated = validateApiResponse(data, apiName);

  if (!validated.success) {
    throw new Error(validated.error);
  }

  return validated.data;
}

/**
 * 抛出式数组验证
 *
 * @param {unknown} data - 响应数据
 * @param {string} [apiName='API'] - API名称
 * @returns {unknown[]} 验证后的数组数据
 * @throws {Error} 验证失败时抛出
 *
 * @example
 * const events = assertArrayResponse(data, 'Events API');
 * console.log(events.length); // TypeScript知道这是数组
 */
export function assertArrayResponse(data, apiName = 'API') {
  const validated = validateArrayResponse(data, apiName);

  if (!validated.success) {
    throw new Error(validated.error);
  }

  return validated.data;
}

/**
 * 安全解析JSON响应
 *
 * @param {string} jsonString - JSON字符串
 * @param {string} [apiName='API'] - API名称
 * @returns {{ success: boolean; data?: unknown; error?: string }}
 *
 * @example
 * const response = await fetch('/api/events');
 * const jsonString = await response.text();
 * const parsed = safeParseJSON(jsonString, 'Events API');
 */
export function safeParseJSON(jsonString, apiName = 'API') {
  try {
    const data = JSON.parse(jsonString);
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: `${apiName} response is not valid JSON: ${error.message}`
    };
  }
}

/**
 * 验证对象包含必填字段
 *
 * @param {unknown} obj - 要验证的对象
 * @param {string[]} requiredFields - 必填字段列表
 * @param {string} [objectName='Object'] - 对象名称（用于错误消息）
 * @returns {{ success: boolean; data?: object; error?: string }}
 *
 * @example
 * const event = { id: 1, name: 'test' };
 * const validated = validateRequiredFields(event, ['id', 'name', 'type'], 'Event');
 * if (!validated.success) {
 *   console.error(validated.error); // "Event is missing required fields: type"
 * }
 */
export function validateRequiredFields(obj, requiredFields, objectName = 'Object') {
  if (typeof obj !== 'object' || obj === null) {
    return {
      success: false,
      error: `${objectName} is not an object`
    };
  }

  const missing = requiredFields.filter(field => !(field in obj));

  if (missing.length > 0) {
    return {
      success: false,
      error: `${objectName} is missing required fields: ${missing.join(', ')}`
    };
  }

  return { success: true, data: obj };
}

/**
 * 使用示例文档
 *
 * @example
 * // ❌ 旧方法：使用可选链（隐藏错误）
 * const params = data?.data || [];
 * if (params.length === 0) {
 *   // 可能是data为undefined，也可能是真的空数组
 *   console.log('No params found');
 * }
 *
 * @example
 * // ✅ 新方法：显式验证（清晰错误消息）
 * const params = assertArrayResponse(data, 'Parameters API');
 * if (params.length === 0) {
 *   // 现在我们知道是真的空数组
 *   console.log('No params found (verified empty array)');
 * }
 *
 * @example
 * // 带错误处理
 * try {
 *   const events = assertArrayResponse(data, 'Events API');
 *   console.log(`Loaded ${events.length} events`);
 * } catch (error) {
 *   // 错误消息: "Events API response missing 'data' field"
 *   // 或: "Events API response data is not an array"
 *   console.error(error.message);
 * }
 */
