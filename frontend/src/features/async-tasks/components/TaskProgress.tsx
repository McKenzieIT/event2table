/**
 * TaskProgress Component
 *
 * Displays task progress with visual indicator
 */

import React from 'react';
import type { TaskStatus } from '../api/taskApi';

interface TaskProgressProps {
  progress: number;
  status: TaskStatus;
  className?: string;
}

/**
 * Get status color based on task status
 */
function getStatusColor(status: TaskStatus): string {
  switch (status) {
    case 'pending':
      return '#f59e0b'; // yellow
    case 'running':
      return '#3b82f6'; // blue
    case 'completed':
      return '#10b981'; // green
    case 'failed':
      return '#ef4444'; // red
    case 'cancelled':
      return '#6b7280'; // gray
    default:
      return '#6b7280';
  }
}

/**
 * Get status label in Chinese
 */
function getStatusLabel(status: TaskStatus): string {
  switch (status) {
    case 'pending':
      return '等待中';
    case 'running':
      return '运行中';
    case 'completed':
      return '已完成';
    case 'failed':
      return '失败';
    case 'cancelled':
      return '已取消';
    default:
      return status;
  }
}

/**
 * TaskProgress component
 *
 * @example
 * <TaskProgress progress={45} status="running" />
 */
export function TaskProgress({ progress, status, className = '' }: TaskProgressProps): React.JSX.Element {
  const color = getStatusColor(status);
  const label = getStatusLabel(status);

  return (
    <div className={`task-progress ${className}`}>
      <div className="task-progress__header">
        <span className="task-progress__label">{label}</span>
        <span className="task-progress__percentage">{progress}%</span>
      </div>
      <div className="task-progress__bar">
        <div
          className="task-progress__fill"
          style={{
            width: `${progress}%`,
            backgroundColor: color,
          }}
        />
      </div>
    </div>
  );
}
