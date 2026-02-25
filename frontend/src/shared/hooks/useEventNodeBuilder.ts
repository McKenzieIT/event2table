/**
 * useEventNodeBuilder Hook
 * 事件节点构建器状态管理Hook
 */

import { useState, useCallback, Dispatch, SetStateAction } from 'react';

// ============================================
// Type Definitions
// ============================================

export interface CanvasField {
  id: string;
  type: 'basic' | 'parameter' | 'custom' | 'fixed';
  name: string;
  displayName: string;
  alias: string;
  dataType: string;
  isEditable: boolean;
  fieldType: string;
  order: number;
  paramId?: number | null;
  jsonPath?: string | null;
}

export interface WhereCondition {
  id: string;
  type: 'condition' | 'group';
  field?: string;
  operator?: string;
  value?: string;
  logicalOp?: string;
  children?: WhereCondition[];
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

export interface UseEventNodeBuilderReturn {
  selectedEvent: unknown;
  setSelectedEvent: Dispatch<SetStateAction<unknown>>;
  canvasFields: CanvasField[];
  setCanvasFields: Dispatch<SetStateAction<CanvasField[]>>;
  addFieldToCanvas: (
    fieldType: string,
    fieldName: string,
    displayName: string,
    paramId?: number | null,
    jsonPath?: string | null
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
  const [selectedEvent, setSelectedEvent] = useState<unknown>(null);
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
    jsonPath: string | null = null
  ) => {
    setCanvasFields(prev => {
      const typeMapping: Record<string, string> = {
        'base': 'basic',
        'param': 'parameter',
        'custom': 'custom',
        'fixed': 'fixed'
      };

      const newField: CanvasField = {
        id: String(Date.now()),
        type: (typeMapping[fieldType] || fieldType) as CanvasField['type'],
        name: fieldName,
        displayName,
        alias: fieldName,
        dataType: fieldType === 'param' ? 'STRING' : 'UNKNOWN',
        isEditable: true,
        fieldType,
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
