/**
 * TaskList Component
 *
 * Displays a list of tasks in a table format
 */

import React from 'react';
import { TaskProgress } from './TaskProgress';
import type { Task } from '../api/taskApi';

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onTaskClick?: (task: Task) => void;
  className?: string;
}

/**
 * Format date to readable string
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * TaskList component
 *
 * @example
 * <TaskList
 *   tasks={tasks}
 *   isLoading={false}
 *   onTaskClick={handleTaskClick}
 * />
 */
export function TaskList({
  tasks,
  isLoading = false,
  onTaskClick,
  className = '',
}: TaskListProps): React.JSX.Element {
  if (isLoading) {
    return (
      <div className={`task-list task-list--loading ${className}`}>
        <div className="task-list__loading">加载中...</div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className={`task-list task-list--empty ${className}`}>
        <div className="task-list__empty">
          <p>暂无任务</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`task-list ${className}`}>
      <table className="task-list__table">
        <thead>
          <tr>
            <th>任务ID</th>
            <th>类型</th>
            <th>状态</th>
            <th>进度</th>
            <th>创建者</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr
              key={task.task_id}
              className="task-list__row"
              onClick={() => onTaskClick?.(task)}
            >
              <td className="task-list__cell task-list__cell--mono">
                {task.task_id.slice(0, 8)}...
              </td>
              <td className="task-list__cell">{task.task_type}</td>
              <td className="task-list__cell">
                <TaskProgress progress={task.progress} status={task.status} />
              </td>
              <td className="task-list__cell">{task.progress}%</td>
              <td className="task-list__cell">{task.created_by || '-'}</td>
              <td className="task-list__cell">{formatDate(task.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
