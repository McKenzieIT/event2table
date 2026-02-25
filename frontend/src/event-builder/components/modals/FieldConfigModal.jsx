/**
 * FieldConfigModal Component
 * 字段配置模态框组件
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Input } from '@shared/ui';
import { Button } from '@shared/ui';

export default function FieldConfigModal({ field, onSave, onClose }) {
  const [formData, setFormData] = useState({
    displayName: '',
    alias: '',
  });

  useEffect(() => {
    if (field) {
      setFormData({
        displayName: field.displayName || '',
        alias: field.alias || '',
      });
    }
  }, [field]);

  const handleSubmit = () => {
    if (!formData.displayName.trim()) {
      toast.error('请输入中文名称');
      return;
    }
    onSave({
      displayName: formData.displayName.trim(),
      alias: formData.alias.trim(),
    });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      tabIndex={0}
      role="button"
      aria-label="关闭"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClose();
        }
      }}
    >
      <div
        className="modal-content glass-card field-config-modal"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="modal-header">
          <h3>配置字段</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框">
            ✕
          </button>
        </div>
        <div className="modal-body">
          <Input
            label="字段名"
            type="text"
            value={field?.fieldName || ''}
            readOnly
          />
          <Input
            label="中文名称"
            type="text"
            placeholder="例如: 角色ID"
            value={formData.displayName}
            onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
            autoFocus
          />
          <Input
            label="Alias (别名)"
            type="text"
            placeholder="例如: user_id"
            value={formData.alias}
            onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
          />
          {field?.fieldType === 'param' && (
            <div className="form-info">
              <span>参数字段将自动使用HQL模板</span>
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSubmit}>
            保存
          </button>
        </div>
      </div>
    </div>
  );
}
