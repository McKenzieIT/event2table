import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import React from 'react';
import FieldCanvas from '../FieldCanvas';

// Mock dnd-kit dependencies
vi.mock('@dnd-kit/core', () => ({
  DndContext: ({ children, onDragStart, onDragEnd }: any) => (
    <div data-testid="dnd-context">
      {children}
      <button
        onClick={() => onDragStart?.({ active: { id: 'test-id' } })}
        data-testid="drag-start"
      >
        Start Drag
      </button>
      <button
        onClick={() => onDragEnd?.({ active: { id: 'test-id' }, over: { id: 'test-id-2' } })}
        data-testid="drag-end"
      >
        End Drag
      </button>
    </div>
  ),
  useSensors: () => [],
  useSensor: () => ({}),
  closestCenter: {},
  DragOverlay: ({ children }: any) => <div data-testid="drag-overlay">{children}</div>,
  PointerSensor: {},
  KeyboardSensor: {},
}));

vi.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }: any) => <div data-testid="sortable-context">{children}</div>,
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }),
  arrayMove: (array: any[], oldIndex: number, newIndex: number) => {
    const result = [...array];
    const [removed] = result.splice(oldIndex, 1);
    result.splice(newIndex, 0, removed);
    return result;
  },
  verticalListSortingStrategy: {},
  sortableKeyboardCoordinates: {},
}));

vi.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: () => '',
    },
  },
}));

// Mock sub-components
vi.mock('../EdgeToolbar', () => ({
  default: ({ onAddBaseField, onAddCustomField, onQuickAddCommon }: any) => (
    <div data-testid="edge-toolbar">
      <button onClick={onAddBaseField} data-testid="add-base-field">
        Add Base Field
      </button>
      <button onClick={onAddCustomField} data-testid="add-custom-field">
        Add Custom Field
      </button>
      <button onClick={onQuickAddCommon} data-testid="quick-add-common">
        Quick Add Common
      </button>
    </div>
  ),
}));

vi.mock('../FieldContextMenu', () => ({
  default: ({ isOpen, onClose, onAddBaseField }: any) =>
    isOpen ? (
      <div data-testid="context-menu">
        <button onClick={onAddBaseField}>Add Base Field</button>
        <button onClick={onClose}>Close</button>
      </div>
    ) : null,
}));

vi.mock('../DeleteConfirmModal', () => ({
  default: ({ isOpen, onConfirm, onCancel }: any) =>
    isOpen ? (
      <div data-testid="delete-modal">
        <button onClick={onConfirm}>Confirm</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    ) : null,
}));

vi.mock('../CanvasStatsDisplay', () => ({
  default: ({ stats }: any) => (
    <div data-testid="canvas-stats">
      <span>Total: {stats.total}</span>
      <span>Base: {stats.baseFields}</span>
      <span>Param: {stats.paramFields}</span>
    </div>
  ),
}));

vi.mock('../DropZone', () => ({
  default: ({ children, onNativeDrop, onNativeDragOver }: any) => (
    <div
      data-testid="drop-zone"
      onDrop={(e) => onNativeDrop?.(e)}
      onDragOver={(e) => onNativeDragOver?.(e)}
    >
      {children}
    </div>
  ),
}));

vi.mock('../EmptyState', () => ({
  default: ({ title }: any) => <div data-testid="empty-state">{title}</div>,
}));

// Mock Button component
vi.mock('react-bootstrap/Button', () => ({
  default: ({ children, onClick, variant, size }: any) => (
    <button
      onClick={onClick}
      data-variant={variant}
      data-size={size}
      className={`btn btn-${variant} btn-${size}`}
    >
      {children}
    </button>
  ),
}));

// Mock generateId function
vi.mock('../../../shared/utils/idGenerator', () => ({
  generateId: () => 'test-id-123',
}));

