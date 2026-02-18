/**
 * CategoryManagementModal - 分类管理模态框
 *
 * 主从视图布局：
 * - 左侧：分类列表（显示分类名和事件数量）
 * - 右侧：分类详情表单（创建/编辑）
 *
 * 功能：
 * - 创建新分类
 * - 编辑现有分类
 * - 删除分类
 * - 保留game_gid URL参数
 */

import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BaseModal, Button, Input, useToast } from '@shared/ui';
import './CategoryManagementModal.css';

const CategoryManagementModal = ({ isOpen, onClose, gameGid }) => {
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();

  // Local state
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });

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

  const categories = apiResponse?.data || [];

  // Create category mutation
  const createMutation = useMutation({
    mutationFn: async (data) => {
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
      queryClient.invalidateQueries(['categories']);
      setIsCreating(false);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('创建分类失败');
    },
  });

  // Update category mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }) => {
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
      queryClient.invalidateQueries(['categories']);
      setSelectedCategory(null);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('更新分类失败');
    },
  });

  // Delete category mutation
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      const response = await fetch(`/api/categories/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete category');
      return response.json();
    },
    onSuccess: () => {
      success('删除分类成功');
      queryClient.invalidateQueries(['categories']);
      setSelectedCategory(null);
      setFormData({ name: '', description: '' });
    },
    onError: (err) => {
      showError('删除分类失败');
    },
  });

  // Handle new category button
  const handleNew = useCallback(() => {
    setIsCreating(true);
    setSelectedCategory(null);
    setFormData({ name: '', description: '' });
  }, []);

  // Handle edit category button
  const handleEdit = useCallback((category) => {
    setIsCreating(false);
    setSelectedCategory(category);
    setFormData({ name: category.name, description: category.description || '' });
  }, []);

  // Handle delete category button
  const handleDelete = useCallback(async (category) => {
    if (!confirm(`确定要删除分类"${category.name}"吗？`)) {
      return;
    }
    await deleteMutation.mutateAsync(category.id);
  }, [deleteMutation]);

  // Handle save (create or update)
  const handleSave = useCallback(async () => {
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
  const handleCancel = useCallback(() => {
    setIsCreating(false);
    setSelectedCategory(null);
    setFormData({ name: '', description: '' });
  }, []);

  if (!isOpen) return null;

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="分类管理" animation="slideUp" glassmorphism size="lg">
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
              <div className="loading">加载中...</div>
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
                    <Button variant="secondary" size="xs" onClick={() => handleEdit(category)}>
                      编辑
                    </Button>
                    <Button variant="danger" size="xs" onClick={() => handleDelete(category)}>
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
                <div className="form-group">
                  <label>分类名称</label>
                  <Input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="分类名称"
                  />
                </div>

                <div className="form-group">
                  <label>描述</label>
                  <Input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="分类描述（可选）"
                  />
                </div>

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
    </BaseModal>
  );
};

export default CategoryManagementModal;
