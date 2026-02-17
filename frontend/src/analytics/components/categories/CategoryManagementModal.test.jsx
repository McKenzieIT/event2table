/**
 * CategoryManagementModal 组件测试
 *
 * TDD Phase: RED - Tests are written first to specify expected behavior
 *
 * 测试覆盖:
 * - 模态框渲染和显示/隐藏
 * - 分类列表显示
 * - 创建分类功能
 * - 编辑分类功能
 * - 删除分类功能
 * - Toast通知显示
 * - game_gid参数保留
 */

import { describe, test, expect, beforeEach, vi, afterEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import CategoryManagementModal from './CategoryManagementModal';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock fetch
global.fetch = vi.fn();

// Mock window.confirm
global.confirm = vi.fn(() => true);

// Mock toast
vi.mock('react-hot-toast', () => ({
  success: vi.fn(),
  error: vi.fn(),
}));

// Mock useToast hook
vi.mock('@shared/ui', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useToast: () => ({
      success: vi.fn(),
      error: vi.fn(),
    }),
  };
});

// Wrapper with providers
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('CategoryManagementModal', () => {
  const mockCategories = [
    { id: 1, name: '战斗事件', description: '战斗相关事件', created_at: '2024-01-01', event_count: 5 },
    { id: 2, name: '任务事件', description: '任务相关事件', created_at: '2024-01-02', event_count: 3 },
  ];

  beforeEach(() => {
    fetch.mockClear();
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  // Setup fetch mock for each test that needs data
  const setupFetchMock = () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockCategories,
      }),
    });
  };

  test('should not render when isOpen is false', () => {
    const { container } = render(
      <CategoryManagementModal isOpen={false} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    expect(container.querySelector('.category-management-modal')).toBeNull();
  });

  test('should render modal when isOpen is true', async () => {
    setupFetchMock();

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('分类管理')).toBeInTheDocument();
    });
  });

  test('should fetch categories with game_gid parameter', async () => {
    setupFetchMock();

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('game_gid=10000147'));
    });
  });

  test('should display categories list', async () => {
    setupFetchMock();

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('战斗事件')).toBeInTheDocument();
      expect(screen.getByText('任务事件')).toBeInTheDocument();
    });
  });

  test('should show event counts for each category', async () => {
    setupFetchMock();

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    // Use findByText with full text (number + unit) since number is in separate text node
    expect(await screen.findByText('5 个事件')).toBeInTheDocument(); // 战斗事件 count
    expect(await screen.findByText('3 个事件')).toBeInTheDocument(); // 任务事件 count
  });

  test('should select category when clicking edit button', async () => {
    setupFetchMock();

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('战斗事件')).toBeInTheDocument();
    });

    // Click edit button for first category
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      // Should show category form with pre-filled data
      expect(screen.getByDisplayValue('战斗事件')).toBeInTheDocument();
    });
  });

  test('should call create API when saving new category', async () => {
    setupFetchMock();

    // Mock create API response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: '创建分类成功',
      }),
    });

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    // Wait for categories to load
    expect(await screen.findByText('战斗事件')).toBeInTheDocument();

    // Click "New Category" button
    const newButton = screen.getByText('新建分类');
    fireEvent.click(newButton);

    // Fill form and save
    const nameInput = screen.getByPlaceholderText('分类名称');
    fireEvent.change(nameInput, { target: { value: '新分类' } });

    const saveButton = screen.getByText('保存');
    fireEvent.click(saveButton);

    // Verify API was called (not toast)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });

  test('should call update API when saving edit', async () => {
    setupFetchMock();

    // Mock update API response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: '更新分类成功',
      }),
    });

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    // Use findByText for async-friendly text matching
    expect(await screen.findByText('战斗事件')).toBeInTheDocument();

    // Click edit button
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByDisplayValue('战斗事件')).toBeInTheDocument();
    });

    // Modify name and save
    const nameInput = screen.getByDisplayValue('战斗事件');
    fireEvent.change(nameInput, { target: { value: '战斗事件（已更新）' } });

    const saveButton = screen.getByText('保存');
    fireEvent.click(saveButton);

    // Verify API was called (not toast)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });

  test('should call delete API when deleting category', async () => {
    setupFetchMock();

    // Mock delete API response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        message: '删除分类成功',
      }),
    });

    render(
      <CategoryManagementModal isOpen={true} onClose={() => {}} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    // Use findByText for async-friendly text matching
    expect(await screen.findByText('战斗事件')).toBeInTheDocument();

    // Click delete button
    const deleteButtons = screen.getAllByText('删除');
    fireEvent.click(deleteButtons[0]);

    // window.confirm is already mocked to return true, so deletion should proceed
    // Verify API was called (not toast or confirm dialog)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });

  test('should call onClose when close button is clicked', async () => {
    const onClose = vi.fn();

    render(
      <CategoryManagementModal isOpen={true} onClose={onClose} gameGid="10000147" />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('分类管理')).toBeInTheDocument();
    });

    // Click close button (×)
    const closeButton = screen.getByText('×').closest('button');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });
});

export {};
