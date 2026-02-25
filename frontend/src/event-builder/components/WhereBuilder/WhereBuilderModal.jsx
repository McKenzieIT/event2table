/**
 * WhereBuilderModal Component
 * WHERE条件构建器主模态框
 */
import React, { useState, useEffect, useMemo, useRef } from 'react';
import { generateWhereClause, validateWhereConditions } from '@shared/utils/whereGenerator';
import WhereBuilderCanvas from './WhereBuilderCanvas';
import './WhereBuilderModal.css';
import { BaseModal } from '@shared/ui/BaseModal';
import toast from 'react-hot-toast';

export default function WhereBuilderModal({
  isOpen,
  onClose,
  conditions,
  onApply,
  onConditionsChange, // ✅ 新增prop：实时回调
  canvasFields, // 可用的字段列表
  selectedEvent, // 当前选择的事件
}) {
  const [preview, setPreview] = useState('');
  const [localConditions, setLocalConditions] = useState(conditions);

  // 保存初始条件的引用，用于检测是否有修改
  const initialConditionsRef = useRef(conditions);

  // ✅ 新增：当本地条件变化时，实时通知父组件
  useEffect(() => {
    onConditionsChange?.(localConditions);
  }, [localConditions, onConditionsChange]);

  // 当外部conditions变化时，同步到本地状态
  useEffect(() => {
    setLocalConditions(conditions);
    initialConditionsRef.current = conditions;
  }, [conditions]);

  // 检测是否有未保存的修改
  const hasUnsavedChanges = useMemo(() => {
    const initial = initialConditionsRef.current;
    // 简单比较：数量不同或内容不同
    if (initial.length !== localConditions.length) {
      return true;
    }
    // 深度比较（简化版）
    return JSON.stringify(initial) !== JSON.stringify(localConditions);
  }, [localConditions]);

  // 生成预览（带防抖优化 - 500ms）
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      const clause = generateWhereClause(localConditions);
      setPreview(clause || '(暂无WHERE条件)');
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [localConditions]);

  // 应用WHERE条件
  const handleApply = () => {
    const validation = validateWhereConditions(localConditions);
    if (!validation.valid) {
      toast.error(`配置错误:\n${validation.errors.join('\n')}`);
      return;
    }
    onApply(localConditions);
    onClose();
  };

  // 关闭前确认逻辑
  const handleBeforeClose = () => {
    // 如果有未保存的修改，返回false显示确认对话框
    if (hasUnsavedChanges) {
      return false;
    }
    // 没有修改，直接关闭
    return true;
  };

  if (!isOpen) return null;

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      size="xl"
      showHeader={false}
      enableEscClose={true}
      onBeforeClose={handleBeforeClose}
      confirmConfig={{
        title: '确认关闭',
        message: '有未保存的WHERE条件修改，确定要关闭吗？',
        confirmText: '放弃修改',
        cancelText: '继续编辑',
      }}
      overlayClassName="where-builder-modal-overlay"
      contentClassName="glass-card where-builder-modal"
    >
      <div className="modal-content glass-card where-builder-modal" style={{ backgroundColor: 'transparent' }}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="header-left">
            <h3>
              <i className="bi bi-funnel"></i>
              WHERE条件构建器
            </h3>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框">
            <i className="bi bi-x"></i>
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* WHERE预览 */}
          <div className="where-preview-section">
            <div className="section-header">
              <h4>WHERE预览</h4>
              <button className="btn btn-sm btn-outline-secondary" onClick={() => {
                navigator.clipboard.writeText(preview);
                toast.success('已复制到剪贴板');
              }}>
                <i className="bi bi-clipboard"></i> 复制
              </button>
            </div>
            <pre className="where-preview-code"><code>{preview}</code></pre>
          </div>

          {/* WHERE构建器画布 */}
          <WhereBuilderCanvas
            conditions={localConditions}
            canvasFields={canvasFields}
            selectedEvent={selectedEvent}
            onUpdate={setLocalConditions}
          />
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <div className="footer-left">
            <span className="text-muted">
              {localConditions.length} 个条件
            </span>
          </div>
          <div className="footer-right">
            <button className="btn btn-secondary" onClick={onClose}>
              取消
            </button>
            <button className="btn btn-primary" onClick={handleApply}>
              <i className="bi bi-check"></i> 应用
            </button>
          </div>
        </div>
      </div>
    </BaseModal>
  );
}
