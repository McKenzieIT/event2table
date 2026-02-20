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

    it('should render loading spinner', () => {
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
    it('should render spinner border', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.spinner-border')).toBeInTheDocument();
    });

    it('should have text-primary class', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.text-primary')).toBeInTheDocument();
    });

    it('should have role="status"', () => {
      const { container } = render(<Loading />);
      const spinnerBorder = container.querySelector('.spinner-border');
      expect(spinnerBorder).toHaveAttribute('role', 'status');
    });

    it('should have visually-hidden text', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.visually-hidden')).toHaveTextContent('Loading...');
    });
  });

  describe('Loading Text', () => {
    it('should render Chinese loading text', () => {
      render(<Loading />);
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should have loading-text class', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.loading-text')).toBeInTheDocument();
    });
  });

  describe('Structure', () => {
    it('should have correct DOM structure', () => {
      const { container } = render(<Loading />);
      
      expect(container.querySelector('.loading-container > .loading-spinner')).toBeInTheDocument();
      expect(container.querySelector('.loading-spinner > .spinner-border')).toBeInTheDocument();
      expect(container.querySelector('.loading-spinner > .loading-text')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be accessible', () => {
      render(<Loading />);
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should have screen reader text', () => {
      const { container } = render(<Loading />);
      const visuallyHidden = container.querySelector('.visually-hidden');
      expect(visuallyHidden).toHaveTextContent('Loading...');
    });
  });

  describe('No Props', () => {
    it('should render without any props', () => {
      const { container } = render(<Loading />);
      expect(container).toBeInTheDocument();
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should be a simple display component', () => {
      const { container } = render(<Loading />);
      expect(container.querySelector('.loading-container')).toBeInTheDocument();
    });
  });
});
