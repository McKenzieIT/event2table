import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, SearchInput } from '@shared/ui';
import './CategoriesList.css';

/**
 * Categories Management Page
 * Displays category cards with search and CRUD operations
 */
export default function CategoriesList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());

  // Fetch categories with React Query
  const { data: categories = [], isLoading, error } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const res = await fetch('/api/categories');
      if (!res.ok) throw new Error('Failed to fetch categories');
      const result = await res.json();
      return result.data || [];
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      const res = await fetch(`/api/categories/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete category');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
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
    onSuccess: () => {
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    }
  });

  // Filter categories
  const filteredCategories = categories.filter(category => {
    return category.name?.toLowerCase().includes(searchTerm.toLowerCase());
  });

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
    if (confirm(`确定删除选中的 ${selectedIds.size} 个分类吗？`)) {
      batchDeleteMutation.mutate(selectedIds);
    }
  };

  const handleDelete = (id) => {
    if (confirm('确定删除此分类吗？')) {
      deleteMutation.mutate(id);
    }
  };

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
          onClick={() => navigate('/categories/create')}
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
          <div className="empty-state">
            <span>📥</span>
            <p>没有找到分类</p>
          </div>
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
                  onClick={() => navigate(`/categories/${category.id}/edit`)}
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
    </div>
  );
}
