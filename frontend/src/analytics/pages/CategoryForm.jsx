import React, { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams, Link } from 'react-router-dom';
import './CategoryForm.css';

/**
 * 分类表单组件
 * 创建/编辑分类
 * 最佳实践: useCallback + 提前返回 + 并行加载
 */
function CategoryForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [errors, setErrors] = useState({});

  // 并行加载数据（编辑模式）
  const { data: initialData, isLoading } = useQuery({
    queryKey: ['category', id],
    queryFn: async () => {
      if (!isEdit) return null;
      const response = await fetch(`/api/categories/${id}`);
      if (!response.ok) throw new Error('加载分类失败');
      return response.json();
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
    mutationFn: async (data) => {
      const url = isEdit ? `/api/categories/${id}` : '/api/categories';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || '操作失败');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['categories']);
      navigate('/categories');
    },
    onError: (error) => {
      setErrors({ submit: error.message });
    }
  });

  // 验证表单（提前返回优化）
  const validateForm = useCallback(() => {
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = '分类名称不能为空';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;
    if (mutation.isLoading) return;

    try {
      await mutation.mutateAsync(formData);
    } catch (error) {
      // Error handled in mutation onError
    }
  };

  if (isLoading) {
    return <div className="loading">加载中...</div>;
  }

  return (
    <div className="category-form-container">
      <div className="page-header">
        <h1>{isEdit ? '编辑分类' : '添加分类'}</h1>
        <Link to="/categories" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="form-card glass-card">
        {errors.submit && (
          <div className="alert alert-danger">{errors.submit}</div>
        )}

        <div className="form-group">
          <label htmlFor="name">分类名称 *</label>
          <input
            type="text"
            id="name"
            className={`form-control ${errors.name ? 'is-invalid' : ''}`}
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="例如: 战斗"
          />
          {errors.name && <div className="invalid-feedback">{errors.name}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="description">描述</label>
          <textarea
            id="description"
            className="form-control"
            rows="4"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="分类的详细描述..."
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={mutation.isLoading}
          >
            {mutation.isLoading ? '提交中...' : (isEdit ? '保存修改' : '创建分类')}
          </button>
          <Link
            to="/categories"
            className="btn btn-outline-secondary"
          >
            取消
          </Link>
        </div>
      </form>
    </div>
  );
}

export default CategoryForm;
