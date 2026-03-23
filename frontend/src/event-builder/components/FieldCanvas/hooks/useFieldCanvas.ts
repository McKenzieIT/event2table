import { useSensors, useSensor, PointerSensor, KeyboardSensor } from '@dnd-kit/core';
import type { UniqueIdentifier, DragStartEvent, DragEndEvent } from '@dnd-kit/core';
import { sortableKeyboardCoordinates , arrayMove } from '@dnd-kit/sortable';
import { useState, useCallback, useMemo } from 'react';

import { FieldType } from '../../../types/fieldTypes';
import { Field, Parameter, createBasicField, createCustomField, createFixedField, createFieldFromParameter, createBaseField, COMMON_BASE_FIELDS, ALL_BASE_FIELDS, calculateFieldStats } from '../utils/fieldUtils';

interface UseFieldCanvasProps {
  fields: Field[];
  parameters: Parameter[];
  whereConditions?: Array<{ id: string; field: string; operator: string; value: unknown }>;
  onAddField: (field: Field) => void;
  onRemoveField: (fieldId: string) => void;
  onUpdateField: (field: Field) => void;
  onReorderFields: (fields: Field[]) => void;
}

/**
 * Custom hook for FieldCanvas logic
 * Manages state, drag and drop, and field operations
 */
export function useFieldCanvas({
  fields,
  parameters,
  whereConditions,
  onAddField,
  onRemoveField,
  onUpdateField,
  onReorderFields
}: UseFieldCanvasProps) {
  // Compact mode state
  const [compactMode, setCompactMode] = useState(true);

  // Active drag state
  const [activeId, setActiveId] = useState<UniqueIdentifier | null>(null);

  // Delete modal state
  const [deleteModal, setDeleteModal] = useState<{
    show: boolean;
    field: Field | null;
  }>({
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

  // Calculate statistics for display
  const stats = useMemo(() => {
    return calculateFieldStats(fields, whereConditions);
  }, [fields, whereConditions]);

  // Handle drag end for reordering
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = fields.findIndex((f) => f.id === active.id);
      const newIndex = fields.findIndex((f) => f.id === over.id);

      const reorderedFields = arrayMove(fields, oldIndex, newIndex);
      if (onReorderFields) {
        onReorderFields(reorderedFields);
      }
    }

    setActiveId(null);
  }, [fields, onReorderFields]);

  // Handle drag start
  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id);
  }, []);

  // Handle drop from event selector
  const handleDrop = useCallback((parameter: Parameter) => {
    const newField = createFieldFromParameter(parameter);
    onAddField(newField);
  }, [onAddField]);

  // Handle native HTML5 drag and drop (from BaseFieldsList and ParamSelector)
  const handleNativeDrop = useCallback((e: React.DragEvent) => {
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
          hive_type: dragData.hive_type,
        } as Field);
      }
    } catch (error) {
      console.error('[FieldCanvas] Error handling drop:', error);
    }
  }, [onAddField]);

  const handleNativeDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    e.currentTarget.classList.add('drag-over');
  }, []);

  const handleNativeDragLeave = useCallback((e: React.DragEvent) => {
    e.currentTarget.classList.remove('drag-over');
  }, []);

  // Handle add field button click
  const handleAddFieldClick = useCallback((type: FieldType) => {
    let newField: Field | undefined;

    switch (type) {
      case FieldType.BASIC:
        newField = createBasicField();
        break;
      case FieldType.CUSTOM:
        newField = createCustomField();
        break;
      case FieldType.FIXED:
        newField = createFixedField();
        break;
      default:
        return;
    }

    if (newField) {
      onAddField(newField);
    }
  }, [onAddField]);

  // Quick add common base fields
  const handleQuickAddCommon = useCallback(() => {
    COMMON_BASE_FIELDS.forEach(field => {
      // Check if field already exists
      const exists = fields.some(f => f.name === field.name);
      if (!exists) {
        const newField = createBaseField(field);
        onAddField(newField);
      }
    });
  }, [fields, onAddField]);

  // Quick add all base fields
  const handleQuickAddAll = useCallback(() => {
    ALL_BASE_FIELDS.forEach(field => {
      // Check if field already exists
      const exists = fields.some(f => f.name === field.name);
      if (!exists) {
        const newField = createBaseField(field);
        onAddField(newField);
      }
    });
  }, [fields, onAddField]);

  // Handle field edit
  const handleEditField = useCallback((field: Field) => {
    if (onUpdateField) {
      // Call parent's edit handler which will open the modal
      onUpdateField(field);
    }
  }, [onUpdateField]);

  // Handle field delete - show confirmation modal
  const handleDeleteField = useCallback((fieldId: string) => {
    const field = fields.find(f => f.id === fieldId);
    if (!field) return;

    setDeleteModal({
      show: true,
      field: field
    });
  }, [fields]);

  // Confirm field deletion
  const confirmDeleteField = useCallback(() => {
    if (deleteModal.field) {
      onRemoveField(deleteModal.field.id);
      setDeleteModal({ show: false, field: null });
    }
  }, [deleteModal, onRemoveField]);

  // Handle context menu (right-click)
  const handleContextMenu = useCallback((event: React.MouseEvent) => {
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

  // Get active field for drag overlay
  const activeField = fields.find((f) => f.id === activeId);

  return {
    // State
    compactMode,
    setCompactMode,
    activeId,
    deleteModal,
    contextMenu,
    stats,
    activeField,
    sensors,
    
    // Handlers
    handleDragStart,
    handleDragEnd,
    handleDrop,
    handleNativeDrop,
    handleNativeDragOver,
    handleNativeDragLeave,
    handleAddFieldClick,
    handleQuickAddCommon,
    handleQuickAddAll,
    handleEditField,
    handleDeleteField,
    confirmDeleteField,
    handleContextMenu,
    closeContextMenu,
    setDeleteModal
  };
}
