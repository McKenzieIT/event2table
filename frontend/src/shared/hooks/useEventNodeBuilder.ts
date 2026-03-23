/**
 * useEventNodeBuilder Hook
 * 事件节点构建器状态管理Hook
 */

import { useState, useCallback, Dispatch, SetStateAction } from 'react';
import type { Event } from '@shared/types/event-types';

// ============================================
// Type Definitions
// ============================================

/**
 * CanvasField - Unified field type for canvas components
 * Compatible with Field from hql-types
 */
export interface CanvasField {
  id: string;
  /** Field type - using string to allow 'basic' | 'parameter' | 'custom' | 'fixed' for backward compatibility */
  type: 'basic' | 'parameter' | 'custom' | 'fixed';
  name: string;
  displayName?: string;
  alias?: string;
  dataType: string;
  isEditable?: boolean;
  /** Internal field type for HQL generation - maps to FieldType enum */
  fieldType: 'base' | 'param' | 'fixed' | 'custom' | string;
  fieldName?: string;  // 字段名称（与 name 相同，用于兼容性）
  order?: number;
  paramId?: number | null;
  jsonPath?: string | null;
}

/**
 * WhereCondition - Unified WHERE condition type
 * Compatible with WhereCondition from whereBuilder.ts
 */
export interface WhereCondition {
  id: string;
  type: 'condition' | 'group';
  field?: string;
  operator?: string;
  value?: string | number | unknown;
  logicalOp?: 'AND' | 'OR';
  children?: WhereCondition[];
  dataType?: string;
  [key: string]: unknown;
}

export interface NodeConfig {
  nameEn: string;
  nameCn: string;
  description: string;
}

export interface SidebarCollapsed {
  eventSection: boolean;
  paramSection: boolean;
  baseSection: boolean;
  hqlPreviewSection: boolean;
  whereBuilderSection: boolean;
  configSection: boolean;
  statsSection: boolean;
}

// Re-export Event from event-types for convenience
export type { Event } from '@shared/types/event-types';

export interface UseEventNodeBuilderReturn {
  selectedEvent: Event | null;
  setSelectedEvent: Dispatch<SetStateAction<Event | null>>;
  canvasFields: CanvasField[];
  setCanvasFields: Dispatch<SetStateAction<CanvasField[]>>;
  addFieldToCanvas: (
    fieldType: string,
    fieldName: string,
    displayName: string,
    paramId?: number | null,
    jsonPath?: string | null,
    hiveType?: string
  ) => void;
  removeField: (fieldId: string) => void;
  updateField: (fieldId: string, updates: Partial<CanvasField>) => void;
  reorderFields: (newFields: CanvasField[]) => void;
  clearCanvas: () => void;
  whereConditions: WhereCondition[];
  setWhereConditions: Dispatch<SetStateAction<WhereCondition[]>>;
  whereBuilderOpen: boolean;
  setWhereBuilderOpen: Dispatch<SetStateAction<boolean>>;
  addWhereCondition: (condition: Partial<WhereCondition>) => void;
  addWhereGroup: (group: Partial<WhereCondition>) => void;
  removeWhereItem: (id: string) => void;
  updateWhereItem: (id: string, updates: Partial<WhereCondition>) => void;
  clearWhereConditions: () => void;
  reorderWhereConditions: (newConditions: WhereCondition[]) => void;
  nodeConfig: NodeConfig;
  setNodeConfig: Dispatch<SetStateAction<NodeConfig>>;
  sidebarCollapsed: SidebarCollapsed;
  setSidebarCollapsed: Dispatch<SetStateAction<SidebarCollapsed>>;
  toggleSidebarSection: (section: string) => void;
  isEditMode: boolean;
  setIsEditMode: Dispatch<SetStateAction<boolean>>;
  editingConfigId: unknown;
  setEditingConfigId: Dispatch<SetStateAction<unknown>>;
  resetAll: () => void;
}

// ============================================
// Hook Implementation
// ============================================

