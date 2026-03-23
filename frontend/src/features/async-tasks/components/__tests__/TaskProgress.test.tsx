/**
 * TaskProgress Component Tests
 */

import { render, screen } from '@test/test-utils';

import type { TaskStatus } from '../../api/taskApi';
import { TaskProgress } from '../TaskProgress';

describe('TaskProgress', () => {
  it('renders progress correctly', () => {
    render(<TaskProgress progress={50} status="running" />);
    
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('运行中')).toBeInTheDocument();
  });

  it('renders different statuses correctly', () => {
    const statuses: TaskStatus[] = ['pending', 'running', 'completed', 'failed', 'cancelled'];
    const labels = ['等待中', '运行中', '已完成', '失败', '已取消'];

    statuses.forEach((status, index) => {
      const { unmount } = render(<TaskProgress progress={0} status={status} />);
      expect(screen.getByText(labels[index])).toBeInTheDocument();
      unmount();
    });
  });

  it('applies custom className', () => {
    const { container } = render(
      <TaskProgress progress={50} status="running" className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
