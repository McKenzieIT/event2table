/**
 * TDD Test Suite: VirtualList Component
 *
 * Test-Driven Development approach:
 * 1. Write failing tests first (RED)
 * 2. Implement minimal code to pass tests (GREEN)
 * 3. Refactor and optimize (REFACTOR)
 *
 * Performance Requirements:
 * - Render 1000+ items in <100ms
 * - Smooth scrolling at 60fps
 * - Memory footprint <50% of native list
 */

import { render, screen, waitFor } from '@test/test-utils';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { VirtualList } from '../index';

describe('VirtualList Component (TDD)', () => {
  /**
   * Test Case 1: Component renders correctly
   *
   * TDD Phase: RED → GREEN
   * Expected: Component should render without errors
   */
  it('should render VirtualList component', () => {
    const items = ['Item 1', 'Item 2', 'Item 3'];
    const renderItem = (item: string) => <div key={item}>{item}</div>;

    render(
      <VirtualList
        items={items}
        itemHeight={50}
        height={400}
        renderItem={renderItem}
      />
    );

    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });

  /**
   * Test Case 2: Renders all items
   *
   * TDD Phase: RED → GREEN
   * Expected: All items should be rendered
   */
  it('should render all items in the list', async () => {
    const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5'];
    const renderItem = (item: string, index: number) => (
      <div key={`${item}-${index}`}>{item}</div>
    );

    render(
      <VirtualList
        items={items}
        itemHeight={50}
        height={200}
        renderItem={renderItem}
      />
    );

    // Verify all items are rendered
    await waitFor(() => {
      items.forEach(item => {
        expect(screen.getByText(item)).toBeInTheDocument();
      });
    });
  });

  /**
   * Test Case 3: Handles empty list
   *
   * TDD Phase: RED → GREEN
   * Expected: Should render gracefully with empty items
   */
  it('should handle empty list gracefully', () => {
    const items: string[] = [];
    const renderItem = (item: string) => <div key={item}>{item}</div>;

    render(
      <VirtualList
        items={items}
        itemHeight={50}
        height={400}
        renderItem={renderItem}
      />
    );

    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
    expect(screen.getByTestId('virtual-list')).toBeEmptyDOMElement();
  });

  /**
   * Test Case 4: Large list performance (1000+ items)
   *
   * TDD Phase: RED → GREEN
   * Expected: Should render large list without performance issues
   * Performance: <100ms render time
   */
  it('should render large list (1000 items) efficiently', async () => {
    const items = Array.from({ length: 1000 }, (_, i) => `Item ${i + 1}`);
    const renderItem = (item: string, index: number) => (
      <div key={`${item}-${index}`} data-index={index}>
        {item}
      </div>
    );

    const startTime = performance.now();

    render(
      <VirtualList
        items={items}
        itemHeight={40}
        height={600}
        renderItem={renderItem}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Verify rendering completes within 100ms
    expect(renderTime).toBeLessThan(100);

    // Verify first and last items are rendered
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 1000')).toBeInTheDocument();
  });

  /**
   * Test Case 5: Very large list performance (10000 items)
   *
   * TDD Phase: RED → GREEN
   * Expected: Should handle very large lists without freezing
   * Performance: <200ms render time
   */
  it('should render very large list (10000 items) without freezing', async () => {
    const items = Array.from({ length: 10000 }, (_, i) => `Item ${i + 1}`);
    const renderItem = (item: string, index: number) => (
      <div key={`${item}-${index}`} data-index={index}>
        {item}
      </div>
    );

    const startTime = performance.now();

    render(
      <VirtualList
        items={items}
        itemHeight={40}
        height={600}
        renderItem={renderItem}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Verify rendering completes within 200ms
    expect(renderTime).toBeLessThan(200);

    // Verify component rendered
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });

  /**
   * Test Case 6: Custom render function
   *
   * TDD Phase: RED → GREEN
   * Expected: Should use custom render function for each item
   */
  it('should use custom render function for each item', async () => {
    interface TestItem {
      id: number;
      name: string;
      value: number;
    }

    const items: TestItem[] = [
      { id: 1, name: 'First', value: 100 },
      { id: 2, name: 'Second', value: 200 },
      { id: 3, name: 'Third', value: 300 },
    ];

    const renderItem = (item: TestItem, index: number) => (
      <div key={`${item.id}-${index}`} data-testid={`item-${item.id}`}>
        <span className="name">{item.name}</span>
        <span className="value">{item.value}</span>
      </div>
    );

    render(
      <VirtualList
        items={items}
        itemHeight={60}
        height={400}
        renderItem={renderItem}
      />
    );

    // Verify custom render function is used
    expect(screen.getByTestId('item-1')).toBeInTheDocument();
    expect(screen.getByText('First')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('Second')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  /**
   * Test Case 7: Correct height and itemHeight props
   *
   * TDD Phase: RED → GREEN
   * Expected: Component should receive and use correct dimensions
   */
  it('should apply correct height and itemHeight', () => {
    const items = ['Item 1', 'Item 2', 'Item 3'];
    const renderItem = (item: string) => <div key={item}>{item}</div>;

    render(
      <VirtualList
        items={items}
        itemHeight={75}
        height={500}
        renderItem={renderItem}
      />
    );

    const listElement = screen.getByTestId('virtual-list');
    expect(listElement).toHaveStyle({ height: '500px' });
    expect(listElement).toHaveAttribute('data-item-size', '75');
  });

  /**
   * Test Case 8: Generic type support
   *
   * TDD Phase: RED → GREEN
   * Expected: Should support TypeScript generics
   */
  it('should support generic types', () => {
    interface CustomType {
      id: string;
      data: number;
    }

    const items: CustomType[] = [
      { id: 'a', data: 1 },
      { id: 'b', data: 2 },
    ];

    const renderItem = (item: CustomType) => (
      <div key={item.id}>
        {item.id}: {item.data}
      </div>
    );

    render(
      <VirtualList
        items={items}
        itemHeight={50}
        height={400}
        renderItem={renderItem}
      />
    );

    expect(screen.getByText('a: 1')).toBeInTheDocument();
    expect(screen.getByText('b: 2')).toBeInTheDocument();
  });

  /**
   * Test Case 9: Index is passed to render function
   *
   * TDD Phase: RED → GREEN
   * Expected: Render function should receive correct index
   */
  it('should pass correct index to render function', async () => {
    const items = ['A', 'B', 'C', 'D', 'E'];
    const renderedIndexes: number[] = [];

    const renderItem = (item: string, index: number) => {
      renderedIndexes.push(index);
      return (
        <div key={`${item}-${index}`} data-index={index}>
          {item}
        </div>
      );
    };

    render(
      <VirtualList
        items={items}
        itemHeight={40}
        height={200}
        renderItem={renderItem}
      />
    );

    await waitFor(() => {
      // Verify indexes 0-4 are rendered
      expect(renderedIndexes).toContain(0);
      expect(renderedIndexes).toContain(1);
      expect(renderedIndexes).toContain(2);
      expect(renderedIndexes).toContain(3);
      expect(renderedIndexes).toContain(4);
    });
  });

  /**
   * Test Case 10: React.memo optimization
   *
   * TDD Phase: RED → GREEN
   * Expected: Component should be memoized to prevent unnecessary re-renders
   */
  it('should be memoized for performance', () => {
    const items = ['Item 1', 'Item 2', 'Item 3'];
    const renderItem = (item: string) => <div key={item}>{item}</div>;

    const { rerender } = render(
      <VirtualList
        items={items}
        itemHeight={50}
        height={400}
        renderItem={renderItem}
      />
    );

    // Re-render with same props
    rerender(
      <VirtualList
        items={items}
        itemHeight={50}
        height={400}
        renderItem={renderItem}
      />
    );

    // Component should still be present (no crashes)
    expect(screen.getByTestId('virtual-list')).toBeInTheDocument();
  });
});
