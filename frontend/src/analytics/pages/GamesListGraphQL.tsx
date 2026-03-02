// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { Link } from 'react-router-dom';
import { GET_GAMES } from '@/graphql/queries';
import {
  Input,
  Badge,
  Spinner,
  SearchInput,
  useToast,
  Skeleton,
  EmptyState,
  Button
} from '@shared/ui';
import { useGameStore } from '@/stores/gameStore';
import { useGameContext } from '@/shared/hooks/useGameContext';
import './ParametersList.css';

/**
 * 游戏管理页面 (GraphQL版本)
 *
 * 功能:
 * - 使用GraphQL查询游戏列表
 * - 支持搜索和过滤
 * - 显示游戏统计信息
 * - 提供游戏管理功能（编辑、删除）
 * - 不需要游戏上下文（全局页面）
 */

interface GameType {
  gid: number;
  name: string;
  odsDb: string;
  eventCount?: number;
  parameterCount?: number;
  description?: string;
}

function GamesListGraphQL() {
  const { success, error: showError, warning } = useToast();
  const { selectGame } = useGameContext();
  const { openGameManagementModal } = useGameStore();

  const [searchTerm, setSearchTerm] = useState('');

  // 使用GraphQL查询游戏列表
  const { data: gamesData, loading: isLoading, error, refetch } = useQuery(GET_GAMES, {
    variables: {
      limit: 100,
      offset: 0
    },
    fetchPolicy: 'cache-and-network',
    pollInterval: 60000, // 每分钟轮询一次
  });

  // 处理游戏数据
  const games = gamesData?.games || [];

  // 客户端搜索过滤
  const filteredGames = useMemo(() => {
    if (!searchTerm) return games;
    return games.filter((game: GameType) =>
      game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      game.gid?.toString().includes(searchTerm)
    );
  }, [games, searchTerm]);

  // 统计数据
  const stats = useMemo(() => {
    const totalGames = games.length;
    const totalEvents = games.reduce((sum, game: GameType) => sum + (game.eventCount || 0), 0);
    const totalParams = games.reduce((sum, game: GameType) => sum + (game.parameterCount || 0), 0);
    const avgEventsPerGame = totalGames > 0 ? (totalEvents / totalGames).toFixed(1) : 0;

    return {
      totalGames,
      totalEvents,
      totalParams,
      avgEventsPerGame
    };
  }, [games]);

  // 处理游戏点击（选择游戏并跳转到仪表板）
  const handleGameClick = useCallback((game: GameType) => {
    selectGame({
      id: game.gid,
      gid: game.gid,
      name: game.name,
      ods_db: game.odsDb
    });
    success(`已切换到游戏: ${game.name}`);
  }, [selectGame, success]);

  // 处理管理游戏
  const handleManageGames = useCallback(() => {
    openGameManagementModal();
  }, [openGameManagementModal]);

  // 错误状态
  if (error) {
    return (
      <div className="parameters-list-container">
        <div className="error-state">
          <i className="bi bi-exclamation-triangle text-warning"></i>
          <h3>加载游戏失败</h3>
          <p>{error.message}</p>
          <button className="btn btn-primary" onClick={() => {
            refetch();
            success('正在重新加载...');
          }}>
            重试
          </button>
        </div>
      </div>
    );
  }

  // 加载状态
  if (isLoading) {
    return (
      <div className="parameters-list-container">
        <div className="loading-container">
          <Spinner size="lg" label="正在加载游戏..." />
        </div>
      </div>
    );
  }

  return (
    <div className="parameters-list-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="header-title">
          <div className="icon-box">
            <i className="bi bi-controller"></i>
          </div>
          <div>
            <h1>游戏管理</h1>
            <p>管理和配置游戏项目</p>
          </div>
        </div>
        <div className="header-actions">
          <Button variant="outline-primary" onClick={handleManageGames}>
            <i className="bi bi-gear"></i>
            管理游戏
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-content">
            <div className="stat-number">{stats.totalGames}</div>
            <div className="stat-label">
              <i className="bi bi-controller"></i> 总游戏数
            </div>
          </div>
        </div>

        <div className="stat-card glass-card purple">
          <div className="stat-content">
            <div className="stat-number">{stats.totalEvents}</div>
            <div className="stat-label">
              <i className="bi bi-journal-code"></i> 总事件数
            </div>
          </div>
        </div>

        <div className="stat-card glass-card green">
          <div className="stat-content">
            <div className="stat-number">{stats.totalParams}</div>
            <div className="stat-label">
              <i className="bi bi-sliders"></i> 总参数数
            </div>
          </div>
        </div>

        <div className="stat-card glass-card orange">
          <div className="stat-content">
            <div className="stat-number">{stats.avgEventsPerGame}</div>
            <div className="stat-label">
              <i className="bi bi-graph-up"></i> 平均事件/游戏
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="filter-bar glass-card">
        <div className="filter-group">
          <SearchInput
            placeholder="搜索游戏名称或GID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-info">
          显示 {filteredGames.length} / {games.length} 个游戏
        </div>
      </div>

      {/* Games Table */}
      <div className="parameters-table-container glass-card">
        <table className="parameters-table">
          <thead>
            <tr>
              <th>GID</th>
              <th>游戏名称</th>
              <th>ODS数据库</th>
              <th>事件数</th>
              <th>参数数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredGames.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <EmptyState
                    icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
                    title={searchTerm ? "未找到匹配的游戏" : "暂无游戏数据"}
                    description={searchTerm ? "请尝试其他搜索词" : "点击右上角'管理游戏'按钮添加游戏"}
                  />
                </td>
              </tr>
            ) : (
              filteredGames.map((game: GameType) => (
                <tr key={game.gid}>
                  <td>
                    <Badge variant="info">{game.gid}</Badge>
                  </td>
                  <td>
                    <span className="param-name-link">{game.name}</span>
                  </td>
                  <td>
                    <Badge variant="secondary">{game.odsDb || '-'}</Badge>
                  </td>
                  <td>
                    <span className="event-name">{game.eventCount || 0}</span>
                  </td>
                  <td>
                    <span className="event-name">{game.parameterCount || 0}</span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => handleGameClick(game)}
                        title="切换到此游戏"
                      >
                        <i className="bi bi-arrow-return-left"></i> 切换
                      </button>
                      <Link
                        to={`/events?game_gid=${game.gid}`}
                        className="btn btn-sm btn-outline-secondary"
                        title="查看事件"
                      >
                        <i className="bi bi-journal-code"></i> 事件
                      </Link>
                      <Link
                        to={`/parameters?game_gid=${game.gid}`}
                        className="btn btn-sm btn-outline-info"
                        title="查看参数"
                      >
                        <i className="bi bi-sliders"></i> 参数
                      </Link>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default GamesListGraphQL;
