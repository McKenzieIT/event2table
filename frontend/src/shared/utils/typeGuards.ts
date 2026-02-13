/**
 * 轻量级类型守卫（零依赖）
 *
 * 运行时开销极小（简单typeof/instanceof检查）
 * 用于在运行时验证数据结构，替代Zod等重型库
 *
 * @module typeGuards
 */

/**
 * 游戏对象类型
 */
export interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  created_at: string;
}

/**
 * 事件对象类型
 */
export interface Event {
  id: number;
  event_name: string;
  display_name: string;
  game_gid: number;
  event_type: 'user' | 'system' | 'auto';
  created_at: string;
}

/**
 * 参数对象类型
 */
export interface Parameter {
  id: number;
  param_name: string;
  param_name_cn: string;
  param_type: 'string' | 'int' | 'float' | 'boolean' | 'json';
  game_gid: number | null;
}

/**
 * API响应基础类型
 */
export interface ApiResponse<T = unknown> {
  data: T;
  success: boolean;
  message?: string;
  timestamp?: string;
}

/**
 * 检查数据是否为Game对象
 */
export function isGame(data: unknown): data is Game {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    typeof data.id === 'number' &&
    'gid' in data &&
    typeof data.gid === 'number' &&
    'name' in data &&
    typeof data.name === 'string' &&
    'ods_db' in data &&
    typeof data.ods_db === 'string'
  );
}

/**
 * 检查数据是否为Event对象
 */
export function isEvent(data: unknown): data is Event {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    typeof data.id === 'number' &&
    'event_name' in data &&
    typeof data.event_name === 'string' &&
    'display_name' in data &&
    typeof data.display_name === 'string' &&
    'game_gid' in data &&
    typeof data.game_gid === 'number'
  );
}

/**
 * 检查数据是否为Parameter对象
 */
export function isParameter(data: unknown): data is Parameter {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    typeof data.id === 'number' &&
    'param_name' in data &&
    typeof data.param_name === 'string' &&
    'param_name_cn' in data &&
    typeof data.param_name_cn === 'string'
  );
}

/**
 * 检查数据是否为Event数组
 */
export function isEventArray(data: unknown): data is Event[] {
  return Array.isArray(data) && data.every(isEvent);
}

/**
 * 检查数据是否为Game数组
 */
export function isGameArray(data: unknown): data is Game[] {
  return Array.isArray(data) && data.every(isGame);
}

/**
 * 检查数据是否为Parameter数组
 */
export function isParameterArray(data: unknown): data is Parameter[] {
  return Array.isArray(data) && data.every(isParameter);
}

/**
 * 检查数据是否为API响应格式
 */
export function isApiResponse(data: unknown): data is ApiResponse<unknown> {
  return (
    typeof data === 'object' &&
    data !== null &&
    'data' in data &&
    'success' in data &&
    typeof data.success === 'boolean'
  );
}

/**
 * 断言数据为Game对象，验证失败则抛出错误
 */
export function assertGame(data: unknown): asserts data is Game {
  if (!isGame(data)) {
    throw new Error(`Invalid Game object: ${JSON.stringify(data)}`);
  }
}

/**
 * 断言数据为Event对象，验证失败则抛出错误
 */
export function assertEvent(data: unknown): asserts data is Event {
  if (!isEvent(data)) {
    throw new Error(`Invalid Event object: ${JSON.stringify(data)}`);
  }
}

/**
 * 断言数据为Event数组，验证失败则抛出错误
 */
export function assertEventArray(data: unknown): asserts data is Event[] {
  if (!isEventArray(data)) {
    throw new Error('Invalid Event array: expected array of Event objects');
  }
}

/**
 * 断言数据为Game数组，验证失败则抛出错误
 */
export function assertGameArray(data: unknown): asserts data is Game[] {
  if (!isGameArray(data)) {
    throw new Error('Invalid Game array: expected array of Game objects');
  }
}

/**
 * 断言数据为Parameter数组，验证失败则抛出错误
 */
export function assertParameterArray(data: unknown): asserts data is Parameter[] {
  if (!isParameterArray(data)) {
    throw new Error('Invalid Parameter array: expected array of Parameter objects');
  }
}

/**
 * 创建数组类型守卫（泛型）
 *
 * @example
 * const isStringArray = createArrayGuard((item): item is string => typeof item === 'string');
 */
export function createArrayGuard<T>(
  itemGuard: (item: unknown) => item is T
): (data: unknown) => data is T[] {
  return (data): data is T[] => {
    return Array.isArray(data) && data.every(itemGuard);
  };
}

/**
 * 创建API响应类型守卫（泛型）
 *
 * @example
 * const isEventResponse = createApiResponseGuard(isEventArray);
 * if (isEventResponse(data)) {
 *   console.log(data.data); // TypeScript知道这是Event[]
 * }
 */
export function createApiResponseGuard<T>(
  dataGuard: (data: unknown) => data is T
): (data: unknown) => data is ApiResponse<T> {
  return (data): data is ApiResponse<T> => {
    return (
      typeof data === 'object' &&
      data !== null &&
      'data' in data &&
      dataGuard((data as ApiResponse<T>).data) &&
      'success' in data &&
      typeof (data as ApiResponse<T>).success === 'boolean'
    );
  };
}

/**
 * 常用的类型守卫集合
 */
export const guards = {
  isGame,
  isEvent,
  isParameter,
  isGameArray,
  isEventArray,
  isParameterArray,
  isApiResponse,
} as const;