describe('FieldCanvas Component', () => {
  const mockProps = {
    fields: [],
    parameters: [],
    whereConditions: [],
    onFieldsChange: vi.fn(),
    onAddField: vi.fn(),
    onRemoveField: vi.fn(),
    onUpdateField: vi.fn(),
    onReorderFields: vi.fn(),
    isLoading: false,
    hasError: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==================== Component Rendering Tests ====================
  describe('Component Rendering', () => {
    it('should render correctly with empty fields', () => {
      render(<FieldCanvas {...mockProps} />);
      expect(screen.getByText('字段画布')).toBeInTheDocument();
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
      expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
    });

    it('should render loading state', () => {
      render(<FieldCanvas {...mockProps} isLoading={true} />);
      expect(screen.getByText('加载参数中...')).toBeInTheDocument();
      expect(screen.queryByTestId('empty-state')).not.toBeInTheDocument();
    });

    it('should render error state', () => {
      render(<FieldCanvas {...mockProps} hasError={true} />);
      expect(screen.getByText('加载参数失败')).toBeInTheDocument();
      expect(screen.queryByTestId('empty-state')).not.toBeInTheDocument();
    });

    it('should render with fields', () => {
      const fields = [
        {
          id: 'field-1',
          type: 'basic',
          name: 'ds',
          alias: 'ds',
          displayName: '分区',
          dataType: 'STRING',
          isEditable: true,
          fieldType: 'base',
          fieldName: 'ds',
        },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      expect(screen.getByText('ds')).toBeInTheDocument();
      expect(screen.getByText('(分区)')).toBeInTheDocument();
    });

    it('should display statistics correctly', () => {
      const fields = [
        { id: '1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
        { id: '2', type: 'parameter', name: 'role_id', alias: 'role_id', displayName: '角色ID', dataType: 'BIGINT', isEditable: true, fieldType: 'param', fieldName: 'role_id' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const stats = screen.getByTestId('canvas-stats');
      expect(stats).toBeInTheDocument();
      expect(stats).toHaveTextContent('Total: 2');
      expect(stats).toHaveTextContent('Base: 1');
      expect(stats).toHaveTextContent('Param: 1');
    });

    it('should render edge toolbar', () => {
      render(<FieldCanvas {...mockProps} />);
      expect(screen.getByTestId('edge-toolbar')).toBeInTheDocument();
      expect(screen.getByTestId('add-base-field')).toBeInTheDocument();
      expect(screen.getByTestId('add-custom-field')).toBeInTheDocument();
      expect(screen.getByTestId('quick-add-common')).toBeInTheDocument();
    });
  });

  // ==================== Drag and Drop Tests ====================
  describe('Drag and Drop Functionality', () => {
    it('should handle drag start', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const dragStartButton = screen.getByTestId('drag-start');
      await userEvent.click(dragStartButton);
      
      // Verify drag overlay appears
      expect(screen.getByTestId('drag-overlay')).toBeInTheDocument();
    });

    it('should handle drag end and reorder fields', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
        { id: 'field-2', type: 'basic', name: 'tm', alias: 'tm', displayName: '上报时间', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'tm' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const dragEndButton = screen.getByTestId('drag-end');
      await userEvent.click(dragEndButton);
      
      expect(mockProps.onReorderFields).toHaveBeenCalled();
    });

    it('should handle native drop from external source', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const dropZone = screen.getByTestId('drop-zone');
      const dragData = JSON.stringify({
        fieldType: 'param',
        fieldName: 'test_field',
        displayName: 'Test Field',
        paramId: 1,
        hive_type: 'STRING',
      });
      
      const dropEvent = new Event('drop', {
        bubbles: true,
        cancelable: true,
      }) as any;
      dropEvent.dataTransfer = {
        getData: vi.fn((format) => {
          if (format === 'application/json' || format === 'text/plain') {
            return dragData;
          }
          return '';
        }),
        dropEffect: '',
      };
      dropEvent.preventDefault = vi.fn();
      dropEvent.stopPropagation = vi.fn();
      
      fireEvent(dropZone, dropEvent);
      
      await waitFor(() => {
        expect(mockProps.onAddField).toHaveBeenCalledWith({
          fieldType: 'param',
          fieldName: 'test_field',
          displayName: 'Test Field',
          paramId: 1,
          hive_type: 'STRING',
        });
      });
    });

    it('should handle drag over', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const dropZone = screen.getByTestId('drop-zone');
      const dragOverEvent = new Event('dragover', {
        bubbles: true,
        cancelable: true,
      }) as any;
      dragOverEvent.dataTransfer = {
        dropEffect: '',
      };
      dragOverEvent.preventDefault = vi.fn();
      
      fireEvent(dropZone, dragOverEvent);
      
      expect(dragOverEvent.preventDefault).toHaveBeenCalled();
    });
  });

  // ==================== Field Addition Tests ====================
  describe('Field Addition', () => {
    it('should add base field when clicking add base field button', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const addBaseFieldButton = screen.getByTestId('add-base-field');
      await userEvent.click(addBaseFieldButton);
      
      expect(mockProps.onAddField).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'basic',
          name: 'ds',
          displayName: '分区',
          alias: 'ds',
          fieldType: 'base',
        })
      );
    });

    it('should add custom field when clicking add custom field button', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const addCustomFieldButton = screen.getByTestId('add-custom-field');
      await userEvent.click(addCustomFieldButton);
      
      expect(mockProps.onAddField).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'custom',
          name: 'custom_field',
          displayName: '自定义字段',
          fieldType: 'custom',
        })
      );
    });

    it('should quick add common fields', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const quickAddCommonButton = screen.getByTestId('quick-add-common');
      await userEvent.click(quickAddCommonButton);
      
      // Should add 4 common fields
      expect(mockProps.onAddField).toHaveBeenCalledTimes(4);
    });

    it('should not add duplicate fields when quick adding common fields', async () => {
      const existingFields = [
        { id: '1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={existingFields} />);
      
      const quickAddCommonButton = screen.getByTestId('quick-add-common');
      await userEvent.click(quickAddCommonButton);
      
      // Should only add 3 fields (ds already exists)
      expect(mockProps.onAddField).toHaveBeenCalledTimes(3);
    });
  });

  // ==================== Field Deletion Tests ====================
  describe('Field Deletion', () => {
    it('should show delete confirmation modal when clicking delete button', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const deleteButtons = screen.getAllByText('删除');
      await userEvent.click(deleteButtons[0]);
      
      expect(screen.getByTestId('delete-modal')).toBeInTheDocument();
    });

    it('should delete field when confirming deletion', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const deleteButtons = screen.getAllByText('删除');
      await userEvent.click(deleteButtons[0]);
      
      const confirmButton = screen.getByText('Confirm');
      await userEvent.click(confirmButton);
      
      expect(mockProps.onRemoveField).toHaveBeenCalledWith('field-1');
      expect(screen.queryByTestId('delete-modal')).not.toBeInTheDocument();
    });

    it('should cancel deletion when clicking cancel button', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const deleteButtons = screen.getAllByText('删除');
      await userEvent.click(deleteButtons[0]);
      
      const cancelButton = screen.getByText('Cancel');
      await userEvent.click(cancelButton);
      
      expect(mockProps.onRemoveField).not.toHaveBeenCalled();
      expect(screen.queryByTestId('delete-modal')).not.toBeInTheDocument();
    });

    it('should display correct delete message for parameter field', async () => {
      const fields = [
        { id: 'field-1', type: 'parameter', name: 'role_id', alias: 'role_id', displayName: '角色ID', dataType: 'BIGINT', isEditable: true, fieldType: 'param', fieldName: 'role_id' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const deleteButtons = screen.getAllByText('删除');
      await userEvent.click(deleteButtons[0]);
      
      const modal = screen.getByTestId('delete-modal');
      expect(modal).toHaveTextContent('参数');
      expect(modal).toHaveTextContent('role_id');
    });
  });

  // ==================== Field Editing Tests ====================
  describe('Field Editing', () => {
    it('should call onUpdateField when clicking edit button', async () => {
      const fields = [
        { id: 'field-1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      const editButtons = screen.getAllByText('编辑');
      await userEvent.click(editButtons[0]);
      
      expect(mockProps.onUpdateField).toHaveBeenCalledWith(fields[0]);
    });
  });

  // ==================== Context Menu Tests ====================
  describe('Context Menu', () => {
    it('should open context menu on right click', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const panelContent = screen.getByTestId('drop-zone').parentElement;
      if (panelContent) {
        fireEvent.contextMenu(panelContent);
        
        await waitFor(() => {
          expect(screen.getByTestId('context-menu')).toBeInTheDocument();
        });
      }
    });

    it('should close context menu when clicking close button', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const panelContent = screen.getByTestId('drop-zone').parentElement;
      if (panelContent) {
        fireEvent.contextMenu(panelContent);
        
        await waitFor(() => {
          const closeButton = screen.getByText('Close');
          userEvent.click(closeButton);
          
          expect(screen.queryByTestId('context-menu')).not.toBeInTheDocument();
        });
      }
    });

    it('should add field from context menu', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const panelContent = screen.getByTestId('drop-zone').parentElement;
      if (panelContent) {
        fireEvent.contextMenu(panelContent);
        
        await waitFor(() => {
          const addBaseFieldButton = screen.getByTestId('context-menu').querySelector('button');
          if (addBaseFieldButton) {
            userEvent.click(addBaseFieldButton);
            
            expect(mockProps.onAddField).toHaveBeenCalled();
          }
        });
      }
    });
  });

  // ==================== State Management Tests ====================
  describe('State Management', () => {
    it('should handle empty fields array gracefully', () => {
      render(<FieldCanvas {...mockProps} fields={undefined as any} />);
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    it('should handle null parameters gracefully', () => {
      render(<FieldCanvas {...mockProps} parameters={null as any} />);
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    it('should handle null whereConditions gracefully', () => {
      render(<FieldCanvas {...mockProps} whereConditions={null as any} />);
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    it('should display correct field type icons', () => {
      const fields = [
        { id: '1', type: 'parameter', name: 'role_id', alias: 'role_id', displayName: '角色ID', dataType: 'BIGINT', isEditable: true, fieldType: 'param', fieldName: 'role_id' },
        { id: '2', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
        { id: '3', type: 'custom', name: 'custom', alias: 'custom', displayName: '自定义', dataType: 'STRING', isEditable: true, fieldType: 'custom', fieldName: 'custom' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      // Check that fields are rendered with their types
      expect(screen.getByText('role_id')).toBeInTheDocument();
      expect(screen.getByText('ds')).toBeInTheDocument();
      expect(screen.getByText('custom')).toBeInTheDocument();
    });

    it('should handle GraphQL enum field types (uppercase)', () => {
      const fields = [
        { id: '1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'BASE', fieldName: 'ds' },
        { id: '2', type: 'parameter', name: 'role_id', alias: 'role_id', displayName: '角色ID', dataType: 'BIGINT', isEditable: true, fieldType: 'PARAM', fieldName: 'role_id' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText('ds')).toBeInTheDocument();
      expect(screen.getByText('role_id')).toBeInTheDocument();
    });
  });

  // ==================== Edge Cases ====================
  describe('Edge Cases', () => {
    it('should handle malformed drop data gracefully', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const dropZone = screen.getByTestId('drop-zone');
      const dropEvent = new Event('drop', {
        bubbles: true,
        cancelable: true,
      }) as any;
      dropEvent.dataTransfer = {
        getData: vi.fn(() => 'invalid json'),
      };
      dropEvent.preventDefault = vi.fn();
      dropEvent.stopPropagation = vi.fn();
      
      fireEvent(dropZone, dropEvent);
      
      // Should not call onAddField with invalid data
      expect(mockProps.onAddField).not.toHaveBeenCalled();
    });

    it('should handle field without alias', () => {
      const fields = [
        { id: '1', type: 'basic', name: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      // Should display fieldName when alias is not provided
      expect(screen.getByText('ds')).toBeInTheDocument();
    });

    it('should handle field with same alias and fieldName', () => {
      const fields = [
        { id: '1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      // Should not show duplicate display name
      expect(screen.queryByText('(ds)')).not.toBeInTheDocument();
    });
  });

  // ==================== Integration Tests ====================
  describe('Integration Tests', () => {
    it('should complete full workflow: add field, reorder, edit, delete', async () => {
      const fields = [
        { id: '1', type: 'basic', name: 'ds', alias: 'ds', displayName: '分区', dataType: 'STRING', isEditable: true, fieldType: 'base', fieldName: 'ds' },
      ];
      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      // Add a new field
      const addCustomFieldButton = screen.getByTestId('add-custom-field');
      await userEvent.click(addCustomFieldButton);
      expect(mockProps.onAddField).toHaveBeenCalled();
      
      // Reorder fields
      const dragEndButton = screen.getByTestId('drag-end');
      await userEvent.click(dragEndButton);
      expect(mockProps.onReorderFields).toHaveBeenCalled();
      
      // Edit field
      const editButtons = screen.getAllByText('编辑');
      await userEvent.click(editButtons[0]);
      expect(mockProps.onUpdateField).toHaveBeenCalled();
      
      // Delete field
      const deleteButtons = screen.getAllByText('删除');
      await userEvent.click(deleteButtons[0]);
      const confirmButton = screen.getByText('Confirm');
      await userEvent.click(confirmButton);
      expect(mockProps.onRemoveField).toHaveBeenCalled();
    });

    it('should handle rapid field additions', async () => {
      render(<FieldCanvas {...mockProps} />);
      
      const addBaseFieldButton = screen.getByTestId('add-base-field');
      
      // Add multiple fields rapidly
      await userEvent.click(addBaseFieldButton);
      await userEvent.click(addBaseFieldButton);
      await userEvent.click(addBaseFieldButton);
      
      expect(mockProps.onAddField).toHaveBeenCalledTimes(3);
    });
  });
});
