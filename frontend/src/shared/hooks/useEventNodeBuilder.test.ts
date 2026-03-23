import { renderHook, act } from '@test/test-utils';
import { describe, it, expect } from 'vitest';

import { useEventNodeBuilder } from './useEventNodeBuilder';

describe('useEventNodeBuilder', () => {
  describe('initial state', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      expect(result.current.selectedEvent).toBeNull();
      expect(result.current.canvasFields).toEqual([]);
      expect(result.current.whereConditions).toEqual([]);
      expect(result.current.isEditMode).toBe(false);
    });

    it('should initialize with default node config', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      expect(result.current.nodeConfig).toEqual({
        nameEn: '',
        nameCn: '',
        description: '',
      });
    });
  });

  describe('canvas fields', () => {
    it('should add field to canvas', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'user_id', 'User ID');
      });
      
      expect(result.current.canvasFields).toHaveLength(1);
      expect(result.current.canvasFields[0].name).toBe('user_id');
      expect(result.current.canvasFields[0].alias).toBe('user_id');
    });

    it('should add field with param ID', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('param', 'param1', 'Param 1', 123);
      });
      
      expect(result.current.canvasFields[0].paramId).toBe(123);
    });

    it('should add field with json path', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('custom', 'custom1', 'Custom 1', null, '$.path');
      });
      
      expect(result.current.canvasFields[0].jsonPath).toBe('$.path');
    });

    it('should remove field from canvas', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'user_id', 'User ID');
      });
      
      const fieldId = result.current.canvasFields[0].id;
      
      act(() => {
        result.current.removeField(fieldId);
      });
      
      expect(result.current.canvasFields).toHaveLength(0);
    });

    it('should update field', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'user_id', 'User ID');
      });
      
      const fieldId = result.current.canvasFields[0].id;
      
      act(() => {
        result.current.updateField(fieldId, { alias: 'userId' });
      });
      
      expect(result.current.canvasFields[0].alias).toBe('userId');
    });

    it('should reorder fields', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'field1', 'Field 1');
        result.current.addFieldToCanvas('base', 'field2', 'Field 2');
        result.current.addFieldToCanvas('base', 'field3', 'Field 3');
      });
      
      const reordered = [result.current.canvasFields[2], result.current.canvasFields[0], result.current.canvasFields[1]];
      
      act(() => {
        result.current.reorderFields(reordered);
      });
      
      expect(result.current.canvasFields[0].name).toBe('field3');
      expect(result.current.canvasFields[1].name).toBe('field1');
      expect(result.current.canvasFields[2].name).toBe('field2');
    });

    it('should clear canvas', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'field1', 'Field 1');
        result.current.addFieldToCanvas('base', 'field2', 'Field 2');
        result.current.clearCanvas();
      });
      
      expect(result.current.canvasFields).toHaveLength(0);
      expect(result.current.whereConditions).toHaveLength(0);
    });
  });

  describe('where conditions', () => {
    it('should add where condition', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereCondition({ field: 'user_id', operator: '=', value: '123' });
      });
      
      expect(result.current.whereConditions).toHaveLength(1);
      expect(result.current.whereConditions[0].field).toBe('user_id');
    });

    it('should add where group', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereGroup({});
      });
      
      expect(result.current.whereConditions).toHaveLength(1);
      expect(result.current.whereConditions[0].type).toBe('group');
    });

    it('should remove where item', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereCondition({ field: 'user_id', operator: '=', value: '123' });
      });
      
      const itemId = result.current.whereConditions[0].id;
      
      act(() => {
        result.current.removeWhereItem(itemId);
      });
      
      expect(result.current.whereConditions).toHaveLength(0);
    });

    it('should update where item', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereCondition({ field: 'user_id', operator: '=', value: '123' });
      });
      
      const itemId = result.current.whereConditions[0].id;
      
      act(() => {
        result.current.updateWhereItem(itemId, { value: '456' });
      });
      
      expect(result.current.whereConditions[0].value).toBe('456');
    });

    it('should clear where conditions', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereCondition({ field: 'user_id', operator: '=', value: '123' });
        result.current.addWhereCondition({ field: 'game_id', operator: '=', value: '456' });
        result.current.clearWhereConditions();
      });
      
      expect(result.current.whereConditions).toHaveLength(0);
    });

    it('should reorder where conditions', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addWhereCondition({ field: 'field1', operator: '=', value: '1' });
        result.current.addWhereCondition({ field: 'field2', operator: '=', value: '2' });
      });
      
      const reordered = [result.current.whereConditions[1], result.current.whereConditions[0]];
      
      act(() => {
        result.current.reorderWhereConditions(reordered);
      });
      
      expect(result.current.whereConditions[0].field).toBe('field2');
    });
  });

  describe('node config', () => {
    it('should update node config', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.setNodeConfig({
          nameEn: 'test_event',
          nameCn: '测试事件',
          description: 'Test description',
        });
      });
      
      expect(result.current.nodeConfig.nameEn).toBe('test_event');
      expect(result.current.nodeConfig.nameCn).toBe('测试事件');
    });
  });

  describe('sidebar', () => {
    it('should toggle sidebar section', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.toggleSidebarSection('eventSection');
      });
      
      expect(result.current.sidebarCollapsed.eventSection).toBe(true);
    });
  });

  describe('edit mode', () => {
    it('should set edit mode', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.setIsEditMode(true);
      });
      
      expect(result.current.isEditMode).toBe(true);
    });

    it('should set editing config ID', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.setEditingConfigId(123);
      });
      
      expect(result.current.editingConfigId).toBe(123);
    });
  });

  describe('reset all', () => {
    it('should reset all state', () => {
      const { result } = renderHook(() => useEventNodeBuilder());
      
      act(() => {
        result.current.addFieldToCanvas('base', 'field1', 'Field 1');
        result.current.addWhereCondition({ field: 'user_id', operator: '=', value: '123' });
        result.current.setNodeConfig({ nameEn: 'test', nameCn: '测试', description: 'desc' });
        result.current.setIsEditMode(true);
        result.current.setEditingConfigId(123);
        result.current.resetAll();
      });
      
      expect(result.current.selectedEvent).toBeNull();
      expect(result.current.canvasFields).toEqual([]);
      expect(result.current.whereConditions).toEqual([]);
      expect(result.current.nodeConfig).toEqual({
        nameEn: '',
        nameCn: '',
        description: '',
      });
      expect(result.current.isEditMode).toBe(false);
      expect(result.current.editingConfigId).toBeNull();
    });
  });
});
