// ⚡️ REACT PERF: Added React.memo, useCallback
// Optimized: Stable callbacks for form handlers

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { Button, Spinner, Input } from '@shared/ui';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import React, { useState, useCallback, memo } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import './CategoryForm.css';

/**
 * TypeScript interfaces for Category Form
 */
interface CategoryFormData {
  name: string;
  description: string;
}

interface Category {
  id?: number;
  name: string;
  description?: string;
}

interface FormErrors {
  name?: string;
  submit?: string;
}

interface CategoryResponse {
  success: boolean;
  data?: Category;
  message?: string;
}

/**
 * 分类表单组件
 * 创建/编辑分类
 * 最佳实践: useCallback + 提前返回 + 并行加载
 */
function CategoryForm() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const [formData, setFormData] = useState<CategoryFormData>({
    name: '',
    description: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});

  // 并行加载数据（编辑模式）
  const { data: initialData, isLoading } = useQuery<Category>({
    queryKey: ['category', id],
    queryFn: async () => {
      if (!isEdit) return null as any;
      const response = await fetch(`/api/categories/${id}`);
      if (!response.ok) throw new Error('加载分类失败');
      const result: CategoryResponse = await response.json();
      return result.data;
    },
    enabled: isEdit,
    onSuccess: (data) => {
      if (data && typeof data === 'object') {
        setFormData({
          name: data.name || '',
          description: data.description || ''
        });
      }
    }
  });

  // 提交mutation
  const mutation = useMutation({
    mutationFn: async (data: CategoryFormData): Promise<CategoryResponse> => {
      const url = isEdit ? `/api/categories/${id}` : '/api/categories';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const result: CategoryResponse = await response.json();
        throw new Error(result.message || '操作失败');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['categories']);
      navigate('/categories');
    },
    onError: (error: Error) => {
      setErrors({ submit: error.message });
    }
  });

  // 验证表单（提前返回优化）
  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = '分类名称不能为空';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;
    if (mutation.isLoading) return;

    try {
      await mutation.mutateAsync(formData);
    } catch (error) {
      // Error handled in mutation onError
    }
  }, [validateForm, mutation.isLoading, mutation.mutateAsync, formData]);

  if (isLoading) {
    return (
      <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  return (
    <div className="category-form-container">
      <div className="page-header">
        <h1>{isEdit ? '编辑分类' : '添加分类'}</h1>
        <Button variant="secondary" onClick={() => navigate('/categories')}>
          <i className="bi bi-arrow-left" aria-hidden="true"></i>
          返回
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="form-card glass-card">
        {errors.submit && (
          <div className="alert alert-danger">{errors.submit}</div>
        )}

        <Input
          id="name"
          name="name"
          label="分类名称 *"
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="例如: 战斗"
          error={errors.name}
        />

        <div className="form-group">
          <label htmlFor="description">描述</label>
          <textarea
            id="description"
            className="form-control"
            rows={4}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="分类的详细描述..."
          />
        </div>

        <div className="form-actions">
          <Button
            variant="primary"
            type="submit"
            loading={mutation.isLoading}
          >
            {mutation.isLoading ? '提交中...' : (isEdit ? '保存修改' : '创建分类')}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/categories')}>
            取消
          </Button>
        </div>
      </form>
    </div>
  );
}

export default memo(CategoryForm);
