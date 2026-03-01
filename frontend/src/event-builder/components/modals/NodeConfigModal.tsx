/**
 * NodeConfigModal Component
 * 节点配置模态框组件
 */
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Input } from '@shared/ui';

/**
 * 节点配置接口
 */
interface NodeConfig {
  nameEn: string;
  nameCn: string;
  description: string;
}

/**
 * 组件Props接口
 */
interface NodeConfigModalProps {
  config?: NodeConfig;
  onChange: (config: NodeConfig) => void;
  onClose: () => void;
  disabled?: boolean;
}

/**
 * 组件类型定义
 */
type NodeConfigModalComponent = React.FC<NodeConfigModalProps>;

/**
 * NodeConfigModal: 节点配置模态框组件
 *
 * 功能：
 * - 配置节点的英文名称、中文名称和描述
 * - 保存时验证必填字段
 * - 支持禁用状态
 */
const NodeConfigModal: NodeConfigModalComponent = ({ config, onChange, onClose, disabled = false }) => {
  const [localConfig, setLocalConfig] = useState<NodeConfig>({
    nameEn: '',
    nameCn: '',
    description: '',
  });

  /**
   * 初始化本地状态
   */
  useEffect(() => {
    if (config) {
      setLocalConfig({
        nameEn: config.nameEn || '',
        nameCn: config.nameCn || '',
        description: config.description || '',
      });
    }
  }, [config]);

  /**
   * 处理字段变更
   */
  const handleChange = (field: keyof NodeConfig, value: string): void => {
    setLocalConfig((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  /**
   * 处理保存
   */
  const handleSave = (): void => {
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

  /**
   * 处理键盘事件
   */
  const handleKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClose();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  const isSaveDisabled = disabled || !localConfig.nameEn.trim() || !localConfig.nameCn.trim();

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      tabIndex={0}
      role="button"
      aria-label="关闭"
      onKeyDown={handleKeyDown}
    >
      <div
        className="modal-content glass-card node-config-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>节点配置</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框" type="button">
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
              rows={4}
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
          <button className="btn btn-secondary" onClick={onClose} type="button">
            取消
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={isSaveDisabled}
            type="button"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

export default NodeConfigModal;
