/**
 * FieldSelectionModal Component
 *
 * Modal for quick field selection with 6 predefined options:
 * - All fields: base + common + params
 * - Params only: only parameter fields
 * - Non-common: base + params (excluding common)
 * - Common: only common fields
 * - Base only: only base fields
 * - Skip: close modal without adding fields
 */
import React, { useCallback } from 'react';
import { useMutation } from '@apollo/client/react';
import { BATCH_ADD_FIELDS_TO_CANVAS } from '@/graphql/mutations';
import { Button } from '@shared/ui/Button';
import { useToast } from '@shared/ui/Toast/Toast';
import './FieldSelectionModal.css';

/**
 * Field selection options
 */
const FIELD_OPTIONS = [
  {
    key: 'all',
    label: '所有字段',
    description: '基础字段 + 公共字段 + 参数字段',
    icon: '📋',
    color: 'primary',
    fieldType: 'all'
  },
  {
    key: 'params',
    label: '仅参数字段',
    description: '只添加事件参数字段',
    icon: '⚙️',
    color: 'info',
    fieldType: 'param'
  },
  {
    key: 'non_common',
    label: '非公共字段',
    description: '基础字段 + 参数字段（不含公共字段）',
    icon: '🔧',
    color: 'warning',
    fieldType: 'non_common'
  },
  {
    key: 'common',
    label: '仅公共字段',
    description: '只添加公共参数字段',
    icon: '🔗',
    color: 'success',
    fieldType: 'common'
  },
  {
    key: 'base',
    label: '仅基础字段',
    description: '只添加基础字段（ds, role_id等）',
    icon: '🏗️',
    color: 'secondary',
    fieldType: 'base'
  },
  {
    key: 'skip',
    label: '跳过',
    description: '手动选择字段',
    icon: '⏭️',
    color: 'ghost',
    fieldType: null
  }
];

/**
 * FieldSelectionModal Component
 */
export default function FieldSelectionModal({
  isOpen,
  onClose,
  eventId,
  onFieldsAdded
}) {
  const { success, error } = useToast();

  // GraphQL mutation for batch adding fields
  const [batchAddFields, { loading }] = useMutation(BATCH_ADD_FIELDS_TO_CANVAS, {
    onCompleted: (data) => {
      if (data?.batchAddFieldsToCanvas?.ok) {
        const { fields, count } = data.batchAddFieldsToCanvas;
        success(`成功添加 ${count} 个字段到画布`);
        onFieldsAdded?.(fields);
        onClose();
      } else if (data?.batchAddFieldsToCanvas?.errors) {
        const errorMsg = data.batchAddFieldsToCanvas.errors.join(', ');
        error(`添加字段失败: ${errorMsg}`);
      }
    },
    onError: (err) => {
      console.error('[FieldSelectionModal] Mutation error:', err);
      error(`添加字段失败: ${err.message}`);
    }
  });

  /**
   * Handle field selection option
   */
  const handleSelectOption = useCallback((option) => {
    if (option.key === 'skip') {
      onClose();
      return;
    }

    batchAddFields({
      variables: {
        eventId,
        fieldType: option.fieldType
      }
    });
  }, [batchAddFields, eventId, onClose]);

  /**
   * Handle backdrop click
   */
  const handleBackdropClick = useCallback((e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="field-selection-modal-overlay"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="field-selection-title"
    >
      <div className="field-selection-modal">
        {/* Header */}
        <div className="field-selection-modal__header">
          <h2 id="field-selection-title" className="field-selection-modal__title">
            <span className="field-selection-modal__title-icon">✨</span>
            选择字段类型
          </h2>
          <p className="field-selection-modal__subtitle">
            快速添加字段到画布，或选择"跳过"手动添加
          </p>
        </div>

        {/* Options Grid */}
        <div className="field-selection-modal__options">
          {FIELD_OPTIONS.map((option) => (
            <button
              key={option.key}
              className={[
                'field-selection-modal__option',
                `field-selection-modal__option--${option.color}`,
                loading && 'field-selection-modal__option--disabled'
              ].filter(Boolean).join(' ')}
              onClick={() => handleSelectOption(option)}
              disabled={loading}
              type="button"
            >
              <div className="field-selection-modal__option-icon">
                {option.icon}
              </div>
              <div className="field-selection-modal__option-content">
                <div className="field-selection-modal__option-label">
                  {option.label}
                </div>
                <div className="field-selection-modal__option-description">
                  {option.description}
                </div>
              </div>
              <div className="field-selection-modal__option-arrow">
                →
              </div>
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="field-selection-modal__footer">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            disabled={loading}
          >
            取消
          </Button>
          <div className="field-selection-modal__footer-info">
            <small className="text-muted">
              提示：选择后将一次性添加所有字段，可在画布中继续调整
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}
