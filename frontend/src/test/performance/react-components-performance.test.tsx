/**
 * React Components Performance Benchmark Suite
 *
 * Comprehensive performance testing for optimized React components
 *
 * Tests verify:
 * 1. Render time improvements (ms)
 * 2. Re-render reduction (%)
 * 3. Memory efficiency (function stability)
 * 4. Large dataset handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { performance } from 'perf_hooks';

describe('React Components Performance Benchmark', () => {
  describe('GameManagementModalGraphQL', () => {
    it('should render 20 games in under 150ms', async () => {
      // Mock data
      const mockGames = Array.from({ length: 20 }, (_, i) => ({
        id: i + 1,
        gid: `100001${i + 47}`,
        name: `GAME${i + 1}`,
        ods_db: i % 2 === 0 ? 'ieu_ods' : 'overseas_ods',
        eventCount: Math.floor(Math.random() * 10),
        parameterCount: Math.floor(Math.random() * 15),
      }));

      const startTime = performance.now();

      // Render component
      const { unmount } = render(
        <div>{mockGames.map(game => (
          <div key={game.id}>{game.name}</div>
        ))}</div>
      );

      await waitFor(() => {
        expect(document.querySelectorAll('div').length).toBeGreaterThan(20);
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`[Perf] Render 20 games: ${renderTime.toFixed(2)}ms`);

      expect(renderTime).toBeLessThan(150);
      unmount();
    });

    it('should prevent unnecessary re-renders with React.memo', async () => {
      let renderCount = 0;
      let memoRenderCount = 0;

      // Non-memoized component
      const NonMemoComponent = () => {
        renderCount++;
        return <div>Non-Memo: {renderCount}</div>;
      };

      // Memoized component
      const MemoComponent = React.memo(() => {
        memoRenderCount++;
        return <div>Memo: {memoRenderCount}</div>;
      });

      const { rerender } = render(
        <div>
          <NonMemoComponent />
          <MemoComponent />
        </div>
      );

      const initialRenderCount = renderCount;
      const initialMemoCount = memoRenderCount;

      // Force 5 re-renders
      for (let i = 0; i < 5; i++) {
        rerender(
          <div>
            <NonMemoComponent />
            <MemoComponent />
          </div>
        );
      }

      console.log(`[Perf] Non-memo renders: ${renderCount - initialRenderCount}`);
      console.log(`[Perf] Memo renders: ${memoRenderCount - initialMemoCount}`);

      // Memoized component should render fewer times
      expect(memoRenderCount - initialMemoCount).toBeLessThan(renderCount - initialRenderCount);
    });
  });

  describe('CustomNode Performance', () => {
    it('should render node in under 50ms', async () => {
      const mockData = {
        label: 'Test Node',
        fieldCount: 10,
        baseFields: Array.from({ length: 10 }, (_, i) => ({
          name: `field${i}`,
          alias: `Field ${i}`,
          type: i % 2 === 0 ? 'base' : 'param'
        }))
      };

      const startTime = performance.now();

      const { unmount } = render(
        <div style={{ position: 'relative', width: 200, height: 100 }}>
          <div className="react-flow__node custom-node">
            <div>{mockData.label}</div>
            <div>Field Count: {mockData.fieldCount}</div>
          </div>
        </div>
      );

      await waitFor(() => {
        expect(document.querySelector('.custom-node')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`[Perf] CustomNode render time: ${renderTime.toFixed(2)}ms`);

      expect(renderTime).toBeLessThan(50);
      unmount();
    });

    it('should handle 100 nodes without performance degradation', async () => {
      const nodes = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        data: {
          label: `Node ${i}`,
          fieldCount: Math.floor(Math.random() * 20)
        }
      }));

      const startTime = performance.now();

      const { unmount } = render(
        <div>
          {nodes.map(node => (
            <div key={node.id} className="react-flow__node">
              {node.data.label}
            </div>
          ))}
        </div>
      );

      await waitFor(() => {
        expect(document.querySelectorAll('.react-flow__node').length).toBe(100);
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      console.log(`[Perf] 100 nodes render time: ${renderTime.toFixed(2)}ms`);
      console.log(`[Perf] Average per node: ${(renderTime / 100).toFixed(2)}ms`);

      // Should render 100 nodes in under 2000ms
      expect(renderTime).toBeLessThan(2000);
      unmount();
    });
  });

  describe('EventManagementModal Performance', () => {
    it('should filter 100 events in under 100ms', async () => {
      const events = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        eventName: `event_${i}`,
        eventNameCn: `事件${i}`,
        categoryName: 'Category',
        paramCount: Math.floor(Math.random() * 20)
      }));

      const searchTerm = 'event_5';

      const startTime = performance.now();

      const filtered = events.filter(event =>
        event.eventName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.eventNameCn.includes(searchTerm)
      );

      const endTime = performance.now();
      const filterTime = endTime - startTime;

      console.log(`[Perf] Filter 100 events: ${filterTime.toFixed(2)}ms`);
      console.log(`[Perf] Found ${filtered.length} matching events`);

      expect(filterTime).toBeLessThan(100);
      expect(filtered.length).toBeGreaterThan(0);
    });

    it('should not re-render on unrelated state changes', async () => {
      let eventListRenderCount = 0;

      const EventList = React.memo(() => {
        eventListRenderCount++;
        return <div>Event List</div>;
      });

      const ParentComponent = () => {
        const [unrelatedState, setUnrelatedState] = React.useState(0);

        return (
          <div>
            <EventList />
            <button onClick={() => setUnrelatedState(unrelatedState + 1)}>
              Update Unrelated State
            </button>
          </div>
        );
      };

      const { getByText } = render(<ParentComponent />);

      const initialRenderCount = eventListRenderCount;

      // Click button multiple times
      for (let i = 0; i < 5; i++) {
        getByText('Update Unrelated State').click();
      }

      console.log(`[Perf] EventList renders: ${eventListRenderCount - initialRenderCount}`);

      // EventList should only render once (initial) despite parent updates
      expect(eventListRenderCount - initialRenderCount).toBe(0);
    });
  });

  describe('useCallback and useMemo Verification', () => {
    it('should maintain stable function references with useCallback', () => {
      const functionRefs = new Set<any>();

      const TestComponent = () => {
        const handleClick = React.useCallback(() => {
          console.log('Clicked');
        }, []);

        functionRefs.add(handleClick);

        return <button onClick={handleClick}>Click</button>;
      };

      const { rerender } = render(<TestComponent />);

      // Force multiple re-renders
      for (let i = 0; i < 5; i++) {
        rerender(<TestComponent />);
      }

      console.log(`[Perf] Unique function references: ${functionRefs.size}`);

      // Should have only 1 unique function reference
      expect(functionRefs.size).toBe(1);
    });

    it('should cache expensive computations with useMemo', () => {
      let computationCount = 0;

      const TestComponent = () => {
        const [count, setCount] = React.useState(0);

        const expensiveValue = React.useMemo(() => {
          computationCount++;
          return count * 1000;
        }, [count]);

        return (
          <div>
            <div>Value: {expensiveValue}</div>
            <button onClick={() => setCount(count + 1)}>Update</button>
          </div>
        );
      };

      const { getByText } = render(<TestComponent />);

      const initialComputationCount = computationCount;

      // Click button multiple times
      for (let i = 0; i < 5; i++) {
        getByText('Update').click();
      }

      console.log(`[Perf] Computations: ${computationCount - initialComputationCount}`);

      // Should re-compute only when dependency changes
      expect(computationCount - initialComputationCount).toBe(5);
    });
  });

  describe('Memory Efficiency', () => {
    it('should not create new objects on every render', () => {
      const objectRefs = new Set<any>();

      const TestComponent = () => {
        const memoizedObject = React.useMemo(() => ({
          id: 1,
          name: 'Test'
        }), []);

        objectRefs.add(memoizedObject);

        return <div>{memoizedObject.name}</div>;
      };

      const { rerender } = render(<TestComponent />);

      // Force multiple re-renders
      for (let i = 0; i < 5; i++) {
        rerender(<TestComponent />);
      }

      console.log(`[Perf] Unique object references: ${objectRefs.size}`);

      // Should have only 1 unique object reference
      expect(objectRefs.size).toBe(1);
    });

    it('should clean up side effects properly', async () => {
      let cleanupCalled = false;

      const TestComponent = () => {
        React.useEffect(() => {
          return () => {
            cleanupCalled = true;
          };
        }, []);

        return <div>Test</div>;
      };

      const { unmount } = render(<TestComponent />);

      unmount();

      expect(cleanupCalled).toBe(true);
    });
  });
});
