/**
 * AddGameModal - Add Game Modal Component
 *
 * Two-layer slide-out animation (on top of game management modal)
 * Form fields: name, GID, ODS database, DWD prefix (optional), description (optional)
 */

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';
import { Button, Input, useToast } from '@shared/ui';
import { useGameStore } from '../../stores/gameStore';
import './AddGameModal.css';

const AddGameModal = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();
  const { openGameManagementModal } = useGameStore();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    gid: '',
    ods_db: 'ieu_ods',
    dwd_prefix: '',
    description: ''
  });

  // Validation errors
  const [errors, setErrors] = useState({});

  // Create game mutation
  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await fetch('/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || 'Failed to create game');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['games']);
      success('游戏创建成功');
      handleClose();
    },
    onError: (err) => {
      showError(`创建失败: ${err.message}`);
    }
  });

  // Handle field change
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = '游戏名称不能为空';
    }

    if (!formData.gid.trim()) {
      newErrors.gid = 'GID不能为空';
    } else if (!/^\d+$/.test(formData.gid.trim())) {
      newErrors.gid = 'GID必须是数字';
    }

    if (!formData.ods_db) {
      newErrors.ods_db = '请选择ODS数据库';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle save
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    createMutation.mutate({
      name: formData.name.trim(),
      gid: formData.gid.trim(),
      ods_db: formData.ods_db,
      dwd_prefix: formData.dwd_prefix.trim() || null,
      description: formData.description.trim() || null
    });
  };

  // Handle close - return to game management modal
  const handleClose = () => {
    // Reset form
    setFormData({
      name: '',
      gid: '',
      ods_db: 'ieu_ods',
      dwd_prefix: '',
      description: ''
    });
    setErrors({});
    onClose();
    // Open game management modal to show the updated list
    openGameManagementModal();
  };

  // Handle cancel
  const handleCancel = () => {
    handleClose();
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleClose}
      title="添加游戏"
      animation="slideUp"
      glassmorphism
      size="lg"
      variant="default"
      className="add-game-modal"
    >
      <div className="add-game-modal__content">
        {/* Game Name */}
        <div className="form-group">
          <label htmlFor="game-name">
            游戏名称 <span className="required">*</span>
          </label>
          <Input
            id="game-name"
            type="text"
            value={formData.name}
            onChange={(e) => handleFieldChange('name', e.target.value)}
            placeholder="输入游戏名称"
            error={errors.name}
            className="cyber-input"
          />
          {errors.name && <span className="error-message">{errors.name}</span>}
        </div>

        {/* GID */}
        <div className="form-group">
          <label htmlFor="game-gid">
            GID <span className="required">*</span>
          </label>
          <Input
            id="game-gid"
            type="text"
            value={formData.gid}
            onChange={(e) => handleFieldChange('gid', e.target.value)}
            placeholder="输入游戏GID（数字）"
            error={errors.gid}
            className="cyber-input"
          />
          {errors.gid && <span className="error-message">{errors.gid}</span>}
          <small className="field-hint">游戏GID，用于生成表名和数据关联</small>
        </div>

        {/* ODS Database */}
        <div className="form-group">
          <label htmlFor="ods-db">
            ODS数据库 <span className="required">*</span>
          </label>
          <select
            id="ods-db"
            value={formData.ods_db}
            onChange={(e) => handleFieldChange('ods_db', e.target.value)}
            className="cyber-select"
          >
            <option value="ieu_ods">ieu_ods</option>
            <option value="overseas_ods">overseas_ods</option>
          </select>
          {errors.ods_db && <span className="error-message">{errors.ods_db}</span>}
          <small className="field-hint">选择ODS数据源</small>
        </div>

        {/* DWD Prefix */}
        <div className="form-group">
          <label htmlFor="dwd-prefix">DWD前缀</label>
          <Input
            id="dwd-prefix"
            type="text"
            value={formData.dwd_prefix}
            onChange={(e) => handleFieldChange('dwd_prefix', e.target.value)}
            placeholder="输入DWD前缀（可选）"
            className="cyber-input"
          />
          <small className="field-hint">DWD层表名前缀，留空使用默认值</small>
        </div>

        {/* Description */}
        <div className="form-group">
          <label htmlFor="description">描述</label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            placeholder="输入游戏描述（可选）"
            rows="3"
            className="cyber-textarea"
          />
        </div>

        {/* Actions */}
        <div className="form-actions">
          <Button
            variant="outline-secondary"
            onClick={handleCancel}
            disabled={createMutation.isLoading}
          >
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={createMutation.isLoading}
          >
            {createMutation.isLoading ? '保存中...' : '保存'}
          </Button>
        </div>
      </div>
    </BaseModal>
  );
};

export { AddGameModal };
export default React.memo(AddGameModal);
