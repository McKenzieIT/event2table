import React, { useState, useCallback, useMemo } from 'react';
import { DndContext, closestCenter, DragOverlay, useSensors, useSensor, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, arrayMove, sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import PropTypes from 'prop-types';
import { Button } from '@shared/ui';
import { EmptyState } from '@shared/ui';
import { FieldType, DataType } from '../types/fieldTypes';
import { generateId } from '@shared/utils/idGenerator';
import SortableFieldItem from './FieldCanvas/SortableFieldItem';
import { DropZone } from './FieldCanvas/DropZone';
import { EdgeToolbar } from './FieldCanvas/EdgeToolbar';
import { CanvasStatsDisplay } from './FieldCanvas/CanvasStatsDisplay';
import { FieldContextMenu } from './FieldCanvas/FieldContextMenu';

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
          hive_type: dragData.hive_type,  // ✅ 新增：Hive数据类型
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

    // ✅ BUGFIX #4: 修复字段类型判断和字段名显示
    // 优先使用 fieldType（后端格式），fallback到 type（内部格式）
    const fieldTypeValue = deleteModal.field.fieldType || deleteModal.field.type;

    const getFieldTypeLabel = (fieldType) => {
      // 处理多种格式：GraphQL enum（大写）、内部格式（小写）、后端格式
      const normalizedType = String(fieldType).toLowerCase();

      const typeLabels = {
        'param': '参数',
        'parameter': '参数',
        'base': '基础字段',
        'basic': '基础字段',
        'custom': '自定义字段',
        'fixed': '固定值'
      };

      return typeLabels[normalizedType] || '字段';
    };

    const fieldType = getFieldTypeLabel(fieldTypeValue);
    const fieldName = deleteModal.field.alias || deleteModal.field.displayName || deleteModal.field.name || deleteModal.field.fieldName;

    return `确定要删除${fieldType}"${fieldName}"吗？`;
  }, [deleteModal]);

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
            <EmptyState
              icon={<i className="bi bi-hand-index" style={{ fontSize: '48px' }} />}
              title="从左侧拖拽参数到此处添加字段"
            />
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
                  {safeFields.map((field, index) => (
                    <SortableFieldItem
                      key={`${field.id}-${index}`}
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
