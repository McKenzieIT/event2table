/**
 * FieldCard Component
 * 字段卡片组件
 */
import React from 'react';
import { FieldType } from '@shared/types/fieldBuilder';

/**
 * 字段数据接口
 */
export interface FieldCardData {
  id: string;
  fieldType: FieldType;
  fieldName?: string;
  name: string;
  displayName?: string;
  alias?: string;
  dataType: string;
  order: number;
}

/**
 * 组件Props接口
 */
export interface FieldCardProps {
  field: FieldCardData;
  onEdit: (field: FieldCardData) => void;
  onDelete: (fieldId: string) => void;
  dragHandleProps?: React.HTMLAttributes<HTMLDivElement>;
  isDragging?: boolean;
}

/**
 * FieldCard Component
 */
export default function FieldCard({
  field,
  onEdit,
  onDelete,
  dragHandleProps,
  isDragging = false
}: FieldCardProps) {
  const getFieldIcon = () => {
    if (field.fieldType === 'base') {
      return <i className="bi bi-list-task"></i>;
    } else if (field.fieldType === 'param') {
      return <i className="bi bi-gear"></i>;
    }
    return <i className="bi bi-dash"></i>;
  };

  return (
    <div className={`field-card ${isDragging ? 'dragging' : ''}`}>
      {dragHandleProps && (
        <div className="field-drag-handle" {...dragHandleProps}>
          <i className="bi bi-grip-vertical"></i>
        </div>
      )}
      <div className="field-icon">{getFieldIcon()}</div>
      <div className="field-order">{field.order}</div>
      <div className="field-info">
        <div className="field-name" title={field.fieldName || field.name}>
          {field.fieldName || field.name}
        </div>
        <div className="field-display" title={field.displayName}>
          {field.displayName}
        </div>
        {field.alias && (
          <div className="field-alias" title={`AS ${field.alias}`}>
            AS {field.alias}
          </div>
        )}
      </div>
      <div className="field-actions">
        <button
          className="btn btn-sm btn-outline-primary"
          onClick={() => onEdit(field)}
          title="编辑字段"
          type="button"
        >
          <i className="bi bi-pencil"></i>
        </button>
        <button
          className="btn btn-sm btn-outline-danger"
          onClick={() => onDelete(field.id)}
          title="删除字段"
          type="button"
        >
          <i className="bi bi-trash"></i>
        </button>
      </div>
    </div>
  );
}
