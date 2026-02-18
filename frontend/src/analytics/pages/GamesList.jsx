import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Input, Checkbox, Spinner, useToast, SearchInput, Card } from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { useGameContext } from '@shared/hooks/useGameContext';
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
  const { selectGame } = useGameContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGames, setSelectedGames] = useState([]);
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });

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

  // Delete game mutation (两阶段删除确认流程)
  const deleteMutation = useMutation({
    mutationFn: async ({ gameGid, gameName, forceDelete = false }) => {
      // 第一次请求：不带confirm，检查是否有关联数据
      const response = await fetch(`/api/games/${gameGid}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(forceDelete ? { confirm: true } : {})
      });

      const data = await response.json();

      // 情况1：游戏没有关联数据，直接删除成功
      if (response.ok && data.success) {
        return { success: true, message: `游戏 "${gameName}" 删除成功`, phase: 'deleted' };
      }

      // 情况2：游戏有关联数据，返回409警告
      if (response.status === 409 && !data.success && !forceDelete) {
        // 提取影响统计数据
        const impact = data.data || {};
        const eventCount = impact.event_count || 0;
        const paramCount = impact.param_count || 0;
        const nodeCount = impact.node_config_count || 0;

        // 抛出特殊错误，包含409状态和影响统计
        const error = new Error('NEEDS_CONFIRMATION');
        error.status = 409;
        error.impact = { eventCount, paramCount, nodeCount };
        error.gameGid = gameGid;
        error.gameName = gameName;
        throw error;
      }

      // 情况3：用户确认后的第二次请求（forceDelete=true）
      if (forceDelete && response.ok && data.success) {
        const deletedEvents = data.data?.deleted_event_count || 0;
        const deletedParams = data.data?.deleted_param_count || 0;
        return {
          success: true,
          message: `游戏 "${gameName}" 及关联数据已删除（事件：${deletedEvents}，参数：${deletedParams}）`,
          phase: 'deleted'
        };
      }

      // 情况4：其他错误（404游戏不存在等）
      if (!response.ok) {
        throw new Error(data.message || '删除失败');
      }

      return data;
    },
    onSuccess: (data) => {
      if (data.phase === 'deleted') {
        success(data.message);
        queryClient.invalidateQueries(['games']);
      }
    },
    onError: (err, variables) => {
      // 处理409确认错误
      if (err.message === 'NEEDS_CONFIRMATION') {
        const { eventCount, paramCount, nodeCount } = err.impact;
        const confirmMessage =
          `⚠️ 该游戏存在以下关联数据：\n` +
          `• 事件：${eventCount} 个\n` +
          `• 参数：${paramCount} 个\n` +
          `• 节点配置：${nodeCount} 个\n\n` +
          `删除游戏将同时删除所有关联数据，此操作不可恢复！\n\n` +
          `确定要删除游戏 "${err.gameName}" 吗？`;

        setConfirmState({
          open: true,
          title: '确认删除',
          message: confirmMessage,
          onConfirm: () => {
            setConfirmState(s => ({ ...s, open: false }));
            // 用户确认后，第二次请求（带confirm=true）
            deleteMutation.mutate({
              gameGid: err.gameGid,
              gameName: err.gameName,
              forceDelete: true
            });
          }
        });
      } else {
        // 其他错误显示错误消息
        showError(`删除失败: ${err.message}`);
      }
    }
  });

  // 使用useCallback优化事件处理函数（避免子组件不必要的重渲染）
  const handleGameSelect = useCallback((game) => {
    selectGame(game);
    navigate(`/canvas?game_gid=${game.gid}`);
  }, [selectGame, navigate]);

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

    // Get selected games data
    const gamesToDelete = games.filter(g => selectedGames.includes(g.gid));
    if (gamesToDelete.length === 0) return;

    // Count total associated data
    let totalEvents = 0;
    let totalParams = 0;
    let totalNodes = 0;

    // Check each game for associated data
    for (const game of gamesToDelete) {
      try {
        const response = await fetch(`/api/games/${game.gid}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ confirm: false })
        });

        if (response.status === 409) {
          const result = await response.json();
          totalEvents += result.data?.event_count || 0;
          totalParams += result.data?.param_count || 0;
          totalNodes += result.data?.node_config_count || 0;
        }
      } catch (err) {
        console.error(`Error checking game ${game.gid}:`, err);
      }
    }

    // Show confirmation dialog with impact summary
    setConfirmState({
      open: true,
      title: '确认批量删除',
      message:
        `确定要删除选中的 ${selectedGames.length} 个游戏吗？\n\n` +
        `影响统计：\n` +
        `• 游戏数量：${selectedGames.length} 个\n` +
        `• 事件总数：${totalEvents} 个\n` +
        `• 参数总数：${totalParams} 个\n` +
        `• 节点配置：${totalNodes} 个\n\n` +
        `警告：此操作将同时删除所有关联数据，且不可恢复！`,
      onConfirm: async () => {
        setConfirmState(s => ({ ...s, open: false }));

        // Delete each game with confirmation
        let successCount = 0;
        let failCount = 0;

        for (const game of gamesToDelete) {
          try {
            // Confirm and delete
            const deleteResponse = await fetch(`/api/games/${game.gid}`, {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ confirm: true })
            });

            if (deleteResponse.ok) {
              successCount++;
            } else {
              failCount++;
              console.error(`Failed to delete game ${game.gid}`);
            }
          } catch (err) {
            failCount++;
            console.error(`Error deleting game ${game.gid}:`, err);
          }
        }

        // Refresh games list and show result
        setSelectedGames([]);
        queryClient.invalidateQueries(['games']);

        if (failCount === 0) {
          success(`批量删除成功：${successCount} 个游戏`);
        } else {
          showError(`批量删除部分失败：成功 ${successCount} 个，失败 ${failCount} 个`);
        }
      }
    });
  }, [selectedGames, games, queryClient, success, showError]);

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
          <Button variant="primary" onClick={() => queryClient.invalidateQueries({ queryKey: ['games'] })} data-testid="reload-button">
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
            <Card
              key={game.gid}
              variant="glass"
              padding="md"
              hover
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
                    // 调用两阶段删除mutation（先检查，后确认）
                    deleteMutation.mutate({
                      gameGid: game.gid,
                      gameName: game.name,
                      forceDelete: false
                    });
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
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="删除"
        cancelText="取消"
        variant="danger"
        onConfirm={confirmState.onConfirm}
        onCancel={() => setConfirmState(s => ({ ...s, open: false }))}
      />
    </div>
  );
}

// 使用React.memo包装，防止不必要的重渲染
export default React.memo(GamesList);
