/**
 * EmptyState Component Tests
 * 测试空状态组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EmptyState } from './EmptyState';

describe('EmptyState Component', () => {
  describe('Rendering', () => {
    it('should render with title', () => {
      render(<EmptyState title="No items found" />);
      expect(screen.getByText('No items found')).toBeInTheDocument();
    });

    it('should render with description', () => {
      render(<EmptyState title="No items" description="Create your first item to get started" />);
      expect(screen.getByText('Create your first item to get started')).toBeInTheDocument();
    });

    it('should render with icon', () => {
      const TestIcon = () => <svg data-testid="empty-icon" />;
      render(<EmptyState title="Empty" icon={<TestIcon />} />);
      expect(screen.getByTestId('empty-icon')).toBeInTheDocument();
    });

    it('should render with action button', () => {
      const handleClick = vi.fn();
      render(
        <EmptyState
          title="Empty"
          action={{ label: 'Create Item', onClick: handleClick }}
        />
      );
      expect(screen.getByText('Create Item')).toBeInTheDocument();
    });

    it('should not render description when not provided', () => {
      render(<EmptyState title="Empty" />);
      expect(screen.queryByText('No description')).not.toBeInTheDocument();
    });

    it('should not render action button when not provided', () => {
      render(<EmptyState title="Empty" />);
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });

  describe('Action Button', () => {
    it('should call onClick when action button is clicked', async () => {
      const handleClick = vi.fn();
      render(
        <EmptyState
          title="Empty"
          action={{ label: 'Create', onClick: handleClick }}
        />
      );

      await userEvent.click(screen.getByText('Create'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should render action button with correct label', () => {
      render(
        <EmptyState
          title="Empty"
          action={{ label: 'Add New Item', onClick: () => {} }}
        />
      );
      expect(screen.getByText('Add New Item')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<EmptyState title="Empty" className="custom-empty" />);
      expect(container.querySelector('.custom-empty')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be accessible', () => {
      render(<EmptyState title="No items found" />);
      expect(screen.getByText('No items found')).toBeInTheDocument();
    });
  });

  describe('Icon Rendering', () => {
    it('should render icon container', () => {
      const { container } = render(
        <EmptyState title="Empty" icon={<div>Icon</div>} />
      );
      expect(container.querySelector('.empty-state__icon')).toBeInTheDocument();
    });

    it('should not render icon container when icon is not provided', () => {
      const { container } = render(<EmptyState title="Empty" />);
      expect(container.querySelector('.empty-state__icon')).not.toBeInTheDocument();
    });
  });
});
