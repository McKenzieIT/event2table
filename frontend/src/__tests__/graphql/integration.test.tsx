// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * GraphQL 集成测试
 *
 * 测试GraphQL查询和变更的完整流程
 */

import { MockedProvider } from '@apollo/client/testing/react';
import { render, screen, waitFor } from '@test/test-utils';
import React from 'react';
import { describe, it, expect } from 'vitest';

import GameManagementModalGraphQL from '../../features/games/GameManagementModalGraphQL';
// ⚠️ FIX: Import from shared/graphql/queries to match what components use
import { GET_GAMES } from '../../shared/graphql/queries';

// Mock数据 - match actual GraphQL response structure
// Note: Using odsDb (camelCase) to match GraphQL query
const mockGames = [
  {
    id: 1,
    gid: 1001,
    name: 'Game 1',
    odsDb: 'ieu_ods',
    eventCount: 10,
    parameterCount: 50,
  },
  {
    id: 2,
    gid: 1002,
    name: 'Game 2',
    odsDb: 'ieu_ods',
    eventCount: 20,
    parameterCount: 100,
  },
];

describe('GraphQL Integration Tests', () => {
  describe('GameManagementModalGraphQL', () => {
    // ⚠️ FIX: Match actual component variables (limit: 20)
    const createMocks = () => [
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

    it('should render games list', async () => {
      render(
        <MockedProvider mocks={createMocks()} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成并检查游戏列表是否渲染
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
        expect(screen.getByText('Game 2')).toBeInTheDocument();
      }, { timeout: 5000 });
    });

    it('should render search input', async () => {
      render(
        <MockedProvider mocks={createMocks()} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
      }, { timeout: 5000 });

      // 检查搜索框存在 - match actual placeholder
      const searchInput = screen.getByPlaceholderText('搜索游戏...');
      expect(searchInput).toBeInTheDocument();
    });

    it('should display game details in list', async () => {
      render(
        <MockedProvider mocks={createMocks()} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
      }, { timeout: 5000 });

      // 检查游戏详情显示
      expect(screen.getByText('GID: 1001')).toBeInTheDocument();
      expect(screen.getByText(/事件数: 10/)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle GraphQL errors gracefully', async () => {
      const errorMocks = [
        {
          request: {
            query: GET_GAMES,
            variables: { limit: 20, offset: 0 },
          },
          error: new Error('Network error'),
        },
      ];

      render(
        <MockedProvider mocks={errorMocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待错误显示 - component shows error message
      await waitFor(() => {
        // Check for any error-related text
        const errorElement = screen.queryByText(/error|错误|失败/i);
        expect(errorElement).toBeTruthy();
      }, { timeout: 5000 });
    });
  });

  describe('Cache Behavior', () => {
    it('should render games on initial load', async () => {
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

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <GameManagementModalGraphQL isOpen={true} onClose={() => {}} />
        </MockedProvider>
      );

      // 等待数据加载
      await waitFor(() => {
        expect(screen.getByText('Game 1')).toBeInTheDocument();
      }, { timeout: 5000 });
    });
  });
});

