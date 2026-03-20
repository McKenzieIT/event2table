/**
 * 测试工具库
 * Test Utilities
 * 
 * 提供统一的测试工具函数和包装器
 */

import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ReactNode } from 'react';

/**
 * 创建测试用的QueryClient
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * 测试包装器Props
 */
interface WrapperProps {
  children: ReactNode;
  queryClient?: QueryClient;
  initialRoute?: string;
}

/**
 * 全局Provider包装器
 */
export function AllProviders({ 
  children, 
  queryClient = createTestQueryClient(),
  initialRoute = '/'
}: WrapperProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

/**
 * 自定义render函数，自动包装Provider
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    queryClient?: QueryClient;
    initialRoute?: string;
  }
) {
  const { queryClient, initialRoute, ...renderOptions } = options || {};
  
  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders queryClient={queryClient} initialRoute={initialRoute}>
        {children}
      </AllProviders>
    ),
    ...renderOptions,
  });
}

/**
 * 等待异步操作完成
 */
export function waitForLoadingToFinish() {
  return new Promise(resolve => setTimeout(resolve, 0));
}

/**
 * Mock localStorage
 */
export function mockLocalStorage() {
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  };
  
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });
  
  return localStorageMock;
}

/**
 * Mock fetch
 */
export function mockFetch(data: any, ok = true) {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok,
      json: () => Promise.resolve(data),
      text: () => Promise.resolve(JSON.stringify(data)),
    } as Response)
  );
  
  return global.fetch;
}

/**
 * 清除所有Mock
 */
export function clearAllMocks() {
  vi.clearAllMocks();
  vi.resetAllMocks();
  vi.restoreAllMocks();
}

// 重新导出所有testing-library工具
export * from '@testing-library/react';
export { renderWithProviders as render };
