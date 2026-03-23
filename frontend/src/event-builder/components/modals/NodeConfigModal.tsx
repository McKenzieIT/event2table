// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * NodeConfigModal Component
 * 节点配置模态框组件
 */
import { useState, useEffect, useRef } from 'react';
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
export const NodeConfigModal: NodeConfigModalComponent = ({ config, onChange, onClose, disabled = false }) => {
  const [localConfig, setLocalConfig] = useState<NodeConfig>({
    nameEn: '',
    nameCn: '',
    description: '',
  });

  // Refs to input elements (for Chrome MCP compatibility)
  const nameEnRef = useRef<HTMLInputElement>(null);
  const nameCnRef = useRef<HTMLInputElement>(null);
  const descRef = useRef<HTMLTextAreaElement>(null);

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
   * Chrome MCP兼容性: 监听DOM值变化并同步到state
   *
   * 问题: Chrome DevTools MCP的fill操作只更新DOM，不触发React onChange事件
   * 解决: 使用useEffect监听DOM值，当DOM与state不同时自动同步
   *
   * 技术细节:
   * - 只在DOM值与state值不同时才更新（避免无限循环）
   * - 批量更新所有变化的字段（减少re-render次数）
   */
  useEffect(() => {
    // Early return if refs not ready
    if (!nameEnRef.current || !nameCnRef.current || !descRef.current) {
      return;
    }

    // Read current DOM values
    const nameEnDomValue = nameEnRef.current.value;
    const nameCnDomValue = nameCnRef.current.value;
    const descDomValue = descRef.current.value;

    // Collect updates (only if DOM differs from state)
    const updates: Partial<NodeConfig> = {};

    if (nameEnDomValue !== localConfig.nameEn) {
      updates.nameEn = nameEnDomValue;
    }
    if (nameCnDomValue !== localConfig.nameCn) {
      updates.nameCn = nameCnDomValue;
    }
    if (descDomValue !== localConfig.description) {
      updates.description = descDomValue;
    }

    // Batch updates to prevent multiple re-renders
    if (Object.keys(updates).length > 0) {
      setLocalConfig(prev => ({ ...prev, ...updates }));
    }
  }, [localConfig.nameEn, localConfig.nameCn, localConfig.description]);

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

  /**
   * Determine if save button should be disabled
   *
   * FIX for P0 #1: Real-time enable strategy
   * - Removed premature validation (!localConfig.nameEn.trim() || !localConfig.nameCn.trim())
   * - Now only checks the `disabled` prop (which indicates if event is selected)
   * - Validation moved to handleSave (submit-time check)
   *
   * Why: Allows users to fill form on first modal open
   * - Before: Button permanently disabled due to empty string validation
   * - After: Button enabled, validation occurs on submit
   */
  const isSaveDisabled = disabled;

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
            ref={nameEnRef}
          />

          <Input
            label="节点中文名称 *"
            type="text"
            placeholder="例如：登录事件节点"
            value={localConfig.nameCn}
            onChange={(e) => handleChange('nameCn', e.target.value)}
            disabled={disabled}
            helperText="节点的中文显示名称"
            ref={nameCnRef}
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
              ref={descRef}
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