export function useEventNodeBuilder(gameGid?: number): UseEventNodeBuilderReturn {
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [canvasFields, setCanvasFields] = useState<CanvasField[]>([]);
  const [whereConditions, setWhereConditions] = useState<WhereCondition[]>([]);
  const [whereBuilderOpen, setWhereBuilderOpen] = useState<boolean>(false);
  const [nodeConfig, setNodeConfig] = useState<NodeConfig>({
    nameEn: '',
    nameCn: '',
    description: '',
  });

  const [sidebarCollapsed, setSidebarCollapsed] = useState<SidebarCollapsed>({
    eventSection: false,
    paramSection: false,
    baseSection: true,
    hqlPreviewSection: false,
    whereBuilderSection: true,
    configSection: true,
    statsSection: true,
  });

  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [editingConfigId, setEditingConfigId] = useState<unknown>(null);

  const addFieldToCanvas = useCallback((
    fieldType: string,
    fieldName: string,
    displayName: string,
    paramId: number | null = null,
    jsonPath: string | null = null,
    hiveType?: string
  ) => {
    setCanvasFields(prev => {
      // Support both lowercase (internal) and uppercase (GraphQL enum) values
      const typeMapping: Record<string, string> = {
        // Internal format (lowercase)
        'base': 'basic',
        'param': 'parameter',
        'custom': 'custom',
        'fixed': 'fixed',
        // GraphQL enum format (uppercase)
        'BASE': 'basic',
        'PARAM': 'parameter',
        'CUSTOM': 'custom',
        'FIXED': 'fixed',
        // GraphQL schema field_type values
        'basic': 'basic',
        'parameter': 'parameter',
      };

      // Normalize fieldType to lowercase for internal checks
      const normalizedFieldType = fieldType.toLowerCase();
      const mappedType = typeMapping[fieldType] || typeMapping[normalizedFieldType] || normalizedFieldType;

      // Generate unique ID to avoid duplicate keys causing component crashes
      // Use combination of timestamp + random + field hash
      const uniqueId = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}-${fieldName}`;

      const newField: CanvasField = {
        id: uniqueId,
        type: mappedType as CanvasField['type'],
        name: fieldName,
        displayName,
        alias: fieldName,
        dataType: hiveType || 'STRING',
        isEditable: true,
        fieldType: normalizedFieldType,
        fieldName,
        order: prev.length + 1,
        paramId,
        jsonPath,
      };
      return [...prev, newField];
    });
  }, []);

  const removeField = useCallback((fieldId: string) => {
    setCanvasFields(prev => prev.filter(f => f.id !== fieldId));
  }, []);

  const updateField = useCallback((fieldId: string, updates: Partial<CanvasField>) => {
    setCanvasFields(prev => prev.map(f =>
      f.id === fieldId ? { ...f, ...updates } : f
    ));
  }, []);

  const reorderFields = useCallback((newFields: CanvasField[]) => {
    const reorderedFields = newFields.map((field, index) => ({
      ...field,
      order: index + 1,
    }));
    setCanvasFields(reorderedFields);
  }, []);

  const clearCanvas = useCallback(() => {
    setCanvasFields([]);
    setWhereConditions([]);
  }, []);

  const resetAll = useCallback(() => {
    setSelectedEvent(null);
    setCanvasFields([]);
    setWhereConditions([]);
    setNodeConfig({
      nameEn: '',
      nameCn: '',
      description: '',
    });
    setIsEditMode(false);
    setEditingConfigId(null);
  }, []);

  const addWhereCondition = useCallback((condition: Partial<WhereCondition>) => {
    setWhereConditions(prev => {
      const newCondition: WhereCondition = {
        id: `where-${Date.now()}`,
        type: 'condition',
        ...condition,
        logicalOp: prev.length > 0 ? 'AND' : undefined
      };
      return [...prev, newCondition];
    });
  }, []);

  const addWhereGroup = useCallback((group: Partial<WhereCondition>) => {
    setWhereConditions(prev => {
      const newGroup: WhereCondition = {
        id: `group-${Date.now()}`,
        type: 'group',
        logicalOp: 'AND',
        children: [],
        ...group
      };
      return [...prev, newGroup];
    });
  }, []);

  const removeWhereItem = useCallback((id: string) => {
    setWhereConditions(prev => {
      function removeRecursive(items: WhereCondition[]): WhereCondition[] {
        return items.filter(item => {
          if (item.id === id) return false;
          if (item.type === 'group' && item.children) {
            item.children = removeRecursive(item.children);
          }
          return true;
        });
      }
      return removeRecursive(prev);
    });
  }, []);

  const updateWhereItem = useCallback((id: string, updates: Partial<WhereCondition>) => {
    setWhereConditions(prev => {
      function updateRecursive(items: WhereCondition[]): WhereCondition[] {
        return items.map(item => {
          if (item.id === id) {
            return { ...item, ...updates };
          }
          if (item.type === 'group' && item.children) {
            return {
              ...item,
              children: updateRecursive(item.children)
            };
          }
          return item;
        });
      }
      return updateRecursive(prev);
    });
  }, []);

  const clearWhereConditions = useCallback(() => {
    setWhereConditions([]);
  }, []);

  const reorderWhereConditions = useCallback((newConditions: WhereCondition[]) => {
    setWhereConditions(newConditions);
  }, []);

  const toggleSidebarSection = useCallback((section: string) => {
    setSidebarCollapsed(prev => ({
      ...prev,
      [section]: !prev[section as keyof SidebarCollapsed],
    }));
  }, []);

  return {
    selectedEvent,
    setSelectedEvent,
    canvasFields,
    setCanvasFields,
    addFieldToCanvas,
    removeField,
    updateField,
    reorderFields,
    clearCanvas,
    whereConditions,
    setWhereConditions,
    whereBuilderOpen,
    setWhereBuilderOpen,
    addWhereCondition,
    addWhereGroup,
    removeWhereItem,
    updateWhereItem,
    clearWhereConditions,
    reorderWhereConditions,
    nodeConfig,
    setNodeConfig,
    sidebarCollapsed,
    setSidebarCollapsed,
    toggleSidebarSection,
    isEditMode,
    setIsEditMode,
    editingConfigId,
    setEditingConfigId,
    resetAll,
  };
}
