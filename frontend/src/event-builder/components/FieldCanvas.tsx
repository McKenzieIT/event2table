/**
 * FieldCanvas Component
 *
 * Drop zone canvas for field management with drag-and-drop support.
 * Accepts dragged parameters from the event selector and manages field list.
 *
 * Features:
 * - Drop zone for dragging parameters/events
 * - Sortable field list with drag handles
 * - Field operations (add, edit, delete, reorder)
 * - Visual feedback for drag operations
 * - Empty state with call-to-action
 *
 * @component FieldCanvas
 */

import React, { useState, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import {
  DndContext,
  useDroppable,
  DragOverlay,
  closestCenter,
  useSensor,
  useSensors,
  PointerSensor,
  KeyboardSensor
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
  arrayMove,
  sortableKeyboardCoordinates
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Field, FieldType, DataType, Parameter } from '@shared/types/fieldBuilder';
import { generateId } from '@shared/utils/fieldBuilder';
import { Button } from '@shared/ui/Button';
import { DeleteConfirmModal } from '@shared/components/DeleteConfirmModal';
import './FieldCanvas.css';

/**
 * Drop zone component for accepting dragged items
 */
function DropZone({ children, onDrop, onNativeDrop, onNativeDragOver, onNativeDragLeave, isActive }) {
  const { isOver, setNodeRef } = useDroppable({
    id: 'field-canvas-drop-zone',
    onDrop: (event) => {
      const { active } = event;
      const data = active.data.current;
      if (data?.type === 'parameter') {
        onDrop(data.parameter);
      } else if (data?.type === 'event') {
        // Event drops are handled at a higher level
        // This is for future enhancement
      }
    }
  });

  return (
    <div
      ref={setNodeRef}
      data-testid="field-canvas-drop-zone"
      className={`drop-zone canvas-area ${isOver ? 'drag-over' : ''} ${isActive ? 'active' : ''}`}
      onDrop={onNativeDrop}
      onDragOver={onNativeDragOver}
      onDragLeave={onNativeDragLeave}
    >
      {children}
    </div>
  );
}

/**
 * Sortable field item component (memoized for performance)
 */
const SortableFieldItem = React.memo(({ field, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({
    id: field.id
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition
  };

  const getFieldTypeIcon = (type) => {
    // Handle both fieldType and type for compatibility
    const field_type = type || field.fieldType;

    switch (field_type) {
      case 'param':
      case FieldType.PARAMETER:
        return 'bi-link';
      case 'base':
      case FieldType.BASIC:
        return 'bi-type';
      case 'custom':
      case FieldType.CUSTOM:
        return 'bi-code';
      case 'fixed':
      case FieldType.FIXED:
        return 'bi-pin';
      default:
        return 'bi-question-circle';
    }
  };

  const getFieldTypeLabel = (type) => {
    // Handle both fieldType and type for compatibility
    const field_type = type || field.fieldType;

    switch (field_type) {
      case 'param':
      case FieldType.PARAMETER:
        return '参数';
      case 'base':
      case FieldType.BASIC:
        return '基础';
      case 'custom':
      case FieldType.CUSTOM:
        return '自定义';
      case 'fixed':
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
      className={`field-item ${isDragging ? 'dragging' : ''}`}
    >
      <div {...listeners} className="field-handle">
        <i className="bi bi-grip-vertical"></i>
      </div>
      <div className="field-info">
        <span className="field-type-badge">
          <i className={`bi ${getFieldTypeIcon(field.fieldType)}`}></i>
          <span className="field-type-label">{getFieldTypeLabel(field.fieldType)}</span>
        </span>
        <div className="field-names">
          <strong className="field-alias">{field.fieldName}</strong>
          <span className="field-original-name">({field.displayName})</span>
        </div>
        <span className={`badge badge-secondary data-type-badge ${field.dataType || 'string'}`}>
          {field.dataType || 'string'}
        </span>
      </div>
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
  // Only re-render if critical properties change
  return prevProps.field.id === nextProps.field.id &&
         prevProps.field.name === nextProps.field.name &&
         prevProps.field.alias === nextProps.field.alias &&
         prevProps.field.fieldType === nextProps.field.fieldType;
});

/**
 * Main FieldCanvas component
 *
 * @param {Object} props - Component props
 * @param {Field[]} props.fields - Array of fields to display
 * @param {Parameter[]} props.parameters - Array of available parameters
 * @param {Function} props.onFieldsChange - Callback when fields change
 * @param {Function} props.onAddField - Callback to add a new field
 * @param {Function} props.onRemoveField - Callback to remove a field
 * @param {Function} props.onUpdateField - Callback to update a field
 * @param {Function} props.onReorderFields - Callback when fields are reordered
 * @param {boolean} props.isLoading - Loading state
 * @param {boolean} props.hasError - Error state
 */
export default function FieldCanvas({
  fields = [],
  parameters = [],
  onFieldsChange,
  onAddField,
  onRemoveField,
  onUpdateField,
  onReorderFields,
  isLoading = false,
  hasError = false
}) {
  // ✅ 添加额外保护，确保 fields 和 parameters 是数组
  const safeFields = Array.isArray(fields) ? fields : [];
  const safeParameters = Array.isArray(parameters) ? parameters : [];

  const [activeId, setActiveId] = useState(null);
  const [deleteModal, setDeleteModal] = useState({
    show: false,
    field: null
  });

  // Configure dnd-kit sensors for drag and drop
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement before drag starts (prevents accidental drags)
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag end for reordering (optimized with useCallback)
  const handleDragEnd = useCallback((event) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = safeFields.findIndex((f) => f.id === active.id);
      const newIndex = safeFields.findIndex((f) => f.id === over.id);

      const reorderedFields = arrayMove(safeFields, oldIndex, newIndex);
      if (onReorderFields) {
        onReorderFields(reorderedFields);
      }
    }

    setActiveId(null);
  }, [safeFields, onReorderFields]);

  // Handle drag start (optimized with useCallback)
  const handleDragStart = useCallback((event) => {
    setActiveId(event.active.id);
  }, []);

  // Handle drop from event selector
  const handleDrop = (parameter) => {
    const newField = {
      id: generateId(),
      type: FieldType.PARAMETER,
      sourceId: parameter.id,
      name: parameter.name,
      alias: parameter.alias || parameter.name,
      dataType: parameter.dataType,
      isEditable: true
    };
    onAddField(newField);
  };

  // Handle native HTML5 drag and drop (from BaseFieldsList and ParamSelector)
  const handleNativeDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    // Remove drag-over styling
    e.currentTarget.classList.remove('drag-over');

    try {
      // Try to get data in multiple formats
      let dragData;
      const jsonData = e.dataTransfer.getData('application/json');
      const textData = e.dataTransfer.getData('text/plain');

      if (jsonData) {
        dragData = JSON.parse(jsonData);
      } else if (textData) {
        dragData = JSON.parse(textData);
      }

      if (!dragData) {
        return;
      }

      // Call onAddField with the correct format
      if (onAddField && dragData.fieldType && dragData.fieldName) {
        onAddField({
          fieldType: dragData.fieldType,
          fieldName: dragData.fieldName,
          displayName: dragData.displayName,
          paramId: dragData.paramId,
        });
      }
    } catch (error) {
      console.error('[FieldCanvas] Error handling drop:', error);
    }
  };

  const handleNativeDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    e.currentTarget.classList.add('drag-over');
  };

  const handleNativeDragLeave = (e) => {
    e.currentTarget.classList.remove('drag-over');
  };

  // Handle add field button click
  const handleAddFieldClick = (type) => {
    let newField;

    switch (type) {
      case FieldType.BASIC:
        newField = {
          id: generateId(),
          type: FieldType.BASIC,
          name: 'ds',
          displayName: '分区',
          alias: 'ds',
          dataType: DataType.STRING,
          isEditable: true,
          // Additional properties for HQLPreviewContainer
          fieldType: 'base',  // Backend API expects 'base'
          fieldName: 'ds',
          paramId: null,
          jsonPath: null
        };
        break;
      case FieldType.CUSTOM:
        newField = {
          id: generateId(),
          type: FieldType.CUSTOM,
          name: 'custom_field',
          displayName: '自定义字段',
          alias: 'custom_field',
          dataType: DataType.STRING,
          mapping: '',
          isEditable: true,
          // Additional properties for HQLPreviewContainer
          fieldType: 'custom',
          fieldName: 'custom_field',
          paramId: null,
          jsonPath: null
        };
        break;
      case FieldType.FIXED:
        newField = {
          id: generateId(),
          type: FieldType.FIXED,
          name: 'fixed_value',
          displayName: '固定值',
          alias: 'fixed_value',
          dataType: DataType.STRING,
          fixedValue: '',
          isEditable: true,
          // Additional properties for HQLPreviewContainer
          fieldType: 'fixed',
          fieldName: 'fixed_value',
          paramId: null,
          jsonPath: null
        };
        break;
      default:
        return;
    }

    onAddField(newField);
  };

  // Handle field edit (optimized with useCallback)
  const handleEditField = useCallback((field) => {
    if (onUpdateField) {
      // Call parent's edit handler which will open the modal
      onUpdateField(field);
    }
  }, [onUpdateField]);

  // Handle field delete - show confirmation modal (optimized with useCallback)
  const handleDeleteField = useCallback((fieldId) => {
    const field = safeFields.find(f => f.id === fieldId);
    if (!field) return;

    setDeleteModal({
      show: true,
      field: field
    });
  }, [safeFields]);

  // Confirm field deletion (optimized with useCallback)
  const confirmDeleteField = useCallback(() => {
    if (deleteModal.field) {
      onRemoveField(deleteModal.field.id);
      setDeleteModal({ show: false, field: null });
    }
  }, [deleteModal, onRemoveField]);

  // Helper function to get field type label
  const getFieldTypeLabel = (fieldType) => {
    const labels = {
      [FieldType.PARAMETER]: '参数',
      [FieldType.BASIC]: '基础字段',
      [FieldType.CUSTOM]: '自定义字段',
      [FieldType.FIXED]: '固定值'
    };
    return labels[fieldType] || '字段';
  };

  // Get active field for drag overlay
  const activeField = fields.find((f) => f.id === activeId);

  if (isLoading) {
    return (
      <div className="field-canvas">
        <div className="panel-header">
          <h3>
            <i className="bi bi-grid-3x3"></i>
            字段画布
          </h3>
        </div>
        <div className="panel-content">
          <div className="loading-state">
            <i className="bi bi-arrow-repeat spin"></i>
            <p>加载参数中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="field-canvas">
        <div className="panel-header">
          <h3>
            <i className="bi bi-grid-3x3"></i>
            字段画布
          </h3>
        </div>
        <div className="panel-content">
          <div className="error-state">
            <i className="bi bi-exclamation-triangle"></i>
            <p>加载参数失败</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="field-canvas">
      <div className="panel-header">
        <h3>
          <i className="bi bi-grid-3x3"></i>
          字段画布
        </h3>
        {safeFields.length > 0 && (
          <span className="badge badge-primary">{safeFields.length}</span>
        )}
      </div>

      <div className="panel-content">
        {safeFields.length === 0 ? (
          <DropZone
            onDrop={handleDrop}
            onNativeDrop={handleNativeDrop}
            onNativeDragOver={handleNativeDragOver}
            onNativeDragLeave={handleNativeDragLeave}
            isActive={true}
          >
            <div className="empty-state">
              <i className="bi bi-hand-index"></i>
              <p>从左侧拖拽参数到此处添加字段</p>
              <div className="add-field-buttons">
                <button
                  className="btn btn-outline-primary"
                  onClick={() => handleAddFieldClick(FieldType.BASIC)}
                >
                  <i className="bi bi-plus-circle"></i>
                  添加基础字段
                </button>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => handleAddFieldClick(FieldType.CUSTOM)}
                >
                  <i className="bi bi-plus-circle"></i>
                  添加自定义字段
                </button>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => handleAddFieldClick(FieldType.FIXED)}
                >
                  <i className="bi bi-plus-circle"></i>
                  添加固定值字段
                </button>
              </div>
            </div>
          </DropZone>
        ) : (
          <DndContext
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            sensors={sensors}
          >
            <SortableContext
              items={safeFields.map(f => f.id)}
              strategy={verticalListSortingStrategy}
            >
              <DropZone
                onDrop={handleDrop}
                onNativeDrop={handleNativeDrop}
                onNativeDragOver={handleNativeDragOver}
                onNativeDragLeave={handleNativeDragLeave}
                isActive={true}
              >
                <div className="field-list">
                  {safeFields.map((field) => (
                    <SortableFieldItem
                      key={field.id}
                      field={field}
                      onEdit={handleEditField}
                      onDelete={handleDeleteField}
                    />
                  ))}
                </div>
              </DropZone>
            </SortableContext>

            {/* Drag Overlay */}
            <DragOverlay>
              {activeField ? (
                <div className="field-item dragging-overlay">
                  <div className="field-handle">
                    <i className="bi bi-grip-vertical"></i>
                  </div>
                  <div className="field-info">
                    <strong>{activeField.alias || activeField.name}</strong>
                  </div>
                </div>
              ) : null}
            </DragOverlay>
          </DndContext>
        )}

        {safeFields.length > 0 && (
          <div className="add-field-section">
            <div className="dropdown">
              <button
                className="btn btn-outline-primary btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
              >
                <i className="bi bi-plus-circle"></i>
                添加字段
              </button>
              <ul className="dropdown-menu">
                <li>
                  <button
                    className="dropdown-item"
                    onClick={() => handleAddFieldClick(FieldType.BASIC)}
                  >
                    <i className="bi bi-type"></i>
                    基础字段
                  </button>
                </li>
                <li>
                  <button
                    className="dropdown-item"
                    onClick={() => handleAddFieldClick(FieldType.CUSTOM)}
                  >
                    <i className="bi bi-code"></i>
                    自定义字段
                  </button>
                </li>
                <li>
                  <button
                    className="dropdown-item"
                    onClick={() => handleAddFieldClick(FieldType.FIXED)}
                  >
                    <i className="bi bi-pin"></i>
                    固定值字段
                  </button>
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteModal.show && (
        <DeleteConfirmModal
          itemName="字段"
          itemDetails={{
            name: deleteModal.field?.alias || deleteModal.field?.name,
            type: getFieldTypeLabel(deleteModal.field?.fieldType)
          }}
          onConfirm={confirmDeleteField}
          onClose={() => setDeleteModal({ show: false, field: null })}
        />
      )}
    </div>
  );
}

FieldCanvas.propTypes = {
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['parameter', 'basic', 'custom', 'fixed']).isRequired,
      sourceId: PropTypes.string,
      name: PropTypes.string.isRequired,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired,
      isEditable: PropTypes.bool
    })
  ),
  parameters: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired
    })
  ),
  onFieldsChange: PropTypes.func.isRequired,
  onAddField: PropTypes.func.isRequired,
  onRemoveField: PropTypes.func.isRequired,
  onUpdateField: PropTypes.func.isRequired,
  onReorderFields: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  hasError: PropTypes.bool
};
