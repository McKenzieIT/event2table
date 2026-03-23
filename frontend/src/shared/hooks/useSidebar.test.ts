import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useSidebar } from './useSidebar';

describe('useSidebar', () => {
  beforeEach(() => {
    // Reset localStorage mock calls
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useSidebar());

      expect(result.current.collapsed).toBe(false);
      expect(result.current.groupStates).toEqual({});
    });

    it('should load state from localStorage', async () => {
      const savedState = { collapsed: true, groupStates: { group1: true } };

      // Mock getItem to return saved state
      vi.mocked(localStorage.getItem).mockImplementation((key: string) => {
        if (key === 'sidebarCollapsed') return JSON.stringify(savedState.collapsed);
        if (key === 'sidebarGroupStates') return JSON.stringify(savedState.groupStates);
        return null;
      });

      const { result } = renderHook(() => useSidebar());

      // Wait for useEffect to complete loading from localStorage
      await waitFor(() => {
        expect(result.current.collapsed).toBe(true);
      });
      expect(result.current.groupStates).toEqual({ group1: true });
    });
  });

  describe('toggleCollapsed', () => {
    it('should toggle collapsed state', () => {
      const { result } = renderHook(() => useSidebar());

      act(() => {
        result.current.toggleCollapsed();
      });

      expect(result.current.collapsed).toBe(true);

      act(() => {
        result.current.toggleCollapsed();
      });

      expect(result.current.collapsed).toBe(false);
    });

    it('should save to localStorage', () => {
      const { result } = renderHook(() => useSidebar());

      act(() => {
        result.current.toggleCollapsed();
      });

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'sidebarCollapsed',
        JSON.stringify(true)
      );
    });

    it('should dispatch custom event', () => {
      const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
      const { result } = renderHook(() => useSidebar());

      act(() => {
        result.current.toggleCollapsed();
      });

      expect(dispatchSpy).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'sidebarToggled' })
      );
    });
  });

  describe('toggleGroup', () => {
    it('should toggle group state', () => {
      const { result } = renderHook(() => useSidebar());

      act(() => {
        result.current.toggleGroup('group1');
      });

      expect(result.current.groupStates.group1).toBe(true);

      act(() => {
        result.current.toggleGroup('group1');
      });

      expect(result.current.groupStates.group1).toBe(false);
    });

    it('should handle multiple groups', () => {
      const { result } = renderHook(() => useSidebar());

      act(() => {
        result.current.toggleGroup('group1');
        result.current.toggleGroup('group2');
      });

      expect(result.current.groupStates.group1).toBe(true);
      expect(result.current.groupStates.group2).toBe(true);
    });
  });

  describe('expandAllGroups', () => {
    it('should expand all groups', () => {
      const { result } = renderHook(() => useSidebar());
      const groupIds = ['group1', 'group2', 'group3'];

      act(() => {
        result.current.expandAllGroups(groupIds);
      });

      expect(result.current.groupStates.group1).toBe(true);
      expect(result.current.groupStates.group2).toBe(true);
      expect(result.current.groupStates.group3).toBe(true);
    });

    it('should save to localStorage', () => {
      const { result } = renderHook(() => useSidebar());
      const groupIds = ['group1', 'group2'];

      act(() => {
        result.current.expandAllGroups(groupIds);
      });

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'sidebarGroupStates',
        JSON.stringify({ group1: true, group2: true })
      );
    });
  });

  describe('collapseAllGroups', () => {
    it('should collapse all groups', () => {
      const { result } = renderHook(() => useSidebar());
      const groupIds = ['group1', 'group2', 'group3'];

      act(() => {
        result.current.expandAllGroups(groupIds);
        result.current.collapseAllGroups(groupIds);
      });

      expect(result.current.groupStates.group1).toBe(false);
      expect(result.current.groupStates.group2).toBe(false);
      expect(result.current.groupStates.group3).toBe(false);
    });

    it('should save to localStorage', () => {
      const { result } = renderHook(() => useSidebar());
      const groupIds = ['group1', 'group2'];

      act(() => {
        result.current.collapseAllGroups(groupIds);
      });

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'sidebarGroupStates',
        JSON.stringify({ group1: false, group2: false })
      );
    });
  });

  describe('localStorage error handling', () => {
    it('should handle localStorage errors gracefully', () => {
      vi.mocked(localStorage.setItem).mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      const { result } = renderHook(() => useSidebar());

      expect(() => {
        act(() => {
          result.current.toggleCollapsed();
        });
      }).not.toThrow();
    });

    it('should handle localStorage get errors gracefully', () => {
      vi.mocked(localStorage.getItem).mockImplementation(() => {
        throw new Error('Storage access denied');
      });

      expect(() => {
        renderHook(() => useSidebar());
      }).not.toThrow();
    });
  });
});
