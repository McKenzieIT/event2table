/**
 * Game Management Modal - 游戏管理模态框
 *
 * 主从视图布局：
 * - 左侧：游戏列表
 * - 右侧：游戏详情编辑
 *
 * 功能：
 * - 点击游戏显示详情
 * - 编辑字段默认disabled
 * - 检测修改后显示保存按钮
 * - 统计数据展示
 * - 删除游戏
 */

import React, { useState, useMemo, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useGameStore } from '@/stores/gameStore';
import { Button, Card, Badge, Spinner } from '@shared/ui';
import './GameManagementModal.css';

/**
 * 游戏管理模态框组件
 */
function GameManagementModal({ isOpen, onClose }) {
  const { currentGame } = useGameStore();
  const [selectedGameGid, setSelectedGameGid] = useState<number | null>(null);
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});

  const queryClient = useQueryClient();

  // 获取所有游戏数据
  const { data: gamesData, isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) throw new Error('Failed to fetch games');
      return response.json();
    },
    enabled: isOpen,
    staleTime: 30 * 1000  // 30 seconds - don't refetch often
  });

  const games = gamesData?.data || [];

  // 处理选择游戏
  const handleSelectGame = useCallback((gameGid: number) => {
    setSelectedGameGid(gameGid);
    setEditMode({});
  }, []);

  // 处理编辑变化
  const handleEditChange = useCallback((field: string, value: any) => {
    setEditMode(prev => ({
      ...prev,
      [field]: value !== ''  // 检测是否有修改
    }));
  }, []);

  // 保存游戏信息
  const handleSaveGame = async () => {
    if (!selectedGameGid) return;

    const game = games.find(g => g.gid === selectedGameGid);
    if (!game) return;

    try {
      const response = await fetch(`/api/games/${game.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editMode.name || game.name,
          ods_db: editMode.ods_db || game.ods_db,
          dwd_prefix: editMode.dwd_prefix || game.dwd_prefix
        })
      });

      if (!response.ok) throw new Error('Failed to save game');

      // 刷新游戏列表
      queryClient.invalidateQueries(['games']);

      // 清除编辑模式
      setEditMode({});
    } catch (error) {
      console.error('Error saving game:', error);
    }
  }, [selectedGameGid, editMode]);

  // 删除游戏
  const handleDeleteGame = async (game: any) => {
    if (!confirm(`确定要删除游戏"${game.name}"吗？`)) return;

    try {
      const response = await fetch(`/api/games/${game.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete game');

      // 刷新游戏列表
      queryClient.invalidateQueries(['games']);

      // 清除选择
      if (selectedGameGid === game.gid) {
        setSelectedGameGid(null);
        setEditMode({});
      }
    } catch (error) {
      console.error('Error deleting game:', error);
    }
  }, []);

  // 统计数据（模拟，实际应从API获取）
  const gameStats = useMemo(() => {
    if (!selectedGameGid) return { eventCount: 0, paramCount: 0, nodeCount: 0, flowCount: 0 };
    const game = games.find(g => g.gid === selectedGameGid);
    if (!game) return gameStats;

    return {
      eventCount: game.event_count || 0,
      paramCount: game.param_count || 0,
      nodeCount: 0,  // TODO: 从API获取
      flowCount: 0    // TODO: 从API获取
    };
  }, [selectedGameGid, games]);

  return (
    <div className="game-management-modal-overlay" onClick={onClose}>
      <div className="game-management-modal" onClick={(e) => e.stopPropagation()}>
        {/* 头部 */}
        <div className="modal-header">
          <h2>游戏管理</h2>
          <Button variant="text" onClick={onClose}>×</Button>
        </div>

        {/* 主内容 */}
        <div className="modal-content">
          {/* 左侧游戏列表 */}
          <div className="games-list">
            {games.map(game => (
              <div
                key={game.gid}
                className={`game-item ${selectedGameGid === game.gid ? 'selected' : ''}`}
                onClick={() => handleSelectGame(game.gid)}
              >
                <div className="game-info">
                  <h3>{game.name}</h3>
                  <p>GID: {game.gid}</p>
                </div>
                <Badge variant="info">
                  {game.event_count || 0} 事件
                </Badge>
              </div>
            ))}
          </div>

          {/* 右侧详情编辑 */}
          {selectedGameGid && (
            <div className="game-details">
              <h3>编辑游戏</h3>

              {/* 表单字段 */}
              <div className="form-fields">
                {/* 游戏名称 */}
                <div className="form-field">
                  <label>游戏名称</label>
                  <input
                    type="text"
                    value={editMode.name || games.find(g => g.gid === selectedGameGid)?.name}
                    onChange={(e) => handleEditChange('name', e.target.value)}
                    disabled={!editMode.name}
                    placeholder="游戏名称"
                  />
                </div>

                {/* GID（只读） */}
                <div className="form-field">
                  <label>GID</label>
                  <input
                    type="text"
                    value={selectedGameGid?.toString() || ''}
                    disabled
                    readOnly
                  />
                </div>

                {/* ODS数据库 */}
                <div className="form-field">
                  <label>ODS数据库</label>
                  <select
                    value={editMode.ods_db || games.find(g => g.gid === selectedGameGid)?.ods_db}
                    onChange={(e) => handleEditChange('ods_db', e.target.value)}
                    disabled={!editMode.ods_db}
                  >
                    <option value="ieu_ods">ieu_ods</option>
                    <option value="overseas_ods">overseas_ods</option>
                  </select>
                  </div>

                {/* DWD前缀（可选） */}
                <div className="form-field">
                  <label>DWD前缀（可选）</label>
                  <input
                    type="text"
                    value={editMode.dwd_prefix || games.find(g => g.gid === selectedGameGid)?.dwd_prefix || ''}
                    onChange={(e) => handleEditChange('dwd_prefix', e.target.value)}
                    disabled={!editMode.dwd_prefix}
                    placeholder="可选"
                  />
                </div>
              </div>

              {/* 统计数据 */}
              <div className="game-stats">
                <div className="stat-item">
                  <div className="stat-icon">📊</div>
                  <div className="stat-content">
                    <div className="stat-value">{gameStats.eventCount}</div>
                    <div>事件</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">⚙️</div>
                  <div className="stat-content">
                    <div className="stat-value">{gameStats.paramCount}</div>
                    <div>参数</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">🔗</div>
                  <div className="stat-content">
                    <div className="stat-value">{gameStats.nodeCount}</div>
                    <div>事件节点</div>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-icon">📋</div>
                  <div className="stat-content">
                    <div className="stat-value">{gameStats.flowCount}</div>
                    <div>HQL流程</div>
                  </div>
                </div>
              </div>

              {/* 保存和删除按钮 */}
              <div className="form-actions">
                <Button
                  variant="primary"
                  onClick={handleSaveGame}
                  disabled={!Object.keys(editMode).some(key => editMode[key])}
                >
                  💾 保存更改
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeleteGame(games.find(g => g.gid === selectedGameGid)!)}
                  className="delete-btn"
                >
                  🗑️ 删除游戏
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* 右上角：添加游戏按钮 */}
        <div className="add-game-button-wrapper">
          <Button
            variant="primary"
            onClick={() => {
              setSelectedGameGid(null);
              setEditMode({});
            }}
            className="add-game-btn"
          >
            + 添加游戏
          </Button>
        </div>
      </div>

      {isLoading && (
        <div className="loading-overlay">
          <Spinner size="lg" label="加载中..." />
        </div>
      )}
    </div>
  );
}

export default GameManagementModal;
