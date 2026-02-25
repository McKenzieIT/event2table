/**
 * NodeConfigModal Component
 * 节点配置模态框组件
 */
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Input } from '@shared/ui';

export default function NodeConfigModal({ config, onChange, onClose, disabled }) {
  const [localConfig, setLocalConfig] = useState({
    nameEn: '',
    nameCn: '',
    description: '',
  });

  // 初始化本地状态
  useEffect(() => {
    if (config) {
      setLocalConfig({
        nameEn: config.nameEn || '',
        nameCn: config.nameCn || '',
        description: config.description || '',
      });
    }
  }, [config]);

  const handleChange = (field, value) => {
    setLocalConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = () => {
    // 验证
    if (!localConfig.nameEn.trim()) {
      toast.error('请输入节点英文名称');
      return;
    }
    if (!localConfig.nameCn.trim()) {
      toast.error('请输入节点中文名称');
      return;
    }

    onChange({
      nameEn: localConfig.nameEn.trim(),
      nameCn: localConfig.nameCn.trim(),
      description: localConfig.description.trim(),
    });
    onClose();
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
        } else if (e.key === 'Escape') {
          e.preventDefault();
          onClose();
        }
      }}
    >
      <div
        className="modal-content glass-card node-config-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>节点配置</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <Input
            label="节点英文名称 *"
            type="text"
            placeholder="例如: login_event_node"
            value={localConfig.nameEn}
            onChange={(e) => handleChange('nameEn', e.target.value)}
            disabled={disabled}
            helperText="用于标识节点的唯一英文名称"
          />

          <Input
            label="节点中文名称 *"
            type="text"
            placeholder="例如：登录事件节点"
            value={localConfig.nameCn}
            onChange={(e) => handleChange('nameCn', e.target.value)}
            disabled={disabled}
            helperText="节点的中文显示名称"
          />

          <div className="form-group">
            <label>节点描述</label>
            <textarea
              className="glass-input"
              rows="4"
              placeholder="简要描述此节点的用途和功能..."
              value={localConfig.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={disabled}
            />
            <small className="help-text">可选，用于说明节点的用途</small>
          </div>

          {disabled && (
            <div className="alert alert-warning">
              <span>请先选择事件并添加字段后再配置节点</span>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={disabled || !localConfig.nameEn.trim() || !localConfig.nameCn.trim()}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}
