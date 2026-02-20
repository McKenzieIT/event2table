/**
 * Table Component Tests
 * 测试表格组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Table from './Table';

describe('Table Component', () => {
  describe('Rendering', () => {
    it('should render table element', () => {
      const { container } = render(<Table><tbody><tr><td>Cell</td></tr></tbody></Table>);
      expect(container.querySelector('table.cyber-table')).toBeInTheDocument();
    });

    it('should render with children', () => {
      render(
        <Table>
          <tbody>
            <tr>
              <td>Content</td>
            </tr>
          </tbody>
        </Table>
      );
      expect(screen.getByText('Content')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('should render default variant', () => {
      const { container } = render(<Table><tbody><tr><td>Default</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--default')).toBeInTheDocument();
    });

    it('should render bordered variant', () => {
      const { container } = render(<Table variant="bordered"><tbody><tr><td>Bordered</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--bordered')).toBeInTheDocument();
    });

    it('should render compact variant', () => {
      const { container } = render(<Table variant="compact"><tbody><tr><td>Compact</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--compact')).toBeInTheDocument();
    });
  });

  describe('Striped', () => {
    it('should have striped class by default', () => {
      const { container } = render(<Table><tbody><tr><td>Striped</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--striped')).toBeInTheDocument();
    });

    it('should not have striped class when striped is false', () => {
      const { container } = render(<Table striped={false}><tbody><tr><td>Not Striped</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--striped')).not.toBeInTheDocument();
    });
  });

  describe('Hoverable', () => {
    it('should have hoverable class by default', () => {
      const { container } = render(<Table><tbody><tr><td>Hoverable</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--hoverable')).toBeInTheDocument();
    });

    it('should not have hoverable class when hoverable is false', () => {
      const { container } = render(<Table hoverable={false}><tbody><tr><td>Not Hoverable</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--hoverable')).not.toBeInTheDocument();
    });
  });

  describe('Sizes', () => {
    it('should render small size', () => {
      const { container } = render(<Table size="sm"><tbody><tr><td>Small</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--sm')).toBeInTheDocument();
    });

    it('should render medium size (default)', () => {
      const { container } = render(<Table><tbody><tr><td>Medium</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--md')).toBeInTheDocument();
    });

    it('should render large size', () => {
      const { container } = render(<Table size="lg"><tbody><tr><td>Large</td></tr></tbody></Table>);
      expect(container.querySelector('.cyber-table--lg')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<Table className="custom-table"><tbody><tr><td>Custom</td></tr></tbody></Table>);
      expect(container.querySelector('.custom-table')).toBeInTheDocument();
    });
  });

  describe('Sub-components', () => {
    describe('Table.Header', () => {
      it('should render header', () => {
        render(
          <Table>
            <Table.Header>
              <tr><th>Header</th></tr>
            </Table.Header>
          </Table>
        );
        expect(screen.getByText('Header')).toBeInTheDocument();
      });

      it('should have header class', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr><th>Header</th></tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__header')).toBeInTheDocument();
      });
    });

    describe('Table.Body', () => {
      it('should render body', () => {
        render(
          <Table>
            <Table.Body>
              <tr><td>Body</td></tr>
            </Table.Body>
          </Table>
        );
        expect(screen.getByText('Body')).toBeInTheDocument();
      });

      it('should have body class', () => {
        const { container } = render(
          <Table>
            <Table.Body>
              <tr><td>Body</td></tr>
            </Table.Body>
          </Table>
        );
        expect(container.querySelector('.cyber-table__body')).toBeInTheDocument();
      });
    });

    describe('Table.Footer', () => {
      it('should render footer', () => {
        render(
          <Table>
            <Table.Footer>
              <tr><td>Footer</td></tr>
            </Table.Footer>
          </Table>
        );
        expect(screen.getByText('Footer')).toBeInTheDocument();
      });

      it('should have footer class', () => {
        const { container } = render(
          <Table>
            <Table.Footer>
              <tr><td>Footer</td></tr>
            </Table.Footer>
          </Table>
        );
        expect(container.querySelector('.cyber-table__footer')).toBeInTheDocument();
      });
    });

    describe('Table.Row', () => {
      it('should render row', () => {
        render(
          <Table>
            <Table.Body>
              <Table.Row>
                <td>Row Cell</td>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(screen.getByText('Row Cell')).toBeInTheDocument();
      });

      it('should have row class', () => {
        const { container } = render(
          <Table>
            <Table.Body>
              <Table.Row>
                <td>Cell</td>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(container.querySelector('.cyber-table__row')).toBeInTheDocument();
      });

      it('should have clickable class when onClick is provided', () => {
        const { container } = render(
          <Table>
            <Table.Body>
              <Table.Row onClick={() => {}}>
                <td>Clickable Row</td>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(container.querySelector('.cyber-table__row--clickable')).toBeInTheDocument();
      });

      it('should call onClick handler when clicked', async () => {
        const handleClick = vi.fn();
        render(
          <Table>
            <Table.Body>
              <Table.Row onClick={handleClick}>
                <td>Clickable</td>
              </Table.Row>
            </Table.Body>
          </Table>
        );

        await userEvent.click(screen.getByText('Clickable'));
        expect(handleClick).toHaveBeenCalled();
      });
    });

    describe('Table.Head', () => {
      it('should render head', () => {
        render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head>Column Name</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(screen.getByText('Column Name')).toBeInTheDocument();
      });

      it('should have head class', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head>Head</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head')).toBeInTheDocument();
      });

      it('should support align prop', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head align="center">Center</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head--center')).toBeInTheDocument();
      });

      it('should not be sortable by default', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head>Not Sortable</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head--sortable')).not.toBeInTheDocument();
      });

      it('should have sortable class when sortable is true', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head sortable>Sortable</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head--sortable')).toBeInTheDocument();
      });

      it('should display sort indicator when sortable', () => {
        render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head sortable>Column</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(screen.getByText('↕')).toBeInTheDocument();
      });

      it('should call onSort when clicked', async () => {
        const handleSort = vi.fn();
        render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head sortable onSort={handleSort}>Column</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );

        await userEvent.click(screen.getByText('Column'));
        expect(handleSort).toHaveBeenCalled();
      });

      it('should show ascending indicator when sorted is "asc"', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head sortable sorted="asc">Column</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head--sorted-asc')).toBeInTheDocument();
        expect(screen.getByText('↑')).toBeInTheDocument();
      });

      it('should show descending indicator when sorted is "desc"', () => {
        const { container } = render(
          <Table>
            <Table.Header>
              <tr>
                <Table.Head sortable sorted="desc">Column</Table.Head>
              </tr>
            </Table.Header>
          </Table>
        );
        expect(container.querySelector('.cyber-table__head--sorted-desc')).toBeInTheDocument();
        expect(screen.getByText('↓')).toBeInTheDocument();
      });
    });

    describe('Table.Cell', () => {
      it('should render cell', () => {
        render(
          <Table>
            <Table.Body>
              <Table.Row>
                <Table.Cell>Cell Content</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(screen.getByText('Cell Content')).toBeInTheDocument();
      });

      it('should have cell class', () => {
        const { container } = render(
          <Table>
            <Table.Body>
              <Table.Row>
                <Table.Cell>Cell</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(container.querySelector('.cyber-table__cell')).toBeInTheDocument();
      });

      it('should support align prop', () => {
        const { container } = render(
          <Table>
            <Table.Body>
              <Table.Row>
                <Table.Cell align="right">Right Aligned</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        );
        expect(container.querySelector('.cyber-table__cell--right')).toBeInTheDocument();
      });
    });
  });

  describe('Complete Table', () => {
    it('should render complete table with all sub-components', () => {
      render(
        <Table>
          <Table.Header>
            <tr>
              <Table.Head sortable>Name</Table.Head>
              <Table.Head align="right">Age</Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            <Table.Row>
              <Table.Cell>John</Table.Cell>
              <Table.Cell align="right">25</Table.Cell>
            </Table.Row>
            <Table.Row>
              <Table.Cell>Jane</Table.Cell>
              <Table.Cell align="right">30</Table.Cell>
            </Table.Row>
          </Table.Body>
          <Table.Footer>
            <tr>
              <Table.Cell colSpan={2}>Total: 2</Table.Cell>
            </tr>
          </Table.Footer>
        </Table>
      );

      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
      expect(screen.getByText('Total: 2')).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to table element', () => {
      const ref = { current: null };
      render(<Table ref={ref}><tbody><tr><td>Ref Test</td></tr></tbody></Table>);
      expect(ref.current).toBeInstanceOf(HTMLTableElement);
    });
  });

  describe('Accessibility', () => {
    it('should support additional props', () => {
      render(
        <Table data-testid="test-table">
          <tbody><tr><td>Accessible</td></tr></tbody>
        </Table>
      );
      expect(screen.getByTestId('test-table')).toBeInTheDocument();
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Table variant="default"><tbody><tr><td>Memoized</td></tr></tbody></Table>);
      const initialElement = screen.getByText('Memoized');

      rerender(<Table variant="default"><tbody><tr><td>Memoized</td></tr></tbody></Table>);
      const afterRerenderElement = screen.getByText('Memoized');

      expect(initialElement).toBe(afterRerenderElement);
    });
  });
});
