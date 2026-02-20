/**
 * PageLoader Component Tests
 * 测试页面加载组件的所有功能
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PageLoader } from './PageLoader';

describe('PageLoader Component', () => {
  describe('Rendering', () => {
    it('should render with default message', () => {
      render(<PageLoader />);
      expect(screen.getByText('加载中...')).toBeInTheDocument();
    });

    it('should render with custom message', () => {
      render(<PageLoader message="Please wait..." />);
      expect(screen.getByText('Please wait...')).toBeInTheDocument();
    });

    it('should render spinner', () => {
      render(<PageLoader />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should not render message when not provided', () => {
      render(<PageLoader message={undefined} />);
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });
  });

  describe('Full Page Mode', () => {
    it('should render overlay when fullPage is true', () => {
      const { container } = render(<PageLoader fullPage={true} />);
      expect(container.querySelector('.page-loader__overlay')).toBeInTheDocument();
    });

    it('should have full-page class when fullPage is true', () => {
      const { container } = render(<PageLoader fullPage={true} />);
      expect(container.querySelector('.page-loader--full')).toBeInTheDocument();
    });

    it('should not render overlay when fullPage is false', () => {
      const { container } = render(<PageLoader fullPage={false} />);
      expect(container.querySelector('.page-loader__overlay')).not.toBeInTheDocument();
    });

    it('should not have full-page class when fullPage is false', () => {
      const { container } = render(<PageLoader fullPage={false} />);
      expect(container.querySelector('.page-loader--full')).not.toBeInTheDocument();
    });

    it('should default to fullPage=true', () => {
      const { container } = render(<PageLoader />);
      expect(container.querySelector('.page-loader__overlay')).toBeInTheDocument();
    });
  });

  describe('Size', () => {
    it('should render with large size by default', () => {
      render(<PageLoader />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });

    it('should support small size', () => {
      render(<PageLoader size="sm" />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });

    it('should support medium size', () => {
      render(<PageLoader size="md" />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });

    it('should support large size', () => {
      render(<PageLoader size="lg" />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Message Display', () => {
    it('should display message below spinner', () => {
      render(<PageLoader message="Loading data..." />);
      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('should have message class', () => {
      const { container } = render(<PageLoader message="Test" />);
      expect(container.querySelector('.page-loader__message')).toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<PageLoader className="custom-loader" />);
      expect(container.querySelector('.custom-loader')).toBeInTheDocument();
    });

    it('should apply custom className when fullPage', () => {
      const { container } = render(<PageLoader fullPage={true} className="custom-loader" />);
      expect(container.querySelector('.custom-loader')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should be accessible with message', () => {
      render(<PageLoader message="Loading content" />);
      expect(screen.getByText('Loading content')).toBeInTheDocument();
    });

    it('should be accessible without message', () => {
      render(<PageLoader message={undefined} />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('Spinner Integration', () => {
    it('should render Spinner component', () => {
      render(<PageLoader />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should pass size prop to Spinner', () => {
      render(<PageLoader size="lg" />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });
  });
});
