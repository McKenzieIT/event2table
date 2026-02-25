/**
 * Shared GameForm Component
 *
 * 统一的游戏表单组件,支持:
 * - Modal 模式 (在模态框中使用)
 * - Page 模式 (在独立页面使用)
 * - 卡片式 ODS 选择器 (优秀的 UX)
 * - 统一的验证逻辑
 * - 实时验证 (touched 机制)
 */

import React, { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Input } from '@shared/ui';
import { ODSSelector } from './ODSSelector';
import { useGameFormValidation } from './useGameFormValidation';
import { useGameFormToast } from './useGameFormToast';
import styles from './GameForm.module.css';

export const GameForm = ({
  mode = 'modal', // 'modal' | 'page'
  onSuccess,
  onCancel,
  initialData = {},
  showDwdPrefix = true,
  showDescription = true,
  submitButtonText = '保存',
  cancelButtonText = '取消',
  disabled = false
}) => {
  const queryClient = useQueryClient();

  // 使用专用的游戏表单Toast通知
  const { onValidation, onCreating, onSuccess: showSuccessToast, onError: showErrorToast } = useGameFormToast();

  // Form state
  const [formData, setFormData] = useState({
    name: initialData.name || '',
    gid: initialData.gid || '',
    ods_db: initialData.ods_db || 'ieu_ods'
  });

  // Custom validation hook
  const {
    errors,
    touched,
    validateField,
    validateForm,
    markTouched,
    clearErrors
  } = useGameFormValidation();

  // Create game mutation
  const createMutation = useMutation({
    mutationFn: async (data) => {
      // 显示"创建中"通知
      onCreating();

      // 确保gid转换为整数
      const gidInt = parseInt(data.gid, 10);
      if (isNaN(gidInt) || gidInt <= 0) {
        throw new Error('游戏GID必须是有效的正整数');
      }

      const payload = {
        name: data.name.trim(),
        gid: gidInt,
        ods_db: data.ods_db
      };

      const response = await fetch('/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const result = await response.json();

        // 构造标准化错误对象，传递给onError
        const error = new Error(result.message || '创建失败');
        error.status = response.status;

        throw error;
      }

      return response.json();
    },
    onSuccess: (response) => {
      queryClient.invalidateQueries(['games']);

      // 使用专用的成功通知
      showSuccessToast(response.data);

      // 调用父组件的成功回调
      onSuccess?.(response.data);
    },
    onError: (err) => {
      // 使用专用的错误通知
      showErrorToast(err);
    }
  });

  // Handle field change with real-time validation
  const handleFieldChange = useCallback((field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Real-time validation if field has been touched
    if (touched[field]) {
      const error = validateField(field, value);
      // Error is set by validateField in the hook
    }
  }, [touched, validateField]);

  // Handle field blur - mark as touched, no toast on blur
  const handleFieldBlur = useCallback((field) => {
    markTouched(field);
  }, [markTouched]);

  // Handle ODS type change (for card selector)
  const handleODSTypeChange = useCallback((odsType) => {
    const odsDb = odsType === 'domestic' ? 'ieu_ods' : 'hdy_data_sg';
    handleFieldChange('ods_db', odsDb);
  }, [handleFieldChange]);

  // Handle save
  const handleSave = async () => {
    // Mark all fields as touched
    Object.keys(formData).forEach(key => markTouched(key));

    if (!validateForm(formData)) {
      return;
    }

    createMutation.mutate(formData);
  };

  // Handle cancel
  const handleCancel = () => {
    onCancel?.();
  };

  const isDomestic = formData.ods_db === 'ieu_ods';
  const isLoading = createMutation.isLoading;

  return (
    <div className={mode === 'page' ? styles.gameFormPage : styles.gameFormModal}>
      {/* Game Name */}
      <div className={styles.formGroup}>
        <label htmlFor="game-name" className={styles.formLabel}>
          <i className="bi bi-type"></i>
          游戏名称
          <span className={styles.required}>*</span>
        </label>
        <Input
          id="game-name"
          type="text"
          value={formData.name}
          onChange={(e) => handleFieldChange('name', e.target.value)}
          onBlur={() => handleFieldBlur('name')}
          placeholder="例如: 我的游戏"
          error={touched.name && errors.name}
          disabled={disabled || isLoading}
        />
      </div>

      {/* GID */}
      <div className={styles.formGroup}>
        <label htmlFor="game-gid" className={styles.formLabel}>
          <i className="bi bi-tag"></i>
          游戏GID
          <span className={styles.required}>*</span>
        </label>
        <Input
          id="game-gid"
          type="text"
          value={formData.gid}
          onChange={(e) => handleFieldChange('gid', e.target.value)}
          onBlur={() => handleFieldBlur('gid')}
          placeholder="例如: 90000001"
          error={touched.gid && errors.gid}
          disabled={disabled || isLoading}
        />
        <span className={styles.fieldHint}>
          <i className="bi bi-info-circle"></i>
          游戏唯一标识符，用于生成表名和数据关联
        </span>
      </div>

      {/* ODS Database - Card Selector (GameForm的优秀特性) */}
      <div className={styles.formGroup}>
        <label className={styles.formLabel}>
          <i className="bi bi-database"></i>
          ODS数据库类型
          <span className={styles.required}>*</span>
        </label>
        <ODSSelector
          value={isDomestic ? 'domestic' : 'overseas'}
          onChange={handleODSTypeChange}
          disabled={disabled || isLoading}
          error={touched.ods_db && errors.ods_db}
        />
        <span className={styles.fieldHint}>
          <i className="bi bi-info-circle"></i>
          选择ODS数据库类型，用于生成源表路径
        </span>
      </div>

      {/* Actions */}
      <div className={styles.formActions}>
        <Button
          variant="outline-secondary"
          onClick={handleCancel}
          disabled={disabled || isLoading}
        >
          {cancelButtonText}
        </Button>
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={disabled || isLoading}
          loading={isLoading}
        >
          {isLoading ? '保存中...' : submitButtonText}
        </Button>
      </div>
    </div>
  );
};

export default React.memo(GameForm);
