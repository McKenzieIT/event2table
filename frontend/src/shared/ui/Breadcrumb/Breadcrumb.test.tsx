/**
 * Breadcrumb Component Tests
 * 测试面包屑导航组件的所有功能
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Breadcrumb, { Breadcrumb as BreadcrumbComponent } from './Breadcrumb';

describe('Breadcrumb Component', () => {
  const mockItems = [
    { label: 'Home', to: '/' },
    { label: 'Products', to: '/products' },
    { label: 'Category', to: '/products/category' },
    { label: 'Product Details', active: true }
  ];

  const renderWithRouter = (component: React.ReactElement) => {
    return render(<BrowserRouter>{component}</BrowserRouter>);
  };

  describe('Rendering', () => {
    it('should render breadcrumb navigation', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('should render breadcrumb label', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      expect(screen.getByLabelText('面包屑导航')).toBeInTheDocument();
    });

    it('should render all breadcrumb items', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Products')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Product Details')).toBeInTheDocument();
    });
  });

  describe('Breadcrumb Items', () => {
    it('should render links for non-active items', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const homeLink = screen.getByText('Home').closest('a');
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should not render link for active item', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const activeItem = screen.getByText('Product Details');
      expect(activeItem.closest('a')).not.toBeInTheDocument();
      expect(activeItem).toHaveClass('breadcrumb-current');
    });

    it('should render active item with active class', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const activeItem = screen.getByText('Product Details');
      expect(activeItem).toHaveClass('breadcrumb-current');
    });

    it('should render non-active items as links', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const links = screen.getAllByRole('link');
      expect(links).toHaveLength(3); // Home, Products, Category
    });

    it('should render last item as active even without active prop', () => {
      const itemsWithoutActive = [
        { label: 'Home', to: '/' },
        { label: 'Page', to: '/page' }
      ];
      
      renderWithRouter(<BreadcrumbComponent items={itemsWithoutActive} />);
      
      const lastItem = screen.getByText('Page');
      expect(lastItem).toHaveClass('active');
    });
  });

  describe('Separators', () => {
    it('should render default separator (>)', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const separators = screen.getAllByText('>');
      expect(separators).toHaveLength(3);
    });

    it('should render custom separator', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} separator="/" />);
      
      const separators = screen.getAllByText('/');
      expect(separators).toHaveLength(3);
    });

    it('should not render separator after last item', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const activeItem = screen.getByText('Product Details');
      const parent = activeItem.parentElement;
      
      expect(parent?.textContent).not.toContain('>');
    });

    it('should render separator between items', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const breadcrumb = screen.getByRole('navigation');
      expect(breadcrumb.textContent).toContain('Home > Products > Category > Product Details');
    });
  });

  describe('Single Item', () => {
    it('should render single breadcrumb item', () => {
      const singleItem = [{ label: 'Home', active: true }];
      
      renderWithRouter(<BreadcrumbComponent items={singleItem} />);
      
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Home')).toHaveClass('breadcrumb-current');
    });

    it('should not render separator for single item', () => {
      const singleItem = [{ label: 'Home', active: true }];
      
      renderWithRouter(<BreadcrumbComponent items={singleItem} />);
      
      expect(screen.queryByText('>')).not.toBeInTheDocument();
    });
  });

  describe('Empty Items', () => {
    it('should render empty breadcrumb when items is empty', () => {
      renderWithRouter(<BreadcrumbComponent items={[]} />);
      
      const breadcrumb = screen.getByRole('navigation');
      expect(breadcrumb).toBeInTheDocument();
      expect(breadcrumb).toBeEmptyDOMElement();
    });
  });

  describe('Items without "to" property', () => {
    it('should render items without links when to is not provided', () => {
      const itemsWithoutTo = [
        { label: 'Section 1' },
        { label: 'Section 2', active: true }
      ];
      
      renderWithRouter(<BreadcrumbComponent items={itemsWithoutTo} />);
      
      const section1 = screen.getByText('Section 1');
      expect(section1.closest('a')).not.toBeInTheDocument();
    });

    it('should still render separator for items without to', () => {
      const itemsWithoutTo = [
        { label: 'Section 1' },
        { label: 'Section 2' }
      ];
      
      renderWithRouter(<BreadcrumbComponent items={itemsWithoutTo} />);
      
      expect(screen.getByText('>')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className to breadcrumb', () => {
      const { container } = renderWithRouter(
        <div className="custom-breadcrumb">
          <BreadcrumbComponent items={mockItems} />
        </div>
      );
      
      expect(container.querySelector('.custom-breadcrumb')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const nav = screen.getByRole('navigation');
      expect(nav).toHaveAttribute('aria-label', '面包屑导航');
    });

    it('should have ordered list structure', () => {
      const { container } = renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      expect(container.querySelector('ol')).toBeInTheDocument();
      expect(container.querySelector('.breadcrumb-list')).toBeInTheDocument();
    });

    it('should have list items', () => {
      const { container } = renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const listItems = container.querySelectorAll('li');
      expect(listItems).toHaveLength(4);
    });

    it('should have breadcrumb-item class on list items', () => {
      const { container } = renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const listItems = container.querySelectorAll('li');
      listItems.forEach(item => {
        expect(item).toHaveClass('breadcrumb-item');
      });
    });
  });

  describe('Navigation', () => {
    it('should navigate when clicking breadcrumb links', () => {
      renderWithRouter(<BreadcrumbComponent items={mockItems} />);
      
      const homeLink = screen.getByText('Home').closest('a');
      expect(homeLink).toHaveAttribute('href', '/');
      
      const productsLink = screen.getByText('Products').closest('a');
      expect(productsLink).toHaveAttribute('href', '/products');
    });
  });

  describe('Default Export', () => {
    it('should export default component', () => {
      expect(Breadcrumb).toBeDefined();
    });

    it('should render default export correctly', () => {
      renderWithRouter(<Breadcrumb items={mockItems} />);
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle items with special characters', () => {
      const itemsWithSpecialChars = [
        { label: 'Home & Away', to: '/' },
        { label: 'Product > Details', active: true }
      ];
      
      renderWithRouter(<BreadcrumbComponent items={itemsWithSpecialChars} />);
      
      expect(screen.getByText('Home & Away')).toBeInTheDocument();
      expect(screen.getByText('Product > Details')).toBeInTheDocument();
    });

    it('should handle items with very long text', () => {
      const longText = 'A'.repeat(100);
      const itemsWithLongText = [
        { label: longText, to: '/' }
      ];
      
      renderWithRouter(<BreadcrumbComponent items={itemsWithLongText} />);
      
      expect(screen.getByText(longText)).toBeInTheDocument();
    });
  });
});
