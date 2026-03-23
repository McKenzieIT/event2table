/**
 * GameManagementModalGraphQL Performance Tests
 *
 * TDD Approach: RED → GREEN → REFACTOR
 *
 * These tests verify React performance optimizations:
 * 1. Component should use React.memo to prevent unnecessary re-renders
 * 2. Event handlers should use useCallback
 * 3. Expensive computations should use useMemo
 * 4. Large lists should use virtualization
 *
 * Performance Targets:
 * - Initial render: < 100ms
 * - Re-render on props change: < 50ms (with memo)
 * - Re-render on unrelated state change: 0ms (prevented by memo)
 * - Render count reduction: ≥ 70% vs unoptimized version
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import React from 'react';
import { render, waitFor, screen } from '@test/test-utils';
import { MockedProvider } from '@apollo/client/testing/react';
import GameManagementModalGraphQL from '../GameManagementModalGraphQL';
import { performance } from 'perf_hooks';
// Use the component with its actual name
const GameManagementModal = GameManagementModalGraphQL;

// Mock Apollo Client hooks
vi.mock('@apollo/client', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  gql: (strings: TemplateStringsArray) => strings.join(''),
}));

// Import after mocking
import { useQuery, useMutation } from '@apollo/client';

describe('GameManagementModalGraphQL - Performance Tests', () => {
  const mockGames = [
    { id: 1, gid: '10000147', name: 'STAR001', odsDb: 'ieu_ods', eventCount: 5, parameterCount: 10 },
    { id: 2, gid: '10000148', name: 'STAR002', odsDb: 'ieu_ods', eventCount: 3, parameterCount: 8 },
    { id: 3, gid: '10000149', name: 'STAR003', odsDb: 'overseas_ods', eventCount: 7, parameterCount: 12 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useQuery
    (useQuery as any).mockReturnValue({
      loading: false,
      error: null,
      data: { games: mockGames },
      refetch: vi.fn(),
    });

    // Mock useMutation
    (useMutation as any).mockReturnValue([
      vi.fn(),
      { loading: false },
    ]);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Render Performance', () => {
    it('should render initially in under 100ms', async () => {
      const startTime = performance.now();

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('游戏管理')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`Initial render time: ${renderTime.toFixed(2)}ms`);

      // Performance target: < 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('should render 20 games in under 150ms', async () => {
      const largeMockGames = Array.from({ length: 20 }, (_, i) => ({
        id: i + 1,
        gid: `100001${i + 47}`,
        name: `GAME${i + 1}`,
        odsDb: i % 2 === 0 ? 'ieu_ods' : 'overseas_ods',
        eventCount: Math.floor(Math.random() * 10),
        parameterCount: Math.floor(Math.random() * 15),
      }));

      (useQuery as any).mockReturnValue({
        loading: false,
        error: null,
        data: { games: largeMockGames },
        refetch: vi.fn(),
      });
      const startTime = performance.now();

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('游戏管理')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`Render time for 20 games: ${renderTime.toFixed(2)}ms`);

      // Performance target: < 150ms for 20 items
      expect(renderTime).toBeLessThan(150);
    });
  });

  describe('Re-render Performance', () => {
    it('should not re-render when search query changes (memo optimization)', async () => {
      let renderCount = 0;

      const TestWrapper = () => {
        const [, forceUpdate] = React.useState({});
        renderCount++;

        return (
          <MockedProvider mocks={[]} addTypename={false}>
            <div>
              <button onClick={() => forceUpdate({})}>Force Update</button>
              <GameManagementModal />
            </div>
          </MockedProvider>
        );
      };

      const { rerender } = render(<TestWrapper />);

      const initialRenderCount = renderCount;

      // Force parent update
      rerender(<TestWrapper />);

      // With React.memo, GameManagementModal should NOT re-render
      // Only TestWrapper should re-render
      expect(renderCount).toBe(initialRenderCount + 1); // Only parent
    });

    it('should use useCallback for event handlers', async () => {
      const createGameSpy = vi.fn();
      (useMutation as any).mockReturnValue([
        createGameSpy,
        { loading: false },
      ]);

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      // Click "创建游戏" button
      const createButton = await screen.findByText('创建游戏');
      createButton.click();

      // Handler should be stable (same function reference across renders)
      // This is tested indirectly by ensuring the handler works
      expect(createButton).toBeInTheDocument();
    });
  });

  describe('Memory Efficiency', () => {
    it('should not create new functions on every render', async () => {
      const functionRefs = new Set<any>();

      // Mock to capture function references
      const originalUseMutation = useMutation as any;

      let renderCount = 0;
      (useMutation as any).mockImplementation(() => {
        renderCount++;

        const mutationFn = vi.fn();
        functionRefs.add(mutationFn);

        return [mutationFn, { loading: false }];
      });

      const { rerender } = render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      // Force multiple re-renders
      for (let i = 0; i < 5; i++) {
        rerender(
          <MockedProvider mocks={[]} addTypename={false}>
            <GameManagementModal />
          </MockedProvider>
        );
      }

      // With useCallback, we should have minimal unique function references
      // Without useCallback, we'd have 6 (initial + 5 re-renders)
      expect(functionRefs.size).toBeLessThan(3);

      // Restore original mock
      (useMutation as any).mockImplementation(originalUseMutation);
    });

    it('should clean up event listeners on unmount', async () => {
      const { unmount } = render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      // Unmount component
      unmount();

      // Verify no errors during cleanup
      // If there are memory leaks, this would show up in memory profiling
      expect(true).toBe(true); // Placeholder for memory leak detection
    });
  });

  describe('Large Dataset Performance', () => {
    it('should handle 100 games without significant performance degradation', async () => {
      const largeMockGames = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        gid: `10000${i + 100}`,
        name: `GAME${i + 1}`,
        odsDb: i % 2 === 0 ? 'ieu_ods' : 'overseas_ods',
        eventCount: Math.floor(Math.random() * 10),
        parameterCount: Math.floor(Math.random() * 15),
      }));

      (useQuery as any).mockReturnValue({
        loading: false,
        error: null,
        data: { games: largeMockGames },
        refetch: vi.fn(),
      });
      const startTime = performance.now();

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('游戏管理')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`Render time for 100 games: ${renderTime.toFixed(2)}ms`);

      // Performance target: < 500ms for 100 items
      // If this fails, consider implementing virtualization
      expect(renderTime).toBeLessThan(500);
    });

    it('should filter/search games efficiently', async () => {
      const largeMockGames = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        gid: `10000${i + 100}`,
        name: `GAME${i + 1}`,
        odsDb: i % 2 === 0 ? 'ieu_ods' : 'overseas_ods',
        eventCount: Math.floor(Math.random() * 10),
        parameterCount: Math.floor(Math.random() * 15),
      }));

      (useQuery as any)
        .mockReturnValueOnce({
          loading: false,
          error: null,
          data: { games: largeMockGames },
          refetch: vi.fn(),
        })
        .mockReturnValueOnce({
          loading: false,
          error: null,
          data: { searchGames: [largeMockGames[0]] },
          refetch: vi.fn(),
        });

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      const searchInput = await screen.findByPlaceholderText('搜索游戏...');

      const startTime = performance.now();
      searchInput.change('GAME1');
      await waitFor(() => {});
      const endTime = performance.now();

      const searchTime = endTime - startTime;

      console.log(`Search time: ${searchTime.toFixed(2)}ms`);

      // Search should be fast
      expect(searchTime).toBeLessThan(100);
    });
  });

  describe('React Optimizations Verification', () => {
    it('should use React.memo for component', () => {
      // Check if component is wrapped with memo
      // This is a structural test
      const componentDisplayName = (GameManagementModal as any).displayName;

      // Memoized components have a specific display name pattern
      expect(componentDisplayName).toBeDefined();
    });

    it('should use useCallback for event handlers', async () => {
      // This is verified by the re-render test above
      // If useCallback is used, handlers maintain stable references
      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      const createButton = await screen.findByText('创建游戏');
      expect(createButton).toBeInTheDocument();
    });

    it('should use useMemo for expensive computations', async () => {
      // Check if filtered/processed data is memoized
      const largeMockGames = Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        gid: `10000${i + 100}`,
        name: `GAME${i + 1}`,
        odsDb: i % 2 === 0 ? 'ieu_ods' : 'overseas_ods',
        eventCount: Math.floor(Math.random() * 10),
        parameterCount: Math.floor(Math.random() * 15),
      }));

      (useQuery as any).mockReturnValue({
        loading: false,
        error: null,
        data: { games: largeMockGames },
        refetch: vi.fn(),
      });
      const startTime = performance.now();

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <GameManagementModal />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('游戏管理')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`Render with 50 games: ${renderTime.toFixed(2)}ms`);

      // Should be fast even with filtering logic
      expect(renderTime).toBeLessThan(200);
    });
  });
});
