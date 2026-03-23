/**
 * TaskFilters Component
 *
 * Filter controls for task list
 */

import React from 'react';

import type { TaskFilters, TaskStatus, TaskType } from '../api/taskApi';

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  availableStatuses?: TaskStatus[];
  availableTypes?: TaskType[];
  className?: string;
}

/**
 * TaskFilters component
 *
 * @example
 * <TaskFilters
 *   filters={{ status: 'running' }}
 *   onFiltersChange={setFilters}
 * />
 */
export function TaskFilters({
  filters,
  onFiltersChange,
  availableStatuses = ['pending', 'running', 'completed', 'failed', 'cancelled'],
  availableTypes = ['batch_import', 'data_export', 'sql_optimization', 'data_processing'],
  className = '',
}: TaskFiltersProps): React.JSX.Element {
  const handleStatusChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value as TaskStatus | '';
    onFiltersChange({
      ...filters,
      status: value || undefined,
    });
  };

  const handleTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value as TaskType | '';
    onFiltersChange({
      ...filters,
      task_type: value || undefined,
    });
  };

  const handleCreatedByChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value.trim();
    onFiltersChange({
      ...filters,
      created_by: value || undefined,
    });
  };

  const handleReset = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = Object.values(filters).some(
    (value) => value !== undefined && value !== ''
  );

  return (
    <div className={`task-filters ${className}`}>
      <div className="task-filters__row">
        <div className="task-filters__field">
          <label htmlFor="status-filter" className="task-filters__label">
            状态
          </label>
          <select
            id="status-filter"
            className="task-filters__select"
            value={filters.status || ''}
            onChange={handleStatusChange}
          >
            <option value="">全部</option>
            {availableStatuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div className="task-filters__field">
          <label htmlFor="type-filter" className="task-filters__label">
            类型
          </label>
          <select
            id="type-filter"
            className="task-filters__select"
            value={filters.task_type || ''}
            onChange={handleTypeChange}
          >
            <option value="">全部</option>
            {availableTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="task-filters__field">
          <label htmlFor="created-by-filter" className="task-filters__label">
            创建者
          </label>
          <input
            id="created-by-filter"
            type="text"
            className="task-filters__input"
            placeholder="输入创建者..."
            value={filters.created_by || ''}
            onChange={handleCreatedByChange}
          />
        </div>

        {hasActiveFilters && (
          <button
            type="button"
            className="task-filters__reset"
            onClick={handleReset}
          >
            重置
          </button>
        )}
      </div>
    </div>
  );
}
