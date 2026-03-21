import React from 'react';
import { FieldType } from '../../types/fieldTypes';
import { Button } from '@shared/ui';

/**
 * Props for EdgeToolbar component
 */
export interface EdgeToolbarProps {
  /** Canvas fields */
  canvasFields: any[];
  /** Add base field callback */
  onAddBaseField: () => void;
  /** Add custom field callback */
  onAddCustomField: () => void;
  /** Add fixed field callback */
  onAddFixedField: () => void;
  /** Quick add common fields callback */
  onQuickAddCommon: () => void;
  /** Quick add all fields callback */
  onQuickAddAll: () => void;
  /** Add field callback */
  onAddField: (field: any) => void;
}

/**
 * EdgeToolbar Component
 */
export const EdgeToolbar: React.FC<EdgeToolbarProps> = ({
  canvasFields,
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
  onQuickAddAll,
  onAddField,
}) => {
  return (
    <div className="edge-toolbar">
      <div className="toolbar-group">
        <Button
          variant="outline-primary"
          size="sm"
          onClick={onAddBaseField}
          title="添加基础字段"
        >
          <i className="bi bi-plus-circle"></i>
          基础字段
        </Button>
        <Button
          variant="outline-success"
          size="sm"
          onClick={onAddCustomField}
          title="添加自定义字段"
        >
          <i className="bi bi-code"></i>
          自定义字段
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={onAddFixedField}
          title="添加固定值"
        >
          <i className="bi bi-pin"></i>
          固定值
        </Button>
      </div>
      <div className="toolbar-divider"></div>
      <div className="toolbar-group">
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={onQuickAddCommon}
          title="快速添加常用字段"
        >
          <i className="bi bi-lightning"></i>
          常用字段
        </Button>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={onQuickAddAll}
          title="添加所有基础字段"
        >
          <i className="bi bi-list-check"></i>
          全部字段
        </Button>
      </div>
    </div>
  );
};

EdgeToolbar.displayName = 'EdgeToolbar';
