import React, { memo } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { FieldType } from '../../types/fieldTypes';
import { Button } from '@shared/ui';

/**
 * Props for SortableFieldItem component
 */
export interface SortableFieldItemProps {
  /** Field data */
  field: any;
  /** Edit callback */
  onEdit: (field: any) => void;
  /** Delete callback */
  onDelete: (fieldId: string) => void;
  /** Compact mode */
  compact?: boolean;
}

/**
 * Sortable field item component (memoized for performance)
 */
const SortableFieldItem = memo<SortableFieldItemProps>(({
  field,
  onEdit,
  onDelete,
  compact = false,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: field.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getFieldTypeIcon = (type: string) => {
    const field_type = type || field.fieldType;

    switch (field_type) {
      case 'param':
      case 'PARAM':
      case FieldType.PARAMETER:
        return 'bi-link';
      case 'base':
      case 'BASE':
      case FieldType.BASIC:
        return 'bi-type';
      case 'custom':
      case 'CUSTOM':
      case FieldType.CUSTOM:
        return 'bi-code';
      case 'fixed':
      case 'FIXED':
      case FieldType.FIXED:
        return 'bi-pin';
      default:
        return 'bi-question-circle';
    }
  };

  const getFieldTypeLabel = (type: string) => {
    const field_type = type || field.fieldType;

    switch (field_type) {
      case 'param':
      case 'PARAM':
      case FieldType.PARAMETER:
        return '参数';
      case 'base':
      case 'BASE':
      case FieldType.BASIC:
        return '基础';
      case 'custom':
      case 'CUSTOM':
      case FieldType.CUSTOM:
        return '自定义';
      case 'fixed':
      case 'FIXED':
      case FieldType.FIXED:
        return '固定值';
      default:
        return '未知';
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      data-field-id={field.id}
      className={`field-item ${compact ? 'compact' : ''} ${isDragging ? 'dragging' : ''}`}
    >
      <div {...listeners} className="field-handle">
        <i className="bi bi-grip-vertical" aria-hidden="true"></i>
      </div>

      {/* Type Badge */}
      <span className="field-type-badge">
        <i className={`bi ${getFieldTypeIcon(field.fieldType)}`}></i>
        <span className="field-type-label">{getFieldTypeLabel(field.fieldType)}</span>
      </span>

      {/* Field Alias */}
      <strong
        className="field-alias"
        title={field.fieldName}
      >
        {field.alias || field.fieldName}
      </strong>

      {/* Original Name */}
      <span className="field-original-name">
        {field.fieldName !== field.alias ? `(${field.displayName || field.fieldName})` : ''}
      </span>

      {/* Data Type Badge */}
      {field.dataType && (
        <span className={`badge badge-secondary data-type-badge ${field.dataType}`}>
          {field.dataType}
        </span>
      )}

      {/* Actions */}
      <div className="field-actions">
        <Button
          variant="outline-primary"
          size="sm"
          onClick={() => onEdit(field)}
        >
          编辑
        </Button>
        <Button
          variant="outline-danger"
          size="sm"
          onClick={() => onDelete(field.id)}
        >
          删除
        </Button>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for React.memo
  return prevProps.field.id === nextProps.field.id &&
         prevProps.field.name === nextProps.field.name &&
         prevProps.field.alias === nextProps.field.alias &&
         prevProps.field.fieldType === nextProps.field.fieldType &&
         prevProps.compact === nextProps.compact;
});

SortableFieldItem.displayName = 'SortableFieldItem';

export default SortableFieldItem;
