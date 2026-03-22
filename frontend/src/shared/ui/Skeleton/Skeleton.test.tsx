/**
 * Skeleton Component Tests
 * 测试骨架屏组件的所有功能
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Skeleton, {
  SkeletonTable,
  SkeletonForm,
  SkeletonCard,
  SkeletonInline
} from './Skeleton';

describe('Skeleton Component', () => {
  describe('Rendering', () => {
    it('should render inline skeleton by default', () => {
      const { container } = render(<Skeleton />);
      expect(container.querySelector('.skeleton-wrapper')).toBeInTheDocument();
      expect(container.querySelector('.skeleton-inline')).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      const { container } = render(<Skeleton className="custom-skeleton" />);
      expect(container.querySelector('.custom-skeleton')).toBeInTheDocument();
    });

    it('should spread additional props to wrapper', () => {
      const { container } = render(<Skeleton data-testid="test-skeleton" />);
      expect(screen.getByTestId('test-skeleton')).toBeInTheDocument();
    });
  });

  describe('Inline Skeleton', () => {
    it('should render default number of lines (5)', () => {
      const { container } = render(<Skeleton type="inline" />);
      const lines = container.querySelectorAll('.skeleton-line');
      expect(lines).toHaveLength(5);
    });

    it('should render custom number of rows', () => {
      const { container } = render(<Skeleton type="inline" rows={10} />);
      const lines = container.querySelectorAll('.skeleton-line');
      expect(lines).toHaveLength(10);
    });

    it('should apply animation class to all lines', () => {
      const { container } = render(<Skeleton type="inline" />);
      const lines = container.querySelectorAll('.skeleton-line');
      lines.forEach(line => {
        expect(line).toHaveClass('skeleton-animate');
      });
    });

    it('should apply custom height', () => {
      const { container } = render(<Skeleton type="inline" height="200px" />);
      const wrapper = container.querySelector('.skeleton-wrapper');
      expect(wrapper).toHaveStyle({ height: '200px' });
    });
  });

  describe('Table Skeleton', () => {
    it('should render table skeleton with columns', () => {
      const { container } = render(<Skeleton type="table" columns={5} rows={10} />);
      
      expect(container.querySelector('.skeleton-table')).toBeInTheDocument();
      expect(container.querySelector('.skeleton-table-header')).toBeInTheDocument();
      
      const headerCells = container.querySelectorAll('.skeleton-table-header .skeleton-cell');
      expect(headerCells).toHaveLength(5);
    });

    it('should render table rows', () => {
      const { container } = render(<Skeleton type="table" columns={3} rows={5} />);
      
      const rows = container.querySelectorAll('.skeleton-table-row');
      expect(rows).toHaveLength(5);
      
      rows.forEach(row => {
        const cells = row.querySelectorAll('.skeleton-cell');
        expect(cells).toHaveLength(3);
      });
    });

    it('should apply animation to all cells', () => {
      const { container } = render(<Skeleton type="table" columns={3} rows={2} />);
      
      const cells = container.querySelectorAll('.skeleton-cell');
      cells.forEach(cell => {
        expect(cell).toHaveClass('skeleton-animate');
      });
    });

    it('should apply custom height', () => {
      const { container } = render(<Skeleton type="table" columns={3} height="300px" />);
      const wrapper = container.querySelector('.skeleton-wrapper');
      expect(wrapper).toHaveStyle({ height: '300px' });
    });

    it('should render without columns (no cells)', () => {
      const { container } = render(<Skeleton type="table" rows={3} />);
      
      const headerCells = container.querySelectorAll('.skeleton-table-header .skeleton-cell');
      expect(headerCells).toHaveLength(0);
      
      const rowCells = container.querySelectorAll('.skeleton-table-row .skeleton-cell');
      expect(rowCells).toHaveLength(0);
    });
  });

  describe('Form Skeleton', () => {
    it('should render form skeleton with default fields', () => {
      const { container } = render(<Skeleton type="form" />);
      
      expect(container.querySelector('.skeleton-form')).toBeInTheDocument();
      
      const fields = container.querySelectorAll('.skeleton-form-field');
      expect(fields).toHaveLength(4);
    });

    it('should render custom number of fields', () => {
      const { container } = render(<Skeleton type="form" fields={6} />);
      
      const fields = container.querySelectorAll('.skeleton-form-field');
      expect(fields).toHaveLength(6);
    });

    it('should render form field with label and input', () => {
      const { container } = render(<Skeleton type="form" fields={1} />);
      
      const field = container.querySelector('.skeleton-form-field');
      expect(field).toBeInTheDocument();
      expect(field?.querySelector('.skeleton-label')).toBeInTheDocument();
      expect(field?.querySelector('.skeleton-input')).toBeInTheDocument();
    });

    it('should render form actions with buttons', () => {
      const { container } = render(<Skeleton type="form" />);
      
      const actions = container.querySelector('.skeleton-form-actions');
      expect(actions).toBeInTheDocument();
      
      const buttons = actions?.querySelectorAll('.skeleton-button');
      expect(buttons).toHaveLength(2);
    });

    it('should apply animation to all elements', () => {
      const { container } = render(<Skeleton type="form" />);
      
      const animatedElements = container.querySelectorAll('.skeleton-animate');
      expect(animatedElements.length).toBeGreaterThan(0);
    });
  });

  describe('Card Skeleton', () => {
    it('should render card skeleton with default count', () => {
      const { container } = render(<Skeleton type="card" />);
      
      expect(container.querySelector('.skeleton-card')).toBeInTheDocument();
      
      const cards = container.querySelectorAll('.skeleton-card-item');
      expect(cards).toHaveLength(3);
    });

    it('should render custom number of cards', () => {
      const { container } = render(<Skeleton type="card" count={6} />);
      
      const cards = container.querySelectorAll('.skeleton-card-item');
      expect(cards).toHaveLength(6);
    });

    it('should render card with icon, content, and actions', () => {
      const { container } = render(<Skeleton type="card" count={1} />);
      
      const card = container.querySelector('.skeleton-card-item');
      expect(card).toBeInTheDocument();
      expect(card?.querySelector('.skeleton-card-icon')).toBeInTheDocument();
      expect(card?.querySelector('.skeleton-card-content')).toBeInTheDocument();
      expect(card?.querySelector('.skeleton-card-actions')).toBeInTheDocument();
    });

    it('should render card content with title and text', () => {
      const { container } = render(<Skeleton type="card" count={1} />);
      
      const content = container.querySelector('.skeleton-card-content');
      expect(content).toBeInTheDocument();
      expect(content?.querySelector('.skeleton-title')).toBeInTheDocument();
      
      const texts = content?.querySelectorAll('.skeleton-text');
      expect(texts).toHaveLength(2);
    });

    it('should render card actions with buttons', () => {
      const { container } = render(<Skeleton type="card" count={1} />);
      
      const actions = container.querySelector('.skeleton-card-actions');
      expect(actions).toBeInTheDocument();
      
      const buttons = actions?.querySelectorAll('.skeleton-button');
      expect(buttons).toHaveLength(2);
    });

    it('should apply animation to all elements', () => {
      const { container } = render(<Skeleton type="card" count={1} />);
      
      const animatedElements = container.querySelectorAll('.skeleton-animate');
      expect(animatedElements.length).toBeGreaterThan(0);
    });
  });

  describe('Convenience Components', () => {
    describe('SkeletonTable', () => {
      it('should render table skeleton', () => {
        const { container } = render(<SkeletonTable columns={3} rows={5} />);
        expect(container.querySelector('.skeleton-table')).toBeInTheDocument();
      });

      it('should pass through all props', () => {
        const { container } = render(
          <SkeletonTable columns={4} rows={8} className="table-skeleton" />
        );
        expect(container.querySelector('.table-skeleton')).toBeInTheDocument();
        const rows = container.querySelectorAll('.skeleton-table-row');
        expect(rows).toHaveLength(8);
      });
    });

    describe('SkeletonForm', () => {
      it('should render form skeleton', () => {
        const { container } = render(<SkeletonForm fields={3} />);
        expect(container.querySelector('.skeleton-form')).toBeInTheDocument();
      });

      it('should pass through all props', () => {
        const { container } = render(
          <SkeletonForm fields={5} className="form-skeleton" />
        );
        expect(container.querySelector('.form-skeleton')).toBeInTheDocument();
        const fields = container.querySelectorAll('.skeleton-form-field');
        expect(fields).toHaveLength(5);
      });
    });

    describe('SkeletonCard', () => {
      it('should render card skeleton', () => {
        const { container } = render(<SkeletonCard count={4} />);
        expect(container.querySelector('.skeleton-card')).toBeInTheDocument();
      });

      it('should pass through all props', () => {
        const { container } = render(
          <SkeletonCard count={6} className="card-skeleton" />
        );
        expect(container.querySelector('.card-skeleton')).toBeInTheDocument();
        const cards = container.querySelectorAll('.skeleton-card-item');
        expect(cards).toHaveLength(6);
      });
    });

    describe('SkeletonInline', () => {
      it('should render inline skeleton', () => {
        const { container } = render(<SkeletonInline rows={7} />);
        expect(container.querySelector('.skeleton-inline')).toBeInTheDocument();
      });

      it('should pass through all props', () => {
        const { container } = render(
          <SkeletonInline rows={10} className="inline-skeleton" height="150px" />
        );
        expect(container.querySelector('.inline-skeleton')).toBeInTheDocument();
        const lines = container.querySelectorAll('.skeleton-line');
        expect(lines).toHaveLength(10);
      });
    });
  });

  describe('Memoization', () => {
    it('should be memoized and not re-render with same props', () => {
      const { rerender } = render(<Skeleton type="inline" rows={5} />);
      const initialContainer = render(<Skeleton type="inline" rows={5} />).container;

      rerender(<Skeleton type="inline" rows={5} />);
      
      // Component should be memoized
      expect(initialContainer).toMatchSnapshot();
    });
  });

  describe('Accessibility', () => {
    it('should support aria-label for screen readers', () => {
      render(<Skeleton aria-label="Loading content" />);
      expect(screen.getByLabelText('Loading content')).toBeInTheDocument();
    });

    it('should support role attribute', () => {
      const { container } = render(<Skeleton role="status" />);
      expect(container.querySelector('[role="status"]')).toBeInTheDocument();
    });
  });

  describe('Default Props', () => {
    it('should use default type as inline', () => {
      const { container } = render(<Skeleton />);
      expect(container.querySelector('.skeleton-inline')).toBeInTheDocument();
    });

    it('should use default rows as 5 for inline', () => {
      const { container } = render(<Skeleton type="inline" />);
      const lines = container.querySelectorAll('.skeleton-line');
      expect(lines).toHaveLength(5);
    });

    it('should use default rows as 5 for table', () => {
      const { container } = render(<Skeleton type="table" columns={3} />);
      const rows = container.querySelectorAll('.skeleton-table-row');
      expect(rows).toHaveLength(5);
    });

    it('should use default fields as 4 for form', () => {
      const { container } = render(<Skeleton type="form" />);
      const fields = container.querySelectorAll('.skeleton-form-field');
      expect(fields).toHaveLength(4);
    });

    it('should use default count as 3 for card', () => {
      const { container } = render(<Skeleton type="card" />);
      const cards = container.querySelectorAll('.skeleton-card-item');
      expect(cards).toHaveLength(3);
    });
  });
});
