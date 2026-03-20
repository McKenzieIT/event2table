/**
 * Async Task API Client
 * 异步任务API客户端
 *
 * @module async-tasks
 */

// ============================================
// Type Definitions
// ============================================

/**
 * 任务状态
 */
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

/**
 * 任务类型
 */
export type TaskType = 'batch_import' | 'data_export' | 'sql_optimization' | 'data_processing' | string;

/**
 * 任务数据结构
 */
export interface Task {
  id: number;
  task_id: string;
  task_type: TaskType;
  status: TaskStatus;
  progress: number;
  result: unknown | null;
  error_message: string | null;
  created_by: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

/**
 * 任务列表响应
 */
export interface TasksResponse {
  success: boolean;
  data: Task[];
  message?: string;
}

/**
 * 单个任务响应
 */
export interface TaskResponse {
  success: boolean;
  data: Task;
  message?: string;
}

/**
 * 任务统计响应
 */
export interface TaskStatisticsResponse {
  success: boolean;
  data: {
    total_tasks: number;
    by_status: Record<TaskStatus, number>;
    by_type: Record<string, number>;
  };
}

/**
 * 任务过滤器
 */
export interface TaskFilters {
  task_type?: TaskType;
  status?: TaskStatus;
  created_by?: string;
  limit?: number;
}

/**
 * 取消任务响应
 */
export interface CancelTaskResponse {
  success: boolean;
  message?: string;
}

// ============================================
// API Functions
// ============================================

/**
 * 获取任务列表
 *
 * @param filters - 过滤条件
 * @returns 任务列表
 * @throws {Error} 当API响应无效或请求失败时
 *
 * @example
 * const tasks = await getTasks({ status: 'running', limit: 20 });
 */
export async function getTasks(filters?: TaskFilters): Promise<Task[]> {
  const params = new URLSearchParams();
  
  if (filters?.task_type) params.append('task_type', filters.task_type);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.created_by) params.append('created_by', filters.created_by);
  if (filters?.limit) params.append('limit', filters.limit.toString());

  const url = `/api/async-tasks${params.toString() ? `?${params}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }

  const result = await response.json() as TasksResponse;

  if (!result.success) {
    throw new Error(result.message || 'Tasks API request failed');
  }

  if (!result.data || !Array.isArray(result.data)) {
    throw new Error('Invalid API response: data is not an array');
  }

  return result.data;
}

/**
 * 获取单个任务详情
 *
 * @param taskId - 任务ID
 * @returns 任务详情
 * @throws {Error} 当任务不存在或请求失败时
 *
 * @example
 * const task = await getTask('550e8400-e29b-41d4-a716-446655440000');
 */
export async function getTask(taskId: string): Promise<Task> {
  const response = await fetch(`/api/async-tasks/${encodeURIComponent(taskId)}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Task not found: ${taskId}`);
    }
    throw new Error(`Failed to fetch task: ${response.statusText}`);
  }

  const result = await response.json() as TaskResponse;

  if (!result.success) {
    throw new Error(result.message || 'Task API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}

/**
 * 取消任务
 *
 * @param taskId - 任务ID
 * @returns 取消结果
 * @throws {Error} 当任务不存在或取消失败时
 *
 * @example
 * await cancelTask('550e8400-e29b-41d4-a716-446655440000');
 */
export async function cancelTask(taskId: string): Promise<void> {
  const response = await fetch(`/api/async-tasks/${encodeURIComponent(taskId)}/cancel`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Task not found: ${taskId}`);
    }
    throw new Error(`Failed to cancel task: ${response.statusText}`);
  }

  const result = await response.json() as CancelTaskResponse;

  if (!result.success) {
    throw new Error(result.message || 'Cancel task API request failed');
  }
}

/**
 * 获取任务统计信息
 *
 * @returns 任务统计信息
 * @throws {Error} 当API响应无效或请求失败时
 *
 * @example
 * const stats = await getTaskStatistics();
 * console.log(stats.total_tasks);
 */
export async function getTaskStatistics(): Promise<TaskStatisticsResponse['data']> {
  const response = await fetch('/api/async-tasks/statistics');

  if (!response.ok) {
    throw new Error(`Failed to fetch task statistics: ${response.statusText}`);
  }

  const result = await response.json() as TaskStatisticsResponse;

  if (!result.success) {
    throw new Error(result.message || 'Task statistics API request failed');
  }

  if (!result.data) {
    throw new Error('Invalid API response: missing data field');
  }

  return result.data;
}
