/**
 * GameManagementModalGraphQL - 游戏管理模态框（GraphQL版本）
 *
 * 使用GraphQL API替代REST API
 * 利用GraphQL的灵活性优化数据获取
 */

import React, { useState, useMemo, useCallback } from 'react';
import { BaseModal, Button, Input, Checkbox, useToast, SearchInput, Skeleton } from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { useGameStore } from '../../stores/gameStore';
import { AddGameModal } from './AddGameModal';
import {
  useGames,
  useSearchGames,
  useUpdateGame,
  useDeleteGame,
} from '../../graphql/hooks';
import { GameType } from '../../types/api.generated';
import './GameManagementModal.css';

interface GameManagementModalGraphQLProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ConfirmState {
  open: boolean;
  type: 'single' | 'batch';
  data: any;
  title: string;
  message: string;
}

const GameManagementModalGraphQL: React.FC<GameManagementModalGraphQLProps> = ({ isOpen, onClose }) => {
  const { success, error: showError } = useToast();
  const { setCurrentGame, currentGame, isAddGameModalOpen, openAddGameModal, closeAddGameModal } = useGameStore();

  // Local state
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedGames, setSelectedGames] = useState<number[]>([]);
  const [selectedGameId, setSelectedGameId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Editable game data state
  const [editingGame, setEditingGame] = useState<Partial<GameType> | null>(null);
  const [hasChanges, setHasChanges] = useState<boolean>(false);
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    type: 'single',
    data: null,
    title: '',
    message: ''
  });

  // GraphQL Hooks
  const { data: gamesData, loading: isLoading, error } = useGames(100, 0);
  const { data: searchData, loading: isSearching } = useSearchGames(searchTerm);

  // Mutations
  const [updateGame] = useUpdateGame();
  const [deleteGame] = useDeleteGame();

  // Get games list
  const games: GameType[] = useMemo(() => {
    if (searchTerm && searchData?.searchGames) {
      return searchData.searchGames;
    }
    return gamesData?.games || [];
  }, [gamesData, searchData, searchTerm]);

  // Filter games based on search term (client-side fallback)
  const filteredGames: GameType[] = useMemo(() => {
    if (!games.length) return [];
    if (searchTerm && searchData?.searchGames) {
      return games; // Already filtered by GraphQL
    }
    return games.filter(game =>
      game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      game.gid?.toString().includes(searchTerm)
    );
  }, [games, searchTerm, searchData]);

  // Handle game selection
  const handleSelectGame = useCallback((game: GameType) => {
    setSelectedGameId(game.gid);
    setEditingGame({ ...game });
    setHasChanges(false);
    setCurrentGame(game);
  }, [setCurrentGame]);

  // Handle game edit
  const handleEditGame = useCallback((field: keyof GameType, value: string) => {
    setEditingGame(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  }, []);

  // Handle save game
  const handleSaveGame = useCallback(async () => {
    if (!editingGame || !hasChanges) return;

    try {
      const { data } = await updateGame({
        variables: {
          gid: editingGame.gid!,
          name: editingGame.name!,
          odsDb: editingGame.odsDb!
        }
      });

      if (data?.updateGame?.ok) {
        success('游戏更新成功');
        setHasChanges(false);
      } else {
        showError(data?.updateGame?.errors?.[0] || '更新失败');
      }
    } catch (err: any) {
      showError(`更新失败: ${err.message}`);
    }
  }, [editingGame, hasChanges, updateGame, success, showError]);

  // Handle delete game
  const handleDeleteGame = useCallback(async (gid: number, confirm = false) => {
    try {
      const { data } = await deleteGame({
        variables: { gid, confirm }
      });

      if (data?.deleteGame?.ok) {
        success('游戏删除成功');
        setSelectedGameId(null);
        setEditingGame(null);
        setSelectedGames(prev => prev.filter(id => id !== gid));
      } else if (data?.deleteGame?.message) {
        // Needs confirmation
        setConfirmState({
          open: true,
          type: 'single',
          data: { gid },
          title: '确认删除',
          message: data.deleteGame.message
        });
      } else {
        showError(data?.deleteGame?.errors?.[0] || '删除失败');
      }
    } catch (err: any) {
      showError(`删除失败: ${err.message}`);
    }
  }, [deleteGame, success, showError]);

  // Handle batch delete
  const handleBatchDelete = useCallback(async () => {
    if (selectedGames.length === 0) return;

    setConfirmState({
      open: true,
      type: 'batch',
      data: { gids: selectedGames },
      title: '批量删除确认',
      message: `确定要删除选中的 ${selectedGames.length} 个游戏吗？`
    });
  }, [selectedGames]);

  // Handle confirm dialog
  const handleConfirmAction = useCallback(async () => {
    if (confirmState.type === 'single') {
      await handleDeleteGame(confirmState.data.gid, true);
    } else if (confirmState.type === 'batch') {
      setIsDeleting(true);
      try {
        for (const gid of confirmState.data.gids) {
          await handleDeleteGame(gid, true);
        }
        setSelectedGames([]);
      } finally {
        setIsDeleting(false);
      }
    }
    setConfirmState({ open: false, type: 'single', data: null, title: '', message: '' });
  }, [confirmState, handleDeleteGame]);

  // Handle checkbox change
  const handleCheckboxChange = useCallback((gid: number, checked: boolean) => {
    setSelectedGames(prev =>
      checked ? [...prev, gid] : prev.filter(id => id !== gid)
    );
  }, []);

  // Render loading state
  if (isLoading) {
    return (
      <BaseModal isOpen={isOpen} onClose={onClose} title="游戏管理" size="lg">
        <div className="game-management-loading">
          <Skeleton height={40} count={5} />
        </div>
      </BaseModal>
    );
  }

  // Render error state
  if (error) {
    return (
      <BaseModal isOpen={isOpen} onClose={onClose} title="游戏管理" size="lg">
        <div className="game-management-error">
          <p>加载失败: {error.message}</p>
          <Button onClick={() => window.location.reload()}>重试</Button>
        </div>
      </BaseModal>
    );
  }

  return (
    <>
      <BaseModal isOpen={isOpen} onClose={onClose} title="游戏管理" size="lg">
        <div className="game-management-container">
          {/* Header */}
          <div className="game-management-header">
            <div className="header-left">
              <SearchInput
                value={searchTerm}
                onChange={(value: string) => setSearchTerm(value)}
                placeholder="搜索游戏名称或GID..."
                loading={isSearching}
              />
            </div>
            <div className="header-right">
              <Button onClick={openAddGameModal} variant="primary">
                + 添加游戏
              </Button>
              {selectedGames.length > 0 && (
                <Button
                  onClick={handleBatchDelete}
                  variant="danger"
                  loading={isDeleting}
                >
                  删除选中 ({selectedGames.length})
                </Button>
              )}
            </div>
          </div>

          {/* Main content */}
          <div className="game-management-content">
            {/* Left: Games list */}
            <div className="games-list">
              <div className="games-list-header">
                <Checkbox
                  checked={selectedGames.length === filteredGames.length && filteredGames.length > 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    if (e.target.checked) {
                      setSelectedGames(filteredGames.map(g => g.gid));
                    } else {
                      setSelectedGames([]);
                    }
                  }}
                />
                <span>游戏列表 ({filteredGames.length})</span>
              </div>
              <div className="games-list-body">
                {filteredGames.map(game => (
                  <div
                    key={game.gid}
                    className={`game-item ${selectedGameId === game.gid ? 'selected' : ''}`}
                    onClick={() => handleSelectGame(game)}
                  >
                    <Checkbox
                      checked={selectedGames.includes(game.gid)}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                        e.stopPropagation();
                        handleCheckboxChange(game.gid, e.target.checked);
                      }}
                    />
                    <div className="game-info">
                      <div className="game-name">{game.name}</div>
                      <div className="game-meta">
                        GID: {game.gid} | 事件: {game.eventCount || 0}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Game details */}
            <div className="game-details">
              {selectedGameId && editingGame ? (
                <>
                  <div className="details-header">
                    <h3>游戏详情</h3>
                    <div className="details-actions">
                      {hasChanges && (
                        <Button onClick={handleSaveGame} variant="primary" size="sm">
                          保存
                        </Button>
                      )}
                      <Button
                        onClick={() => handleDeleteGame(editingGame.gid!)}
                        variant="danger"
                        size="sm"
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                  <div className="details-body">
                    <Input
                      label="GID"
                      value={editingGame.gid?.toString()}
                      disabled
                    />
                    <Input
                      label="游戏名称"
                      value={editingGame.name}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleEditGame('name', e.target.value)}
                    />
                    <Input
                      label="ODS数据库"
                      value={editingGame.odsDb}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleEditGame('odsDb', e.target.value)}
                    />
                    <Input
                      label="事件数量"
                      value={editingGame.eventCount?.toString() || '0'}
                      disabled
                    />
                    <Input
                      label="参数数量"
                      value={editingGame.parameterCount?.toString() || '0'}
                      disabled
                    />
                  </div>
                </>
              ) : (
                <div className="no-selection">
                  <p>请从左侧列表选择一个游戏</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </BaseModal>

      {/* Add Game Modal */}
      <AddGameModal
        isOpen={isAddGameModalOpen}
        onClose={closeAddGameModal}
      />

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmState.open}
        onClose={() => setConfirmState({ open: false, type: 'single', data: null, title: '', message: '' })}
        onConfirm={handleConfirmAction}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="确认"
        cancelText="取消"
      />
    </>
  );
};

export default GameManagementModalGraphQL;