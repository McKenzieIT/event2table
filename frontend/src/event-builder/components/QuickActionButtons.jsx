/**
 * QuickActionButtons Component
 *
 * Dropdown toolbar for quick field addition with 6 options:
 * - All fields, Params only, Non-common, Common, Base only, Manual
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useMutation } from '@apollo/client/react';
import { BATCH_ADD_FIELDS_TO_CANVAS } from '@/graphql/mutations';
import { Button } from '@shared/ui/Button';
import { useToast } from '@shared/ui/Toast/Toast';
import './QuickActionButtons.css';

/**
 * Quick action options (same as FieldSelectionModal)
 */
const QUICK_ACTIONS = [
  {
    key: 'all',
    label: '所有字段',
    description: '基础 + 公共 + 参数',
    icon: '📋',
    color: 'primary',
    fieldType: 'all'
  },
  {
    key: 'params',
    label: '仅参数',
    description: '只添加参数字段',
    icon: '⚙️',
    color: 'info',
    fieldType: 'param'
  },
  {
    key: 'non_common',
    label: '非公共',
    description: '基础 + 参数',
    icon: '🔧',
    color: 'warning',
    fieldType: 'non_common'
  },
  {
    key: 'common',
    label: '公共字段',
    description: '只添加公共字段',
    icon: '🔗',
    color: 'success',
    fieldType: 'common'
  },
  {
    key: 'base',
    label: '基础字段',
    description: '只添加基础字段',
    icon: '🏗️',
    color: 'secondary',
    fieldType: 'base'
  }
];

/**
 * QuickActionButtons Component
 */
export default function QuickActionButtons({
  eventId,
  onFieldsAdded,
  disabled = false
}) {
  const { success, error } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // GraphQL mutation for batch adding fields
  const [batchAddFields, { loading }] = useMutation(BATCH_ADD_FIELDS_TO_CANVAS, {
    onCompleted: (data) => {
      if (data?.batchAddFieldsToCanvas?.ok) {
        const { fields, count } = data.batchAddFieldsToCanvas;
        success(`成功添加 ${count} 个字段到画布`);
        onFieldsAdded?.(fields);
        setIsOpen(false);
      } else if (data?.batchAddFieldsToCanvas?.errors) {
        const errorMsg = data.batchAddFieldsToCanvas.errors.join(', ');
        error(`添加字段失败: ${errorMsg}`);
      }
    },
    onError: (err) => {
      console.error('[QuickActionButtons] Mutation error:', err);
      error(`添加字段失败: ${err.message}`);
    }
  });

  /**
   * Handle dropdown toggle
   */
  const toggleDropdown = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  /**
   * Handle action selection
   */
  const handleSelectAction = useCallback((action) => {
    batchAddFields({
      variables: {
        eventId,
        fieldType: action.fieldType
      }
    });
  }, [batchAddFields, eventId]);

  /**
   * Close dropdown when clicking outside
   */
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  /**
   * Handle keyboard escape
   */
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  return (
    <div className="quick-action-buttons" ref={dropdownRef}>
      {/* Main Button */}
      <Button
        variant="primary"
        size="sm"
        onClick={toggleDropdown}
        disabled={disabled || !eventId || loading}
        className="quick-action-buttons__trigger"
      >
        <span className="quick-action-buttons__trigger-icon">⚡</span>
        <span>快速添加</span>
        <span className={[
          'quick-action-buttons__trigger-arrow',
          isOpen && 'quick-action-buttons__trigger-arrow--open'
        ].filter(Boolean).join(' ')}>
          ▼
        </span>
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="quick-action-buttons__dropdown">
          <div className="quick-action-buttons__dropdown-header">
            <span className="quick-action-buttons__dropdown-title">快速添加字段</span>
          </div>

          <div className="quick-action-buttons__dropdown-actions">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.key}
                className={[
                  'quick-action-buttons__action',
                  `quick-action-buttons__action--${action.color}`,
                  loading && 'quick-action-buttons__action--disabled'
                ].filter(Boolean).join(' ')}
                onClick={() => handleSelectAction(action)}
                disabled={loading}
                type="button"
                title={action.description}
              >
                <span className="quick-action-buttons__action-icon">
                  {action.icon}
                </span>
                <span className="quick-action-buttons__action-label">
                  {action.label}
                </span>
                <span className="quick-action-buttons__action-description">
                  {action.description}
                </span>
                {loading && (
                  <span className="quick-action-buttons__action-spinner">
                    ⏳
                  </span>
                )}
              </button>
            ))}
          </div>

          <div className="quick-action-buttons__dropdown-footer">
            <small className="text-muted">
              💡 提示：选择后将批量添加字段
            </small>
          </div>
        </div>
      )}
    </div>
  );
}
