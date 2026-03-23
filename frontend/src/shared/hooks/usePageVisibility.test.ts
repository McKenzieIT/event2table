import { renderHook, act } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { usePageVisibility, usePollingInterval, useSmartPolling } from './usePageVisibility';

describe('usePageVisibility', () => {
  beforeEach(() => {
    vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('usePageVisibility', () => {
    it('should return true when page is visible', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
      const { result } = renderHook(() => usePageVisibility());
      expect(result.current).toBe(true);
    });

    it('should return false when page is hidden', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
      const { result } = renderHook(() => usePageVisibility());
      expect(result.current).toBe(false);
    });

    it('should update on visibility change', () => {
      const { result } = renderHook(() => usePageVisibility());
      
      expect(result.current).toBe(true);
      
      act(() => {
        vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
        const event = new Event('visibilitychange');
        document.dispatchEvent(event);
      });
      
      expect(result.current).toBe(false);
    });

    it('should cleanup event listener on unmount', () => {
      const removeSpy = vi.spyOn(document, 'removeEventListener');
      const { unmount } = renderHook(() => usePageVisibility());
      
      unmount();
      
      expect(removeSpy).toHaveBeenCalledWith(
        'visibilitychange',
        expect.any(Function)
      );
    });
  });

  describe('usePollingInterval', () => {
    it('should return visible interval when page is visible', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
      const { result } = renderHook(() => usePollingInterval(10000, 60000));
      expect(result.current).toBe(10000);
    });

    it('should return hidden interval when page is hidden', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
      const { result } = renderHook(() => usePollingInterval(10000, 60000));
      expect(result.current).toBe(60000);
    });

    it('should use default intervals', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
      const { result } = renderHook(() => usePollingInterval());
      expect(result.current).toBe(10000);
    });

    it('should update interval on visibility change', () => {
      const { result } = renderHook(() => usePollingInterval(10000, 60000));
      
      expect(result.current).toBe(10000);
      
      act(() => {
        vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
        const event = new Event('visibilitychange');
        document.dispatchEvent(event);
      });
      
      expect(result.current).toBe(60000);
    });
  });

  describe('useSmartPolling', () => {
    it('should return live status when page is visible', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
      const { result } = renderHook(() => useSmartPolling(10000, 5000));
      
      expect(result.current.status).toBe('live');
      expect(result.current.isVisible).toBe(true);
      expect(result.current.pollingInterval).toBe(10000);
    });

    it('should return paused status when page is hidden', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
      const { result } = renderHook(() => useSmartPolling(10000, 5000));
      
      expect(result.current.status).toBe('paused');
      expect(result.current.isVisible).toBe(false);
      expect(result.current.pollingInterval).toBe(60000);
    });

    it('should use 6x interval when hidden', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
      const { result } = renderHook(() => useSmartPolling(5000, 3000));
      
      expect(result.current.pollingInterval).toBe(30000);
    });

    it('should respect minimum interval', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
      // Use baseInterval=500 so that 500*6=3000 < minInterval=5000
      // This tests that Math.max() correctly returns the minimum
      const { result } = renderHook(() => useSmartPolling(500, 5000));

      expect(result.current.pollingInterval).toBe(5000);
    });

    it('should update status on visibility change', () => {
      const { result } = renderHook(() => useSmartPolling(10000, 5000));
      
      expect(result.current.status).toBe('live');
      
      act(() => {
        vi.spyOn(document, 'hidden', 'get').mockReturnValue(true);
        const event = new Event('visibilitychange');
        document.dispatchEvent(event);
      });
      
      expect(result.current.status).toBe('paused');
    });

    it('should use default intervals', () => {
      vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
      const { result } = renderHook(() => useSmartPolling());
      
      expect(result.current.pollingInterval).toBe(10000);
      expect(result.current.status).toBe('live');
    });
  });
});
