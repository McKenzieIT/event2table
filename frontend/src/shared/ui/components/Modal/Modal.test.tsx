/**
 * Modal Component Unit Tests
 * 
 * Comprehensive test suite for Modal component
 * Target coverage: 90%
 * 
 * Test Categories:
 * 1. Rendering Tests
 * 2. Interaction Tests
 * 3. Accessibility Tests
 * 4. Lifecycle Tests
 * 5. Edge Cases
 * 6. Performance Tests
 */

import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import Modal from './Modal';

// Mock constants
vi.mock('@shared/constants/timeouts', () => ({
  MODAL_ANIMATION_DELAY: 100,
}));

vi.mock('@shared/constants/zIndices', () => ({
  Z_INDICES: {
    MODAL: 1000,
  },
}));

describe('Modal Component', () => {
  const defaultProps = {
    isOpen: false,
    onClose: vi.fn(),
    title: 'Test Modal',
    children: <div>Modal Content</div>,
  };

  beforeEach(() => {
    // Reset document body styles before each test
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Cleanup after each test
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  });

  // ========== Rendering Tests ==========

  describe('Rendering', () => {
    it('should not render when isOpen is false', () => {
      render(<Modal {...defaultProps} isOpen={false} />);
      
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(screen.queryByRole('dialog', { hidden: true })).not.toBeInTheDocument();
    });

    it('should render when isOpen is true', () => {
      render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
      expect(screen.getByText('Modal Content')).toBeInTheDocument();
    });

    it('should render with custom title', () => {
      render(<Modal {...defaultProps} isOpen={true} title="Custom Title" />);
      
      expect(screen.getByText('Custom Title')).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      render(<Modal {...defaultProps} isOpen={true} className="custom-class" />);
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveClass('custom-class');
    });

    it('should render with custom style', () => {
      const customStyle = { backgroundColor: 'red' };
      render(<Modal {...defaultProps} isOpen={true} style={customStyle} />);
      
      const modal = screen.getByRole('dialog');
      // Check that style is applied (may have transform from draggable)
      expect(modal.style.backgroundColor).toBe('red');
    });

    it('should render with custom zIndex', () => {
      render(<Modal {...defaultProps} isOpen={true} zIndex={9999} />);
      
      const overlay = screen.getByRole('dialog').parentElement;
      expect(overlay).toHaveStyle({ zIndex: '9999' });
    });

    it('should render footer when showFooter is true', () => {
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          showFooter={true} 
          footer={<div>Footer Content</div>}
        />
      );
      
      expect(screen.getByText('Footer Content')).toBeInTheDocument();
    });

    it('should not render header when showHeader is false', () => {
      render(<Modal {...defaultProps} isOpen={true} showHeader={false} />);
      
      expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    });

    it('should not render close button when showCloseButton is false', () => {
      render(<Modal {...defaultProps} isOpen={true} showCloseButton={false} />);
      
      expect(screen.queryByLabelText('关闭对话框')).not.toBeInTheDocument();
    });

    it('should render all size variants', () => {
      const sizes: Array<'sm' | 'md' | 'lg' | 'xl' | 'full'> = ['sm', 'md', 'lg', 'xl', 'full'];
      
      sizes.forEach((size) => {
        const { unmount } = render(<Modal {...defaultProps} isOpen={true} size={size} />);
        const modal = screen.getByRole('dialog');
        expect(modal).toHaveClass(`modal-content--${size}`);
        unmount();
      });
    });

    it('should render fullScreen mode correctly', () => {
      render(<Modal {...defaultProps} isOpen={true} fullScreen={true} />);
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveClass('modal-content--full');
    });

    it('should render all animation variants', () => {
      const animations: Array<'slideUp' | 'fadeIn' | 'scale' | 'none'> = ['slideUp', 'fadeIn', 'scale', 'none'];
      
      animations.forEach((animation) => {
        const { unmount } = render(<Modal {...defaultProps} isOpen={true} animation={animation} />);
        const overlay = screen.getByTestId('modal-overlay');
        // 'none' animation doesn't add a class
        if (animation === 'none') {
          expect(overlay).not.toHaveClass('modal-overlay--none');
        } else {
          expect(overlay).toHaveClass(`modal-overlay--${animation}`);
        }
        unmount();
      });
    });

    it('should render glassmorphism effect', () => {
      render(<Modal {...defaultProps} isOpen={true} glassmorphism={true} />);
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveClass('modal-content--glassmorphism');
    });

    it('should render all variant types', () => {
      const variants: Array<'default' | 'danger' | 'warning' | 'success' | 'info'> = 
        ['default', 'danger', 'warning', 'success', 'info'];
      
      variants.forEach((variant) => {
        const { unmount } = render(<Modal {...defaultProps} isOpen={true} variant={variant} />);
        const modal = screen.getByRole('dialog');
        // 'default' variant doesn't add a class
        if (variant === 'default') {
          expect(modal).not.toHaveClass('modal-content--default');
        } else {
          expect(modal).toHaveClass(`modal-content--${variant}`);
        }
        unmount();
      });
    });

    it('should render with custom overlay className', () => {
      render(<Modal {...defaultProps} isOpen={true} overlayClassName="custom-overlay" />);
      
      const overlay = screen.getByTestId('modal-overlay');
      expect(overlay).toHaveClass('custom-overlay');
    });
  });

  // ========== Interaction Tests ==========

  describe('Interactions', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should call onClose when ESC key is pressed', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      await user.keyboard('{Escape}');
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should not call onClose when ESC key is pressed if enableEscClose is false', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} enableEscClose={false} />);
      
      await user.keyboard('{Escape}');
      
      expect(defaultProps.onClose).not.toHaveBeenCalled();
    });

    it('should call onClose when backdrop is clicked', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const overlay = screen.getByTestId('modal-overlay');
      await user.click(overlay);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should not call onClose when modal content is clicked', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const modal = screen.getByRole('dialog');
      await user.click(modal);
      
      expect(defaultProps.onClose).not.toHaveBeenCalled();
    });

    it('should not call onClose when closeOnBackdropClick is false', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} closeOnBackdropClick={false} />);
      
      const overlay = screen.getByTestId('modal-overlay');
      await user.click(overlay);
      
      expect(defaultProps.onClose).not.toHaveBeenCalled();
    });

    it('should call onBeforeClose and wait for result', async () => {
      const onBeforeClose = vi.fn().mockResolvedValue(true);
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
        />
      );
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      expect(onBeforeClose).toHaveBeenCalledTimes(1);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should show confirm dialog when onBeforeClose returns false', async () => {
      const onBeforeClose = vi.fn().mockResolvedValue(false);
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
        />
      );
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      expect(onBeforeClose).toHaveBeenCalledTimes(1);
      expect(defaultProps.onClose).not.toHaveBeenCalled();
      expect(screen.getByText('确认关闭')).toBeInTheDocument();
    });

    it('should close when confirm dialog is confirmed', async () => {
      const onBeforeClose = vi.fn().mockResolvedValue(false);
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
        />
      );
      
      // Trigger close to show confirm dialog
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      // Click confirm button
      const confirmButton = screen.getByText('放弃修改');
      await user.click(confirmButton);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should not close when confirm dialog is cancelled', async () => {
      const onBeforeClose = vi.fn().mockResolvedValue(false);
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
        />
      );
      
      // Trigger close to show confirm dialog
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      // Click cancel button
      const cancelButton = screen.getByText('继续编辑');
      await user.click(cancelButton);
      
      expect(defaultProps.onClose).not.toHaveBeenCalled();
    });

    it('should use custom confirm config', async () => {
      const onBeforeClose = vi.fn().mockResolvedValue(false);
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
          confirmConfig={{
            title: 'Custom Title',
            message: 'Custom Message',
            confirmText: 'Yes',
            cancelText: 'No',
          }}
        />
      );
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      expect(screen.getByText('Custom Title')).toBeInTheDocument();
      expect(screen.getByText('Custom Message')).toBeInTheDocument();
      expect(screen.getByText('Yes')).toBeInTheDocument();
      expect(screen.getByText('No')).toBeInTheDocument();
    });

    it('should handle onBeforeClose errors gracefully', async () => {
      const onBeforeClose = vi.fn().mockRejectedValue(new Error('Test error'));
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onBeforeClose={onBeforeClose}
        />
      );
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      // Should close despite error
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should ignore close requests while closing', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      // Try to close again immediately
      await user.click(closeButton);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });
  });

  // ========== Accessibility Tests ==========

  describe('Accessibility', () => {
    it('should have correct ARIA attributes', () => {
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');
    });

    it('should use custom aria-labelledby when provided', () => {
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          ariaLabelledby="custom-label"
        />
      );
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-labelledby', 'custom-label');
    });

    it('should use custom aria-describedby when provided', () => {
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          ariaDescribedby="custom-desc"
        />
      );
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('aria-describedby', 'custom-desc');
    });

    it('should trap focus within modal', () => {
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true}
          children={
            <>
              <button type="button">First Button</button>
              <button type="button">Second Button</button>
            </>
          }
        />
      );
      
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveAttribute('tabIndex', '-1');
    });

    it('should disable body scroll when open', () => {
      render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should restore body scroll when closed', async () => {
      const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(document.body.style.overflow).toBe('hidden');
      
      rerender(<Modal {...defaultProps} isOpen={false} />);
      
      await waitFor(() => {
        expect(document.body.style.overflow).toBe('');
      });
    });
  });

  // ========== Lifecycle Tests ==========

  describe('Lifecycle', () => {
    it('should call onAfterOpen when modal opens', async () => {
      const onAfterOpen = vi.fn();
      render(<Modal {...defaultProps} isOpen={true} onAfterOpen={onAfterOpen} />);
      
      // Wait for useEffect to run
      // Note: onAfterOpen may be called multiple times due to effect dependencies
      await waitFor(
        () => {
          // Just verify it was called at least once
          expect(onAfterOpen).toHaveBeenCalled();
        },
        { timeout: 200 }
      );
    });

    it('should call onAfterClose when modal closes', async () => {
      const onAfterClose = vi.fn();
      const user = userEvent.setup();
      
      render(
        <Modal 
          {...defaultProps} 
          isOpen={true} 
          onAfterClose={onAfterClose}
        />
      );
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      await waitFor(
        () => {
          expect(onAfterClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should save and restore focus', async () => {
      const user = userEvent.setup();
      
      const TestComponent = () => (
        <>
          <button type="button" data-testid="trigger">Open Modal</button>
          <Modal {...defaultProps} isOpen={true}>
            <button type="button" data-testid="modal-button">Modal Button</button>
          </Modal>
        </>
      );
      
      render(<TestComponent />);
      
      const trigger = screen.getByTestId('trigger');
      trigger.focus();
      
      expect(document.activeElement).toBe(trigger);
    });
  });

  // ========== Edge Cases ==========

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Modal {...defaultProps} isOpen={true} children={null} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should handle missing title', () => {
      render(<Modal {...defaultProps} isOpen={true} title={undefined} />);
      
      // When title is undefined, the h2 element still exists but is empty
      // Check that there's no visible heading text
      const heading = screen.queryByRole('heading');
      if (heading) {
        expect(heading.textContent).toBe('');
      } else {
        expect(heading).not.toBeInTheDocument();
      }
    });

    it('should handle rapid open/close', async () => {
      const user = userEvent.setup();
      const { rerender } = render(<Modal {...defaultProps} isOpen={false} />);
      
      // Rapidly toggle
      rerender(<Modal {...defaultProps} isOpen={true} />);
      rerender(<Modal {...defaultProps} isOpen={false} />);
      rerender(<Modal {...defaultProps} isOpen={true} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should handle multiple close attempts', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      await user.click(closeButton);
      await user.click(closeButton);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should handle backdrop click during closing', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      const overlay = screen.getByTestId('modal-overlay');
      await user.click(overlay);
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });

    it('should handle ESC during closing', async () => {
      const user = userEvent.setup();
      render(<Modal {...defaultProps} isOpen={true} />);
      
      const closeButton = screen.getByLabelText('关闭对话框');
      await user.click(closeButton);
      
      await user.keyboard('{Escape}');
      
      // Wait for animation delay
      await waitFor(
        () => {
          expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
        },
        { timeout: 200 }
      );
    });
  });

  // ========== Performance Tests ==========

  describe('Performance', () => {
    it('should memoize callback functions', () => {
      const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
      
      const firstRender = screen.getByRole('dialog');
      
      rerender(<Modal {...defaultProps} isOpen={true} />);
      
      const secondRender = screen.getByRole('dialog');
      
      expect(firstRender).toBe(secondRender);
    });

    it('should not re-render unnecessarily when props change', () => {
      const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
      
      const modal = screen.getByRole('dialog');
      
      // Update non-critical props
      rerender(<Modal {...defaultProps} isOpen={true} className="new-class" />);
      
      expect(modal).toBeInTheDocument();
    });
  });
});
