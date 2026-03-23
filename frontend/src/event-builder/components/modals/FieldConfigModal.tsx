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
import React, { useState, useEffect, useRef, useCallback } from 'react';
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
 * ✅ BUGFIX #2-3: 优化交互性
 * - 添加ref管理输入元素
 * - 使用useCallback优化性能
 * - 改进键盘事件处理
 * - 确保表单状态正确更新
 */
export const FieldConfigModal: FieldConfigModalComponent = ({ field, onSave, onClose }) => {
  const [formData, setFormData] = useState<FieldFormData>({
    displayName: '',
    alias: '',
  });

  const aliasInputRef = useRef<HTMLInputElement>(null);

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
   * ✅ BUGFIX #2-3: 处理表单提交（使用useCallback优化）
   */
  const handleSubmit = useCallback((): void => {
    if (!formData.displayName.trim()) {
      toast.error('请输入中文名称');
      return;
    }
    onSave({
      displayName: formData.displayName.trim(),
      alias: formData.alias.trim(),
    });
  }, [formData, onSave]);

  /**
   * ✅ BUGFIX #2-3: 处理键盘事件（改进焦点管理）
   */
  const handleKeyDown = useCallback((e: React.KeyboardEvent): void => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  }, [handleSubmit, onClose]);

  /**
   * ✅ BUGFIX #2-3: 处理中文名称输入
   */
  const handleDisplayNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>): void => {
    setFormData(prev => ({ ...prev, displayName: e.target.value }));
  }, []);

  /**
   * ✅ BUGFIX #2-3: 处理别名输入
   */
  const handleAliasChange = useCallback((e: React.ChangeEvent<HTMLInputElement>): void => {
    setFormData(prev => ({ ...prev, alias: e.target.value }));
  }, []);

  /**
   * 处理键盘事件（overlay）
   */
  const handleOverlayKeyDown = useCallback((e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClose();
    }
  }, [onClose]);

  /**
   * ✅ BUGFIX #2-3: 阻止事件冒泡，防止意外关闭
   */
  const handleModalContentClick = useCallback((e: React.MouseEvent): void => {
    e.stopPropagation();
  }, []);

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
        onClick={handleModalContentClick}
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
            onChange={handleDisplayNameChange}
            onKeyDown={handleKeyDown}
            autoFocus
          />
          <Input
            ref={aliasInputRef}
            label="Alias (别名)"
            type="text"
            placeholder="例如: user_id"
            value={formData.alias}
            onChange={handleAliasChange}
            onKeyDown={handleKeyDown}
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
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            type="button"
            disabled={!formData.displayName.trim()}
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

