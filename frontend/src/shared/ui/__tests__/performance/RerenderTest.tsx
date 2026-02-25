// @ts-nocheck - TypeScript检查暂禁用
/**
 * Re-render Performance Test
 *
 * Tests React.memo effectiveness by measuring component re-renders
 * when parent component updates.
 *
 * Run with: npm test -- RerenderTest
 */

import React, { useState, useEffect, useRef } from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Button } from '../../index';
import { Card } from '../../index';
import { Input } from '../../index';
import { Table } from '../../index';
import { Badge } from '../../index';

// Track render counts
interface RenderTracker {
  renderCount: number;
  componentName: string;
}

const renderCounts = new Map<string, number>();

function trackRender(componentName: string) {
  const current = renderCounts.get(componentName) || 0;
  renderCounts.set(componentName, current + 1);
}

function resetRenderCounts() {
  renderCounts.clear();
}

function getRenderCount(componentName: string): number {
  return renderCounts.get(componentName) || 0;
}

// Test Components
function TrackedButton({ onClick, children }: any) {
  trackRender('Button');
  return <Button onClick={onClick}>{children}</Button>;
}

function TrackedCard({ children }: any) {
  trackRender('Card');
  return <Card>{children}</Card>;
}

function TrackedInput({ value, onChange }: any) {
  trackRender('Input');
  return <Input value={value} onChange={onChange} />;
}

function TrackedBadge({ children }: any) {
  trackRender('Badge');
  return <Badge>{children}</Badge>;
}

