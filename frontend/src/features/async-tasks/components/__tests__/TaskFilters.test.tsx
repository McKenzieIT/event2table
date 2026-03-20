/**
 * TaskFilters Component Tests
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { TaskFilters } from '../TaskFilters';
import type { TaskFilters as TaskFiltersType } from '../../api/taskApi';

describe('TaskFilters', () => {
  const mockFilters: TaskFiltersType = {};
  const setFilters = vi.fn();

  it('renders filter controls correctly', () => {
    render(
      <TaskFilters filters={mockFilters} onFiltersChange={setFilters} />
    );
    
    expect(screen.getByLabelText('状态')).toBeInTheDocument();
    expect(screen.getByLabelText('类型')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('输入创建者...')).toBeInTheDocument();
  });

  it('calls onFiltersChange when status changes', () => {
    render(
      <TaskFilters filters={mockFilters} onFiltersChange={setFilters} />
    );
    
    const statusSelect = screen.getByLabelText('状态');
    fireEvent.change(statusSelect, { target: { value: 'running' } });
    
    expect(setFilters).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'running' })
    );
  });

  it('calls onFiltersChange when type changes', () => {
    render(
      <TaskFilters filters={mockFilters} onFiltersChange={setFilters} />
    );
    
    const typeSelect = screen.getByLabelText('类型');
    fireEvent.change(typeSelect, { target: { value: 'batch_import' } });
    
    expect(setFilters).toHaveBeenCalledWith(
      expect.objectContaining({ task_type: 'batch_import' })
    );
  });

  it('calls onFiltersChange when created_by changes', () => {
    render(
      <TaskFilters filters={mockFilters} onFiltersChange={setFilters} />
    );
    
    const createdByInput = screen.getByPlaceholderText('输入创建者...');
    fireEvent.change(createdByInput, { target: { value: 'user1' } });
    
    expect(setFilters).toHaveBeenCalledWith(
      expect.objectContaining({ created_by: 'user1' })
    );
  });

  it('resets filters when reset button is clicked', () => {
    const activeFilters: TaskFiltersType = {
      status: 'running',
      task_type: 'batch_import',
      created_by: 'user1',
    };
    
    render(
      <TaskFilters filters={activeFilters} onFiltersChange={setFilters} />
    );
    
    const resetButton = screen.getByText('重置');
    fireEvent.click(resetButton);
    
    expect(setFilters).toHaveBeenCalledWith({});
  });

  it('does not show reset button when no active filters', () => {
    render(
      <TaskFilters filters={mockFilters} onFiltersChange={setFilters} />
    );
    
    expect(screen.queryByText('重置')).not.toBeInTheDocument();
  });
});
