/**
 * useUnifiedEscHandler单元测试 - 简化版
 */

import { renderHook, act } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useUnifiedEscHandler } from '../hooks/useUnifiedEscHandler';

describe('useUnifiedEscHandler', () => {
  let mockCallback: any;

  beforeEach(() => {
    mockCallback = vi.fn();
    document.body.innerHTML = '';
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('应该在ESC键按下时调用回调函数', () => {
    renderHook(() => useUnifiedEscHandler(mockCallback, { enabled: true }));

    act(() => {
      const escEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escEvent);
    });

    expect(mockCallback).toHaveBeenCalledTimes(1);
  });

  it('应该在INPUT元素上按ESC时不调用回调', () => {
    renderHook(() => useUnifiedEscHandler(mockCallback, {
      enabled: true,
      disableOnEditable: true
    }));

    const input = document.createElement('input');
    document.body.appendChild(input);
    input.focus();

    act(() => {
      const escEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      input.dispatchEvent(escEvent);
    });

    expect(mockCallback).not.toHaveBeenCalled();
    document.body.removeChild(input);
  });

  it('应该支持防抖', () => {
    vi.useFakeTimers();

    renderHook(() => useUnifiedEscHandler(mockCallback, {
      enabled: true,
      debounceMs: 200
    }));

    act(() => {
      const escEvent1 = new KeyboardEvent('keydown', { key: 'Escape' });
      const escEvent2 = new KeyboardEvent('keydown', { key: 'Escape' });
      document.dispatchEvent(escEvent1);
      document.dispatchEvent(escEvent2);
      vi.advanceTimersByTime(200);
    });

    expect(mockCallback).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});
