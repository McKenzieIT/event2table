/**
 * ⚠️ DEPRECATED - 此组件已废弃，请使用GameManagementModalGraphQL.tsx
 *
 * 废弃时间：2026-03-19
 * 废弃原因：
 * - 项目统一使用GraphQL API
 * - GameManagementModalGraphQL提供更好的类型安全和性能
 * - 避免维护两套相似代码，降低维护成本
 *
 * 迁移指南：
 * 1. 将导入从 'GameManagementModal' 改为 'GameManagementModalGraphQL'
 * 2. 更新mutation调用为GraphQL mutations（使用Apollo Client）
 * 3. 删除fetch API调用，改用useMutation hook
 *
 * 示例：
 * // ❌ 旧代码（REST API）
 * import GameManagementModal from '@/features/games/GameManagementModal';
 *
 * // ✅ 新代码（GraphQL）
 * import GameManagementModal from '@/features/games/GameManagementModalGraphQL';
 *
 * @deprecated 使用 GameManagementModalGraphQL 替代
 * @see GameManagementModalGraphQL
 *
 * 保留原因：向后兼容，确保现有代码不会立即崩溃
 * 计划删除时间：2026-06-19（废弃后3个月）
 */

// ⚡️ REACT PERF - Features: Optimized with React.memo, useCallback, useMemo
// ✅ Performance optimization: Prevent unnecessary re-renders in game management
// See: docs/reports/2026-03-06/FEATURES-OPTIMIZATION-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
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

import React, { useState, useMemo, useCallback, memo, ReactElement } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal, Button, Input, Checkbox, useToast, SearchInput, Skeleton, EmptyState } from '@shared/ui';
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

      </Modal>