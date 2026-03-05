// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * FieldConfigModal Component
 * 字段配置模态框组件
 */
import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Input } from '@shared/ui';

/**
 * 字段接口
 */
interface Field {
  fieldName: string;
  fieldType: 'base' | 'param' | 'custom' | 'fixed';
  displayName?: string;
  alias?: string;
  dataType?: string;
}

/**
 * 表单数据接口
 */
interface FieldFormData {
  displayName: string;
  alias: string;
}

/**
 * 组件Props接口
 */
interface FieldConfigModalProps {
  field?: Field;
  onSave: (data: FieldFormData) => void;
  onClose: () => void;
}

/**
 * 组件类型定义
 */
type FieldConfigModalComponent = React.FC<FieldConfigModalProps>;

/**
 * FieldConfigModal: 字段配置模态框组件
 *
 * 功能：
 * - 配置字段的中文名称和别名
 * - 显示字段名和类型（只读）
 * - 保存配置时验证必填字段
 */
const FieldConfigModal: FieldConfigModalComponent = ({ field, onSave, onClose }) => {
  const [formData, setFormData] = useState<FieldFormData>({
    displayName: '',
    alias: '',
  });

  /**
   * 初始化表单数据
   */
  useEffect(() => {
    if (field) {
      setFormData({
        displayName: field.displayName || '',
        alias: field.alias || '',
      });
    }
  }, [field]);

  /**
   * 处理表单提交
   */
  const handleSubmit = (): void => {
    if (!formData.displayName.trim()) {
      toast.error('请输入中文名称');
      return;
    }
    onSave({
      displayName: formData.displayName.trim(),
      alias: formData.alias.trim(),
    });
  };

  /**
   * 处理键盘事件
   */
  const handleKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter') {
      handleSubmit();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  /**
   * 处理键盘事件（overlay）
   */
  const handleOverlayKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
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
      onKeyDown={handleOverlayKeyDown}
    >
      <div
        className="modal-content glass-card field-config-modal"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="modal-header">
          <h3>配置字段</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框" type="button">
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
          <button className="btn btn-secondary" onClick={onClose} type="button">
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSubmit} type="button">
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

export default FieldConfigModal;
