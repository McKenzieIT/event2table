import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Input, Checkbox, Spinner, useToast, SearchInput } from '@shared/ui';
import './GamesList.css';

/**
 * GamesList 游戏列表组件
 *
 * 性能优化：
 * - React.memo防止不必要的重渲染
 * - useMemo优化过滤计算
 * - useCallback优化事件处理函数
 *
 * 按钮设计规范：
 * - 纯文字标签（无图标）
 * - 语义化颜色匹配操作类型
 * - 使用统一的Button组件
 */
function GamesList() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGames, setSelectedGames] = useState([]);

  // Get games list
  const { data: apiResponse, isLoading, error, refetch } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) throw new Error('Failed to fetch games');
      return response.json();
    },
    staleTime: 30 * 1000, // 30秒内不重新获取（平衡性能和实时性）
    refetchOnWindowFocus: false, // 窗口焦点变化时不重新获取
  });

  // 当从创建/编辑页面返回时，刷新列表
  useEffect(() => {
    // 检查是否从创建/编辑页面返回
    const state = location.state;
    if (state?.refresh) {
      refetch();
    }
  }, [location.state, refetch]);

  const games = apiResponse?.data || [];

  // 客户端过滤优化（useMemo记忆化，避免重复计算）
  const filteredGames = useMemo(() => {
    if (!games) return [];
    return games.filter(game =>
      game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      game.gid?.toString().includes(searchTerm)
    );
  }, [games, searchTerm]);

  // Delete game mutation
  const deleteMutation = useMutation({
    mutationFn: async (gameId) => {
      const response = await fetch(`/api/games/${gameId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete game');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['games']);
    }
  });

  // 使用useCallback优化事件处理函数（避免子组件不必要的重渲染）
  const handleGameSelect = useCallback((game) => {
    // Set current game context
    localStorage.setItem('selectedGameGid', game.gid);

    // 设置全局游戏数据，供EventNodeBuilder使用
    window.gameData = {
      gid: game.gid,
      name: game.name,
      ods_db: game.ods_db,
    };

    // 将游戏添加到全局列表
    if (!window.gamesList) {
      window.gamesList = [];
    }
    if (!window.gamesList.find(g => g.gid === game.gid)) {
      window.gamesList.push(window.gameData);
    }

    // 导出游戏数据变更事件
    window.dispatchEvent(new CustomEvent('gameChanged', { detail: window.gameData }));

    // Navigate to Canvas page
    navigate(`/canvas?game_gid=${game.gid}`);
  }, [navigate]);

  const handleToggleSelect = useCallback((gameId) => {
    setSelectedGames(prev => {
      if (prev.includes(gameId)) {
        return prev.filter(id => id !== gameId);
      } else {
        return [...prev, gameId];
      }
    });
  }, []);

  const handleBatchDelete = useCallback(async () => {
    if (selectedGames.length === 0) return;
    if (!confirm(`确定要删除选中的 ${selectedGames.length} 个游戏吗？\n\n警告：此操作将同时删除所有关联的事件和参数，且不可恢复！`)) return;

    try {
      // Use the backend batch delete API (expects database IDs)
      const response = await fetch('/api/games/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: selectedGames })
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || '删除失败');
      }

      const data = await response.json();
      setSelectedGames([]);
      // Refresh games list
      queryClient.invalidateQueries(['games']);
      success(data.message || `成功删除 ${selectedGames.length} 个游戏`);
    } catch (err) {
      showError(`删除失败: ${err.message}`);
    }
  }, [selectedGames, queryClient, success, showError]);

  const handleCreateGame = useCallback(() => {
    // 导航到创建页面，传递回调函数
    navigate('/games/create', {
      state: { fromList: true }
    });
  }, [navigate]);

  const handleEditGame = useCallback((gameId) => {
    // 导航到编辑页面，传递回调函数
    navigate(`/games/${gameId}/edit`, {
      state: { fromList: true }
    });
  }, [navigate]);

  const handleClearSelection = useCallback(() => {
    setSelectedGames([]);
  }, []);

  if (error) {
    return (
      <div className="games-list-page" data-testid="games-list-page">
        <div className="error-message" data-testid="error-message">
          <p>加载游戏列表失败: {error.message}</p>
          <Button variant="primary" onClick={() => window.location.reload()} data-testid="reload-button">
            重新加载
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="games-list-page" data-testid="games-list-page">
      <div className="page-header" data-testid="games-list-header">
        <h1>游戏管理</h1>
        <div className="header-actions">
          {selectedGames.length > 0 && (
            <Button
              variant="danger"
              onClick={handleBatchDelete}
              data-testid="delete-selected-button"
            >
              删除选中 ({selectedGames.length})
            </Button>
          )}
          <Button
            variant="primary"
            onClick={handleCreateGame}
            data-testid="add-game-button"
          >
            新增游戏
          </Button>
        </div>
      </div>

      <div className="search-bar" data-testid="search-bar">
        <SearchInput
          placeholder="搜索游戏名称或GID..."
          value={searchTerm}
          onChange={(value) => setSearchTerm(value)}
          data-testid="search-input"
        />
      </div>

      {selectedGames.length > 0 && (
        <div className="selection-bar" data-testid="selection-bar">
          <span>已选择 {selectedGames.length} 个游戏</span>
          <Button variant="outline-secondary" size="sm" onClick={handleClearSelection} data-testid="clear-selection-button">
            取消选择
          </Button>
        </div>
      )}

      {isLoading && !games.length ? (
        <div className="loading-spinner" data-testid="loading-state">
          <Spinner size="lg" label="正在加载游戏列表..." />
        </div>
      ) : filteredGames.length === 0 ? (
        <div className="empty-state" data-testid="empty-state">
          <p>暂无游戏</p>
          <Button variant="primary" onClick={handleCreateGame} data-testid="add-first-game-button">
            新增游戏
          </Button>
        </div>
      ) : (
        <div className="games-grid" data-testid="games-grid">
          {filteredGames.map(game => (
            <div
              key={game.gid}
              className={`game-card ${selectedGames.includes(game.id) ? 'selected' : ''}`}
              data-testid={`game-card-${game.gid}`}
            >
              <Checkbox
                checked={selectedGames.includes(game.id)}
                onChange={(checked) => handleToggleSelect(game.id)}
                className="game-checkbox"
                data-testid={`game-checkbox-${game.id}`}
              />
              <div className="game-icon">
                <span>游戏</span>
              </div>
              <div className="game-info">
                <h3>{game.name}</h3>
                <p className="game-gid">GID: {game.gid}</p>
                <p className="game-db">数据库: {game.ods_db}</p>
              </div>
              <div className="game-actions">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => handleEditGame(game.gid)}
                  data-testid={`edit-game-button-${game.gid}`}
                >
                  编辑
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    if (confirm(`确定要删除游戏「${game.name}」吗？\n\n警告：此操作将同时删除所有关联的事件和参数，且不可恢复！`)) {
                      deleteMutation.mutate(game.gid);
                    }
                  }}
                  data-testid={`delete-game-button-${game.gid}`}
                >
                  删除
                </Button>
                <Button
                  variant="success"
                  size="sm"
                  onClick={() => handleGameSelect(game)}
                  data-testid={`enter-canvas-button-${game.gid}`}
                >
                  跳转
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// 使用React.memo包装，防止不必要的重渲染
export default React.memo(GamesList);
