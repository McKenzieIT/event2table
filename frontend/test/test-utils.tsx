/**
 * 测试工具库
 * Test Utilities
 * 
 * 提供统一的测试工具函数和包装器
 */

import { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client/react';
import { ToastProvider } from '@shared/ui/Toast/Toast';
import { ErrorBoundary } from '@shared/ui/ErrorBoundary/ErrorBoundary';
import client from '@shared/apollo/client';
import { ReactFlowProvider } from 'reactflow';
import { vi } from 'vitest';

// ============================================================================
// Mock Outlet Context Types
// ============================================================================

/**
 * Mock游戏数据类型
 * 匹配MainLayout中的GameData接口
 */
export interface MockGameData {
  id: number;
  gid: number;
  name: string;
  ods_db?: string;
}

/**
 * Mock Outlet Context类型
 * 匹配MainLayout中的OutletContextType接口
 */
export interface MockOutletContext {
  currentGame: MockGameData | null;
  setCurrentGame: (game: MockGameData) => void;
}

/**
 * 默认mock游戏数据
 */
export const DEFAULT_MOCK_GAME: MockGameData = {
  id: 1,
  gid: 10000147,
  name: 'Test Game',
  ods_db: 'ieu_ods',
};

/**
 * 创建mock游戏上下文
 * 
 * 用于在测试中模拟useOutletContext返回值
 * 
 * @param overrides - 覆盖默认值的属性
 * @returns MockOutletContext对象
 * 
 * @example
 * // 在测试文件中使用vi.mock
 * vi.mock('react-router-dom', async () => {
 *   const actual = await vi.importActual('react-router-dom');
 *   return {
 *     ...actual,
 *     useOutletContext: () => createMockGameContext(),
 *   };
 * });
 * 
 * @example
 * // 模拟无游戏上下文
 * vi.mock('react-router-dom', async () => {
 *   const actual = await vi.importActual('react-router-dom');
 *   return {
 *     ...actual,
 *     useOutletContext: () => createMockGameContext({ currentGame: null }),
 *   };
 * });
 */
export function createMockGameContext(
  overrides: Partial<MockOutletContext> = {}
): MockOutletContext {
  const setCurrentGame = vi.fn();
  return {
    currentGame: DEFAULT_MOCK_GAME,
    setCurrentGame,
    ...overrides,
  };
}

/**
 * 创建mock游戏数据
 * @param overrides - 覆盖默认值的属性
 * @returns MockGameData对象
 */
export function createMockGameData(
  overrides: Partial<MockGameData> = {}
): MockGameData {
  return {
    ...DEFAULT_MOCK_GAME,
    ...overrides,
  };
}

// ============================================================================
// useOutletContext Mock Helper
// ============================================================================

/**
 * 创建可变的useOutletContext mock
 * 
 * 用于需要在测试中动态修改context的场景
 * 
 * @returns 包含mockOutletContext函数和mock对象的对象
 * 
 * @example
 * // 在测试文件顶部
 * const { mockOutletContext, mockOutletContextFn } = createMutableOutletContext();
 * 
 * vi.mock('react-router-dom', async () => {
 *   const actual = await vi.importActual('react-router-dom');
 *   return {
 *     ...actual,
 *     useOutletContext: () => mockOutletContextFn(),
 *   };
 * });
 * 
 * // 在测试中修改context
 * mockOutletContext({ currentGame: null });
 */
export function createMutableOutletContext() {
  const mockFn = vi.fn();
  
  // 默认返回有游戏上下文
  mockFn.mockReturnValue(createMockGameContext());
  
  return {
    /** 调用mockFn获取当前context */
    mockOutletContextFn: mockFn,
    /** 设置新的context值 */
    mockOutletContext: (overrides: Partial<MockOutletContext> = {}) => {
      mockFn.mockReturnValue(createMockGameContext(overrides));
    },
    /** 重置为默认context */
    resetOutletContext: () => {
      mockFn.mockReturnValue(createMockGameContext());
    },
  };
}

// ============================================================================
// Provider Components
// ============================================================================

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
 * Provider 顺序与 main.tsx 保持一致
 */
export function AllProviders({ 
  children, 
  queryClient = createTestQueryClient(),
  initialRoute = '/',
}: WrapperProps) {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ApolloProvider client={client}>
          <QueryClientProvider client={queryClient}>
            <ReactFlowProvider>
              <ToastProvider>
                {children}
              </ToastProvider>
            </ReactFlowProvider>
          </QueryClientProvider>
        </ApolloProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

/**
 * Provider包装器（不包含ApolloProvider）
 * 用于需要使用MockedProvider的GraphQL测试
 */
export function ProvidersWithoutApollo({ 
  children, 
  queryClient = createTestQueryClient(),
  initialRoute = '/',
}: WrapperProps) {
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
 * 自定义renderHook函数，自动包装Provider
 * 
 * 解决useLocation等hooks需要Router上下文的问题
 */
export function renderHookWithProviders<Result, Props>(
  hook: (props: Props) => Result,
  options?: {
    queryClient?: QueryClient;
    initialRoute?: string;
  }
) {
  const { queryClient, initialRoute } = options || {};
  
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AllProviders queryClient={queryClient} initialRoute={initialRoute}>
      {children}
    </AllProviders>
  );
  
  return renderHook(hook, { wrapper });
}

/**
 * 用于GraphQL测试的render函数（不包含ApolloProvider）
 * 需要配合MockedProvider使用
 */
export function renderWithMockedApollo(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    queryClient?: QueryClient;
    initialRoute?: string;
  }
) {
  const { queryClient, initialRoute, ...renderOptions } = options || {};
  
  return render(ui, {
    wrapper: ({ children }) => (
      <ProvidersWithoutApollo queryClient={queryClient} initialRoute={initialRoute}>
        {children}
      </ProvidersWithoutApollo>
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
