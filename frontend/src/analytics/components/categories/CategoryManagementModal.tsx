// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * CategoryManagementModal - Category Management Modal
 *
 * Master-detail view layout:
 * - Left: Category list (shows category name and event count)
 * - Right: Category detail form (create/edit)
 *
 * Features:
 * - Create new category
 * - Edit existing category
 * - Delete category
 * - Preserve game_gid URL parameter
 */

import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import { Modal, Button, Input, Spinner, useToast } from '@shared/ui';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import React, { useState, useCallback, useRef, useEffect } from 'react';
import './CategoryManagementModal.css';

interface Category {
  id: number;
  name: string;
  description?: string;
  event_count?: number;
}

interface CategoryFormData {
  name: string;
  description: string;
}

interface CategoryManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  gameGid?: number;
}

const CategoryManagementModal: React.FC<CategoryManagementModalProps> = ({
  isOpen,
  onClose,
  gameGid
}) => {
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();

  // Local state
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [formData, setFormData] = useState<CategoryFormData>({ name: '', description: '' });

  // Refs to input elements (for Chrome MCP compatibility)
  const nameRef = useRef<HTMLInputElement>(null);
  const descRef = useRef<HTMLInputElement>(null);

  // Promise-based confirm dialog
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  // Fetch categories list
  const { data: apiResponse, isLoading } = useQuery({
    queryKey: ['categories', gameGid],
    queryFn: async () => {
      const response = await fetch(`/api/categories?game_gid=${gameGid}`);
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    },
    enabled: isOpen && !!gameGid,
  });

  const categories: Category[] = apiResponse?.data || [];

  // Create category mutation
  const createMutation = useMutation({
    mutationFn: async (data: CategoryFormData) => {
      const response = await fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create category');
      return response.json();
    },
    onSuccess: () => {
      success('创建分类成功');
      // Fix: Use complete cache key with gameGid for precise invalidation
      queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
      setIsCreating(false);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('创建分类失败');
    },
  });

  // Update category mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: CategoryFormData }) => {
      const response = await fetch(`/api/categories/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to update category');
      return response.json();
    },
    onSuccess: () => {
      success('更新分类成功');
      // Fix: Use complete cache key with gameGid for precise invalidation
      queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
      setSelectedCategory(null);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('更新分类失败');
    },
  });

  // Delete category mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`/api/categories/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete category');
      return response.json();
    },
    onSuccess: () => {
      success('删除分类成功');
      // Fix: Use complete cache key with gameGid for precise invalidation
      queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });
      setSelectedCategory(null);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('删除分类失败');
    },
  });

  // Handle new category button
  const handleNew = useCallback((): void => {
    setIsCreating(true);
    setSelectedCategory(null);
    setFormData({ name: '', description: '' });
  }, []);

  // Handle edit category button
  const handleEdit = useCallback((category: Category): void => {
    setIsCreating(false);
    setSelectedCategory(category);
    setFormData({ name: category.name, description: category.description || '' });
  }, []);

  // Handle delete category button
  const handleDelete = useCallback(async (category: Category): Promise<void> => {
    if (!(await confirm(`确定要删除分类"${category.name}"吗？`))) {
      return;
    }
    await deleteMutation.mutateAsync(category.id);
  }, [deleteMutation, confirm]);

  // Handle save (create or update)
  const handleSave = useCallback(async (): Promise<void> => {
    if (!formData.name.trim()) {
      showError('分类名称不能为空');
      return;
    }

    if (isCreating) {
      await createMutation.mutateAsync(formData);
    } else if (selectedCategory) {
      await updateMutation.mutateAsync({ id: selectedCategory.id, data: formData });
    }
  }, [formData, isCreating, selectedCategory, createMutation, updateMutation, showError]);

  // Handle cancel
  const handleCancel = useCallback((): void => {
    setIsCreating(false);
    setSelectedCategory(null);
    setFormData({ name: '', description: '' });
  }, []);

  // Chrome MCP兼容性: 监听DOM值变化并同步到state
  useEffect(() => {
    if (!nameRef.current || !descRef.current) {
      return;
    }

    const nameDomValue = nameRef.current.value;
    const descDomValue = descRef.current.value;

    const updates: Partial<CategoryFormData> = {};

    if (nameDomValue !== formData.name) {
      updates.name = nameDomValue;
    }
    if (descDomValue !== formData.description) {
      updates.description = descDomValue;
    }

    if (Object.keys(updates).length > 0) {
      setFormData(prev => ({ ...prev, ...updates }));
    }
  }, [formData.name, formData.description]);

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="分类管理" animation="slideUp" glassmorphism size="lg">
      <div className="category-management-modal">
        {/* Left Panel: Category List */}
        <div className="category-list-panel">
          <div className="panel-header">
            <h3>分类列表</h3>
            <Button variant="primary" size="sm" onClick={handleNew}>
              新建分类
            </Button>
          </div>

          <div className="category-list">
            {isLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
                <Spinner size="lg" label="加载中..." />
              </div>
            ) : categories.length === 0 ? (
              <div className="empty-state">暂无分类</div>
            ) : (
              categories.map((category) => (
                <div key={category.id} className="category-item">
                  <div className="category-info">
                    <div className="category-name">{category.name}</div>
                    <div className="category-count">{category.event_count || 0} 个事件</div>
                  </div>
                  <div className="category-actions">
                    <Button variant="secondary" size="sm" onClick={() => handleEdit(category)}>
                      编辑
                    </Button>
                    <Button variant="danger" size="sm" onClick={() => handleDelete(category)}>
                      删除
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Panel: Category Form */}
        <div className="category-form-panel">
          {isCreating || selectedCategory ? (
            <>
              <div className="panel-header">
                <h3>{isCreating ? '新建分类' : '编辑分类'}</h3>
              </div>

              <div className="category-form">
                <Input
                  label="分类名称"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="分类名称"
                  required
                  ref={nameRef}
                />

                <Input
                  label="描述"
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="分类描述（可选）"
                  ref={descRef}
                />

                <div className="form-actions">
                  <Button variant="secondary" onClick={handleCancel}>
                    取消
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleSave}
                    disabled={createMutation.isPending || updateMutation.isPending}
                  >
                    保存
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-form-state">
              <p>请选择一个分类进行编辑，或创建新分类</p>
            </div>
          )}
        </div>
      </div>

      {/* Promise-based confirm dialog */}
      <ConfirmDialogComponent />
    </Modal>
  );
};

export default CategoryManagementModal;
