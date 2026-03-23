/**
 * useFlowLoad Hook Tests
 *
 * Tests for the useFlowLoad React Query hook
 */

import { describe, test, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@test/test-utils';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useFlowLoad } from '../useFlowLoad';
import type { SavedFlow } from '../../types';

// Mock fetch
global.fetch = vi.fn();

// Mock queryKeys
vi.mock('../../api/queryKeys', () => ({
  queryKeys: {
    flows: {
      detail: (flowId: number) => ['flows', 'detail', flowId],
    },
  },
}));

describe('useFlowLoad', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  const createWrapper = () => {
    return ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  const mockFlowData: SavedFlow = {
    id: 1,
    game_id: 10000147,
    name: 'Test Flow',
    flow_data: {
      nodes: [
        {
          id: 'node-1',
          type: 'event',
          x: 100,
          y: 100,
          data: { label: 'Event Node' },
        },
      ],
      edges: [],
    },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  describe('successful flow loading', () => {
    test('should load flow data successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: mockFlowData,
        }),
      });

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockFlowData);
      expect(result.current.error).toBeNull();
      expect(global.fetch).toHaveBeenCalledWith('/api/flows/1');
    });

    test('should cache flow data by flow ID', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: mockFlowData,
        }),
      });

      const { result, rerender } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Re-render with same flow ID - should use cache
      rerender();

      await waitFor(() => {
        expect(result.current.data).toEqual(mockFlowData);
      });

      // Fetch should still only be called once (cached)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('error handling', () => {
    test('should handle API error response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: 'Flow not found',
        }),
      });

      const { result } = renderHook(() => useFlowLoad(999), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Flow not found');
      expect(result.current.data).toBeUndefined();
    });

    test('should handle API failure response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: false,
          error: 'Server error',
        }),
      });

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Server error');
    });

    test('should handle network error', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Network error');
    });

    test('should handle missing error in response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Failed to fetch flow');
    });
  });

  describe('query disabling', () => {
    test('should not fetch when flowId is undefined', () => {
      const { result } = renderHook(() => useFlowLoad(undefined), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isFetching).toBe(false);
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test('should not fetch when flowId is null', () => {
      const { result } = renderHook(() => useFlowLoad(null), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isFetching).toBe(false);
      expect(global.fetch).not.toHaveBeenCalled();
    });

    test('should not fetch when flowId is 0', () => {
      const { result } = renderHook(() => useFlowLoad(0), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isFetching).toBe(false);
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('loading states', () => {
    test('should show loading state while fetching', async () => {
      let resolveFetch: (value: any) => void;
      const fetchPromise = new Promise((resolve) => {
        resolveFetch = resolve;
      });

      (global.fetch as any).mockReturnValueOnce(fetchPromise);

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.isFetching).toBe(true);

      resolveFetch!({
        ok: true,
        json: async () => ({
          success: true,
          data: mockFlowData,
        }),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe('refetching', () => {
    test('should support manual refetch', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: mockFlowData,
        }),
      });

      const { result } = renderHook(() => useFlowLoad(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Refetch
      await result.current.refetch();

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
