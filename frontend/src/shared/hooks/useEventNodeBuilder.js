/**
 * useEventNodeBuilder Hook
 * 事件节点构建器状态管理Hook
 *
 * @param {number} gameGid - 游戏GID
 * @returns {Object} 状态和操作函数
 */
import { useState, useCallback } from 'react';

export function useEventNodeBuilder(gameGid) {
  // ===== 事件选择 =====
  const [selectedEvent, setSelectedEvent] = useState(null);

  // ===== 画布字段 =====
  const [canvasFields, setCanvasFields] = useState([]);

  // ===== WHERE条件 =====
  const [whereConditions, setWhereConditions] = useState([]);
  const [whereBuilderOpen, setWhereBuilderOpen] = useState(false);

  // ===== 节点配置 =====
  const [nodeConfig, setNodeConfig] = useState({
    nameEn: '',
    nameCn: '',
    description: '',
  });

  // ===== UI状态 =====
  const [sidebarCollapsed, setSidebarCollapsed] = useState({
    eventSection: false,
    paramSection: false,
    baseSection: true,
    hqlPreviewSection: false,
    whereBuilderSection: true,
    configSection: true,
    statsSection: true,
  });

  // ===== 编辑模式 =====
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingConfigId, setEditingConfigId] = useState(null);

  // ===== 操作函数 =====

  /**
   * 添加字段到画布
   * @param {string} fieldType - 字段类型 (base/param)
   * @param {string} fieldName - 字段名
   * @param {string} displayName - 显示名称
   * @param {number|null} paramId - 参数ID（可选）
   * @param {string|null} jsonPath - JSON路径（用于param类型）
   */
  const addFieldToCanvas = useCallback((fieldType, fieldName, displayName, paramId = null, jsonPath = null) => {
    setCanvasFields(prev => {
      // Map field types for UI and API compatibility
      // FieldCanvas UI expects: type = 'basic'|'parameter'|'custom'|'fixed'
      // Backend API expects: fieldType = 'base'|'param'|'custom'|'fixed'
      const typeMapping = {
        'base': 'basic',       // UI: 'basic', API: 'base'
        'param': 'parameter',  // UI: 'parameter', API: 'param'
        'custom': 'custom',    // Both: 'custom'
        'fixed': 'fixed'       // Both: 'fixed'
      };

      const newField = {
        id: String(Date.now()),  // Convert to string to match FieldCanvas PropTypes
        type: typeMapping[fieldType] || fieldType,  // FieldCanvas expects mapped 'type'
        name: fieldName,  // FieldCanvas expects 'name' not 'fieldName'
        displayName,  // Human-readable name
        alias: fieldName,
        dataType: fieldType === 'param' ? 'STRING' : 'UNKNOWN',  // FieldCanvas requires dataType
        isEditable: true,
        // Keep original fieldType for backend API compatibility
        fieldType,  // Backend expects: 'base', 'param', 'custom', 'fixed'
        fieldName,
        order: prev.length + 1,
        paramId,  // Keep as number (valid type)
        jsonPath,  // Add jsonPath for param type fields
      };
      return [...prev, newField];
    });
  }, []);

  /**
   * 从画布移除字段
   * @param {number} fieldId - 字段ID
   */
  const removeField = useCallback((fieldId) => {
    setCanvasFields(prev => prev.filter(f => f.id !== fieldId));
  }, []);

  /**
   * 更新字段
   * @param {number} fieldId - 字段ID
   * @param {Object} updates - 更新数据
   */
  const updateField = useCallback((fieldId, updates) => {
    setCanvasFields(prev => prev.map(f =>
      f.id === fieldId ? { ...f, ...updates } : f
    ));
  }, []);

  /**
   * 重新排序字段
   * @param {Array} newFields - 新的字段数组
   */
  const reorderFields = useCallback((newFields) => {
    const reorderedFields = newFields.map((field, index) => ({
      ...field,
      order: index + 1,
    }));
    setCanvasFields(reorderedFields);
  }, []);

  /**
   * 清空画布
   */
  const clearCanvas = useCallback(() => {
    setCanvasFields([]);
    setWhereConditions([]);
  }, []);

  /**
   * 重置所有状态
   */
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

  // ===== WHERE条件操作函数 =====

  /**
   * 添加WHERE条件
   * @param {Object} condition - WHERE条件对象
   */
  const addWhereCondition = useCallback((condition) => {
    setWhereConditions(prev => {
      const newCondition = {
        id: `where-${Date.now()}`,
        type: 'condition',
        ...condition,
        logicalOp: prev.length > 0 ? 'AND' : undefined
      };
      return [...prev, newCondition];
    });
  }, []);

  /**
   * 添加WHERE分组
   * @param {Object} group - WHERE分组对象
   */
  const addWhereGroup = useCallback((group) => {
    setWhereConditions(prev => {
      const newGroup = {
        id: `group-${Date.now()}`,
        type: 'group',
        logicalOp: 'AND',
        children: [],
        ...group
      };
      return [...prev, newGroup];
    });
  }, []);

  /**
   * 移除WHERE项
   * @param {string} id - WHERE项ID
   */
  const removeWhereItem = useCallback((id) => {
    setWhereConditions(prev => {
      function removeRecursive(items) {
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

  /**
   * 更新WHERE项
   * @param {string} id - WHERE项ID
   * @param {Object} updates - 更新数据
   */
  const updateWhereItem = useCallback((id, updates) => {
    setWhereConditions(prev => {
      function updateRecursive(items) {
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

  /**
   * 清空WHERE条件
   */
  const clearWhereConditions = useCallback(() => {
    setWhereConditions([]);
  }, []);

  /**
   * 重新排序WHERE项
   * @param {WhereItem[]} newConditions - 新的WHERE项数组
   */
  const reorderWhereConditions = useCallback((newConditions) => {
    setWhereConditions(newConditions);
  }, []);

  /**
   * 切换侧边栏折叠状态
   * @param {string} section - 区块名称
   */
  const toggleSidebarSection = useCallback((section) => {
    setSidebarCollapsed(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);

  return {
    // 事件选择
    selectedEvent,
    setSelectedEvent,

    // 画布字段
    canvasFields,
    setCanvasFields,
    addFieldToCanvas,
    removeField,
    updateField,
    reorderFields,
    clearCanvas,

    // WHERE条件
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

    // 节点配置
    nodeConfig,
    setNodeConfig,

    // UI状态
    sidebarCollapsed,
    setSidebarCollapsed,
    toggleSidebarSection,

    // 编辑模式
    isEditMode,
    setIsEditMode,
    editingConfigId,
    setEditingConfigId,

    // 重置
    resetAll,
  };
}
