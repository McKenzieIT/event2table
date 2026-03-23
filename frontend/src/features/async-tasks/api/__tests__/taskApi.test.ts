/**
 * Task API Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

import { getTasks, getTask, cancelTask, getTaskStatistics } from '../taskApi';
import type { Task, TaskFilters, TaskStatus } from '../taskApi';

// Mock fetch
(globalThis as any).fetch = vi.fn();

describe('Task API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getTasks', () => {
    it('fetches tasks successfully', async () => {
      const mockTasks: Task[] = [
        {
          id: 1,
          task_id: '550e8400-e29b-41d4-a716-446655440000',
          task_type: 'batch_import',
          status: 'running',
          progress: 50,
          result: null,
          error_message: null,
          created_by: 'user1',
          created_at: '2024-01-01T00:00:00',
          started_at: '2024-01-01T00:00:00',
          completed_at: null,
        },
      ];

      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockTasks }),
      });

      const tasks = await getTasks();
      expect(tasks).toEqual(mockTasks);
      expect((globalThis as any).fetch).toHaveBeenCalledWith('/api/async-tasks');
    });

    it('fetches tasks with filters', async () => {
      const filters: TaskFilters = { status: 'running' as TaskStatus, limit: 10 };
      
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] }),
      });

      await getTasks(filters);
      expect((globalThis as any).fetch).toHaveBeenCalledWith(
        '/api/async-tasks?status=running&limit=10'
      );
    });

    it('throws error when API response is not successful', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, message: 'Error' }),
      });

      await expect(getTasks()).rejects.toThrow('Error');
    });

    it('throws error when fetch fails', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      });

      await expect(getTasks()).rejects.toThrow('Failed to fetch tasks: Not Found');
    });
  });

  describe('getTask', () => {
    const taskId = '550e8400-e29b-41d4-a716-446655440000';
    const mockTask: Task = {
      id: 1,
      task_id: taskId,
      task_type: 'batch_import',
      status: 'running',
      progress: 50,
      result: null,
      error_message: null,
      created_by: 'user1',
      created_at: '2024-01-01T00:00:00',
      started_at: '2024-01-01T00:00:00',
      completed_at: null,
    };

    it('fetches a single task successfully', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockTask }),
      });

      const task = await getTask(taskId);
      expect(task).toEqual(mockTask);
      expect((globalThis as any).fetch).toHaveBeenCalledWith(`/api/async-tasks/${taskId}`);
    });

    it('throws error when task is not found (404)', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(getTask(taskId)).rejects.toThrow(`Task not found: ${taskId}`);
    });

    it('throws error when API response is not successful', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, message: 'Error' }),
      });

      await expect(getTask(taskId)).rejects.toThrow('Error');
    });
  });

  describe('cancelTask', () => {
    const taskId = '550e8400-e29b-41d4-a716-446655440000';

    it('cancels a task successfully', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await cancelTask(taskId);
      expect((globalThis as any).fetch).toHaveBeenCalledWith(`/api/async-tasks/${taskId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('throws error when task is not found (404)', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(cancelTask(taskId)).rejects.toThrow(`Task not found: ${taskId}`);
    });

    it('throws error when API response is not successful', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, message: 'Error' }),
      });

      await expect(cancelTask(taskId)).rejects.toThrow('Error');
    });
  });

  describe('getTaskStatistics', () => {
    const mockStatistics = {
      total_tasks: 10,
      by_status: {
        pending: 2,
        running: 3,
        completed: 4,
        failed: 1,
        cancelled: 0,
      },
      by_type: {
        batch_import: 5,
        data_export: 5,
      },
    };

    it('fetches task statistics successfully', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockStatistics }),
      });

      const statistics = await getTaskStatistics();
      expect(statistics).toEqual(mockStatistics);
      expect((globalThis as any).fetch).toHaveBeenCalledWith('/api/async-tasks/statistics');
    });

    it('throws error when API response is not successful', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false, message: 'Error' }),
      });

      await expect(getTaskStatistics()).rejects.toThrow('Error');
    });

    it('throws error when fetch fails', async () => {
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      });

      await expect(getTaskStatistics()).rejects.toThrow('Failed to fetch task statistics: Not Found');
    });
  });
});
