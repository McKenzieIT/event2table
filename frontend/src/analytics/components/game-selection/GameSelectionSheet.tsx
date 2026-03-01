import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { SearchInput, EmptyState } from '@shared/ui';
import './GameSelectionSheet.css';

interface Game {
  gid: number;
  name: string;
}

interface GameSelectionSheetProps {
  /** Controls sheet visibility */
  isOpen: boolean;
  /** Called when sheet should close */
  onClose: () => void;
  /** Called when a game is selected, receives game object */
  onSelect: (game: Game) => void;
}

/**
 * GameSelectionSheet Component
 *
 * Provides a slide-out sheet for game selection
 */
export function GameSelectionSheet({ isOpen, onClose, onSelect }: GameSelectionSheetProps): React.JSX.Element {
  const { data: apiResponse, isLoading, error } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const res = await fetch('/api/games');
      if (!res.ok) throw new Error('加载失败');
      return res.json();
    },
  });

  const games: Game[] = apiResponse?.data || [];

  const [searchTerm, setSearchTerm] = useState('');

  // Filter games by search term (name or GID)
  const filteredGames = games?.filter(game =>
    game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    game.gid?.toString().includes(searchTerm)
  ) || [];

  const handleGameSelect = (game: Game) => {
    onSelect(game);
    onClose();
  };

  if (!isOpen) return <></>;

  return (
    <>
      <div className="game-selection-sheet open">
        <div className="sheet-overlay" onClick={onClose}></div>
        <div className="sheet-content">
          <div className="sheet-header">
            <h2>选择游戏</h2>
            <button className="close-btn" onClick={onClose} aria-label="关闭">
              <i className="bi bi-x-lg"></i>
            </button>
          </div>

          <div className="sheet-body">
            <div className="search-container">
              <SearchInput
                placeholder="搜索游戏名称或GID..."
                value={searchTerm}
                onChange={(value) => setSearchTerm(value)}
                autoFocus
              />
            </div>

            <div className="games-list">
              {isLoading ? (
                <div className="loading-state">
                  <i className="bi bi-hourglass-split"></i>
                  <span>加载中...</span>
                </div>
              ) : error ? (
                <div className="error-state">
                  <i className="bi bi-exclamation-circle"></i>
                  <span>加载失败: {(error as Error).message}</span>
                </div>
              ) : filteredGames.length === 0 ? (
                <div className="empty-state">
                  <i className="bi bi-search"></i>
                  <span>未找到匹配的游戏</span>
                </div>
              ) : (
                filteredGames.map(game => (
                  <div
                    key={game.gid}
                    className="game-item"
                    onClick={() => handleGameSelect(game)}
                    role="button"
                    tabIndex={0}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        handleGameSelect(game);
                      }
                    }}
                  >
                    <div className="game-icon">
                      <i className="bi bi-controller"></i>
                    </div>
                    <div className="game-info">
                      <div className="game-name">{game.name}</div>
                      <div className="game-gid">GID: {game.gid}</div>
                    </div>
                    <i className="bi bi-chevron-right game-chevron"></i>
                  </div>
                ))
              )}
            </div>

            {games && games.length > 0 && (
              <div className="sheet-footer">
                <span className="game-count">
                  共 {games.length} 个游戏
                  {filteredGames.length !== games.length && ` (${filteredGames.length} 个匹配)`}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
