// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * NodeConfigModal Component (Refactored with useChromeMCPCompatibleInput)
 * 节点配置模态框组件
 *
 * This version demonstrates the use of the useChromeMCPCompatibleInput hook
 * to simplify Chrome MCP compatibility handling.
 */
import { useChromeMCPCompatibleInput } from '@shared/hooks';
import { Input } from '@shared/ui';
import { useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

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
 * NodeConfigModal: 节点配置模态框组件 (Refactored)
 *
 * 功能：
 * - 配置节点的英文名称、中文名称和描述
 * - 保存时验证必填字段
 * - 支持禁用状态
 * - Chrome MCP兼容性（使用useChromeMCPCompatibleInput hook）
 *
 * @example
 * ```tsx
 * <NodeConfigModal
 *   config={{ nameEn: 'login', nameCn: '登录', description: 'Login event' }}
 *   onChange={(config) => console.log('Config changed:', config)}
 *   onClose={() => console.log('Modal closed')}
 *   disabled={false}
 * />
 * ```
 */
const NodeConfigModalRefactored: NodeConfigModalComponent = ({
  config,
  onChange,
  onClose,
  disabled = false,
}) => {
  /**
   * 使用Chrome MCP兼容性hook管理表单状态
   *
   * 优势：
   * - 自动处理DOM到state的同步（Chrome MCP兼容性）
   * - 自动创建refs
   * - 提供register函数简化ref注册
   * - 提供handleChange统一处理字段变更
   */
  const { values, handleChange, register, resetValues } =
    useChromeMCPCompatibleInput({
      initialValues: {
        nameEn: '',
        nameCn: '',
        description: '',
      },
      onValuesChange: (currentValues) => {
        // 可选：在这里处理值变化（例如实时验证）
        // console.log('Values changed:', currentValues);
      },
    });

  /**
   * 初始化本地状态
   * 当config prop变化时，重置表单值
   */
  useEffect(() => {
    if (config) {
      resetValues({
        nameEn: config.nameEn || '',
        nameCn: config.nameCn || '',
        description: config.description || '',
      });
    }
  }, [config, resetValues]);

  /**
   * 处理保存
   */
  const handleSave = useCallback((): void => {
    // 验证必填字段
    if (!values.nameEn.trim()) {
      toast.error('请输入节点英文名称');
      return;
    }
    if (!values.nameCn.trim()) {
      toast.error('请输入节点中文名称');
      return;
    }

    onChange({
      nameEn: values.nameEn.trim(),
      nameCn: values.nameCn.trim(),
      description: values.description.trim(),
    });
    onClose();
  }, [values, onChange, onClose]);

  /**
   * 处理键盘事件
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent): void => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClose();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    },
    [onClose]
  );

  /**
   * Determine if save button should be disabled
   *
   * FIX for P0 #1: Real-time enable strategy
   * - Removed premature validation (!values.nameEn.trim() || !values.nameCn.trim())
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
          <button
            className="modal-close"
            onClick={onClose}
            aria-label="关闭对话框"
            type="button"
          >
            ✕
          </button>
        </div>

        <div className="modal-body">
          <Input
            label="节点英文名称 *"
            type="text"
            placeholder="例如: login_event_node"
            value={values.nameEn}
            onChange={(e) => handleChange('nameEn', e.target.value)}
            disabled={disabled}
            helperText="用于标识节点的唯一英文名称"
            ref={register('nameEn') as React.RefObject<HTMLInputElement>}
          />

          <Input
            label="节点中文名称 *"
            type="text"
            placeholder="例如：登录事件节点"
            value={values.nameCn}
            onChange={(e) => handleChange('nameCn', e.target.value)}
            disabled={disabled}
            helperText="节点的中文显示名称"
            ref={register('nameCn') as React.RefObject<HTMLInputElement>}
          />

          <div className="form-group">
            <label>节点描述</label>
            <textarea
              className="glass-input"
              rows={4}
              placeholder="简要描述此节点的用途和功能..."
              value={values.description}
              onChange={(e) => handleChange('description', e.target.value)}
              disabled={disabled}
              ref={register('description') as React.RefObject<HTMLTextAreaElement>}
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

export default NodeConfigModalRefactored;

/**
 * MIGRATION GUIDE: From Original to Refactored Version
 *
 * Before (Original):
 * ```tsx
 * const [localConfig, setLocalConfig] = useState<NodeConfig>({...});
 * const nameEnRef = useRef<HTMLInputElement>(null);
 * const nameCnRef = useRef<HTMLInputElement>(null);
 * const descRef = useRef<HTMLTextAreaElement>(null);
 *
 * // Manual DOM sync useEffect (15+ lines of code)
 * useEffect(() => {
 *   if (!nameEnRef.current || !nameCnRef.current || !descRef.current) return;
 *   const nameEnDomValue = nameEnRef.current.value;
 *   const nameCnDomValue = nameCnRef.current.value;
 *   const descDomValue = descRef.current.value;
 *   const updates: Partial<NodeConfig> = {};
 *   if (nameEnDomValue !== localConfig.nameEn) updates.nameEn = nameEnDomValue;
 *   if (nameCnDomValue !== localConfig.nameCn) updates.nameCn = nameCnDomValue;
 *   if (descDomValue !== localConfig.description) updates.description = descDomValue;
 *   if (Object.keys(updates).length > 0) {
 *     setLocalConfig(prev => ({ ...prev, ...updates }));
 *   }
 * }, [localConfig.nameEn, localConfig.nameCn, localConfig.description]);
 *
 * const handleChange = (field: keyof NodeConfig, value: string): void => {
 *   setLocalConfig((prev) => ({ ...prev, [field]: value }));
 * };
 *
 * <Input ref={nameEnRef} ... />
 * <Input ref={nameCnRef} ... />
 * <textarea ref={descRef} ... />
 * ```
 *
 * After (Refactored with hook):
 * ```tsx
 * const { values, handleChange, register, resetValues } = useChromeMCPCompatibleInput<NodeConfig>({
 *   initialValues: { nameEn: '', nameCn: '', description: '' },
 * });
 *
 * // No manual DOM sync needed - hook handles it automatically!
 * // No manual ref creation needed - hook provides register function!
 * // No manual handleChange needed - hook provides it!
 *
 * <Input ref={register('nameEn')} ... />
 * <Input ref={register('nameCn')} ... />
 * <textarea ref={register('description')} ... />
 * ```
 *
 * Benefits:
 * ✅ Reduced code from ~60 lines to ~10 lines
 * ✅ No manual DOM synchronization logic
 * ✅ Automatic ref management
 * ✅ Type-safe field access
 * ✅ Consistent behavior across all forms
 * ✅ Easy to test and maintain
 */
