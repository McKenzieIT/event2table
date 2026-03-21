import React from 'react';
import { DndContext, closestCenter, DragOverlay } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import type { UniqueIdentifier, DragStartEvent, DragEndEvent } from '@dnd-kit/core';
import { EmptyState } from '@shared/ui';
import SortableFieldItem from './SortableFieldItem';
import { DropZone } from './DropZone';
import { EdgeToolbar } from './EdgeToolbar';
import { FieldContextMenu } from './FieldContextMenu';
import { Field } from './utils/fieldUtils';
import { FieldType } from '../../types/fieldTypes';
import { getDeleteMessage } from './utils/fieldUtils';

interface FieldCanvasContentProps {
  fields: Field[];
  compactMode: boolean;
  sensors: any;
  activeId: UniqueIdentifier | null;
  activeField: Field | undefined;
  contextMenu: { isOpen: boolean; x: number; y: number };
  deleteModal: { show: boolean; field: Field | null };
  
  // Handlers
  handleDragStart: (event: DragStartEvent) => void;
  handleDragEnd: (event: DragEndEvent) => void;
  handleDrop: (parameter: any) => void;
  handleNativeDrop: (e: React.DragEvent) => void;
  handleNativeDragOver: (e: React.DragEvent<Element>) => void;
  handleNativeDragLeave: (e: React.DragEvent) => void;
  handleEditField: (field: Field) => void;
  handleDeleteField: (fieldId: string) => void;
  handleContextMenu: (event: React.MouseEvent) => void;
  closeContextMenu: () => void;
  confirmDeleteField: () => void;
  setDeleteModal: (modal: { show: boolean; field: Field | null }) => void;
  
  // EdgeToolbar handlers
  onAddBaseField: () => void;
  onAddCustomField: () => void;
  onAddFixedField: () => void;
  onQuickAddCommon: () => void;
  onQuickAddAll: () => void;
  onAddField: (field: Field) => void;
}

/**
 * FieldCanvasContent - 画布主要内容组件
 * 包含字段列表、拖拽逻辑、上下文菜单等
 * 使用 React.memo 优化性能
 */
const FieldCanvasContent = React.memo<FieldCanvasContentProps>(({
  fields,
  compactMode,
  sensors,
  activeId,
  activeField,
  contextMenu,
  deleteModal,
  handleDragStart,
  handleDragEnd,
  handleDrop,
  handleNativeDrop,
  handleNativeDragOver,
  handleNativeDragLeave,
  handleEditField,
  handleDeleteField,
  handleContextMenu,
  closeContextMenu,
  confirmDeleteField,
  setDeleteModal,
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
  onQuickAddAll,
  onAddField
}) => {
  const DeleteConfirmModal = React.lazy(() => import('./DeleteConfirmModal'));

  return (
    <>
      <div
        className="panel-content"
        onContextMenu={handleContextMenu}
      >
        {fields.length === 0 ? (
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
              items={fields.map(f => f.id)}
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
                  {fields.map((field, index) => (
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
          canvasFields={fields}
          onAddBaseField={onAddBaseField}
          onAddCustomField={onAddCustomField}
          onAddFixedField={onAddFixedField}
          onQuickAddCommon={onQuickAddCommon}
          onQuickAddAll={onQuickAddAll}
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
          onAddBaseField();
          closeContextMenu();
        }}
        onAddCustomField={() => {
          onAddCustomField();
          closeContextMenu();
        }}
        onAddFixedField={() => {
          onAddFixedField();
          closeContextMenu();
        }}
        onQuickAddCommon={() => {
          onQuickAddCommon();
          closeContextMenu();
        }}
      />

      {/* Delete Confirmation Modal */}
      {deleteModal.show && deleteModal.field && (
        <React.Suspense fallback={null}>
          <DeleteConfirmModal
            isOpen={deleteModal.show}
            title="确认删除字段"
            message={getDeleteMessage(deleteModal.field)}
            confirmText="删除"
            cancelText="取消"
            onConfirm={confirmDeleteField}
            onCancel={() => setDeleteModal({ show: false, field: null })}
          />
        </React.Suspense>
      )}
    </>
  );
});

FieldCanvasContent.displayName = 'FieldCanvasContent';

export default FieldCanvasContent;
