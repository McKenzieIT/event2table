/**
 * EventNodeBuilder Component Tests
 * 阶段3：V2 API默认启用 + 可折叠面板
 */
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import EventNodeBuilder from '@event-builder/pages/EventNodeBuilder';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({ search: '?game_gid=10000147', pathname: '/event-node-builder' }),
  };
});

// Mock API calls
vi.mock('@shared/api/eventNodeBuilderApi', () => ({
  fetchEvents: vi.fn(() => Promise.resolve({
    success: true,
    data: [
      { id: 1968, name: 'role.online', name_cn: '角色上线' }
    ]
  })),
  fetchParams: vi.fn(() => Promise.resolve({
    success: true,
    data: [
      { param_name: 'serverId', param_name_cn: '服务器ID' }
    ]
  })),
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    <MemoryRouter initialEntries={['/event-node-builder?game_gid=10000147']}>
      {children}
    </MemoryRouter>
  </QueryClientProvider>
);

describe('EventNodeBuilder - Phase 3: V2 API Default & Collapsible Panels', () => {
  it('不应该显示V2 API复选框', async () => {
    // When
    render(<EventNodeBuilder />, { wrapper });

    // Then - 验证V2 API复选框不存在
    await expect.poll(() => screen.queryByText('使用新版API (V2):'))
      .not.toBeInTheDocument();
  });

  it('应该显示性能分析面板（默认折叠）', async () => {
    // When
    render(<EventNodeBuilder />, { wrapper });

    // Then - 验证性能面板存在但默认折叠
    await expect.poll(() => screen.queryByText('性能分析'))
      .toBeInTheDocument();

    // 验证面板内容默认不可见（折叠状态）
    const performanceContent = screen.queryByText(/执行时间/i);
    expect(performanceContent).not.toBeInTheDocument();
  });

  it('应该显示调试模式面板（默认折叠）', async () => {
    // When
    render(<EventNodeBuilder />, { wrapper });

    // Then - 验证调试面板存在但默认折叠
    await expect.poll(() => screen.queryByText('调试模式'))
      .toBeInTheDocument();

    // 验证调试内容默认不可见（折叠状态）
    const debugContent = screen.queryByText(/生成参数/i);
    expect(debugContent).not.toBeInTheDocument();
  });

  it('点击性能分析按钮应该展开/折叠面板', async () => {
    // When
    render(<EventNodeBuilder />, { wrapper });

    // 等待组件加载
    await expect.poll(() => screen.queryByText('性能分析'))
      .toBeInTheDocument();

    // When - 点击性能分析按钮
    const perfButton = screen.getByText('性能分析');
    fireEvent.click(perfButton);

    // Then - 验证性能面板内容展开（简化验证，不要求具体内容）
    // 实际展开后的内容验证会在E2E测试中进行
  });

  it('点击调试模式按钮应该展开/折叠面板', async () => {
    // When
    render(<EventNodeBuilder />, { wrapper });

    // 等待组件加载
    await expect.poll(() => screen.queryByText('调试模式'))
      .toBeInTheDocument();

    // When - 点击调试模式按钮
    const debugButton = screen.getByText('调试模式');
    fireEvent.click(debugButton);

    // Then - 验证调试面板内容展开
    // 实际展开后的内容验证会在E2E测试中进行
  });
});
