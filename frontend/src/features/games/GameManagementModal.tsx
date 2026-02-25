/**
 * GameManagementModal - 游戏管理模态框
 *
 * 主从视图布局：
 * - 左侧：游戏列表（支持搜索、多选）
 * - 右侧：选中游戏详细信息（可编辑）
 * - 顶部：添加游戏、批量删除
 *
 * 交互逻辑：
 * - 默认所有可编辑字段为disabled
 * - 检测onChange事件，移除disabled + 显示保存按钮
 * - 点击保存 → 提交API → 恢复disabled
 */

import React, { useState, useMemo, useCallback, ReactElement } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BaseModal, Button, Input, Checkbox, useToast, SearchInput, Skeleton } from '@shared/ui';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import { useGameStore } from '../../stores/gameStore';
import { AddGameModal } from './AddGameModal';
import { ODSSelector } from '@shared/components/GameForm/ODSSelector';
import { GameType } from '../../types/api.generated';
import './GameManagementModal.css';

interface GameManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ConfirmState {
  open: boolean;
  type: 'single' | 'batch' | null;
  data: any;
  title: string;
  message: string;
}

interface FormData {
  gid: string;
  name: string;
  ods_db: string;
}

interface FormErrors {
  [key: string]: string | undefined;
}

const GameManagementModal: React.FC<GameManagementModalProps> = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
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
  const [errors, setErrors] = useState<FormErrors>({});
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    type: null,
    data: null,
    title: '',
    message: ''
  });

  // Promise-based confirm dialog
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  // Fetch games list
  const { data: apiResponse, isLoading, error } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) throw new Error('Failed to fetch games');
      return response.json();
    },
    enabled: isOpen,
    staleTime: 5 * 1000,  // ✅ 从30秒缩短到5秒，提升数据一致性
    refetchOnWindowFocus: true,  // ✅ 启用窗口焦点刷新
  });

  const games: GameType[] = apiResponse?.data || [];

  // Filter games based on search term
  const filteredGames: GameType[] = useMemo(() => {
    if (!games.length) return [];
    return games.filter(game =>
      game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      game.gid?.toString().includes(searchTerm)
    );
  }, [games, searchTerm]);

  // Delete game mutation (with two-phase confirmation)
  const deleteMutation = useMutation({
    mutationFn: async ({ gid, confirm }: { gid: number; confirm: boolean }) => {
      const response = await fetch(`/api/games/${gid}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm })
      });

      // Handle 409 Conflict - needs confirmation
      if (response.status === 409) {
        const result = await response.json();
        return { needsConfirmation: true, data: result.data };
      }

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || 'Failed to delete game');
      }

      return { success: true };
    },
    onSuccess: async (result, variables) => {
      // If needs confirmation, show detailed dialog
      if (result.needsConfirmation) {
        const confirmMessage =
          `游戏有关联数据，删除将清除以下内容：\n` +
          `• ${result.data?.event_count || 0} 个事件\n` +
          `• ${result.data?.param_count || 0} 个参数\n` +
          `• ${result.data?.node_config_count || 0} 个节点配置\n\n` +
          `确定要继续删除吗？此操作不可撤销！`;

        if (await confirm(confirmMessage)) {
          // Retry with confirmation
          deleteMutation.mutate({ gid: variables.gid, confirm: true });
        }
        return;
      }

      // Success - invalidate queries and show success message
      queryClient.invalidateQueries(['games']);
      success('游戏删除成功');
      if (selectedGameId === editingGame?.gid) {
        setSelectedGameId(null);
        setEditingGame(null);
        setHasChanges(false);
      }
    },
    onError: (err: Error) => {
      showError(`删除失败: ${err.message}`);
    }
  });

  // Handle batch delete - delete games one by one with confirmation
  const handleBatchDelete = useCallback(async () => {
    if (selectedGames.length === 0) return;

    // Get selected games data
    const gamesToDelete = games.filter(g => selectedGames.includes(g.gid));
    if (gamesToDelete.length === 0) return;

    // Count total associated data (without triggering deletion)
    let totalEvents = 0;
    let totalParams = 0;
    let totalNodes = 0;
    const gamesWithAssociations: string[] = [];

    // Check each game for associated data using a safe GET request
    for (const game of gamesToDelete) {
      // Use the event_count from the games list data we already have
      totalEvents += game.eventCount || 0;
      totalParams += game.parameterCount || 0;
      totalNodes += 0; // Note: game.node_config_count is not available in GameType

      if ((game.eventCount || 0) > 0 ||
          (game.parameterCount || 0) > 0 ||
          false) { // Note: node_config_count check removed as it's not in GameType
        gamesWithAssociations.push(game.name);
      }
    }

    // Show confirmation dialog with impact summary
    const confirmMessage =
      `确定要删除选中的 ${selectedGames.length} 个游戏吗？\n\n` +
      `影响统计：\n` +
      `• 游戏数量：${selectedGames.length} 个\n` +
      `• 事件总数：${totalEvents} 个\n` +
      `• 参数总数：${totalParams} 个\n` +
      `• 节点配置：${totalNodes} 个\n\n` +
      (gamesWithAssociations.length > 0
        ? `⚠️ 以下游戏有关联数据：\n${gamesWithAssociations.map(name => `  • ${name}`).join('\n')}\n\n`
        : '') +
      `警告：此操作将同时删除所有关联数据，且不可恢复！`;

    if (!(await confirm(confirmMessage))) {
      return;
    }

    // Start deleting
    setIsDeleting(true);

    try {
      // Delete each game with confirmation
      let successCount = 0;
      let failCount = 0;
      const errors: Array<{ game: string; gid: number; status?: number; message?: string; error?: string }> = [];

      for (const game of gamesToDelete) {
        try {
          // Single request: confirm and delete
          const deleteResponse = await fetch(`/api/games/${game.gid}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: true })
          });

          // ✅ 404不算失败 - 游戏已被删除
          if (deleteResponse.ok || deleteResponse.status === 404) {
            successCount++;
          } else {
            failCount++;
            const errorResult = await deleteResponse.json().catch(() => ({}));
            console.error(`Failed to delete game ${game.gid}:`, {
              status: deleteResponse.status,
              statusText: deleteResponse.statusText,
              body: errorResult
            });
            errors.push({
              game: game.name,
              gid: game.gid,
              status: deleteResponse.status,
              message: errorResult.message || errorResult.error || 'Unknown error'
            });
          }
        } catch (err: any) {
          failCount++;
          console.error(`Error deleting game ${game.gid}:`, err);
          errors.push({
            game: game.name,
            gid: game.gid,
            error: err.message
          });
        }
      }

      // Refresh games list and show result
      queryClient.invalidateQueries(['games']);
      setSelectedGames([]);

      if (failCount === 0) {
        success(`批量删除成功：${successCount} 个游戏`);
      } else {
        const errorDetails = errors.map(e =>
          `- ${e.game} (GID: ${e.gid}): ${e.status || 'NETWORK'} - ${e.message || e.error || 'Unknown error'}`
        ).join('\n');
        console.error('批量删除错误详情:\n' + errorDetails);
        showError(`批量删除部分失败：成功 ${successCount} 个，失败 ${failCount} 个`);
      }
    } finally {
      setIsDeleting(false);
    }
  }, [selectedGames, games, queryClient, success, showError]);

  // Update game mutation
  const updateMutation = useMutation({
    mutationFn: async ({ gid, ...data }: { gid: number } & Partial<GameType>) => {
      const response = await fetch(`/api/games/${gid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to update game');
      return response.json();
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['games']);
      success('游戏更新成功');
      setHasChanges(false);

      // Update editing game state
      const updatedGame = games.find(g => g.gid === variables.gid);
      if (updatedGame) {
        setEditingGame({ ...updatedGame, ...variables });
      }
    },
    onError: (err: Error) => {
      showError(`更新失败: ${err.message}`);
    }
  });

  // Handle game selection
  const handleSelectGame = useCallback((game: GameType) => {
    setSelectedGameId(game.gid);
    setEditingGame({ ...game });
    setHasChanges(false);
    setErrors({});
  }, []);

  // Handle toggle select for batch operations
  const handleToggleSelect = useCallback((gameId: number) => {
    setSelectedGames(prev => {
      // Use gid instead of id for selection
      if (prev.includes(gameId)) {
        return prev.filter(id => id !== gameId);
      } else {
        return [...prev, gameId];
      }
    });
  }, []);

  // Handle field change - enable editing and show save button
  const handleFieldChange = useCallback((field: keyof Partial<GameType>, value: string) => {
    setEditingGame(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!editingGame) return;

    // 验证
    const newErrors: FormErrors = {};
    if (!editingGame.name?.trim()) {
      newErrors.name = '游戏名称不能为空';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // 清除错误
    setErrors({});

    updateMutation.mutate({
      gid: editingGame.gid!,
      name: editingGame.name!,
      ods_db: editingGame.odsDb!
    });
  }, [editingGame, updateMutation]);

  // Handle cancel edit
  const handleCancelEdit = useCallback(() => {
    const originalGame = games.find(g => g.gid === editingGame?.gid);
    if (originalGame) {
      setEditingGame({ ...originalGame });
      setHasChanges(false);
    }
  }, [editingGame, games]);

  // Handle delete (triggers first phase of deletion)
  const handleDelete = useCallback((game: GameType) => {
    // Start deletion process (will show confirmation if needed)
    deleteMutation.mutate({ gid: game.gid, confirm: false });
  }, [deleteMutation]);

  // Handle add game
  const handleAddGame = useCallback(() => {
    // Open the AddGameModal (two-layer slide-out)
    openAddGameModal();
  }, [openAddGameModal]);

  // Get selected game for statistics
  const selectedGameData = useMemo(() => {
    if (!editingGame) return null;
    return games.find(g => g.gid === editingGame.gid);
  }, [editingGame, games]);

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title="游戏管理"
      animation="slideUp"
      glassmorphism
      size="full"
      className="game-management-modal"
    >
      <div className="game-management-content">
        {/* Left Panel - Game List */}
        <div className="game-list-panel">
          <div className="panel-header">
            <div className="panel-title">
              <h3>游戏列表</h3>
              <span className="game-count">({games.length})</span>
            </div>
            <div className="panel-actions">
              {selectedGames.length > 0 && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleBatchDelete}
                  disabled={isDeleting}
                >
                  删除选中 ({selectedGames.length})
                </Button>
              )}
              <Button
                variant="primary"
                size="sm"
                onClick={handleAddGame}
              >
                添加游戏
              </Button>
            </div>
          </div>

          <div className="panel-search">
            <SearchInput
              placeholder="搜索游戏名称或GID..."
              value={searchTerm}
              onChange={(value: string) => setSearchTerm(value)}
              debounceMs={300}
            />
          </div>

          <div className="game-list">
            {isLoading ? (
              <div className="loading-state">
                <Skeleton type="card" count={3} />
              </div>
            ) : filteredGames.length === 0 ? (
              <div className="empty-state">暂无游戏</div>
            ) : (
              filteredGames.map(game => (
                <div
                  key={game.gid}
                  className={`game-list-item ${selectedGameId === game.gid ? 'active' : ''}`}
                  onClick={() => handleSelectGame(game)}
                >
                  <Checkbox
                    checked={selectedGames.includes(game.gid)}
                    onChange={(checked: boolean) => handleToggleSelect(game.gid)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div className="game-item-info">
                    <div className="game-item-name">{game.name}</div>
                    <div className="game-item-gid">GID: {game.gid}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Panel - Game Details */}
        <div className="game-detail-panel">
          {editingGame ? (
            <>
              <div className="panel-header">
                <div className="panel-title">
                  <h3>游戏详情</h3>
                </div>
                {hasChanges && (
                  <div className="panel-actions">
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      onClick={handleCancelEdit}
                    >
                      取消
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleSave}
                      disabled={updateMutation.isLoading}
                    >
                      保存
                    </Button>
                  </div>
                )}
              </div>

              <div className="game-detail-content">
                <div className="detail-section">
                  <h4>基本信息</h4>

                  {/* 编辑提示 */}
                  {!hasChanges && (
                    <div className="edit-hint">
                      <span className="hint-icon">✎</span>
                      点击任意字段开始编辑，修改后自动显示保存按钮
                    </div>
                  )}

                  {/* 未保存更改提示 */}
                  {hasChanges && (
                    <div className="unsaved-changes-hint">
                      <span className="hint-icon">⚠</span>
                      有未保存的更改，请点击"保存"按钮保存修改
                    </div>
                  )}

                  <Input
                    label="游戏名称"
                    type="text"
                    value={editingGame.name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      handleFieldChange('name', e.target.value);
                      // 清除该字段的错误
                      if (errors.name) {
                        setErrors(prev => ({ ...prev, name: undefined }));
                      }
                    }}
                    placeholder="输入游戏名称"
                    required
                    error={errors.name}
                  />

                  <Input
                    label="游戏GID"
                    type="text"
                    value={editingGame.gid?.toString()}
                    disabled={true}
                    className="readonly-field"
                  />
                  <small className="field-hint">GID为只读字段，创建后不可修改</small>

                  {/* ODS Database - Card Selector (与新增游戏保持一致) */}
                  <div className="form-group">
                    <label className="form-label">ODS数据库类型</label>
                    <ODSSelector
                      value={editingGame.odsDb === 'ieu_ods' ? 'domestic' : 'overseas'}
                      onChange={(odsType: 'domestic' | 'overseas') => {
                        const odsDb = odsType === 'domestic' ? 'ieu_ods' : 'overseas_ods';
                        handleFieldChange('odsDb', odsDb);
                      }}
                      disabled={false}
                    />
                    <small className="field-hint">选择ODS数据库类型，用于生成源表路径</small>
                  </div>
                </div>

                {selectedGameData && (
                  <div className="detail-section">
                    <h4>统计数据</h4>
                    <div className="stats-grid">
                      <div className="stat-item">
                        <div className="stat-label">事件数</div>
                        <div className="stat-value">{selectedGameData.eventCount || 0}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">参数数</div>
                        <div className="stat-value">{selectedGameData.parameterCount || 0}</div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="detail-section detail-section--danger">
                  <h4>危险操作</h4>
                  <Button
                    variant="danger"
                    onClick={() => handleDelete(editingGame)}
                    disabled={deleteMutation.isLoading}
                  >
                    删除游戏
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-detail-state">
              <p>请从左侧选择一个游戏查看详情</p>
            </div>
          )}
        </div>
      </div>

      {/* Two-layer modal: Add Game Modal */}
      <AddGameModal
        isOpen={isAddGameModalOpen}
        onClose={closeAddGameModal}
      />

      {/* Promise-based confirm dialog */}
      <ConfirmDialogComponent />
    </BaseModal>
  );
};

export default React.memo(GameManagementModal);