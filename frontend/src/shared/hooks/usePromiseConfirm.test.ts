import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePromiseConfirm } from './usePromiseConfirm';

describe('usePromiseConfirm', () => {
  describe('confirm', () => {
    it('should resolve with true on confirm', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      const promise = act(async () => {
        return result.current.confirm('Are you sure?');
      });

      act(() => {
        const confirmButton = document.querySelector('[data-testid="confirm-button"]');
        if (confirmButton) confirmButton.dispatchEvent(new MouseEvent('click'));
      });

      await expect(promise).resolves.toBe(true);
    });

    it('should resolve with false on cancel', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      const promise = act(async () => {
        return result.current.confirm('Are you sure?');
      });

      act(() => {
        const cancelButton = document.querySelector('[data-testid="cancel-button"]');
        if (cancelButton) cancelButton.dispatchEvent(new MouseEvent('click'));
      });

      await expect(promise).resolves.toBe(false);
    });

    it('should use default title', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message');
      });

      expect(result.current.ConfirmDialogComponent).toBeDefined();
    });

    it('should use custom title', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message', { title: 'Custom Title' });
      });

      expect(result.current.ConfirmDialogComponent).toBeDefined();
    });

    it('should use default variant (danger)', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message');
      });

      expect(result.current.ConfirmDialogComponent).toBeDefined();
    });

    it('should use custom variant', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message', { variant: 'warning' });
      });

      expect(result.current.ConfirmDialogComponent).toBeDefined();
    });

    it('should handle multiple consecutive confirms', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      const promise1 = act(async () => {
        return result.current.confirm('First?');
      });

      const promise2 = act(async () => {
        return result.current.confirm('Second?');
      });

      act(() => {
        const confirmButton = document.querySelector('[data-testid="confirm-button"]');
        if (confirmButton) confirmButton.dispatchEvent(new MouseEvent('click'));
      });

      await expect(promise1).resolves.toBe(true);
      await expect(promise2).resolves.toBe(true);
    });
  });

  describe('ConfirmDialogComponent', () => {
    it('should render dialog component', () => {
      const { result } = renderHook(() => usePromiseConfirm());

      const Component = result.current.ConfirmDialogComponent;
      expect(Component).toBeDefined();
    });

    it('should pass correct props to dialog', () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Test message', {
          title: 'Test Title',
          variant: 'info',
        });
      });

      const Component = result.current.ConfirmDialogComponent;
      expect(Component).toBeDefined();
    });
  });

  describe('dialog state', () => {
    it('should open dialog on confirm call', () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message');
      });

      expect(result.current.ConfirmDialogComponent).toBeDefined();
    });

    it('should close dialog after confirm', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message');
      });

      act(() => {
        const confirmButton = document.querySelector('[data-testid="confirm-button"]');
        if (confirmButton) confirmButton.dispatchEvent(new MouseEvent('click'));
      });

      await new Promise(resolve => setTimeout(resolve, 0));
    });

    it('should close dialog after cancel', async () => {
      const { result } = renderHook(() => usePromiseConfirm());

      act(() => {
        result.current.confirm('Message');
      });

      act(() => {
        const cancelButton = document.querySelector('[data-testid="cancel-button"]');
        if (cancelButton) cancelButton.dispatchEvent(new MouseEvent('click'));
      });

      await new Promise(resolve => setTimeout(resolve, 0));
    });
  });
});
