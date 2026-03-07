// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
// 游戏管理组件 - GraphQL版本 (已迁移)
// 替代原有的REST API版本

import React, { useState, useCallback, memo } from 'react';
import { useQuery, useMutation } from '@apollo/client/react';
import { 
  GET_GAMES, 
  GET_GAME, 
  CREATE_GAME, 
  UPDATE_GAME, 
  DELETE_GAME,
  SEARCH_GAMES 
} from '../../shared/graphql/operations';

interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  iconPath?: string;
  eventCount: number;
  parameterCount: number;
  createdAt: string;
  updatedAt: string;
}

export const GameManagementModal: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingGame, setEditingGame] = useState<Game | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // 查询游戏列表
  const { loading, error, data, refetch } = useQuery(GET_GAMES, {
    variables: { limit: 20, offset: 0 },
    fetchPolicy: 'cache-and-network',
  });

  // 搜索游戏
  const { data: searchData, loading: searchLoading } = useQuery(SEARCH_GAMES, {
    variables: { query: searchQuery },
    skip: !searchQuery,
  });

  // 创建游戏
  const [createGame, { loading: creating }] = useMutation(CREATE_GAME, {
    onCompleted: (result) => {
      if (result.createGame.ok) {
        alert('游戏创建成功!');
        setShowCreateForm(false);
        refetch();
      } else {
        alert(`创建失败: ${result.createGame.errors.join(', ')}`);
      }
    },
    onError: (error) => {
      alert(`创建失败: ${error.message}`);
    },
  });

  // 更新游戏
  const [updateGame, { loading: updating }] = useMutation(UPDATE_GAME, {
    onCompleted: (result) => {
      if (result.updateGame.ok) {
        alert('游戏更新成功!');
        setEditingGame(null);
        refetch();
      } else {
        alert(`更新失败: ${result.updateGame.errors.join(', ')}`);
      }
    },
  });

  // 删除游戏
  const [deleteGame, { loading: deleting }] = useMutation(DELETE_GAME, {
    onCompleted: (result) => {
      if (result.deleteGame.ok) {
        alert('游戏删除成功!');
        refetch();
      } else {
        alert(`删除失败: ${result.deleteGame.errors.join(', ')}`);
      }
    },
  });

  // ✅ 使用 useCallback 优化 - 处理创建游戏
  const handleCreateGame = useCallback((gameData: any) => {
    createGame({
      variables: {
        gid: parseInt(gameData.gid),
        name: gameData.name,
        ods_db: gameData.ods_db,
      },
    });
  }, [createGame]);

  // ✅ 使用 useCallback 优化 - 处理更新游戏
  const handleUpdateGame = useCallback((gameData: any) => {
    if (!editingGame) return;

    updateGame({
      variables: {
        gid: editingGame.gid,
        name: gameData.name,
        ods_db: gameData.ods_db,
      },
    });
  }, [editingGame, updateGame]);

  // ✅ 使用 useCallback 优化 - 处理删除游戏
  const handleDeleteGame = useCallback((game: Game) => {
    if (confirm(`确定要删除游戏 "${game.name}" 吗?`)) {
      deleteGame({
        variables: {
          gid: game.gid,
          confirm: true,
        },
      });
    }
  }, [deleteGame]);

  if (loading) return <div className="loading">加载中...</div>;
  if (error) return <div className="error">错误: {error.message}</div>;

  const games = searchQuery ? searchData?.searchGames : data?.games;

  return (
    <div className="game-management-modal">
      <div className="modal-header">
        <h2>游戏管理</h2>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          创建游戏
        </button>
      </div>

      {/* 搜索框 */}
      <div className="search-box">
        <input
          type="text"
          placeholder="搜索游戏..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchLoading && <span>搜索中...</span>}
      </div>

      {/* 游戏列表 */}
      <div className="game-list">
        {games?.map((game: Game) => (
          <div key={game.id} className="game-item">
            <div className="game-info">
              <h3>{game.name}</h3>
              <p>GID: {game.gid}</p>
              <p>数据库: {game.ods_db}</p>
              <div className="game-stats">
                <span>事件数: {game.eventCount}</span>
                <span>参数数: {game.parameterCount}</span>
              </div>
            </div>
            <div className="game-actions">
              <button 
                className="btn-secondary"
                onClick={() => setEditingGame(game)}
              >
                编辑
              </button>
              <button 
                className="btn-danger"
                onClick={() => handleDeleteGame(game)}
                disabled={deleting}
              >
                删除
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 创建游戏表单 */}
      {showCreateForm && (
        <GameForm
          onSubmit={handleCreateGame}
          onCancel={() => setShowCreateForm(false)}
          loading={creating}
        />
      )}

      {/* 编辑游戏表单 */}
      {editingGame && (
        <GameForm
          game={editingGame}
          onSubmit={handleUpdateGame}
          onCancel={() => setEditingGame(null)}
          loading={updating}
        />
      )}
    </div>
  );
};

// 游戏表单组件
interface GameFormProps {
  game?: Game | null;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  loading: boolean;
}

const GameForm: React.FC<GameFormProps> = ({ game, onSubmit, onCancel, loading }) => {
  const [formData, setFormData] = useState({
    gid: game?.gid || '',
    name: game?.name || '',
    ods_db: game?.ods_db || 'ieu_ods',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>{game ? '编辑游戏' : '创建游戏'}</h3>
        <form onSubmit={handleSubmit}>
          {!game && (
            <div className="form-group">
              <label>GID:</label>
              <input
                type="number"
                value={formData.gid}
                onChange={(e) => setFormData({ ...formData, gid: e.target.value })}
                required
              />
            </div>
          )}
          <div className="form-group">
            <label>游戏名称:</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>数据库:</label>
            <select
              value={formData.ods_db}
              onChange={(e) => setFormData({ ...formData, ods_db: e.target.value })}
            >
              <option value="ieu_ods">ieu_ods</option>
              <option value="overseas_ods">overseas_ods</option>
            </select>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? '提交中...' : '提交'}
            </button>
            <button type="button" className="btn-secondary" onClick={onCancel}>
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ✅ 添加 React.memo 优化渲染性能
const GameManagementModalGraphQLMemo = memo(GameManagementModal);

export default GameManagementModalGraphQLMemo;
