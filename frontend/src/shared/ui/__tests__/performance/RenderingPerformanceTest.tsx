// @ts-nocheck - TypeScript检查暂禁用
/**
 * Rendering Performance Test
 *
 * Measures rendering time for large numbers of components.
 * Uses performance.mark() for accurate timing.
 *
 * Run with: npm test -- RenderingPerformanceTest
 */

import React, { useState, useEffect } from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Button } from '../../index';
import { Card } from '../../index';
import { Input } from '../../index';
import { Table } from '../../index';
import { Badge } from '../../index';
import { Modal } from '../../index';

interface PerformanceMetrics {
  componentName: string;
  testType: string;
  renderTime: number;
  componentCount: number;
  avgTimePerComponent: number;
  targetFPS: number;
  achievedFPS: number;
  withinBudget: boolean;
}

const TARGET_FRAME_TIME = 16.67; // 60fps = 16.67ms per frame

function measurePerformance<T>(
  name: string,
  testType: string,
  fn: () => T,
  componentCount: number
): PerformanceMetrics {
  // Start measurement
  performance.mark(`${name}-start`);

  const result = fn();

  // End measurement
  performance.mark(`${name}-end`);
  performance.measure(name, `${name}-start`, `${name}-end`);

  const measure = performance.getEntriesByName(name)[0];
  const renderTime = measure.duration;

  // Clean up
  performance.clearMarks();
  performance.clearMeasures();

  const avgTimePerComponent = renderTime / componentCount;
  const achievedFPS = 1000 / renderTime;
  const withinBudget = renderTime < TARGET_FRAME_TIME;

  return {
    componentName: name,
    testType,
    renderTime,
    componentCount,
    avgTimePerComponent,
    targetFPS: 60,
    achievedFPS,
    withinBudget,
  };
}

