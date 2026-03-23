// Simple test to isolate the import issue
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '@shared/ui/Toast/Toast';
import { ErrorBoundary } from '@shared/ui/ErrorBoundary/ErrorBoundary';
import { ReactFlowProvider } from 'reactflow';

// Simple wrapper without Apollo
function SimpleWrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <ReactFlowProvider>
            <ToastProvider>
              {children}
            </ToastProvider>
          </ReactFlowProvider>
        </QueryClientProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

describe('Simple Import Test', () => {
  it('should render a simple component with all providers', () => {
    render(
      <SimpleWrapper>
        <div>Test Content</div>
      </SimpleWrapper>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should import and render SelectGamePrompt', async () => {
    const { default: SelectGamePrompt } = await import('@shared/ui/SelectGamePrompt');
    
    render(
      <SimpleWrapper>
        <SelectGamePrompt message="测试消息" />
      </SimpleWrapper>
    );
    
    expect(screen.getByText('测试消息')).toBeInTheDocument();
  });

  it('should import and render ConfirmDialog', async () => {
    const { ConfirmDialog } = await import('@shared/ui/ConfirmDialog/ConfirmDialog');

    render(
      <SimpleWrapper>
        <ConfirmDialog
          open={true}
          onCancel={() => {}}
          onConfirm={() => {}}
          title="测试对话框"
          message="测试消息"
        />
      </SimpleWrapper>
    );

    expect(screen.getByText('测试对话框')).toBeInTheDocument();
  });
});
