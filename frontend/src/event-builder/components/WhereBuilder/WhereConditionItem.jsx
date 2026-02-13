/**
 * WhereConditionItem Component
 * 单个WHERE条件项
 */
import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import FieldSelector from './FieldSelector';
import OperatorSelector from './OperatorSelector';
import ValueInput from './ValueInput';
import './WhereConditionItem.css';

export default function WhereConditionItem({
  condition,
  onUpdate,
  onDelete,
  index,
  isFirst
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging
  } = useSortable({ id: condition.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition: 'transition 200ms ease',
    opacity: isDragging ? 0.5 : 1
  };

  const handleChange = (field, value) => {
    onUpdate(condition.id, { [field]: value });
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="where-condition-item"
    >
      {/* 拖拽手柄 */}
      <div className="drag-handle" {...attributes} {...listeners}>
        <i className="bi bi-grip-vertical"></i>
      </div>

      {/* 逻辑操作符（非首个条件显示） */}
      {!isFirst && (
        <div className="logical-op-selector">
          <select
            value={condition.logicalOp || 'AND'}
            onChange={(e) => handleChange('logicalOp', e.target.value)}
          >
            <option value="AND">AND</option>
            <option value="OR">OR</option>
          </select>
        </div>
      )}

      {/* 字段选择 */}
      <FieldSelector
        value={condition.field}
        onChange={(value) => handleChange('field', value)}
      />

      {/* 操作符选择 */}
      <OperatorSelector
        value={condition.operator}
        onChange={(value) => handleChange('operator', value)}
        field={condition.field}
      />

      {/* 值输入 */}
      <ValueInput
        value={condition.value}
        onChange={(value) => handleChange('value', value)}
        operator={condition.operator}
        field={condition.field}
      />

      {/* 删除按钮 */}
      <button
        className="btn btn-sm btn-outline-danger"
        onClick={() => onDelete(condition.id)}
        title="删除条件"
      >
        <i className="bi bi-trash"></i>
      </button>
    </div>
  );
}