describe('React.memo Re-render Tests', () => {
  beforeEach(() => {
    resetRenderCounts();
  });

  describe('Button Component', () => {
    test('should not re-render when parent state changes (unrelated props)', () => {
      function Parent() {
        const [count, setCount] = useState(0);
        const handleClick = () => setCount(c => c + 1);

        return (
          <div>
            <TrackedButton onClick={handleClick}>Click me</TrackedButton>
            <button onClick={() => setCount(c => c + 1)}>Force Update</button>
            <span>Count: {count}</span>
          </div>
        );
      }

      const { container } = render(<Parent />);

      const initialRenderCount = getRenderCount('Button');
      expect(initialRenderCount).toBe(1);

      // Force parent update
      const forceUpdateBtn = container.querySelectorAll('button')[1];
      fireEvent.click(forceUpdateBtn);

      // Button should not re-render due to React.memo
      const afterUpdateRenderCount = getRenderCount('Button');
      expect(afterUpdateRenderCount).toBe(initialRenderCount);
    });

    test('should re-render when onClick changes', () => {
      function Parent() {
        const [count, setCount] = useState(0);

        const handleClick = () => setCount(c => c + 1);

        return (
          <div>
            <TrackedButton onClick={handleClick}>Click me</TrackedButton>
            <span>Count: {count}</span>
          </div>
        );
      }

      const { container } = render(<Parent />);
      const initialRenderCount = getRenderCount('Button');

      // Click button - this should trigger re-render because onClick changes
      const button = container.querySelector('button') as HTMLElement;
      fireEvent.click(button);

      // Button should re-render because onClick reference changed
      const afterClickRenderCount = getRenderCount('Button');
      expect(afterClickRenderCount).toBeGreaterThan(initialRenderCount);
    });
  });

  describe('Card Component', () => {
    test('should not re-render Card sub-components when parent updates', () => {
      let headerRenders = 0;
      let bodyRenders = 0;

      function TestCard() {
        const [count, setCount] = useState(0);

        return (
          <Card>
            <Card.Header ref={useRef(null)}>
              {(() => {
                headerRenders++;
                return null;
              })()}
              Header
            </Card.Header>
            <Card.Body ref={useRef(null)}>
              {(() => {
                bodyRenders++;
                return null;
              })()}
              Body
            </Card.Body>
            <button onClick={() => setCount(c => c + 1)}>Update</button>
            <span>{count}</span>
          </Card>
        );
      }

      const { container } = render(<TestCard />);

      const initialHeaderRenders = headerRenders;
      const initialBodyRenders = bodyRenders;

      // Force update
      const updateBtn = container.querySelector('button') as HTMLElement;
      fireEvent.click(updateBtn);

      // Sub-components should not re-render due to React.memo
      expect(headerRenders).toBe(initialHeaderRenders);
      expect(bodyRenders).toBe(initialBodyRenders);
    });
  });

  describe('Input Component', () => {
    test('should not re-render when other state changes', () => {
      function Parent() {
        const [inputValue, setInputValue] = useState('');
        const [otherState, setOtherState] = useState(0);

        return (
          <div>
            <TrackedInput value={inputValue} onChange={setInputValue} />
            <button onClick={() => setOtherState(s => s + 1)}>Other State</button>
            <span>{otherState}</span>
          </div>
        );
      }

      const { container } = render(<Parent />);
      const initialRenderCount = getRenderCount('Input');

      // Change unrelated state
      const otherStateBtn = container.querySelector('button') as HTMLElement;
      fireEvent.click(otherStateBtn);

      // Input should not re-render
      const afterUpdateRenderCount = getRenderCount('Input');
      expect(afterUpdateRenderCount).toBe(initialRenderCount);
    });

    test('should re-render when value changes', () => {
      function Parent() {
        const [inputValue, setInputValue] = useState('');

        return (
          <div>
            <TrackedInput value={inputValue} onChange={setInputValue} />
          </div>
        );
      }

      const { container } = render(<Parent />);
      const initialRenderCount = getRenderCount('Input');

      // Change input value
      const input = container.querySelector('input') as HTMLElement;
      fireEvent.change(input, { target: { value: 'test' } });

      // Input should re-render
      const afterChangeRenderCount = getRenderCount('Input');
      expect(afterChangeRenderCount).toBeGreaterThan(initialRenderCount);
    });
  });

  describe('Badge Component', () => {
    test('should not re-render when parent updates', () => {
      function Parent() {
        const [count, setCount] = useState(0);

        return (
          <div>
            <TrackedBadge>Test Badge</TrackedBadge>
            <button onClick={() => setCount(c => c + 1)}>Update</button>
            <span>{count}</span>
          </div>
        );
      }

      const { container } = render(<Parent />);
      const initialRenderCount = getRenderCount('Badge');

      // Force parent update
      const updateBtn = container.querySelector('button') as HTMLElement;
      fireEvent.click(updateBtn);

      // Badge should not re-render due to React.memo
      const afterUpdateRenderCount = getRenderCount('Badge');
      expect(afterUpdateRenderCount).toBe(initialRenderCount);
    });
  });

  describe('Table Component', () => {
    test('should not re-render table rows when sorting changes', () => {
      let rowRenders = 0;

      function TestTable() {
        const [sortState, setSortState] = useState(null);

        return (
          <Table>
            <Table.Header>
              <Table.Head
                sortable
                sorted={sortState}
                onSort={setSortState}
              >
                Name
              </Table.Head>
            </Table.Header>
            <Table.Body>
              {['Item 1', 'Item 2', 'Item 3'].map((item, idx) => (
                <Table.Row key={idx}>
                  {(() => {
                    rowRenders++;
                    return null;
                  })()}
                  <Table.Cell>{item}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        );
      }

      const { container } = render(<TestTable />);
      const initialRowRenders = rowRenders;

      // Click header to sort
      const header = container.querySelector('th') as HTMLElement;
      fireEvent.click(header);

      // Rows should not re-render (only sort state changes)
      expect(rowRenders).toBe(initialRowRenders);
    });
  });

  describe('Performance Benchmarks', () => {
    test('Button: 1000 components with memo should render efficiently', () => {
      const startTime = performance.now();

      function ButtonGrid() {
        const [count, setCount] = useState(0);

        return (
          <div>
            {Array.from({ length: 1000 }, (_, i) => (
              <Button key={i} onClick={() => setCount(c => c + 1)}>
                Button {i}
              </Button>
            ))}
            <span>Count: {count}</span>
          </div>
        );
      }

      render(<ButtonGrid />);
      const renderTime = performance.now() - startTime;

      // Should render 1000 buttons in less than 500ms
      expect(renderTime).toBeLessThan(500);
    });

    test('Card: 100 cards with memo should not cascade re-renders', () => {
      let totalRenders = 0;

      function CardGrid() {
        const [count, setCount] = useState(0);

        return (
          <div>
            {Array.from({ length: 100 }, (_, i) => (
              <Card key={i}>
                <Card.Body>
                  {(() => {
                    totalRenders++;
                    return <div>Card {i}</div>;
                  })()}
                </Card.Body>
              </Card>
            ))}
            <button onClick={() => setCount(c => c + 1)}>Update Parent</button>
          </div>
        );
      }

      const { container } = render(<CardGrid />);
      const initialRenders = totalRenders;

      // Force parent update
      const updateBtn = container.querySelector('button') as HTMLElement;
      fireEvent.click(updateBtn);

      // Cards should not re-render due to memo
      expect(totalRenders).toBe(initialRenders);
    });
  });
});

// Export utilities for manual testing
export { trackRender, getRenderCount, resetRenderCounts };
