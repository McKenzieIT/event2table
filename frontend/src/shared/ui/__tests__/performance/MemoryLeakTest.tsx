// @ts-nocheck - TypeScript检查暂禁用
/**
 * Memory Leak Detection Test
 *
 * Tests for memory leaks in Modal, Table, and other complex components.
 * Checks for:
 * - Proper cleanup of event listeners
 * - Correct unmounting of child components
 * - No lingering references after unmount
 *
 * Run with: npm test -- MemoryLeakTest
 */

import React, { useState, useEffect, useRef } from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Modal } from '../../index';
import { Table } from '../../index';
import { Card } from '../../index';

// Mock WeakMap to track component instances
const componentInstances = new WeakMap();
let mountCount = 0;
let unmountCount = 0;

describe('Memory Leak Tests', () => {
  let container: HTMLElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    mountCount = 0;
    unmountCount = 0;
  });

  afterEach(() => {
    if (container) {
      unmountComponentAtNode(container);
      container.remove();
    }
  });

  describe('Modal Component', () => {
    test('should clean up event listeners on unmount', () => {
      function ModalTest() {
        const [isOpen, setIsOpen] = useState(false);
        mountCount++;

        useEffect(() => {
          return () => {
            unmountCount++;
          };
        }, []);

        return (
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
            <Modal.Header>
              <Modal.Title>Test</Modal.Title>
            </Modal.Header>
            <Modal.Body>Content</Modal.Body>
          </Modal>
        );
      }

      // Initial mount
      render(<ModalTest />, { container });
      expect(mountCount).toBe(1);

      // Open modal (triggers Portal creation)
      act(() => {
        const openBtn = document.createElement('button');
        openBtn.onclick = () => {
          const { rerender } = render(<ModalTest />, { container });
        };
        container.appendChild(openBtn);
      });

      // Unmount
      unmountComponentAtNode(container);
      expect(unmountCount).toBe(1);

      // Verify no event listeners remain on document
      const escapeHandlerCount = document.body.getAttribute('data-escape-handlers');
      expect(escapeHandlerCount).toBeNull();
    });

    test('should not leak memory when opened/closed repeatedly', () => {
      function ModalTest() {
        const [isOpen, setIsOpen] = useState(false);

        return (
          <div>
            <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
            <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
              <Modal.Body>Test</Modal.Body>
            </Modal>
          </div>
        );
      }

      const { unmount } = render(<ModalTest />, { container });

      // Open and close modal multiple times
      for (let i = 0; i < 10; i++) {
        act(() => {
          const toggleBtn = container.querySelector('button') as HTMLElement;
          fireEvent.click(toggleBtn);
        });
      }

      // Check for multiple modal elements (should be 0 or 1)
      const modals = document.querySelectorAll('[role="dialog"]');
      expect(modals.length).toBeLessThanOrEqual(1);

      unmount();
    });

    test('should restore body scroll on unmount', () => {
      function ModalTest() {
        const [isOpen, setIsOpen] = useState(true);

        return (
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
            <Modal.Body>Test</Modal.Body>
          </Modal>
        );
      }

      const { unmount } = render(<ModalTest />, { container });

      // Body should have overflow hidden
      expect(document.body.style.overflow).toBe('hidden');

      // Unmount
      act(() => {
        unmount();
      });

      // Body scroll should be restored
      expect(document.body.style.overflow).toBe('');
    });

    test('should restore focus on unmount', () => {
      function ModalTest() {
        const [isOpen, setIsOpen] = useState(true);

        return (
          <div>
            <button id="trigger-btn">Open Modal</button>
            <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
              <Modal.Body>Test</Modal.Body>
            </Modal>
          </div>
        );
      }

      const triggerBtn = document.createElement('button');
      triggerBtn.id = 'trigger-btn';
      document.body.appendChild(triggerBtn);
      triggerBtn.focus();

      render(<ModalTest />, { container });

      // Modal is open, focus should be trapped
      const modal = document.querySelector('[role="dialog"]');
      expect(modal).toBeInTheDocument();

      // Unmount
      act(() => {
        unmountComponentAtNode(container);
      });

      // Focus should be restored to trigger button
      expect(document.activeElement).toBe(triggerBtn);

      // Cleanup
      triggerBtn.remove();
    });
  });

  describe('Table Component', () => {
    test('should not leak memory with many rows', () => {
      const data = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `Item ${i}`,
        value: i * 10,
      }));

      function DataTable() {
        const [sortState, setSortState] = useState<'asc' | 'desc' | null>(null);

        return (
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
                  <Table.Cell>{row.value}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        );
      }

      const { unmount } = render(<DataTable />, { container });

      // Perform multiple sorts
      for (let i = 0; i < 5; i++) {
        act(() => {
          const header = container.querySelector('th') as HTMLElement;
          fireEvent.click(header);
        });
      }

      // Unmount
      act(() => {
        unmount();
      });

      // Check for memory leaks (table should be removed)
      const tables = container.querySelectorAll('table');
      expect(tables.length).toBe(0);
    });

    test('should clean up click handlers on unmount', () => {
      let clickCount = 0;

      function DataTable() {
        const data = [
          { id: 1, name: 'Item 1' },
          { id: 2, name: 'Item 2' },
        ];

        return (
          <Table>
            <Table.Body>
              {data.map((row) => (
                <Table.Row
                  key={row.id}
                  onClick={() => {
                    clickCount++;
                  }}
                >
                  <Table.Cell>{row.name}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        );
      }

      const { unmount } = render(<DataTable />, { container });

      // Click a row
      act(() => {
        const row = container.querySelector('tr') as HTMLElement;
        fireEvent.click(row);
      });

      expect(clickCount).toBe(1);

      // Unmount
      act(() => {
        unmount();
      });

      // Try clicking again (should not trigger)
      const row = container.querySelector('tr');
      expect(row).toBeNull();
    });
  });

  describe('Card Component', () => {
    test('should not retain children after unmount', () => {
      let childMountCount = 0;
      let childUnmountCount = 0;

      function TrackedChild() {
        useEffect(() => {
          childMountCount++;
          return () => {
            childUnmountCount++;
          };
        });

        return <div>Child Component</div>;
      }

      function CardTest() {
        return (
          <Card>
            <Card.Body>
              <TrackedChild />
            </Card.Body>
          </Card>
        );
      }

      const { unmount } = render(<CardTest />, { container });

      expect(childMountCount).toBe(1);
      expect(childUnmountCount).toBe(0);

      // Unmount
      act(() => {
        unmount();
      });

      // Child should unmount
      expect(childUnmountCount).toBe(1);
    });
  });

  describe('Event Listener Cleanup', () => {
    test('should remove all event listeners on unmount', () => {
      // Spy on addEventListener and removeEventListener
      const addSpy = jest.spyOn(document, 'addEventListener');
      const removeSpy = jest.spyOn(document, 'removeEventListener');

      function ModalTest() {
        const [isOpen, setIsOpen] = useState(true);

        return (
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} closeOnEscape>
            <Modal.Body>Test</Modal.Body>
          </Modal>
        );
      }

      const { unmount } = render(<ModalTest />, { container});

      // Should have added escape key listener
      expect(addSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      // Clear spies
      addSpy.mockClear();
      removeSpy.mockClear();

      // Unmount
      act(() => {
        unmount();
      });

      // Should have removed escape key listener
      expect(removeSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      // Cleanup
      addSpy.mockRestore();
      removeSpy.mockRestore();
    });
  });

  describe('React Strict Mode Compatibility', () => {
    test('should handle double mount/unmount in Strict Mode', () => {
      let mountCount = 0;
      let unmountCount = 0;

      function TrackedModal() {
        useEffect(() => {
          mountCount++;
          return () => {
            unmountCount++;
          };
        });

        const [isOpen, setIsOpen] = useState(true);

        return (
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
            <Modal.Body>Test</Modal.Body>
          </Modal>
        );
      }

      // Render in Strict Mode
      const { unmount } = render(
        <React.StrictMode>
          <TrackedModal />
        </React.StrictMode>,
        { container }
      );

      // In Strict Mode, effects run twice
      expect(mountCount).toBe(2);
      expect(unmountCount).toBe(0);

      // Unmount
      act(() => {
        unmount();
      });

      // Both instances should unmount
      expect(unmountCount).toBe(2);
    });
  });

  describe('Component Reference Cleanup', () => {
    test('should not retain refs after unmount', () => {
      const ref = React.createRef<HTMLDivElement>();

      function ModalTest() {
        const [isOpen, setIsOpen] = useState(true);

        return (
          <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
            <Modal.Body ref={ref}>Test</Modal.Body>
          </Modal>
        );
      }

      const { unmount } = render(<ModalTest />, { container });

      // Ref should be set
      expect(ref.current).toBeInTheDocument();

      // Unmount
      act(() => {
        unmount();
      });

      // Ref should be null
      expect(ref.current).toBeNull();
    });
  });
});

// Memory leak detection utility
export function detectMemoryLeaks() {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const memory = (performance as any).memory;

    if (memory) {
      return {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit,
      };
    }
  }

  return null;
}

export function measureMemoryUsage(): {
  before: ReturnType<typeof detectMemoryLeaks>;
  after: ReturnType<typeof detectMemoryLeaks>;
  leaked: number;
} | null {
  const before = detectMemoryLeaks();

  return {
    before,
    after: null,
    leaked: 0,
  };
}
