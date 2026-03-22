/**
 * Drawer Component Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Drawer } from '../Drawer';

describe('Drawer Component', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
    document.body.style.overflow = '';
  });

  afterEach(() => {
    document.body.style.overflow = '';
  });

  describe('Rendering', () => {
    it('should not render when closed', () => {
      render(
        <Drawer open={false} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(screen.queryByTestId('drawer')).not.toBeInTheDocument();
    });

    it('should render when open', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(screen.getByTestId('drawer')).toBeInTheDocument();
      expect(screen.getByTestId('drawer-overlay')).toBeInTheDocument();
      expect(screen.getByTestId('drawer-content')).toBeInTheDocument();
    });

    it('should render title when provided', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} title="Test Title">
          <div>Content</div>
        </Drawer>
      );

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByTestId('drawer-close-button')).toBeInTheDocument();
    });

    it('should not render title when not provided', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(screen.queryByTestId('drawer-close-button')).not.toBeInTheDocument();
    });

    it('should render children content', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Test Content</div>
        </Drawer>
      );

      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });
  });

  describe('Direction', () => {
    it('should render with right direction by default', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).toHaveAttribute('data-direction', 'right');
    });

    it('should render with left direction', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} direction="left">
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).toHaveAttribute('data-direction', 'left');
    });

    it('should render with right direction', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} direction="right">
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).toHaveAttribute('data-direction', 'right');
    });
  });

  describe('Close Behavior', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose} title="Title">
          <div>Content</div>
        </Drawer>
      );

      const closeButton = screen.getByTestId('drawer-close-button');
      await user.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when overlay is clicked', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      const overlay = screen.getByTestId('drawer-overlay');
      await user.click(overlay);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not call onClose when overlay is clicked but closeOnOverlayClick is false', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose} closeOnOverlayClick={false}>
          <div>Content</div>
        </Drawer>
      );

      const overlay = screen.getByTestId('drawer-overlay');
      await user.click(overlay);

      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('should call onClose when ESC key is pressed', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      await user.keyboard('{Escape}');

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not call onClose when ESC key is pressed but closeOnEscape is false', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose} closeOnEscape={false}>
          <div>Content</div>
        </Drawer>
      );

      await user.keyboard('{Escape}');

      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  describe('Overlay', () => {
    it('should show overlay by default', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(screen.getByTestId('drawer-overlay')).toBeInTheDocument();
    });

    it('should not show overlay when showOverlay is false', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} showOverlay={false}>
          <div>Content</div>
        </Drawer>
      );

      expect(screen.queryByTestId('drawer-overlay')).not.toBeInTheDocument();
    });
  });

  describe('Body Scroll Lock', () => {
    it('should disable body scroll when open', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should enable body scroll when closed', () => {
      const { rerender } = render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(document.body.style.overflow).toBe('hidden');

      rerender(
        <Drawer open={false} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(document.body.style.overflow).toBe('');
    });

    it('should restore body scroll on unmount', () => {
      const { unmount } = render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      expect(document.body.style.overflow).toBe('hidden');

      unmount();

      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('Focus Management', () => {
    it('should trap focus within drawer when enableFocusTrap is true', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose} title="Title">
          <button>Button 1</button>
          <button>Button 2</button>
        </Drawer>
      );

      const buttons = screen.getAllByRole('button');
      const closeButton = screen.getByTestId('drawer-close-button');
      const button1 = buttons.find((btn) => btn.textContent === 'Button 1');
      const button2 = buttons.find((btn) => btn.textContent === 'Button 2');

      // Wait for focus to be set (component uses setTimeout)
      await waitFor(() => {
        expect(closeButton).toHaveFocus();
      });

      // Tab to Button 1
      await user.tab();
      expect(button1).toHaveFocus();

      // Tab to Button 2
      await user.tab();
      expect(button2).toHaveFocus();

      // Tab should cycle back to close button
      await user.tab();
      expect(closeButton).toHaveFocus();
    });

    it('should not trap focus when enableFocusTrap is false', async () => {
      const user = userEvent.setup();
      render(
        <Drawer open={true} onClose={mockOnClose} enableFocusTrap={false}>
          <button>Button 1</button>
        </Drawer>
      );

      const button = screen.getByText('Button 1');
      
      // Focus should not be automatically trapped
      expect(button).not.toHaveFocus();
    });

    it('should restore focus to previous element on close', async () => {
      const buttonOutside = document.createElement('button');
      buttonOutside.textContent = 'Outside Button';
      document.body.appendChild(buttonOutside);
      buttonOutside.focus();

      const { rerender } = render(
        <Drawer open={true} onClose={mockOnClose} title="Title">
          <div>Content</div>
        </Drawer>
      );

      const closeButton = screen.getByTestId('drawer-close-button');
      
      // Wait for focus to be set
      await waitFor(() => {
        expect(closeButton).toHaveFocus();
      });

      rerender(
        <Drawer open={false} onClose={mockOnClose} title="Title">
          <div>Content</div>
        </Drawer>
      );

      expect(buttonOutside).toHaveFocus();

      document.body.removeChild(buttonOutside);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} title="Test Title">
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).toHaveAttribute('role', 'dialog');
      expect(drawer).toHaveAttribute('aria-modal', 'true');
      expect(drawer).toHaveAttribute('aria-labelledby', 'drawer-title');
    });

    it('should not have aria-labelledby when title is not provided', () => {
      render(
        <Drawer open={true} onClose={mockOnClose}>
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).not.toHaveAttribute('aria-labelledby');
    });

    it('should have aria-label on close button', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} title="Title">
          <div>Content</div>
        </Drawer>
      );

      const closeButton = screen.getByTestId('drawer-close-button');
      expect(closeButton).toHaveAttribute('aria-label', '关闭');
    });
  });

  describe('Custom Styling', () => {
    it('should apply custom className', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} className="custom-class">
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer).toHaveClass('custom-class');
    });

    it('should apply custom z-index', () => {
      render(
        <Drawer open={true} onClose={mockOnClose} zIndex={2000}>
          <div>Content</div>
        </Drawer>
      );

      const drawer = screen.getByTestId('drawer');
      expect(drawer.style.zIndex).toBe('2001');
    });
  });
});
