/**
 * HQL Version API Client
 * HQL版本管理API客户端
 *
 * @module hqlVersion
 */

// ============================================
// Type Definitions
// ============================================

/**
 * HQL版本信息
 */
export interface HqlVersion {
  id: number;
  event_id: number;
  version_number: number;
  hql_content: string;
  change_description?: string;
  created_at: string;
  created_by?: string;
  is_current: boolean;
}

/**
 * 保存版本请求
 */
export interface SaveVersionRequest {
  event_id: number;
  hql_content: string;
  change_description?: string;
}

/**
 * 保存版本响应
 */
export interface SaveVersionResponse {
  version: HqlVersion;
}

/**
 * 版本对比请求
 */
export interface CompareVersionsRequest {
  version_id_1: number;
  version_id_2: number;
}

/**
 * 版本对比结果
 */
export interface VersionDiff {
  version1: HqlVersion;
  version2: HqlVersion;
  diff: string;
  summary: {
    additions: number;
    deletions: number;
    changes: number;
  };
}

/**
 * 版本历史响应
 */
export interface VersionHistoryResponse {
  versions: HqlVersion[];
  total: number;
}

/**
 * 回滚版本请求
 */
export interface RollbackVersionRequest {
  version_id: number;
}

/**
 * 回滚版本响应
 */
export interface RollbackVersionResponse {
  version: HqlVersion;
}

/**
 * API响应包装器
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// ============================================
// API Functions
// ============================================

/**
 * 保存HQL版本
 *
 * @param data - 保存版本请求数据
 * @returns 保存的版本信息
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await saveVersion({
 *   event_id: 123,
 *   hql_content: 'SELECT * FROM table',
 *   change_description: 'Initial version'
 * });
 */
export const saveVersion = async (
  data: SaveVersionRequest
): Promise<SaveVersionResponse> => {
  const response = await fetch('/api/hql-versions/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to save version: ${response.statusText}`);
  }

  const result: ApiResponse<SaveVersionResponse> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Save version request failed');
  }

  return result.data as SaveVersionResponse;
};

/**
 * 对比两个版本
 *
 * @param data - 版本对比请求数据
 * @returns 版本对比结果
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const diff = await compareVersions({
 *   version_id_1: 1,
 *   version_id_2: 2
 * });
 */
export const compareVersions = async (
  data: CompareVersionsRequest
): Promise<VersionDiff> => {
  const response = await fetch('/api/hql-versions/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to compare versions: ${response.statusText}`);
  }

  const result: ApiResponse<VersionDiff> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Compare versions request failed');
  }

  return result.data as VersionDiff;
};

/**
 * 获取版本历史
 *
 * @param eventId - 事件ID
 * @returns 版本历史列表
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await getVersionHistory(123);
 * const versions = response.versions;
 */
export const getVersionHistory = async (
  eventId: number
): Promise<VersionHistoryResponse> => {
  const response = await fetch(`/api/hql-versions/history/${eventId}`);

  if (!response.ok) {
    throw new Error(`Failed to get version history: ${response.statusText}`);
  }

  const result: ApiResponse<VersionHistoryResponse> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Get version history request failed');
  }

  return result.data as VersionHistoryResponse;
};

/**
 * 回滚到指定版本
 *
 * @param data - 回滚版本请求数据
 * @returns 回滚后的版本信息
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const response = await rollbackToVersion({ version_id: 1 });
 */
export const rollbackToVersion = async (
  data: RollbackVersionRequest
): Promise<RollbackVersionResponse> => {
  const response = await fetch('/api/hql-versions/rollback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to rollback version: ${response.statusText}`);
  }

  const result: ApiResponse<RollbackVersionResponse> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Rollback version request failed');
  }

  return result.data as RollbackVersionResponse;
};

/**
 * 获取最新版本
 *
 * @param eventId - 事件ID
 * @returns 最新版本信息
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const version = await getLatestVersion(123);
 */
export const getLatestVersion = async (
  eventId: number
): Promise<HqlVersion> => {
  const response = await fetch(`/api/hql-versions/latest/${eventId}`);

  if (!response.ok) {
    throw new Error(`Failed to get latest version: ${response.statusText}`);
  }

  const result: ApiResponse<HqlVersion> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Get latest version request failed');
  }

  return result.data as HqlVersion;
};

/**
 * 获取特定版本
 *
 * @param versionId - 版本ID
 * @returns 版本信息
 * @throws {Error} 当API请求失败时
 *
 * @example
 * const version = await getVersion(1);
 */
export const getVersion = async (
  versionId: number
): Promise<HqlVersion> => {
  const response = await fetch(`/api/hql-versions/${versionId}`);

  if (!response.ok) {
    throw new Error(`Failed to get version: ${response.statusText}`);
  }

  const result: ApiResponse<HqlVersion> = await response.json();

  if (!result.success) {
    throw new Error(result.error || result.message || 'Get version request failed');
  }

  return result.data as HqlVersion;
};
