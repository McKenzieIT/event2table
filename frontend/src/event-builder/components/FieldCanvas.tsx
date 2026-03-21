import React from 'react';
import PropTypes from 'prop-types';
import { FieldType } from '../types/fieldTypes';
import { useFieldCanvas } from './FieldCanvas/hooks/useFieldCanvas';
import FieldCanvasHeader from './FieldCanvas/FieldCanvasHeader';
import FieldCanvasContent from './FieldCanvas/FieldCanvasContent';
import FieldCanvasLoading from './FieldCanvas/FieldCanvasLoading';
import FieldCanvasError from './FieldCanvas/FieldCanvasError';

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
interface FieldCanvasProps {
  fields?: Array<{
    id: string;
    type: string;
    name: string;
    alias?: string;
    displayName?: string;
    dataType: string;
    isEditable?: boolean;
    fieldType?: string;
    fieldName?: string;
    paramId?: number | string | null;
    jsonPath?: string | null;
    sourceId?: string;
    mapping?: string;
    fixedValue?: string;
    hive_type?: string;
  }>;
  parameters?: Array<{
    id: string;
    name: string;
    alias?: string;
    dataType: string;
  }>;
  whereConditions?: Array<{
    id: string;
    field: string;
    operator: string;
    value: unknown;
  }>;
  onFieldsChange: (fields: unknown[]) => void;
  onAddField: (field: unknown) => void;
  onRemoveField: (fieldId: string) => void;
  onUpdateField: (field: unknown) => void;
  onReorderFields: (fields: unknown[]) => void;
  isLoading?: boolean;
  hasError?: boolean;
}

/**
 * FieldCanvas - Main field canvas component
 * Refactored to use custom hooks and sub-components for better maintainability
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
}: FieldCanvasProps) {
  // ✅ 添加额外保护，确保 fields 和 parameters 是数组
  const safeFields = Array.isArray(fields) ? fields : [];
  const safeParameters = Array.isArray(parameters) ? parameters : [];

  // Use custom hook for canvas logic
  const canvas = useFieldCanvas({
    fields: safeFields,
    parameters: safeParameters,
    whereConditions,
    onAddField: onAddField as any,
    onRemoveField,
    onUpdateField: onUpdateField as any,
    onReorderFields: onReorderFields as any
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
        fields={safeFields}
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
        handleNativeDragOver={canvas.handleNativeDragOver as any}
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
        onAddField={onAddField as any}
      />
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
      displayName: PropTypes.string,
      dataType: PropTypes.string.isRequired,
      isEditable: PropTypes.bool,
      fieldType: PropTypes.oneOf(['base', 'param', 'basic', 'custom', 'fixed']),
      fieldName: PropTypes.string,
      paramId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      jsonPath: PropTypes.string,
      mapping: PropTypes.string,
      fixedValue: PropTypes.string,
      hive_type: PropTypes.string,
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
