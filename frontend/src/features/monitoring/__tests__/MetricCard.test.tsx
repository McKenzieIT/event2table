/**
 * MetricCard Component Tests
 *
 * Tests for MetricCard component
 */

import { render, screen } from '@test/test-utils';
import { describe, it, expect } from 'vitest';

import { MetricCard } from '../components/MetricCard';

describe('MetricCard Component', () => {
  it('should render label and value', () => {
    render(<MetricCard label="Test Label" value={123.45} unit="ms" />);

    expect(screen.getByText('Test Label')).toBeInTheDocument();
    expect(screen.getByText('123.45')).toBeInTheDocument();
    expect(screen.getByText('ms')).toBeInTheDocument();
  });

  it('should render trend up', () => {
    render(<MetricCard label="Test" value={100} trend="up" trendValue={5.0} />);

    expect(screen.getByText('↑ 5.0% vs last period')).toBeInTheDocument();
    expect(screen.getByText('↑ 5.0% vs last period')).toHaveClass('text-green-500');
  });

  it('should render trend down', () => {
    render(<MetricCard label="Test" value={100} trend="down" trendValue={3.0} />);

    expect(screen.getByText('↓ 3.0% vs last period')).toBeInTheDocument();
    expect(screen.getByText('↓ 3.0% vs last period')).toHaveClass('text-red-500');
  });

  it('should render trend neutral', () => {
    render(<MetricCard label="Test" value={100} trend="neutral" trendValue={0.0} />);

    expect(screen.getByText('→ 0.0% vs last period')).toBeInTheDocument();
    expect(screen.getByText('→ 0.0% vs last period')).toHaveClass('text-gray-400');
  });

  it('should render icon when provided', () => {
    const icon = <span data-testid="test-icon">Icon</span>;
    render(<MetricCard label="Test" value={100} icon={icon} />);

    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <MetricCard label="Test" value={100} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });
});
