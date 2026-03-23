/**
 * TaskDetail Component
 *
 * Displays detailed information about a task
 */

import React from 'react';

import type { Task } from '../api/taskApi';

import { TaskProgress } from './TaskProgress';

interface TaskDetailProps {
  task: Task;
  onCancelTask?: (taskId: string) => void;
  isCancelling?: boolean;
  className?: string;
}

/**
 * Format date to readable string
 */
function formatDate(dateString: string | null): string {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * TaskDetail component
 *
 * @example
 * <TaskDetail
 *   task={task}
 *   onCancelTask={handleCancel}
 *   isCancelling={false}
 * />
 */
export function TaskDetail({
  task,
  onCancelTask,
  isCancelling = false,
  className = '',
}: TaskDetailProps): React.JSX.Element {
  const canCancel = task.status === 'pending' || task.status === 'running';

  return (
    <div className={`task-detail ${className}`}>
      <div className="task-detail__header">
        <h3 className="task-detail__title">任务详情</h3>
        {canCancel && onCancelTask && (
          <button
            type="button"
            className="task-detail__cancel-btn"
            onClick={() => onCancelTask(task.task_id)}
            disabled={isCancelling}
          >
            {isCancelling ? '取消中...' : '取消任务'}
          </button>
        )}
      </div>

      <div className="task-detail__content">
        <div className="task-detail__section">
          <TaskProgress progress={task.progress} status={task.status} />
        </div>

        {task.error_message && (
          <div className="task-detail__section task-detail__section--error">
            <h4 className="task-detail__section-title">错误信息</h4>
            <p className="task-detail__error-message">{task.error_message}</p>
          </div>
        )}

        <div className="task-detail__grid">
          <div className="task-detail__field">
            <span className="task-detail__label">任务ID</span>
            <span className="task-detail__value task-detail__value--mono">
              {task.task_id}
            </span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">任务类型</span>
            <span className="task-detail__value">{task.task_type}</span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">状态</span>
            <span className="task-detail__value">{task.status}</span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">进度</span>
            <span className="task-detail__value">{task.progress}%</span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">创建者</span>
            <span className="task-detail__value">
              {task.created_by || '-'}
            </span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">创建时间</span>
            <span className="task-detail__value">
              {formatDate(task.created_at)}
            </span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">开始时间</span>
            <span className="task-detail__value">
              {formatDate(task.started_at)}
            </span>
          </div>

          <div className="task-detail__field">
            <span className="task-detail__label">完成时间</span>
            <span className="task-detail__value">
              {formatDate(task.completed_at)}
            </span>
          </div>
        </div>

        {task.result && (
          <div className="task-detail__section">
            <h4 className="task-detail__section-title">任务结果</h4>
            <pre className="task-detail__result">
              {JSON.stringify(task.result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
