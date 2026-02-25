/**
 * Games Component with GraphQL
 * 
 * Example component demonstrating GraphQL integration
 */

import React from 'react';
import { useGames, useDeleteGame } from '../graphql';

interface GamesGraphQLProps {
  limit?: number;
}

export const GamesGraphQL: React.FC<GamesGraphQLProps> = ({ limit = 10 }) => {
  const { loading, error, data } = useGames(limit);
  const [deleteGame] = useDeleteGame();

  if (loading) return <div>Loading games...</div>;
  if (error) return <div>Error loading games: {error.message}</div>;

  const games = data?.games || [];

  const handleDelete = async (gid: number, confirm: boolean = false) => {
    try {
      const result = await deleteGame({
        variables: { gid, confirm },
      });

      if (result.data?.deleteGame?.ok) {
        console.log('Game deleted successfully');
      } else {
        console.warn(result.data?.deleteGame?.errors?.join(', ') || 'Failed to delete game');
      }
    } catch (err) {
      console.error('Error deleting game:', err);
    }
  };

  return (
    <div className="games-container">
      <h2>Games (GraphQL)</h2>
      <table>
        <thead>
          <tr>
            <th>GID</th>
            <th>Name</th>
            <th>ODS DB</th>
            <th>Events</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {games.map((game: any) => (
            <tr key={game.gid}>
              <td>{game.gid}</td>
              <td>{game.name}</td>
              <td>{game.odsDb}</td>
              <td>{game.eventCount}</td>
              <td>
                <button onClick={() => handleDelete(game.gid, true)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GamesGraphQL;
