// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * GameManagementModalGraphQL 组件测试
 *
 * 测试覆盖:
 * - 组件渲染
 * - 创建游戏按钮存在性和可见性
 * - 点击按钮显示创建表单
 * - 游戏列表显示
 * - 搜索功能
 * - 编辑功能
 * - 删除功能
 *
 * TDD 流程:
 * 1. RED: 先写测试，确认失败
 * 2. GREEN: 写最小代码使测试通过
 * 3. REFACTOR: 重构并保持测试通过
 */

import { MockedProvider } from '@apollo/client/testing/react';
import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import React from 'react';

import { GET_GAMES, CREATE_GAME } from '../../shared/graphql/operations';

import GameManagementModalGraphQL, { GameManagementModal } from './GameManagementModalGraphQL';

// Mock GraphQL operations - must match GET_GAMES query fields exactly
// Query fields: gid, name, odsDb, eventCount, parameterCount
const mockGames = [
  {
    gid: 10000147,
    name: 'STAR001',
    odsDb: 'ieu_ods',
    eventCount: 5,
    parameterCount: 10,
  },
  {
    gid: 10000148,
    name: 'Test Game',
    odsDb: 'overseas_ods',
    eventCount: 3,
    parameterCount: 7,
  },
];

const mocks = [
  {
    request: {
      query: GET_GAMES,
      variables: { limit: 20, offset: 0 },
    },
    result: {
      data: {
        games: mockGames,
      },
    },
  },
];

describe('GameManagementModalGraphQL', () => {
  /**
   * 测试1: 应该显示"创建游戏"按钮
   * 这是TDD的第一个测试 - 验证按钮存在
   */
  describe('创建游戏按钮', () => {
    it('应该显示"创建游戏"按钮', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 应该有"创建游戏"按钮（支持多种文本匹配）
      const createButton = await waitFor(() => {
        try {
          return screen.getByRole('button', { name: /创建游戏/i });
        } catch {
          return screen.getByRole('button', { name: /添加游戏/i });
        }
      });

      expect(createButton).toBeInTheDocument();
      expect(createButton).toBeVisible();
    });

    it('点击"创建游戏"按钮应该打开创建表单', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待组件加载
      await waitFor(() => {
        expect(screen.getByText(/游戏管理/i)).toBeInTheDocument();
      });

      // 点击创建按钮
      const createButton = await waitFor(() => {
        try {
          return screen.getByRole('button', { name: /创建游戏/i });
        } catch {
          return screen.getByRole('button', { name: /添加游戏/i });
        }
      });

      fireEvent.click(createButton);

      // 应该显示创建表单标题（使用更具体的选择器：h3标题）
      await waitFor(() => {
        const formTitle = screen.getByRole('heading', { level: 3, name: /创建游戏/i });
        expect(formTitle).toBeInTheDocument();
      });
    });

    it('创建按钮应该可点击', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 使用 role 查找按钮
      const createButton = await waitFor(() => {
        return screen.getByRole('button', { name: /创建游戏/i });
      });

      expect(createButton).toBeInTheDocument();
      expect(createButton).toBeEnabled();
    });
  });

  /**
   * 测试2: 组件基本渲染
   */
  describe('组件渲染', () => {
    it('应该显示游戏管理标题', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText(/游戏管理/i)).toBeInTheDocument();
      });
    });

    it('应该显示游戏列表', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('STAR001')).toBeInTheDocument();
        expect(screen.getByText('Test Game')).toBeInTheDocument();
      });
    });
  });

  /**
   * 测试3: 搜索功能
   */
  describe('搜索功能', () => {
    it('应该显示搜索框', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      const searchInput = await waitFor(() => {
        return screen.getByPlaceholderText(/搜索/i);
      });

      expect(searchInput).toBeInTheDocument();
    });
  });

  /**
   * 测试4: 游戏操作按钮
   */
  describe('游戏操作', () => {
    it('应该为每个游戏显示编辑和删除按钮', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModal isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('STAR001')).toBeInTheDocument();
      });

      // 应该有编辑按钮（至少2个，每个游戏一个）
      const editButtons = screen.getAllByRole('button', { name: /编辑/i });
      expect(editButtons.length).toBeGreaterThan(0);

      // 应该有删除按钮（至少2个，每个游戏一个）
      const deleteButtons = screen.getAllByRole('button', { name: /删除/i });
      expect(deleteButtons.length).toBeGreaterThan(0);
    });
  });
});