describe('Rendering Performance Tests', () => {
  describe('Button Component', () => {
    test('should render 100 buttons quickly', () => {
      function ButtonGrid() {
        const handleClick = () => {};

        return (
          <div>
            {Array.from({ length: 100 }, (_, i) => (
              <Button key={i} onClick={handleClick}>
                Button {i}
              </Button>
            ))}
          </div>
        );
      }

      const metrics = measurePerformance(
        'Button-100',
        'Initial Render',
        () => render(<ButtonGrid />),
        100
      );

      console.log(`Button (100): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per component)`);

      // Should render 100 buttons in less than 100ms
      expect(metrics.renderTime).toBeLessThan(100);
    });

    test('should render 1000 buttons efficiently', () => {
      function ButtonGrid() {
        const handleClick = () => {};

        return (
          <div>
            {Array.from({ length: 1000 }, (_, i) => (
              <Button key={i} onClick={handleClick}>
                Button {i}
              </Button>
            ))}
          </div>
        );
      }

      const metrics = measurePerformance(
        'Button-1000',
        'Initial Render',
        () => render(<ButtonGrid />),
        1000
      );

      console.log(`Button (1000): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per component)`);

      // Should render 1000 buttons in less than 500ms
      expect(metrics.renderTime).toBeLessThan(500);
    });
  });

  describe('Card Component', () => {
    test('should render 50 cards with sub-components quickly', () => {
      function CardGrid() {
        return (
          <div>
            {Array.from({ length: 50 }, (_, i) => (
              <Card key={i}>
                <Card.Header>
                  <Card.Title>Card {i}</Card.Title>
                </Card.Header>
                <Card.Body>
                  <p>Content for card {i}</p>
                </Card.Body>
                <Card.Footer>
                  <Button>Action</Button>
                </Card.Footer>
              </Card>
            ))}
          </div>
        );
      }

      const metrics = measurePerformance('Card-50', 'Initial Render', () => render(<CardGrid />), 50);

      console.log(`Card (50): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per card)`);

      // Should render 50 cards in less than 200ms
      expect(metrics.renderTime).toBeLessThan(200);
    });
  });

  describe('Input Component', () => {
    test('should render 100 inputs efficiently', () => {
      function InputGrid() {
        const [values, setValues] = useState(Array(100).fill(''));

        return (
          <div>
            {Array.from({ length: 100 }, (_, i) => (
              <Input
                key={i}
                value={values[i]}
                onChange={(val) => {
                  const newValues = [...values];
                  newValues[i] = val;
                  setValues(newValues);
                }}
                placeholder={`Input ${i}`}
              />
            ))}
          </div>
        );
      }

      const metrics = measurePerformance('Input-100', 'Initial Render', () => render(<InputGrid />), 100);

      console.log(`Input (100): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per input)`);

      // Should render 100 inputs in less than 150ms
      expect(metrics.renderTime).toBeLessThan(150);
    });
  });

  describe('Table Component', () => {
    test('should render table with 100 rows efficiently', () => {
      const data = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
        value: Math.random() * 1000,
      }));

      function DataTable() {
        return (
          <Table>
            <Table.Header>
              <Table.Row>
                <Table.Head>ID</Table.Head>
                <Table.Head>Name</Table.Head>
                <Table.Head>Value</Table.Head>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {data.map((row) => (
                <Table.Row key={row.id}>
                  <Table.Cell>{row.id}</Table.Cell>
                  <Table.Cell>{row.name}</Table.Cell>
                  <Table.Cell>{row.value.toFixed(2)}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        );
      }

      const metrics = measurePerformance(
        'Table-100-rows',
        'Initial Render',
        () => render(<DataTable />),
        100
      );

      console.log(`Table (100 rows): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per row)`);

      // Should render 100-row table in less than 200ms
      expect(metrics.renderTime).toBeLessThan(200);
    });

    test('should re-render efficiently when sorting changes', () => {
      const data = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
        value: Math.random() * 1000,
      }));

      function DataTable() {
        const [sortState, setSortState] = useState<'asc' | 'desc' | null>(null);

        return (
          <div>
            <button onClick={() => setSortState(sortState === 'asc' ? 'desc' : 'asc')}>Toggle Sort</button>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head sortable sorted={sortState} onSort={setSortState}>
                    Name
                  </Table.Head>
                  <Table.Head>Value</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {data.map((row) => (
                  <Table.Row key={row.id}>
                    <Table.Cell>{row.name}</Table.Cell>
                    <Table.Cell>{row.value.toFixed(2)}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      }

      const { container } = render(<DataTable />);

      // Measure re-render time
      const metrics = measurePerformance(
        'Table-sort',
        'Re-render',
        () => {
          const sortBtn = container.querySelector('button') as HTMLElement;
          fireEvent.click(sortBtn);
          return container;
        },
        50
      );

      console.log(`Table sort (50 rows): ${metrics.renderTime.toFixed(2)}ms`);

      // Sort should be fast
      expect(metrics.renderTime).toBeLessThan(50);
    });
  });

  describe('Badge Component', () => {
    test('should render 500 badges quickly', () => {
      function BadgeGrid() {
        return (
          <div>
            {Array.from({ length: 500 }, (_, i) => (
              <Badge key={i}>Badge {i}</Badge>
            ))}
          </div>
        );
      }

      const metrics = measurePerformance('Badge-500', 'Initial Render', () => render(<BadgeGrid />), 500);

      console.log(`Badge (500): ${metrics.renderTime.toFixed(2)}ms (${metrics.avgTimePerComponent.toFixed(3)}ms per badge)`);

      // Should render 500 badges in less than 100ms (they're very simple)
      expect(metrics.renderTime).toBeLessThan(100);
    });
  });

  describe('Modal Component', () => {
    test('should mount and unmount quickly', () => {
      function ModalTest() {
        const [isOpen, setIsOpen] = useState(false);

        return (
          <div>
            <button onClick={() => setIsOpen(true)}>Open</button>
            <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
              <Modal.Header>
                <Modal.Title>Test Modal</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <p>Modal content</p>
              </Modal.Body>
            </Modal>
          </div>
        );
      }

      const { container } = render(<ModalTest />);

      // Measure mount time
      const mountMetrics = measurePerformance(
        'Modal-mount',
        'Mount',
        () => {
          const openBtn = container.querySelector('button') as HTMLElement;
          fireEvent.click(openBtn);
          return container;
        },
        1
      );

      console.log(`Modal mount: ${mountMetrics.renderTime.toFixed(2)}ms`);

      // Should mount in less than 50ms
      expect(mountMetrics.renderTime).toBeLessThan(50);
    });
  });

  describe('Mixed Component Stress Test', () => {
    test('should render complex dashboard efficiently', () => {
      function Dashboard() {
        const [searchTerm, setSearchTerm] = useState('');

        return (
          <div>
            {/* Header with buttons */}
            <div>
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
            </div>

            {/* Search input */}
            <Input value={searchTerm} onChange={setSearchTerm} placeholder="Search..." />

            {/* Stats cards */}
            {Array.from({ length: 6 }, (_, i) => (
              <Card key={i}>
                <Card.Header>
                  <Card.Title>Stat {i}</Card.Title>
                </Card.Header>
                <Card.Body>
                  <Badge>{Math.floor(Math.random() * 1000)}</Badge>
                </Card.Body>
              </Card>
            ))}

            {/* Data table */}
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.Head>ID</Table.Head>
                  <Table.Head>Name</Table.Head>
                  <Table.Head>Status</Table.Head>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {Array.from({ length: 20 }, (_, i) => (
                  <Table.Row key={i}>
                    <Table.Cell>{i}</Table.Cell>
                    <Table.Cell>Item {i}</Table.Cell>
                    <Table.Cell>
                      <Badge variant={i % 2 === 0 ? 'success' : 'warning'}>
                        {i % 2 === 0 ? 'Active' : 'Pending'}
                      </Badge>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </div>
        );
      }

      const metrics = measurePerformance(
        'Dashboard-complex',
        'Complex UI',
        () => render(<Dashboard />),
        30 // Approximate component count
      );

      console.log(`Dashboard: ${metrics.renderTime.toFixed(2)}ms`);

      // Complex dashboard should render in less than 300ms
      expect(metrics.renderTime).toBeLessThan(300);
    });
  });
});

// Export metrics collection
export { measurePerformance, type PerformanceMetrics };
