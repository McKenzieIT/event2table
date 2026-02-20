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
// @ts-nocheck - TypeScript检查暂禁用（dnd-kit和组件类型待完善）

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
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
import CanvasStatsDisplay from './CanvasStatsDisplay';
import EdgeToolbar from './EdgeToolbar';
import FieldContextMenu from './FieldContextMenu';
import './FieldCanvas.css';
import './CanvasHeader.css';
import './EdgeToolbar/EdgeToolbar.css';
import './FieldContextMenu.css';

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
const SortableFieldItem = React.memo(({
  field,
  onEdit,
  onDelete,
  compact = false  // Compact mode prop (default false for backward compatibility)
}) => {
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

      {/* Field Alias - 扁平化 */}
      <strong
        className="field-alias"
        title={field.fieldName}  // Tooltip for truncated text
      >
        {field.alias || field.fieldName}
      </strong>

      {/* Original Name - 扁平化 */}
      <span className="field-original-name">
        {field.fieldName !== field.alias ? `(${field.displayName || field.fieldName})` : ''}
      </span>

      {/* Data Type Badge - 可选显示 */}
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
  // Only re-render if critical properties change
  return prevProps.field.id === nextProps.field.id &&
         prevProps.field.name === nextProps.field.name &&
         prevProps.field.alias === nextProps.field.alias &&
         prevProps.field.fieldType === nextProps.field.fieldType &&
         prevProps.compact === nextProps.compact;  // Compare compact prop
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
  whereConditions = [],
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

  // Compact mode state (default true as per user request)
  const [compactMode, setCompactMode] = useState(true);

  const [activeId, setActiveId] = useState(null);
  const [deleteModal, setDeleteModal] = useState({
    show: false,
    field: null
  });

  // Right click context menu state
  const [contextMenu, setContextMenu] = useState({
    isOpen: false,
    x: 0,
    y: 0
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

  // Quick add common base fields
  const handleQuickAddCommon = useCallback(() => {
    const commonFields = [
      { name: 'ds', displayName: '分区', alias: 'ds', dataType: DataType.STRING },
      { name: 'role_id', displayName: '角色ID', alias: 'role_id', dataType: DataType.BIGINT },
      { name: 'account_id', displayName: '账号ID', alias: 'account_id', dataType: DataType.BIGINT },
      { name: 'tm', displayName: '上报时间', alias: 'tm', dataType: DataType.STRING }
    ];

    commonFields.forEach(field => {
      // Check if field already exists
      const exists = safeFields.some(f => f.name === field.name);
      if (!exists) {
        const newField = {
          id: generateId(),
          type: FieldType.BASIC,
          name: field.name,
          displayName: field.displayName,
          alias: field.alias,
          dataType: field.dataType,
          isEditable: true,
          fieldType: 'base',
          fieldName: field.name,
          paramId: null,
          jsonPath: null
        };
        onAddField(newField);
      }
    });
  }, [safeFields, onAddField]);

  // Quick add all base fields
  const handleQuickAddAll = useCallback(() => {
    const allFields = [
      { name: 'ds', displayName: '分区', alias: 'ds', dataType: DataType.STRING },
      { name: 'role_id', displayName: '角色ID', alias: 'role_id', dataType: DataType.BIGINT },
      { name: 'account_id', displayName: '账号ID', alias: 'account_id', dataType: DataType.BIGINT },
      { name: 'utdid', displayName: '设备ID', alias: 'utdid', dataType: DataType.STRING },
      { name: 'tm', displayName: '上报时间', alias: 'tm', dataType: DataType.STRING },
      { name: 'ts', displayName: '上报时间戳', alias: 'ts', dataType: DataType.BIGINT },
      { name: 'envinfo', displayName: '环境信息', alias: 'envinfo', dataType: DataType.STRING }
    ];

    allFields.forEach(field => {
      // Check if field already exists
      const exists = safeFields.some(f => f.name === field.name);
      if (!exists) {
        const newField = {
          id: generateId(),
          type: FieldType.BASIC,
          name: field.name,
          displayName: field.displayName,
          alias: field.alias,
          dataType: field.dataType,
          isEditable: true,
          fieldType: 'base',
          fieldName: field.name,
          paramId: null,
          jsonPath: null
        };
        onAddField(newField);
      }
    });
  }, [safeFields, onAddField]);

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

  // Handle context menu (right-click)
  const handleContextMenu = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();

    setContextMenu({
      isOpen: true,
      x: event.clientX,
      y: event.clientY
    });
  }, []);

  // Close context menu
  const closeContextMenu = useCallback(() => {
    setContextMenu({
      isOpen: false,
      x: 0,
      y: 0
    });
  }, []);

  // Generate delete confirmation message
  const getDeleteMessage = useCallback(() => {
    if (!deleteModal.field) return '';
    const fieldType = getFieldTypeLabel(deleteModal.field.fieldType);
    const fieldName = deleteModal.field.alias || deleteModal.field.name;
    return `确定要删除${fieldType}"${fieldName}"吗？`;
  }, [deleteModal]);

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
            <i className="bi bi-grid-3x3" aria-hidden="true"></i>
            字段画布
          </h3>
        </div>
        <div className="panel-content">
          <div className="loading-state">
            <i className="bi bi-arrow-repeat spin" aria-hidden="true"></i>
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
            <i className="bi bi-grid-3x3" aria-hidden="true"></i>
            字段画布
          </h3>
        </div>
        <div className="panel-content">
          <div className="error-state">
            <i className="bi bi-exclamation-triangle" aria-hidden="true"></i>
            <p>加载参数失败</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate statistics for display
  const stats = useMemo(() => {
    const baseFields = safeFields.filter(f => f.fieldType === 'base' || f.fieldType === FieldType.BASIC).length;
    const paramFields = safeFields.filter(f => f.fieldType === 'param' || f.fieldType === FieldType.PARAMETER).length;
    return {
      total: safeFields.length,
      baseFields,
      paramFields,
      whereCount: whereConditions ? whereConditions.length : 0,
    };
  }, [safeFields, whereConditions]);

  return (
    <div className="field-canvas">
      <div className="panel-header compact">
        <h3>
          <i className="bi bi-grid-3x3" aria-hidden="true"></i>
          字段画布
        </h3>

        {/* Statistics Display - 紧凑型统计信息 */}
        <CanvasStatsDisplay stats={stats} />
      </div>

      <div
        className="panel-content"
        onContextMenu={handleContextMenu}
      >
        {safeFields.length === 0 ? (
          <DropZone
            onDrop={handleDrop}
            onNativeDrop={handleNativeDrop}
            onNativeDragOver={handleNativeDragOver}
            onNativeDragLeave={handleNativeDragLeave}
            isActive={true}
          >
            <div className="empty-state">
              <i className="bi bi-hand-index" aria-hidden="true"></i>
              <p>从左侧拖拽参数到此处添加字段</p>
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
                      compact={compactMode}
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
                    <i className="bi bi-grip-vertical" aria-hidden="true"></i>
                  </div>
                  <div className="field-info">
                    <strong>{activeField.alias || activeField.name}</strong>
                  </div>
                </div>
              ) : null}
            </DragOverlay>
          </DndContext>
        )}

        {/* Edge Toolbar - 底部边缘激活栏 */}
        <EdgeToolbar
          canvasFields={safeFields}
          onAddBaseField={() => handleAddFieldClick(FieldType.BASIC)}
          onAddCustomField={() => handleAddFieldClick(FieldType.CUSTOM)}
          onAddFixedField={() => handleAddFieldClick(FieldType.FIXED)}
          onQuickAddCommon={handleQuickAddCommon}
          onQuickAddAll={handleQuickAddAll}
          onAddField={onAddField}
        />
      </div>

      {/* Field Context Menu - 右键菜单 */}
      <FieldContextMenu
        isOpen={contextMenu.isOpen}
        x={contextMenu.x}
        y={contextMenu.y}
        onClose={closeContextMenu}
        onAddBaseField={() => {
          handleAddFieldClick(FieldType.BASIC);
          closeContextMenu();
        }}
        onAddCustomField={() => {
          handleAddFieldClick(FieldType.CUSTOM);
          closeContextMenu();
        }}
        onAddFixedField={() => {
          handleAddFieldClick(FieldType.FIXED);
          closeContextMenu();
        }}
        onQuickAddCommon={() => {
          handleQuickAddCommon();
          closeContextMenu();
        }}
      />

      {/* Delete Confirmation Modal */}
      {deleteModal.show && (
        <DeleteConfirmModal
          isOpen={deleteModal.show}
          title="确认删除字段"
          message={getDeleteMessage()}
          confirmText="删除"
          cancelText="取消"
          onConfirm={confirmDeleteField}
          onCancel={() => setDeleteModal({ show: false, field: null })}
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
      isEditable: PropTypes.bool,
      fieldType: PropTypes.oneOf(['base', 'param', 'basic', 'custom', 'fixed']),
      fieldName: PropTypes.string,
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
  whereConditions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
      operator: PropTypes.string.isRequired,
      value: PropTypes.any,
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
