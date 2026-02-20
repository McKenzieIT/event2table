import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, SearchInput, useToast } from '@shared/ui';
import EmptyState from '@shared/ui/EmptyState/EmptyState';
import { useGameStore } from '@/stores/gameStore';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import CategoryModal from '../components/categories/CategoryModal';
import './CategoriesList.css';

/**
 * Categories Management Page
 * Displays category cards with search and CRUD operations
 *
 * Requires: game_gid URL parameter (enforced by backend API)
 */
export default function CategoriesList() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { currentGame, setCurrentGame } = useGameStore();
  const { success, error: showError } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  // Read game_gid from URL parameters
  const gameGid = new URLSearchParams(location.search).get('game_gid');

  // Load game data if game_gid is in URL but not in store
  useEffect(() => {
    if (gameGid && (!currentGame || currentGame.gid != gameGid)) {
      fetch(`/api/games/${gameGid}`)
        .then(res => res.json())
        .then(result => {
          if (result.data) {
            setCurrentGame(result.data);
          }
        })
        .catch(err => {
          console.error('Failed to load game:', err);
        });
    }
  }, [gameGid, currentGame, setCurrentGame]);

  // Fetch categories with React Query (requires game_gid)
  const { data: categories = [], isLoading, error } = useQuery({
    queryKey: ['categories', gameGid],
    queryFn: async () => {
      if (!gameGid) {
        throw new Error('game_gid is required');
      }

      const res = await fetch(`/api/categories?game_gid=${gameGid}`);
      if (!res.ok) {
        if (res.status === 400) {
          throw new Error('game_gid is required');
        }
        if (res.status === 404) {
          throw new Error(`Game ${gameGid} not found`);
        }
        throw new Error('Failed to fetch categories');
      }

      const result = await res.json();
      const data = result.data || [];

      // 确保返回的是数组
      if (!Array.isArray(data)) {
        console.error('Categories API returned non-array data:', data);
        return [];
      }

      return data;
    },
    enabled: !!gameGid // Only run query if gameGid exists
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      const res = await fetch(`/api/categories/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete category');
      return res.json();
    },
    onSuccess: () => {
      success('删除分类成功');
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: () => {
      showError('删除分类失败');
    }
  });

  // Batch delete mutation
  const batchDeleteMutation = useMutation({
    mutationFn: async (ids) => {
      const res = await fetch('/api/categories/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: Array.from(ids) })
      });
      if (!res.ok) throw new Error('Failed to batch delete categories');
      return res.json();
    },
    onSuccess: (data, ids) => {
      success(`批量删除成功：${ids.size} 个分类`);
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    },
    onError: () => {
      showError('批量删除失败');
    }
  });

  // FIX: 使用useMemo优化过滤逻辑，避免每次渲染都重新计算
  const filteredCategories = useMemo(() => 
    categories.filter(category => {
      return category.name?.toLowerCase().includes(searchTerm.toLowerCase());
    }), 
    [categories, searchTerm]
  );

  // Selection handlers
  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredCategories.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredCategories.map(c => c.id)));
    }
  };

  const handleBatchDelete = () => {
    if (selectedIds.size === 0) return;
    setConfirmState({
      open: true,
      title: '确认批量删除',
      message: `确定删除选中的 ${selectedIds.size} 个分类吗？`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        batchDeleteMutation.mutate(selectedIds);
      }
    });
  };

  const handleDelete = (id) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: '确定删除此分类吗？',
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        deleteMutation.mutate(id);
      }
    });
  };

  // Show error if game_gid is missing
  if (!gameGid) {
    return (
      <div className="error-state">
        <h2>请先选择游戏</h2>
        <p>分类管理需要选择一个游戏才能查看。</p>
        <Button onClick={() => navigate('/')}>
          返回首页选择游戏
        </Button>
      </div>
    );
  }

  if (isLoading) return <div className="loading-state">加载中...</div>;
  if (error) return <div className="error-state">加载失败: {error.message}</div>;

  return (
    <div className="categories-page">
      <div className="page-header">
        <div className="header-left">
          <h1>分类管理</h1>
          <span className="category-count">共 {filteredCategories.length} 个分类</span>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setEditingCategory(null);
            setIsModalOpen(true);
          }}
        >
          新建分类
        </Button>
      </div>

      {/* Selection Bar */}
      {selectedIds.size > 0 && (
        <div className="selection-bar">
          <span className="selection-count">已选择 {selectedIds.size} 个分类</span>
          <div className="selection-actions">
            <Button
              variant="danger"
              onClick={handleBatchDelete}
              disabled={batchDeleteMutation.isPending}
            >
              批量删除
            </Button>
            <Button
              variant="secondary"
              onClick={() => setSelectedIds(new Set())}
            >
              取消选择
            </Button>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="categories-toolbar">
        <div className="search-box">
          <SearchInput
            placeholder="搜索分类名称或编码..."
            value={searchTerm}
            onChange={(value) => setSearchTerm(value)}
          />
        </div>
      </div>

      {/* Category Cards Grid */}
      <div className="categories-grid">
        {filteredCategories.length === 0 ? (
          <EmptyState
            icon={<span aria-hidden="true">📥</span>}
            title="没有找到分类"
            description="尝试调整搜索条件"
          />
        ) : (
          filteredCategories.map(category => (
            <div key={category.id} className="category-card">
              <div className="card-header">
                <input
                  type="checkbox"
                  checked={selectedIds.has(category.id)}
                  onChange={() => toggleSelect(category.id)}
                />
                <h3>{category.name}</h3>
              </div>
              <div className="card-body">
                {category.description && (
                  <p className="category-description">{category.description}</p>
                )}
                {category.event_count !== undefined && (
                  <div className="category-stats">
                    <span className="stat-item">
                      📄
                      {category.event_count} 个事件
                    </span>
                  </div>
                )}
              </div>
              <div className="card-footer">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setEditingCategory(category);
                    setIsModalOpen(true);
                  }}
                >
                  编辑
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDelete(category.id)}
                  disabled={deleteMutation.isPending}
                >
                  删除
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

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

      <CategoryModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingCategory(null);
        }}
        gameGid={gameGid}
        initialData={editingCategory}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['categories'] });
        }}
      />
    </div>
  );
}
