/**
 * Task Management Page
 *
 * Main page for managing async tasks
 */

import React, { useState, useCallback } from 'react';

import type { Task, TaskFilters as TaskFiltersType } from '../api/taskApi';
import { TaskList, TaskFilters, TaskDetail } from '../components';
import { useTasks, useTaskPolling, useCancelTask } from '../hooks';
import './TaskManagementPage.css';

/**
 * TaskManagementPage component
 *
 * Features:
 * - Display task list with filters
 * - View task details
 * - Cancel running tasks
 * - Auto-refresh task list
 * - Polling for active tasks
 */
export function TaskManagementPage(): React.JSX.Element {
  const [filters, setFilters] = useState<TaskFiltersType>({});
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  const { data: tasks = [], isLoading, refetch } = useTasks(filters);
  const { mutateAsync: cancelTask, isPending: isCancelling } = useCancelTask();
  const { data: selectedTask } = useTaskPolling(selectedTaskId, 2000);

  const handleFiltersChange = useCallback((newFilters: TaskFiltersType) => {
    setFilters(newFilters);
    setSelectedTaskId(null);
  }, []);

  const handleTaskClick = useCallback((task: Task) => {
    setSelectedTaskId(task.task_id);
  }, []);

  const handleCancelTask = useCallback(async (taskId: string) => {
    try {
      await cancelTask(taskId);
      refetch();
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  }, [cancelTask, refetch]);

  const handleCloseDetail = useCallback(() => {
    setSelectedTaskId(null);
  }, []);

  return (
    <div className="task-management-page">
      <div className="task-management-page__header">
        <h1 className="task-management-page__title">异步任务管理</h1>
      </div>

      <div className="task-management-page__content">
        <div className="task-management-page__main">
          <TaskFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />

          <TaskList
            tasks={tasks}
            isLoading={isLoading}
            onTaskClick={handleTaskClick}
          />
        </div>

        {selectedTask && selectedTaskId && (
          <div className="task-management-page__detail">
            <div className="task-management-page__detail-header">
              <h2 className="task-management-page__detail-title">任务详情</h2>
              <button
                type="button"
                className="task-management-page__close-btn"
                onClick={handleCloseDetail}
              >
                关闭
              </button>
            </div>

            <TaskDetail
              task={selectedTask}
              onCancelTask={handleCancelTask}
              isCancelling={isCancelling}
            />
          </div>
        )}
      </div>
    </div>
  );
}
