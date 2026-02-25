/**
 * CategoriesListGraphQL - 分类管理页面(GraphQL版本)
 *
 * 完整迁移自CategoriesList.jsx,保留所有功能:
 * - 分类列表展示(卡片式)
 * - 搜索功能
 * - 批量选择和删除
 * - 单个分类编辑和删除
 * - 新建分类
 * - 分类统计信息(事件数量)
 *
 * 使用GraphQL API替代REST API
 */

import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, SearchInput, Skeleton, ErrorState, useToast } from '@shared/ui';
import EmptyState from '@shared/ui/EmptyState/EmptyState';
import { useGameStore } from '@/stores/gameStore';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { useCategories, useSearchCategories, useDeleteCategory, useGame } from '@/graphql/hooks';
import CategoryModal from '../components/categories/CategoryModal';
import './CategoriesList.css';

/**
 * Categories Management Page (GraphQL Version)
 * Displays category cards with search and CRUD operations
 *
 * Requires: game_gid URL parameter (enforced by backend API)
 */
export default function CategoriesListGraphQL() {
  const navigate = useNavigate();
  const location = useLocation();
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
      // Use GraphQL to fetch game data
      const fetchGame = async () => {
        try {
          const response = await fetch(`/api/games/${gameGid}`);
          const result = await response.json();
          if (result.data) {
            setCurrentGame(result.data);
          }
        } catch (err) {
          console.error('Failed to load game:', err);
        }
      };
      fetchGame();
    }
  }, [gameGid, currentGame, setCurrentGame]);

  // GraphQL queries - Fetch categories with React Query
  const { data: categoriesData = [], loading: isLoading, error, refetch } = useCategories(100, 0);

  const { data: searchData, loading: searchLoading } = useSearchCategories(searchTerm);

  // GraphQL mutations
  const [deleteCategory] = useDeleteCategory();

  // Get categories list
  const categories = useMemo(() => {
    if (searchTerm && searchData?.searchCategories) {
      return searchData.searchCategories;
    }
    return categoriesData?.categories || [];
  }, [categoriesData, searchData, searchTerm]);

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

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return;
    setConfirmState({
      open: true,
      title: '确认批量删除',
      message: `确定删除选中的 ${selectedIds.size} 个分类吗？`,
      onConfirm: async () => {
        setConfirmState(s => ({ ...s, open: false }));
        try {
          // Delete categories one by one (GraphQL doesn't have batch delete yet)
          let successCount = 0;
          for (const id of selectedIds) {
            const result = await deleteCategory({
              variables: { id }
            });
            if (result.data?.deleteCategory?.ok) {
              successCount++;
            }
          }
          success(`批量删除成功：${successCount} 个分类`);
          setSelectedIds(new Set());
          refetch();
        } catch (err) {
          showError(`批量删除失败: ${err.message}`);
        }
      }
    });
  };

  const handleDelete = (id) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: '确定删除此分类吗？',
      onConfirm: async () => {
        setConfirmState(s => ({ ...s, open: false }));
        try {
          const result = await deleteCategory({
            variables: { id }
          });
          if (result.data?.deleteCategory?.ok) {
            success('删除分类成功');
            refetch();
          } else {
            showError(result.data?.deleteCategory?.errors?.[0] || '删除失败');
          }
        } catch (err) {
          showError(`删除失败: ${err.message}`);
        }
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

  const loading = isLoading || searchLoading;
  if (loading) {
    return (
      <div className="categories-page">
        <div className="page-header">
          <div className="header-left">
            <h1>分类管理 (GraphQL)</h1>
          </div>
        </div>
        <div className="categories-grid">
          <Skeleton type="card" count={6} />
        </div>
      </div>
    );
  }
  if (error) {
    return <ErrorState message={error.message} onRetry={() => refetch()} />;
  }

  return (
    <div className="categories-page">
      <div className="page-header">
        <div className="header-left">
          <h1>分类管理 (GraphQL)</h1>
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
                {category.eventCount !== undefined && (
                  <div className="category-stats">
                    <span className="stat-item">
                      📄
                      {category.eventCount} 个事件
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
          refetch();
        }}
      />
    </div>
  );
}
