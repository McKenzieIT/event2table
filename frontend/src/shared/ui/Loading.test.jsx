/**
 * Loading Component Tests
 * 测试加载组件的所有功能
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Loading from './Loading';

describe('Loading Component', () => {
  describe('Rendering', () => {
    it('should render loading container', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.loading-container')).toBeInTheDocument();
    });

    it('should render spinner', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.loading-spinner')).toBeInTheDocument();
    });

    it('should render loading text', () => {
      render(<Loading />);
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should have data-testid attribute', () => {
      render(<Loading />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Spinner', () => {
    it('should render spinner-border element', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.spinner-border')).toBeInTheDocument();
    });

    it('should have text-primary class', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.text-primary')).toBeInTheDocument();
    });

    it('should have role="status"', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('[role="status"]')).toBeInTheDocument();
    });

    it('should have visually-hidden text', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.visually-hidden')).toHaveTextContent('Loading...');
    });
  });

  describe('Loading Text', () => {
    it('should display "加载中..." text', () => {
      render(<Loading />);
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should have loading-text class', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.loading-text')).toBeInTheDocument();
    });

    it('should be inside spinner container', () => {
      const { container } = render(<Loading />);
      const spinner = container.querySelector('.loading-spinner');
      expect(spinner).toContainElement(screen.getByText('加载中...'));
    });
  });

  describe('Accessibility', () => {
    it('should have role="status" on spinner', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.spinner-border')).toHaveAttribute('role', 'status');
    });

    it('should have visually-hidden text for screen readers', () => {
      const { container } = render(<Loading />);
      const hiddenText = container.querySelector('.visually-hidden');
      expect(hiddenText).toBeInTheDocument();
      expect(hiddenText).toHaveTextContent('Loading...');
    });
  });

  describe('Structure', () => {
    it('should have correct DOM structure', () => {
      const { container } = render(<Loading />);
      
      expect(container.querySelector('.loading-container')).toBeInTheDocument();
      expect(container.querySelector('.loading-container > .loading-spinner')).toBeInTheDocument();
      expect(container.querySelector('.loading-spinner > .spinner-border')).toBeInTheDocument();
      expect(container.querySelector('.loading-spinner > .loading-text')).toBeInTheDocument();
    });
  });

  describe('No Props', () => {
    it('should work without any props', () => {
      expect(() => render(<Loading />)).not.toThrow();
    });

    it('should render consistently without props', () => {
      const { container: container1 } = render(<Loading />);
      const { container: container2 } = render(<Loading />);
      
      expect(container1.innerHTML).toBe(container2.innerHTML);
    });
  });
});
