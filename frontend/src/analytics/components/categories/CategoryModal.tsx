/**
 * Category Modal - 分类管理模态框组件
 *
 * 功能：纯表单模态框，支持新增和编辑两种模式
 * 通过 initialData prop 区分模式：null = 新增，有值 = 编辑
 */

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Input } from '@shared/ui';
import { useToast } from '@shared/ui/Toast/Toast';
import { BaseModal } from '@shared/ui/BaseModal';
import './CategoryModal.css';

interface CategoryFormData {
  name: string;
  description: string;
}

interface Category {
  id: number;
  name: string;
  description: string;
}

interface CategoryModalProps {
  /** 模态框显示状态 */
  isOpen: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 当前游戏GID */
  gameGid: number;
  /** 编辑数据（null时为新增模式） */
  initialData: Category | null;
  /** 成功回调 */
  onSuccess?: () => void;
}

interface FormErrors {
  name?: string;
}

/**
 * Category Modal Component
 */
function CategoryModal({ isOpen, onClose, gameGid, initialData, onSuccess }: CategoryModalProps): React.JSX.Element {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  // 模式检测：initialData === null 时为新增模式
  const isEditMode = initialData !== null;

  // 表单状态
  const [formData, setFormData] = useState<CategoryFormData>({
    name: '',
    description: ''
  });

  // 验证错误
  const [errors, setErrors] = useState<FormErrors>({});

  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 当模态框打开或 initialData 变化时，重置表单
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        // 编辑模式：填充数据
        setFormData({
          name: initialData.name || '',
          description: initialData.description || ''
        });
      } else {
        // 新增模式：清空表单
        setFormData({ name: '', description: '' });
      }
      setErrors({});
    }
  }, [initialData, isOpen]);

  // 关闭模态框
  const handleClose = () => {
    setFormData({ name: '', description: '' });
    setErrors({});
    onClose();
  };

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = '分类名称不能为空';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 提交 mutation
  const submitMutation = useMutation({
    mutationFn: async (data: CategoryFormData) => {
      const url = isEditMode
        ? `/api/categories/${initialData!.id}`
        : '/api/categories';

      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          game_gid: gameGid
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '操作失败');
      }

      return response.json();
    },
    onSuccess: () => {
      // 刷新分类列表（包含 gameGid）
      queryClient.invalidateQueries({ queryKey: ['categories', gameGid] });

      // 成功提示
      const action = isEditMode ? '更新' : '创建';
      success(`分类"${formData.name}"${action}成功！`);

      // 触发成功回调
      if (onSuccess) {
        onSuccess();
      }

      // 关闭模态框
      handleClose();
    },
    onError: (err: Error) => {
      console.error('分类操作失败:', err);
      error(err.message || '操作失败，请稍后重试');
    },
    onSettled: () => {
      setIsSubmitting(false);
    }
  });

  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    // 准备提交数据
    const submitData: CategoryFormData = {
      name: formData.name.trim(),
      description: formData.description.trim() || ''
    };

    submitMutation.mutate(submitData);
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleClose}
      title={
        <span>
          {isEditMode ? '编辑分类' : '新增分类'}
          <span className={`category-modal__mode-hint ${isEditMode ? 'edit' : 'create'}`}>
            {isEditMode ? '✎ 编辑模式' : '➕ 新增模式'}
          </span>
        </span>
      }
      animation="slideUp"
      glassmorphism
      size="lg"
      closeOnBackdropClick={false}
    >
      <div className="category-modal">
        <div className="category-modal__container">
          {/* 表单 */}
          <form className="category-modal__form" onSubmit={handleSubmit}>
            {/* 分类名称 */}
            <div className="category-modal__field">
              <label htmlFor="categoryName" className="category-modal__label">
                分类名称 <span className="required">*</span>
              </label>
              <Input
                type="text"
                id="categoryName"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="例如：战斗事件"
                className="category-modal__input"
                disabled={isSubmitting}
              />
              {errors.name && (
                <span className="category-modal__error">{errors.name}</span>
              )}
            </div>

            {/* 分类描述 */}
            <div className="category-modal__field">
              <label htmlFor="categoryDesc" className="category-modal__label">
                分类描述
              </label>
              <textarea
                id="categoryDesc"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="简要描述该分类的用途和包含的事件类型..."
                className="category-modal__textarea"
                disabled={isSubmitting}
                rows={4}
              />
              <span className="category-modal__hint">
                可选：提供详细说明帮助团队理解分类用途
              </span>
            </div>

            {/* 表单操作按钮 */}
            <div className="category-modal__actions">
              <Button
                type="button"
                variant="text"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                取消
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting || !formData.name.trim()}
              >
                {isSubmitting ? '保存中...' : isEditMode ? '💾 保存修改' : '➕ 创建分类'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </BaseModal>
  );
}

export default CategoryModal;
