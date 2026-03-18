// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * GamesPageGraphQL 组件测试
 *
 * TDD 流程完成验证:
 * ✅ RED: 测试编写完成
 * ✅ GREEN: 按钮已存在于代码中
 * ✅ REFACTOR: 添加了 data-testid 和 aria-label
 *
 * 测试覆盖:
 * - 创建游戏按钮存在性和可见性
 * - 点击按钮打开创建对话框
 * - 对话框表单字段验证
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import GamesPageGraphQL from './GamesPageGraphQL';
import { GET_GAMES, CREATE_GAME } from '../graphql/queries/games';

// Mock game data
const mockGames = [
  {
    gid: 10000147,
    name: 'STAR001',
    odsDb: 'ieu_ods',
    eventCount: 5,
    parameterCount: 10,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
  },
  {
    gid: 90000001,
    name: 'E2E Test Game 1',
    odsDb: 'ieu_ods',
    eventCount: 0,
    parameterCount: 0,
    createdAt: '2026-03-01T00:00:00Z',
    updatedAt: '2026-03-01T00:00:00Z',
  },
];

// GraphQL mocks
const mocks = [
  {
    request: {
      query: GET_GAMES,
      variables: { limit: 100, offset: 0 },
    },
    result: {
      data: {
        games: mockGames,
      },
    },
  },
];

describe('GamesPageGraphQL - TDD 验证', () => {
  /**
   * 测试1: 验证创建游戏按钮存在（TDD RED → GREEN → REFACTOR 完成）
   */
  describe('创建游戏按钮', () => {
    it('应该显示"创建游戏"按钮', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      // 等待按钮出现
      const createButton = await waitFor(() => {
        return screen.getByRole('button', { name: /创建游戏/i });
      });

      // 验证按钮存在且可见
      expect(createButton).toBeInTheDocument();
      expect(createButton).toBeVisible();

      // 验证按钮有正确的 testid（REFACTOR 阶段添加）
      expect(createButton).toHaveAttribute('data-testid', 'create-game-button');

      // 验证按钮有可访问性标签
      expect(createButton).toHaveAttribute('aria-label', '创建游戏');
    });

    it('点击"创建游戏"按钮应该打开创建对话框', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      // 点击创建按钮
      const createButton = await waitFor(() => {
        return screen.getByRole('button', { name: /创建游戏/i });
      });

      fireEvent.click(createButton);

      // 验证对话框打开
      await waitFor(() => {
        const dialogTitle = screen.getByText('创建游戏');
        expect(dialogTitle).toBeInTheDocument();
      });

      // 验证表单字段存在
      expect(screen.getByLabelText('游戏GID')).toBeInTheDocument();
      expect(screen.getByLabelText('游戏名称')).toBeInTheDocument();
      expect(screen.getByLabelText('ODS数据库')).toBeInTheDocument();
    });

    it('创建按钮应该有加号图标', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      const createButton = await waitFor(() => {
        return screen.getByRole('button', { name: /创建游戏/i });
      });

      // 验证按钮有图标（MUI IconButton 或 Button with startIcon）
      const icon = createButton.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  /**
   * 测试2: 组件基本渲染
   */
  describe('组件渲染', () => {
    it('应该显示页面标题', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('游戏管理 (GraphQL版本)')).toBeInTheDocument();
      });
    });

    it('应该显示游戏列表', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('STAR001')).toBeInTheDocument();
        expect(screen.getByText('E2E Test Game 1')).toBeInTheDocument();
      });
    });

    it('应该显示GraphQL提示信息', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      await waitFor(() => {
        const alert = screen.getByText(/此页面使用GraphQL API获取数据/);
        expect(alert).toBeInTheDocument();
      });
    });
  });

  /**
   * 测试3: 游戏操作按钮
   */
  describe('游戏操作', () => {
    it('应该为每个游戏显示编辑和删除按钮', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText('STAR001')).toBeInTheDocument();
      });

      // 验证编辑按钮（通过 Tooltip）
      const editButtons = screen.getAllByLabelText('编辑');
      expect(editButtons.length).toBeGreaterThan(0);

      // 验证删除按钮（通过 Tooltip）
      const deleteButtons = screen.getAllByLabelText('删除');
      expect(deleteButtons.length).toBeGreaterThan(0);
    });

    it('应该有刷新按钮', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      const refreshButton = await waitFor(() => {
        return screen.getByLabelText('刷新');
      });

      expect(refreshButton).toBeInTheDocument();
    });
  });

  /**
   * 测试4: 表单验证
   */
  describe('创建表单', () => {
    it('应该验证必填字段', async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GamesPageGraphQL />
        </MockedProvider>
      );

      // 打开创建对话框
      const createButton = await waitFor(() => {
        return screen.getByRole('button', { name: /创建游戏/i });
      });

      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('创建游戏')).toBeInTheDocument();
      });

      // 验证提交按钮在表单未填写时被禁用
      const submitButton = screen.getByRole('button', { name: '创建' });
      expect(submitButton).toBeDisabled();
    });
  });
});
