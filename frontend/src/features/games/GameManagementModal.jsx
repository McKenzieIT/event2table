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

import React, { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal, Button, Input, Checkbox, useToast, SearchInput } from '@shared/ui';
import { useGameStore } from '../../stores/gameStore';
import { AddGameModal } from './AddGameModal';
import './GameManagementModal.css';

const GameManagementModal = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();
  const { setCurrentGame, currentGame, isAddGameModalOpen, openAddGameModal, closeAddGameModal } = useGameStore();

  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGames, setSelectedGames] = useState([]);
  const [selectedGameId, setSelectedGameId] = useState(null);

  // Editable game data state
  const [editingGame, setEditingGame] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch games list
  const { data: apiResponse, isLoading, error } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) throw new Error('Failed to fetch games');
      return response.json();
    },
    enabled: isOpen,
    staleTime: 30 * 1000,
  });

  const games = apiResponse?.data || [];

  // Filter games based on search term
  const filteredGames = useMemo(() => {
    if (!games.length) return [];
    return games.filter(game =>
      game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      game.gid?.toString().includes(searchTerm)
    );
  }, [games, searchTerm]);

  // Delete game mutation
  const deleteMutation = useMutation({
    mutationFn: async (gid) => {
      const response = await fetch(`/api/games/${gid}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || 'Failed to delete game');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['games']);
      success('游戏删除成功');
      if (selectedGameId === editingGame?.gid) {
        setSelectedGameId(null);
        setEditingGame(null);
        setHasChanges(false);
      }
    },
    onError: (err) => {
      showError(`删除失败: ${err.message}`);
    }
  });

  // Batch delete mutation
  const batchDeleteMutation = useMutation({
    mutationFn: async (ids) => {
      const response = await fetch('/api/games/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids })
      });
      if (!response.ok) throw new Error('Failed to batch delete games');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['games']);
      setSelectedGames([]);
      success('批量删除成功');
    },
    onError: (err) => {
      showError(`批量删除失败: ${err.message}`);
    }
  });

  // Update game mutation
  const updateMutation = useMutation({
    mutationFn: async ({ gid, ...data }) => {
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
    onError: (err) => {
      showError(`更新失败: ${err.message}`);
    }
  });

  // Handle game selection
  const handleSelectGame = useCallback((game) => {
    setSelectedGameId(game.gid);
    setEditingGame({ ...game });
    setHasChanges(false);
  }, []);

  // Handle toggle select for batch operations
  const handleToggleSelect = useCallback((gameId) => {
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
  const handleFieldChange = useCallback((field, value) => {
    setEditingGame(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!editingGame) return;

    updateMutation.mutate({
      gid: editingGame.gid,
      name: editingGame.name,
      ods_db: editingGame.ods_db
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

  // Handle delete
  const handleDelete = useCallback((game) => {
    if (confirm(`确定要删除游戏「${game.name}」吗？\n\n警告：此操作将同时删除所有关联的事件和参数，且不可恢复！`)) {
      deleteMutation.mutate(game.gid);
    }
  }, [deleteMutation]);

  // Handle batch delete
  const handleBatchDelete = useCallback(async () => {
    if (selectedGames.length === 0) return;
    if (!confirm(`确定要删除选中的 ${selectedGames.length} 个游戏吗？\n\n警告：此操作将同时删除所有关联的事件和参数，且不可恢复！`)) {
      return;
    }

    batchDeleteMutation.mutate(selectedGames);
  }, [selectedGames, batchDeleteMutation]);

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
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="游戏管理"
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
                  disabled={batchDeleteMutation.isLoading}
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
              onChange={(value) => setSearchTerm(value)}
              debounceMs={300}
            />
          </div>

          <div className="game-list">
            {isLoading ? (
              <div className="loading-state">加载中...</div>
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
                    onChange={(checked) => handleToggleSelect(game.gid)}
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
                  <div className="form-group">
                    <label>游戏名称</label>
                    <Input
                      type="text"
                      value={editingGame.name}
                      onChange={(e) => handleFieldChange('name', e.target.value)}
                      disabled={!hasChanges}
                      placeholder="输入游戏名称"
                    />
                  </div>

                  <div className="form-group">
                    <label>游戏GID</label>
                    <Input
                      type="text"
                      value={editingGame.gid}
                      disabled={true}
                      className="readonly-field"
                    />
                    <small className="field-hint">GID为只读字段，创建后不可修改</small>
                  </div>

                  <div className="form-group">
                    <label>ODS数据库</label>
                    <select
                      value={editingGame.ods_db}
                      onChange={(e) => handleFieldChange('ods_db', e.target.value)}
                      disabled={!hasChanges}
                      className="cyber-select"
                    >
                      <option value="ieu_ods">ieu_ods</option>
                      <option value="overseas_ods">overseas_ods</option>
                    </select>
                  </div>
                </div>

                {selectedGameData && (
                  <div className="detail-section">
                    <h4>统计数据</h4>
                    <div className="stats-grid">
                      <div className="stat-item">
                        <div className="stat-label">事件数</div>
                        <div className="stat-value">{selectedGameData.event_count || 0}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">参数数</div>
                        <div className="stat-value">{selectedGameData.param_count || 0}</div>
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
    </Modal>
  );
};

export default React.memo(GameManagementModal);
