/**
 * TaskList Component Tests
 */

import { render, screen } from '@testing-library/react';
import { TaskList } from '../TaskList';
import type { Task } from '../../api/taskApi';

describe('TaskList', () => {
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
    {
      id: 2,
      task_id: '660e8400-e29b-41d4-a716-446655440001',
      task_type: 'data_export',
      status: 'completed',
      progress: 100,
      result: null,
      error_message: null,
      created_by: 'user2',
      created_at: '2024-01-01T00:00:00',
      started_at: '2024-01-01T00:00:00',
      completed_at: '2024-01-01T01:00:00',
    },
  ];

  it('renders task list correctly', () => {
    render(<TaskList tasks={mockTasks} />);
    
    expect(screen.getByText('batch_import')).toBeInTheDocument();
    expect(screen.getByText('data_export')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(<TaskList tasks={[]} isLoading={true} />);
    
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<TaskList tasks={[]} />);
    
    expect(screen.getByText('暂无任务')).toBeInTheDocument();
  });

  it('calls onTaskClick when a task is clicked', () => {
    const handleClick = vi.fn();
    render(<TaskList tasks={mockTasks} onTaskClick={handleClick} />);
    
    const rows = screen.getAllByRole('row');
    rows[1].click(); // Click first data row
    
    expect(handleClick).toHaveBeenCalledWith(mockTasks[0]);
  });

  it('applies custom className', () => {
    const { container } = render(
      <TaskList tasks={mockTasks} className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
