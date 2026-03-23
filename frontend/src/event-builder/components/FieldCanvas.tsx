import type { CanvasField, WhereCondition } from '@shared/hooks/useEventNodeBuilder';
import React, { memo } from 'react';

import { FieldType } from '../types/fieldTypes';

import FieldCanvasContent from './FieldCanvas/FieldCanvasContent';
import FieldCanvasError from './FieldCanvas/FieldCanvasError';
import FieldCanvasHeader from './FieldCanvas/FieldCanvasHeader';
import FieldCanvasLoading from './FieldCanvas/FieldCanvasLoading';
import { useFieldCanvas } from './FieldCanvas/hooks/useFieldCanvas';
import type { Field, Parameter } from './FieldCanvas/utils/fieldUtils';

// Re-export CanvasField for backward compatibility
export type { CanvasField } from '@shared/hooks/useEventNodeBuilder';

/** Drag-drop field type - partial field for drag operations */
export interface DragDropField {
  id?: string;
  type?: string;
  fieldType?: 'base' | 'param' | 'fixed' | 'custom' | string;
  name?: string;
  fieldName?: string;
  displayName?: string;
  alias?: string;
  paramId?: number | null;
  hive_type?: string;
  dataType?: string;
  sourceId?: string;
}

interface FieldCanvasProps {
  fields?: CanvasField[];
  parameters?: Parameter[];
  whereConditions?: WhereCondition[];
  onFieldsChange?: (fields: CanvasField[]) => void;
  onAddField?: (field: DragDropField) => void;
  onRemoveField?: (fieldId: string) => void;
  onUpdateField?: (field: CanvasField) => void;
  onReorderFields?: (fields: CanvasField[]) => void;
  isLoading?: boolean;
  hasError?: boolean;
}

/**
 * FieldCanvas - Main field canvas component
 * Refactored to use custom hooks and sub-components for better maintainability
 */
function FieldCanvasInner({
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
}: FieldCanvasProps) {
  // Ensure fields and parameters are arrays
  const safeFields = Array.isArray(fields) ? fields : [];
  const safeParameters = Array.isArray(parameters) ? parameters : [];

  // Convert CanvasField[] to Field[] for useFieldCanvas compatibility
  const convertedFields: Field[] = safeFields.map(f => ({
    id: f.id,
    type: f.type,
    name: f.name,
    alias: f.alias,
    displayName: f.displayName,
    dataType: f.dataType,
    isEditable: f.isEditable,
    fieldType: f.fieldType,
    fieldName: f.fieldName,
    // Convert null to undefined for paramId compatibility
    paramId: f.paramId ?? undefined,
    jsonPath: f.jsonPath,
  }));

  // Convert callbacks to match Field type
  const handleAddField = onAddField ? (field: Field) => {
    onAddField({
      id: field.id,
      type: field.type,
      fieldType: field.fieldType as 'base' | 'param' | 'fixed' | 'custom' | string,
      name: field.name,
      fieldName: field.fieldName,
      displayName: field.displayName,
      alias: field.alias,
      // Ensure paramId is number | null
      paramId: typeof field.paramId === 'number' ? field.paramId : null,
      hive_type: field.hive_type,
      dataType: field.dataType,
      sourceId: field.sourceId,
    });
  } : undefined;

  const handleUpdateField = onUpdateField ? (field: Field) => {
    onUpdateField({
      id: field.id,
      type: (field.type || 'basic') as 'basic' | 'parameter' | 'custom' | 'fixed',
      name: field.name,
      displayName: field.displayName,
      alias: field.alias,
      dataType: field.dataType,
      isEditable: field.isEditable,
      fieldType: field.fieldType || 'base',
      fieldName: field.fieldName,
      // Ensure paramId is number | null
      paramId: typeof field.paramId === 'number' ? field.paramId : null,
      jsonPath: field.jsonPath ?? null,
    });
  } : undefined;

  const handleReorderFields = onReorderFields ? (reorderedFields: Field[]) => {
    onReorderFields(reorderedFields.map(f => ({
      id: f.id,
      type: (f.type || 'basic') as 'basic' | 'parameter' | 'custom' | 'fixed',
      name: f.name,
      displayName: f.displayName,
      alias: f.alias,
      dataType: f.dataType,
      isEditable: f.isEditable,
      fieldType: f.fieldType || 'base',
      fieldName: f.fieldName,
      // Ensure paramId is number | null
      paramId: typeof f.paramId === 'number' ? f.paramId : null,
      jsonPath: f.jsonPath ?? null,
    })));
  } : undefined;

  // Convert whereConditions to the format expected by useFieldCanvas
  const convertedWhereConditions = whereConditions?.map(c => ({
    id: c.id,
    field: c.field || '',
    operator: c.operator || '=',
    value: c.value,
  }));

  // Use custom hook for canvas logic
  const canvas = useFieldCanvas({
    fields: convertedFields,
    parameters: safeParameters,
    whereConditions: convertedWhereConditions,
    onAddField: handleAddField || (() => {}),
    onRemoveField: onRemoveField || (() => {}),
    onUpdateField: handleUpdateField || (() => {}),
    onReorderFields: handleReorderFields || (() => {})
  });

  // Handle loading state
  if (isLoading) {
    return <FieldCanvasLoading />;
  }

  // Handle error state
  if (hasError) {
    return <FieldCanvasError />;
  }

  return (
    <div className="field-canvas">
      {/* Header with statistics */}
      <FieldCanvasHeader stats={canvas.stats} />

      {/* Main content with fields and interactions */}
      <FieldCanvasContent
        fields={convertedFields}
        compactMode={canvas.compactMode}
        sensors={canvas.sensors}
        activeId={canvas.activeId}
        activeField={canvas.activeField}
        contextMenu={canvas.contextMenu}
        deleteModal={canvas.deleteModal}
        handleDragStart={canvas.handleDragStart}
        handleDragEnd={canvas.handleDragEnd}
        handleDrop={canvas.handleDrop}
        handleNativeDrop={canvas.handleNativeDrop}
        handleNativeDragOver={canvas.handleNativeDragOver as (e: React.DragEvent<Element>) => void}
        handleNativeDragLeave={canvas.handleNativeDragLeave}
        handleEditField={canvas.handleEditField}
        handleDeleteField={canvas.handleDeleteField}
        handleContextMenu={canvas.handleContextMenu}
        closeContextMenu={canvas.closeContextMenu}
        confirmDeleteField={canvas.confirmDeleteField}
        setDeleteModal={canvas.setDeleteModal}
        onAddBaseField={() => canvas.handleAddFieldClick(FieldType.BASIC)}
        onAddCustomField={() => canvas.handleAddFieldClick(FieldType.CUSTOM)}
        onAddFixedField={() => canvas.handleAddFieldClick(FieldType.FIXED)}
        onQuickAddCommon={canvas.handleQuickAddCommon}
        onQuickAddAll={canvas.handleQuickAddAll}
        onAddField={handleAddField || (() => {})}
      />
    </div>
  );
}

// Use memo with named function for proper displayName
const FieldCanvas = memo(FieldCanvasInner);

FieldCanvas.displayName = 'FieldCanvas';

export default FieldCanvas;