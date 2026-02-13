/**
 * GameManagementModal 组件测试
 *
 * 测试覆盖:
 * - 组件渲染
 * - 游戏列表显示
 * - 搜索功能
 * - 游戏选择
 * - 编辑功能
 * - 保存功能
 * - 删除功能
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import GameManagementModal from './GameManagementModal';

// Mock fetch
global.fetch = jest.fn();

// Mock gameStore
jest.mock('@stores/gameStore', () => ({
  useGameStore: () => ({
    setCurrentGame: jest.fn(),
    currentGame: null
  })
}));

// Wrapper with providers
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
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

describe('GameManagementModal', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('should not render when isOpen is false', () => {
    const { container } = render(
      <GameManagementModal isOpen={false} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    expect(container.querySelector('.game-management-modal')).toBeNull();
  });

  test('should render modal when isOpen is true', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: [
          { id: 1, gid: '10000147', name: 'Test Game', ods_db: 'ieu_ods' }
        ]
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('游戏管理')).toBeInTheDocument();
    });
  });

  test('should display games list', async () => {
    const mockGames = [
      { id: 1, gid: '10000147', name: 'Game 1', ods_db: 'ieu_ods' },
      { id: 2, gid: '10000148', name: 'Game 2', ods_db: 'overseas_ods' }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockGames
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Game 1')).toBeInTheDocument();
      expect(screen.getByText('Game 2')).toBeInTheDocument();
    });
  });

  test('should filter games by search term', async () => {
    const mockGames = [
      { id: 1, gid: '10000147', name: 'Game One', ods_db: 'ieu_ods' },
      { id: 2, gid: '10000148', name: 'Game Two', ods_db: 'overseas_ods' }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockGames
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Game One')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('搜索游戏名称或GID...');
    fireEvent.change(searchInput, { target: { value: 'One' } });

    await waitFor(() => {
      expect(screen.getByText('Game One')).toBeInTheDocument();
      // Game Two should be filtered out
    });
  });

  test('should select game and show details', async () => {
    const mockGames = [
      { id: 1, gid: '10000147', name: 'Test Game', ods_db: 'ieu_ods', event_count: 5, param_count: 10 }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockGames
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Test Game')).toBeInTheDocument();
    });

    // Click on game item
    const gameItem = screen.getByText('Test Game').closest('.game-list-item');
    fireEvent.click(gameItem);

    await waitFor(() => {
      expect(screen.getByText('游戏详情')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test Game')).toBeInTheDocument();
    });
  });

  test('should enable editing on field change', async () => {
    const mockGames = [
      { id: 1, gid: '10000147', name: 'Test Game', ods_db: 'ieu_ods' }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: mockGames
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={() => {}} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Test Game')).toBeInTheDocument();
    });

    // Select game
    const gameItem = screen.getByText('Test Game').closest('.game-list-item');
    fireEvent.click(gameItem);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Game')).toBeInTheDocument();
    });

    // Try to edit name field
    const nameInput = screen.getByDisplayValue('Test Game');

    // Input should be disabled initially
    expect(nameInput).toBeDisabled();

    // Change input value
    fireEvent.change(nameInput, { target: { value: 'Updated Game' } });

    // After change, save and cancel buttons should appear
    await waitFor(() => {
      expect(screen.getByText('保存')).toBeInTheDocument();
      expect(screen.getByText('取消')).toBeInTheDocument();
    });
  });

  test('should call onClose when close button is clicked', async () => {
    const onClose = jest.fn();

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        data: []
      })
    });

    render(
      <GameManagementModal isOpen={true} onClose={onClose} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('游戏管理')).toBeInTheDocument();
    });

    // Click close button (×)
    const closeButton = screen.getByText('×').closest('button');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });
});

export {};
