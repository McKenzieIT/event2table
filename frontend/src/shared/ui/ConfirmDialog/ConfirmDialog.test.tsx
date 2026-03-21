/**
 * ConfirmDialog Component Tests
 * 测试确认对话框组件的所有功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConfirmDialog from './ConfirmDialog';

describe('ConfirmDialog Component', () => {
  const defaultProps = {
    open: true,
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
  };

  beforeEach(() => {
    // Reset document body style before each test
    document.body.style.overflow = '';
  });

  afterEach(() => {
    // Clean up document body style after each test
    document.body.style.overflow = '';
  });

  describe('Rendering', () => {
    it('should render when open is true', () => {
      render(<ConfirmDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Confirm Action')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
    });

    it('should not render when open is false', () => {
      render(<ConfirmDialog {...defaultProps} open={false} />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render default button text', () => {
      render(<ConfirmDialog {...defaultProps} />);

      expect(screen.getByRole('button', { name: '取消' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: '确认' })).toBeInTheDocument();
    });

    it('should render custom button text', () => {
      render(
        <ConfirmDialog
          {...defaultProps}
          confirmText="Delete"
          cancelText="Keep"
        />
      );

      expect(screen.getByRole('button', { name: 'Keep' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
    });

    it('should render with aria attributes', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'confirm-dialog-title');
      expect(dialog).toHaveAttribute('aria-describedby', 'confirm-dialog-message');
    });
  });

  describe('User Interactions', () => {
    it('should call onConfirm when confirm button is clicked', async () => {
      const onConfirm = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onConfirm={onConfirm} />);

      await user.click(screen.getByRole('button', { name: '确认' }));

      expect(onConfirm).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when cancel button is clicked', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);

      await user.click(screen.getByRole('button', { name: '取消' }));

      expect(onCancel).toHaveBeenCalledTimes(1);
    });

    it('should call onCancel when overlay is clicked', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);

      const overlay = screen.getByRole('presentation');
      await user.click(overlay);

      expect(onCancel).toHaveBeenCalledTimes(1);
    });

    it('should not call onCancel when dialog content is clicked', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);

      const dialog = screen.getByRole('dialog');
      await user.click(dialog);

      expect(onCancel).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard Interactions', () => {
    it('should call onCancel when Escape key is pressed', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);

      await user.keyboard('{Escape}');

      expect(onCancel).toHaveBeenCalledTimes(1);
    });

    it('should not call onCancel when dialog is closed', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} open={false} onCancel={onCancel} />);

      await user.keyboard('{Escape}');

      expect(onCancel).not.toHaveBeenCalled();
    });

    it('should handle multiple Escape key presses', async () => {
      const onCancel = vi.fn();
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);

      await user.keyboard('{Escape}');
      await user.keyboard('{Escape}');

      expect(onCancel).toHaveBeenCalledTimes(2);
    });
  });

  describe('Body Scroll Lock', () => {
    it('should lock body scroll when dialog opens', () => {
      const { rerender } = render(<ConfirmDialog {...defaultProps} open={false} />);

      expect(document.body.style.overflow).toBe('');

      rerender(<ConfirmDialog {...defaultProps} open={true} />);

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should unlock body scroll when dialog closes', () => {
      const { rerender } = render(<ConfirmDialog {...defaultProps} open={true} />);

      expect(document.body.style.overflow).toBe('hidden');

      rerender(<ConfirmDialog {...defaultProps} open={false} />);

      expect(document.body.style.overflow).toBe('');
    });

    it('should unlock body scroll on unmount', () => {
      const { unmount } = render(<ConfirmDialog {...defaultProps} open={true} />);

      expect(document.body.style.overflow).toBe('hidden');

      unmount();

      expect(document.body.style.overflow).toBe('');
    });

    it('should restore previous body scroll style', () => {
      document.body.style.overflow = 'auto';

      const { unmount } = render(<ConfirmDialog {...defaultProps} open={true} />);
      unmount();

      expect(document.body.style.overflow).toBe('auto');
    });
  });

  describe('Variants', () => {
    it('should render primary variant by default', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const confirmButton = screen.getByRole('button', { name: '确认' });
      expect(confirmButton).toHaveClass('cyber-button--primary');
    });

    it('should render danger variant', () => {
      render(<ConfirmDialog {...defaultProps} variant="danger" />);

      const confirmButton = screen.getByRole('button', { name: '确认' });
      expect(confirmButton).toHaveClass('cyber-button--danger');
    });

    it('should render warning variant', () => {
      render(<ConfirmDialog {...defaultProps} variant="warning" />);

      const confirmButton = screen.getByRole('button', { name: '确认' });
      expect(confirmButton).toHaveClass('cyber-button--warning');
    });

    it('should render info variant', () => {
      render(<ConfirmDialog {...defaultProps} variant="info" />);

      const confirmButton = screen.getByRole('button', { name: '确认' });
      expect(confirmButton).toHaveClass('cyber-button--info');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA roles', () => {
      render(<ConfirmDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByRole('presentation')).toBeInTheDocument();
    });

    it('should have aria-modal attribute', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
    });

    it('should link title and message with aria attributes', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-labelledby', 'confirm-dialog-title');
      expect(dialog).toHaveAttribute('aria-describedby', 'confirm-dialog-message');

      const title = screen.getByText('Confirm Action');
      expect(title.id).toBe('confirm-dialog-title');

      const message = screen.getByText('Are you sure you want to proceed?');
      expect(message.id).toBe('confirm-dialog-message');
    });

    it('should be focusable', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeVisible();
    });
  });

  describe('Event Handler Updates', () => {
    it('should use updated onCancel handler', async () => {
      const user = userEvent.setup();
      const onCancel1 = vi.fn();
      const onCancel2 = vi.fn();

      const { rerender } = render(
        <ConfirmDialog {...defaultProps} onCancel={onCancel1} />
      );

      await user.keyboard('{Escape}');
      expect(onCancel1).toHaveBeenCalledTimes(1);

      rerender(<ConfirmDialog {...defaultProps} onCancel={onCancel2} />);

      await user.keyboard('{Escape}');
      expect(onCancel2).toHaveBeenCalledTimes(1);
      expect(onCancel1).toHaveBeenCalledTimes(1);
    });

    it('should use updated onConfirm handler', async () => {
      const user = userEvent.setup();
      const onConfirm1 = vi.fn();
      const onConfirm2 = vi.fn();

      const { rerender } = render(
        <ConfirmDialog {...defaultProps} onConfirm={onConfirm1} />
      );

      await user.click(screen.getByRole('button', { name: '确认' }));
      expect(onConfirm1).toHaveBeenCalledTimes(1);

      rerender(<ConfirmDialog {...defaultProps} onConfirm={onConfirm2} />);

      await user.click(screen.getByRole('button', { name: '确认' }));
      expect(onConfirm2).toHaveBeenCalledTimes(1);
      expect(onConfirm1).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty title and message', () => {
      render(
        <ConfirmDialog
          {...defaultProps}
          title=""
          message=""
        />
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should handle very long title and message', () => {
      const longText = 'A'.repeat(1000);

      render(
        <ConfirmDialog
          {...defaultProps}
          title={longText}
          message={longText}
        />
      );

      expect(screen.getByText(longText)).toBeInTheDocument();
      expect(screen.getAllByText(longText)).toHaveLength(2);
    });

    it('should handle special characters in title and message', () => {
      const specialText = '<script>alert("test")</script>';

      render(
        <ConfirmDialog
          {...defaultProps}
          title={specialText}
          message={specialText}
        />
      );

      // React will escape the script tags
      expect(screen.getByText(specialText)).toBeInTheDocument();
    });

    it('should handle rapid open/close changes', () => {
      const { rerender } = render(<ConfirmDialog {...defaultProps} open={true} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();

      rerender(<ConfirmDialog {...defaultProps} open={false} />);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

      rerender(<ConfirmDialog {...defaultProps} open={true} />);
      expect(screen.getByRole('dialog')).toBeInTheDocument();

      rerender(<ConfirmDialog {...defaultProps} open={false} />);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  describe('Integration Tests', () => {
    it('should work in typical delete confirmation scenario', async () => {
      const user = userEvent.setup();
      const handleConfirm = vi.fn();
      const handleCancel = vi.fn();

      render(
        <ConfirmDialog
          open={true}
          title="Delete Item"
          message="Are you sure you want to delete this item? This action cannot be undone."
          confirmText="Delete"
          cancelText="Cancel"
          variant="danger"
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      );

      expect(screen.getByText('Delete Item')).toBeInTheDocument();
      expect(screen.getByText(/Are you sure/)).toBeInTheDocument();

      // User cancels
      await user.click(screen.getByRole('button', { name: 'Cancel' }));
      expect(handleCancel).toHaveBeenCalledTimes(1);
      expect(handleConfirm).not.toHaveBeenCalled();
    });

    it('should work in typical form confirmation scenario', async () => {
      const user = userEvent.setup();
      const handleConfirm = vi.fn();
      const handleCancel = vi.fn();

      render(
        <ConfirmDialog
          open={true}
          title="Submit Form"
          message="Do you want to submit the form with the current values?"
          confirmText="Submit"
          cancelText="Review"
          variant="primary"
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      );

      // User confirms
      await user.click(screen.getByRole('button', { name: 'Submit' }));
      expect(handleConfirm).toHaveBeenCalledTimes(1);
      expect(handleCancel).not.toHaveBeenCalled();
    });
  });
});
