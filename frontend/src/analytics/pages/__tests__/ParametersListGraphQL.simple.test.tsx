/**
 * 简化的测试文件 - 用于调试渲染问题
 */

import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { gql } from '@apollo/client';
import React from 'react';

// Mock all dependencies FIRST
vi.mock('@/stores/gameStore', () => ({
  useGameStore: () => ({
    currentGame: { gid: 1, name: 'Test Game' },
  }),
}));

vi.mock('@shared/ui', () => ({
  Button: ({ children }: any) => <button>{children}</button>,
  Input: (props: any) => <input {...props} />,
  Select: ({ children }: any) => <select>{children}</select>,
  Badge: ({ children }: any) => <span>{children}</span>,
  Spinner: () => <div>Loading...</div>,
  SearchInput: (props: any) => <input placeholder="搜索..." {...props} />,
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  }),
  EmptyState: ({ title }: any) => <div>{title}</div>,
  SelectGamePrompt: ({ message }: any) => <div>{message}</div>,
  Skeleton: () => <div>Loading...</div>,
}));

vi.mock('@shared/components', () => ({
  NavLinkWithGameContext: ({ children }: any) => <a>{children}</a>,
}));

vi.mock('@/shared/components/VirtualList/OptimizedVirtualList', () => ({
  default: ({ items, renderItem, itemHeight, height, className }: any) => (
    <div className={className} style={{ height, overflow: 'auto' }}>
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
  default: () => null,
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Link: ({ children }: any) => <a>{children}</a>,
  };
});

vi.mock('@apollo/client/testing', () => ({
  MockedProvider: ({ children, mocks }: any) => {
    // Simple mock that just renders children
    return <div data-testid="mocked-provider">{children}</div>;
  },
}));

// Create a simple mock component
const SimpleComponent = () => {
  return <div>Test Component</div>;
};

describe('Debug Test', () => {
  it('should render simple component', () => {
    render(<SimpleComponent />);
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  it('should render with MockedProvider', () => {
    const GET_PARAMETERS_MANAGEMENT = gql`
      query GetParametersManagement($gameGid: Int!) {
        parametersManagement(gameGid: $gameGid) {
          id
          paramName
        }
      }
    `;

    const mocks = [
      {
        request: {
          query: GET_PARAMETERS_MANAGEMENT,
          variables: { gameGid: 1 },
        },
        result: {
          data: {
            parametersManagement: [
              { id: 1, paramName: 'param_1' },
            ],
          },
        },
      },
    ];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <SimpleComponent />
      </MockedProvider>
    );

    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });
});