/**
 * Test to diagnose the exact cause of Element type is invalid errors
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { createElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactFlowProvider } from 'reactflow';
import { ToastProvider, ErrorBoundary } from '@shared/ui';

// Create test query client
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

describe('Provider Stack Diagnostics', () => {
  it('should render with all providers', () => {
    const queryClient = createTestQueryClient();

    const { container } = render(
      createElement(
        ErrorBoundary,
        null,
        createElement(
          BrowserRouter,
          null,
          createElement(
            QueryClientProvider,
            { client: queryClient },
            createElement(
              ReactFlowProvider,
              null,
              createElement(
                ToastProvider,
                null,
                createElement('div', null, 'Test Content')
              )
            )
          )
        )
      )
    );

    expect(container).toBeDefined();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});
