import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@test/test-utils';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('basic functionality', () => {
    it('should return initial value immediately', () => {
      const { result } = renderHook(() => useDebounce('initial', 300));
      expect(result.current).toBe('initial');
    });

    it('should debounce value changes', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: 'updated', delay: 300 });
      
      expect(result.current).toBe('initial');
      
      act(() => {
        vi.advanceTimersByTime(299);
      });
      
      expect(result.current).toBe('initial');
      
      act(() => {
        vi.advanceTimersByTime(1);
      });
      
      expect(result.current).toBe('updated');
    });

    it('should use default delay of 300ms', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value),
        { initialProps: { value: 'initial' } }
      );

      rerender({ value: 'updated' });
      
      expect(result.current).toBe('initial');
      
      act(() => {
        vi.advanceTimersByTime(300);
      });
      
      expect(result.current).toBe('updated');
    });
  });

  describe('rapid changes', () => {
    it('should only update after delay from last change', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: 'change1', delay: 300 });
      act(() => {
        vi.advanceTimersByTime(100);
      });
      
      rerender({ value: 'change2', delay: 300 });
      act(() => {
        vi.advanceTimersByTime(100);
      });
      
      rerender({ value: 'change3', delay: 300 });
      
      expect(result.current).toBe('initial');
      
      act(() => {
        vi.advanceTimersByTime(300);
      });
      
      expect(result.current).toBe('change3');
    });

    it('should reset timer on each change', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: 'change1', delay: 300 });
      
      act(() => {
        vi.advanceTimersByTime(200);
      });
      
      rerender({ value: 'change2', delay: 300 });
      
      act(() => {
        vi.advanceTimersByTime(200);
      });
      
      expect(result.current).toBe('initial');
      
      act(() => {
        vi.advanceTimersByTime(100);
      });
      
      expect(result.current).toBe('change2');
    });
  });

  describe('cleanup', () => {
    it('should cleanup timer on unmount', () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
      
      const { unmount } = renderHook(() => useDebounce('test', 300));
      
      unmount();
      
      expect(clearTimeoutSpy).toHaveBeenCalled();
    });

    it('should cleanup timer on value change', () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
      const { rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: 'updated', delay: 300 });
      
      expect(clearTimeoutSpy).toHaveBeenCalled();
    });
  });

  describe('different value types', () => {
    it('should work with numbers', () => {
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value),
        { initialProps: { value: 0 } }
      );

      rerender({ value: 42 });
      
      act(() => {
        vi.advanceTimersByTime(300);
      });
      
      expect(result.current).toBe(42);
    });

    it('should work with objects', () => {
      const obj1 = { id: 1, name: 'test' };
      const obj2 = { id: 2, name: 'updated' };
      
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value),
        { initialProps: { value: obj1 } }
      );

      rerender({ value: obj2 });
      
      act(() => {
        vi.advanceTimersByTime(300);
      });
      
      expect(result.current).toBe(obj2);
    });

    it('should work with arrays', () => {
      const arr1 = [1, 2, 3];
      const arr2 = [4, 5, 6];
      
      const { result, rerender } = renderHook(
        ({ value }) => useDebounce(value),
        { initialProps: { value: arr1 } }
      );

      rerender({ value: arr2 });
      
      act(() => {
        vi.advanceTimersByTime(300);
      });
      
      expect(result.current).toBe(arr2);
    });
  });
});
