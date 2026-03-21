/**
 * Minimal test to debug the rendering issue
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock all dependencies first
vi.mock('@/stores/gameStore', () => ({
  useGameStore: () => ({
    currentGame: { gid: 1, name: 'Test Game' },
  }),
}));

vi.mock('@shared/ui', () => ({
  Button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  Input: (props: any) => <input {...props} />,
  Select: ({ children, ...props }: any) => <select {...props}>{children}</select>,
  Badge: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  Spinner: ({ label }: any) => <div>{label}</div>,
  SearchInput: (props: any) => <input {...props} data-testid="search-input" />,
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  }),
  EmptyState: ({ icon, title, description }: any) => (
    <div>
      {icon}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  ),
  SelectGamePrompt: ({ message }: any) => <div>{message}</div>,
  Skeleton: () => <div className="skeleton">Loading...</div>,
}));

vi.mock('@shared/components', () => ({
  NavLinkWithGameContext: ({ to, children, ...props }: any) => (
    <a href={to} {...props}>{children}</a>
  ),
}));

vi.mock('@/shared/components/VirtualList/OptimizedVirtualList', () => ({
  default: ({ items, renderItem, itemHeight, height, className }: any) => (
    <div className={className} style={{ height, overflow: 'auto' }} data-testid="virtual-list">
      {items.map((item: any, index: number) => (
        <div key={index} style={{ height: itemHeight }}>
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  ),
}));

vi.mock('@/shared/utils/performanceMonitor', () => ({
  usePerformanceMonitor: vi.fn(),
}));

vi.mock('@analytics/components/parameters/ParameterDetailDrawer', () => ({
  default: ({ isOpen, onClose, parameter }: any) => {
    if (!isOpen) return null;
    return (
      <div data-testid="parameter-drawer">
        <h3>Parameter Detail</h3>
        <p>{parameter?.paramName}</p>
        <button onClick={onClose}>Close</button>
      </div>
    );
  },
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Link: ({ to, children, ...props }: any) => <a href={to} {...props}>{children}</a>,
  };
});

// Now import the component
import ParametersListGraphQL from '../ParametersListGraphQL';

describe('ParametersListGraphQL - Debug', () => {
  it('should import the component', () => {
    expect(ParametersListGraphQL).toBeDefined();
  });
});
