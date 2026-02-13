/**
 * Add Game Modal - 添加游戏模态框组件
 *
 * 功能：两层模态框，在游戏管理模态框之上滑出
 * 保存后返回游戏管理列表
 *
 */

import React, { useState } from 'react';
import { useGameStore } from '@/stores/gameStore';
import { Button, Input } from '@shared/ui';
import './AddGameModal.css';

/**
 * Add Game Modal Component
 */
function AddGameModal({ isOpen, onClose }) {
  const { setCurrentGame } = useGameStore();
  const [formData, setFormData] = useState({
    name: '',
    gid: '',
    ods_db: 'ieu_ods',
    dwd_prefix: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const [isSubmitting, setIsSubmitting] = useState(false);

  // 重置表单
  const resetForm = () => {
    setFormData({
      name: '',
      gid: '',
      ods_db: 'ieu_ods',
      dwd_prefix: ''
    });
    setErrors({});
  };

  // 关闭模态框
  const handleClose = () => {
    resetForm();
    onClose();
  };

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = '游戏名称不能为空';
    }

    if (!formData.gid.toString().trim()) {
      newErrors.gid = 'GID不能为空';
    }

    if (!formData.ods_db) {
      newErrors.ods_db = '请选择ODS数据库';
    }

    // GID必须是数字
    if (formData.gid && isNaN(Number(formData.gid))) {
      newErrors.gid = 'GID必须是数字';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 提交游戏创建
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name.trim(),
          gid: Number(formData.gid),
          ods_db: formData.ods_db,
          dwd_prefix: formData.dwd_prefix || null
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || '创建游戏失败');
      }

      const result = await response.json();

      // 更新gameStore
      setCurrentGame(result.data);

      // 关闭模态框并重置表单
      handleClose();

      // 显示成功提示（需要使用toast）
      alert(`游戏"${formData.name}"创建成功！`);

    } catch (error) {
      console.error('Error creating game:', error);
      alert(`创建失败: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`add-game-modal-overlay ${isOpen ? 'open' : ''}`}>
      <div className="add-game-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-container">
          {/* 头部 */}
          <div className="modal-header">
            <h2>添加游戏</h2>
            <button className="close-btn" onClick={handleClose} aria-label="关闭">
              ×
            </button>
          </div>

          {/* 表单 */}
          <form className="add-game-form" onSubmit={handleSubmit}>
            {/* 游戏名称 */}
            <div className="form-field">
              <label htmlFor="gameName">游戏名称 *</label>
              <Input
                type="text"
                id="gameName"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="例如：测试游戏"
                required
              />
              {errors.name && (
                <span className="error-message">{errors.name}</span>
              )}
            </div>

            {/* GID */}
            <div className="form-field">
              <label htmlFor="gameGid">GID *</label>
              <Input
                type="text"
                id="gameGid"
                value={formData.gid}
                onChange={(e) => setFormData(prev => ({ ...prev, gid: e.target.value }))}
                placeholder="例如：10000147"
                required
              />
              {errors.gid && (
                <span className="error-message">{errors.gid}</span>
              )}
            </div>

            {/* ODS数据库 */}
            <div className="form-field">
              <label htmlFor="odsDb">ODS数据库 *</label>
              <select
                id="odsDb"
                value={formData.ods_db}
                onChange={(e) => setFormData(prev => ({ ...prev, ods_db: e.target.value }))}
                disabled={isSubmitting}
                >
                <option value="">请选择</option>
                <option value="ieu_ods">ieu_ods</option>
                <option value="overseas_ods">overseas_ods</option>
              </select>
              {errors.ods_db && (
                <span className="error-message">{errors.ods_db}</span>
              )}
            </div>

            {/* DWD前缀（可选） */}
            <div className="form-field">
              <label htmlFor="dwdPrefix">DWD前缀</label>
              <Input
                type="text"
                id="dwdPrefix"
                value={formData.dwd_prefix}
                onChange={(e) => setFormData(prev => ({ ...prev, dwd_prefix: e.target.value }))}
                placeholder="例如：dwd_"
                disabled={isSubmitting}
              />
              {errors.dwd_prefix && (
                <span className="error-message">{errors.dwd_prefix}</span>
              )}
            </div>

            {/* 提交按钮 */}
            <div className="form-actions">
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting || Object.keys(errors).length > 0}
              >
                {isSubmitting ? '创建中...' : '➕ 添加游戏'}
              </Button>
            </div>
          </form>

          {/* 取消按钮 */}
          <div className="form-actions">
            <Button
              type="button"
              variant="text"
              onClick={handleClose}
              disabled={isSubmitting}
              >
                取消
              </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddGameModal;
