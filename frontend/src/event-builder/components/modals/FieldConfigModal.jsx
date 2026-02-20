/**
 * FieldConfigModal Component
 * 字段配置模态框组件
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

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
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content glass-card"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="modal-header">
          <h3>配置字段</h3>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>字段名</label>
            <input
              type="text"
              className="glass-input"
              value={field?.fieldName || ''}
              readOnly
            />
          </div>
          <div className="form-group">
            <label>中文名称</label>
            <input
              type="text"
              className="glass-input"
              placeholder="例如: 角色ID"
              value={formData.displayName}
              onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Alias (别名)</label>
            <input
              type="text"
              className="glass-input"
              placeholder="例如: user_id"
              value={formData.alias}
              onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
            />
          </div>
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
