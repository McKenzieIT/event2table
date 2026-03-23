// @ts-nocheck
/**
 * Smoke test: Verify the component has the create button
 */

import React from 'react';
import { render, screen } from '@test/test-utils';
import { MockedProvider } from '@apollo/client/testing';
import GameManagementModal from './GameManagementModalGraphQL';
import { GET_GAMES } from '../../shared/graphql/operations';

const mockGames = [
  {
    id: 1,
    gid: 10000147,
    name: 'STAR001',
    odsDb: 'ieu_ods',
    eventCount: 5,
    parameterCount: 10,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
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

describe('GameManagementModalGraphQL Smoke Test', () => {
  it('should render the create game button', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GameManagementModal />
      </MockedProvider>
    );

    // Wait for the component to load
    const button = await screen.findByText('创建游戏', { exact: false });
    expect(button).toBeInTheDocument();
    expect(button.tagName).toBe('BUTTON');
  });
});
