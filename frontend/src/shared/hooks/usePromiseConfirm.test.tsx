import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { usePromiseConfirm } from './usePromiseConfirm';

/**
 * Test wrapper component that combines hook and dialog rendering
 * Uses a ref to expose the confirm function after render
 */
function TestWrapper({
  confirmRef,
}: {
  confirmRef: React.MutableRefObject<((message: string, options?: { title?: string; variant?: string }) => Promise<boolean>) | null>;
}) {
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  // Expose confirm function to parent via ref
  confirmRef.current = confirm;

  return <ConfirmDialogComponent />;
}

describe('usePromiseConfirm', () => {
  describe('confirm', () => {
    it('should resolve with true on confirm', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      let confirmResult: boolean | undefined;

      // Start the confirm promise (don't await yet)
      const promise = confirmRef.current!('Are you sure?').then((res) => {
        confirmResult = res;
      });

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Are you sure?')).toBeDefined();
      });

      // Find and click confirm button
      const buttons = screen.getAllByRole('button');
      const confirmButton = buttons.find(btn => btn.textContent === '确认');

      await act(async () => {
        if (confirmButton) {
          fireEvent.click(confirmButton);
        }
      });

      // Wait for promise to resolve
      await promise;

      expect(confirmResult).toBe(true);
    });

    it('should resolve with false on cancel', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      let confirmResult: boolean | undefined;

      // Start the confirm promise (don't await yet)
      const promise = confirmRef.current!('Are you sure?').then((res) => {
        confirmResult = res;
      });

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Are you sure?')).toBeDefined();
      });

      // Find and click cancel button
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');

      await act(async () => {
        if (cancelButton) {
          fireEvent.click(cancelButton);
        }
      });

      // Wait for promise to resolve
      await promise;

      expect(confirmResult).toBe(false);
    });

    it('should use default title', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm with default title
      const promise = confirmRef.current!('Message');

      // Wait for dialog to appear with default title (in the h4 title element)
      await waitFor(() => {
        const titleElement = screen.getByRole('heading', { level: 4 });
        expect(titleElement).toBeDefined();
        expect(titleElement.textContent).toBe('确认'); // Default title
      });

      // Cleanup - click cancel to close
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });

    it('should use custom title', async () => {
      const confirmRef = { current: null as ((message: string, options?: { title?: string }) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm with custom title
      const promise = confirmRef.current!('Message', { title: 'Custom Title' });

      // Wait for dialog to appear with custom title
      await waitFor(() => {
        expect(screen.getByText('Custom Title')).toBeDefined();
      });

      // Cleanup - click cancel to close
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });

    it('should use default variant (danger)', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm
      const promise = confirmRef.current!('Message');

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Message')).toBeDefined();
      });

      // Cleanup - click cancel to close
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });

    it('should use custom variant', async () => {
      const confirmRef = { current: null as ((message: string, options?: { variant?: string }) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm with custom variant
      const promise = confirmRef.current!('Message', { variant: 'warning' });

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Message')).toBeDefined();
      });

      // Cleanup - click cancel to close
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });

    it('should handle multiple consecutive confirms', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      let confirmResult1: boolean | undefined;
      let confirmResult2: boolean | undefined;

      // Start first confirm
      const promise1 = confirmRef.current!('First?').then((res) => {
        confirmResult1 = res;
      });

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('First?')).toBeDefined();
      });

      // Find and click confirm button for first
      let buttons = screen.getAllByRole('button');
      let confirmButton = buttons.find(btn => btn.textContent === '确认');

      await act(async () => {
        if (confirmButton) {
          fireEvent.click(confirmButton);
        }
      });

      await promise1;

      // Start second confirm
      const promise2 = confirmRef.current!('Second?').then((res) => {
        confirmResult2 = res;
      });

      // Wait for dialog to appear again
      await waitFor(() => {
        expect(screen.getByText('Second?')).toBeDefined();
      });

      // Find and click confirm button for second
      buttons = screen.getAllByRole('button');
      confirmButton = buttons.find(btn => btn.textContent === '确认');

      await act(async () => {
        if (confirmButton) {
          fireEvent.click(confirmButton);
        }
      });

      await promise2;

      expect(confirmResult1).toBe(true);
      expect(confirmResult2).toBe(true);
    });
  });

  describe('ConfirmDialogComponent', () => {
    it('should render dialog component', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available (component is rendered)
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });
    });

    it('should pass correct props to dialog', async () => {
      const confirmRef = { current: null as ((message: string, options?: { title?: string; variant?: string }) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm with custom props
      const promise = confirmRef.current!('Test message', {
        title: 'Test Title',
        variant: 'info',
      });

      // Wait for dialog to appear with custom props
      await waitFor(() => {
        expect(screen.getByText('Test Title')).toBeDefined();
        expect(screen.getByText('Test message')).toBeDefined();
      });

      // Cleanup - click cancel to close
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });
  });

  describe('dialog state', () => {
    it('should open dialog on confirm call', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm
      const promise = confirmRef.current!('Message');

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Message')).toBeDefined();
      });

      // Cleanup
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');
      await act(async () => {
        if (cancelButton) fireEvent.click(cancelButton);
      });

      await promise;
    });

    it('should close dialog after confirm', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm
      const promise = confirmRef.current!('Message');

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Message')).toBeDefined();
      });

      // Find and click confirm button
      const buttons = screen.getAllByRole('button');
      const confirmButton = buttons.find(btn => btn.textContent === '确认');

      await act(async () => {
        if (confirmButton) {
          fireEvent.click(confirmButton);
        }
      });

      await promise;

      // Wait for dialog to close
      await waitFor(() => {
        expect(screen.queryByText('Message')).toBeNull();
      });
    });

    it('should close dialog after cancel', async () => {
      const confirmRef = { current: null as ((message: string) => Promise<boolean>) | null };

      render(<TestWrapper confirmRef={confirmRef} />);

      // Wait for confirm function to be available
      await waitFor(() => {
        expect(confirmRef.current).not.toBeNull();
      });

      // Call confirm
      const promise = confirmRef.current!('Message');

      // Wait for dialog to appear
      await waitFor(() => {
        expect(screen.getByText('Message')).toBeDefined();
      });

      // Find and click cancel button
      const buttons = screen.getAllByRole('button');
      const cancelButton = buttons.find(btn => btn.textContent === '取消');

      await act(async () => {
        if (cancelButton) {
          fireEvent.click(cancelButton);
        }
      });

      await promise;

      // Wait for dialog to close
      await waitFor(() => {
        expect(screen.queryByText('Message')).toBeNull();
      });
    });
  });
});
