// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * HQLPreviewContainer Component
 * HQL预览容器组件 - 连接API和HQLPreview组件
 *
 * @description
 * 负责管理HQL生成的业务逻辑：
 * - 调用API生成HQL
 * - 管理加载状态和错误处理
 * - 处理字段和条件的变化
 * - 支持view/procedure/custom三种模式
 *
 * @module HQLPreviewContainer
 */

import React, { useState, useEffect, useCallback } from 'react';
import { previewHQL } from '@shared/api/eventNodeBuilder';
import type { Event, WhereCondition } from '@shared/api/eventNodeBuilderApi';
import HQLPreview from './HQLPreview';

// ============================================
// Type Definitions
// ============================================

/**
 * HQL预览容器专用的字段配置接口
 */
export interface HQLPreviewContainerField {
  /** 参数ID */
  paramId?: number;
  /** 字段名称 */
  fieldName: string;
  /** 字段显示名称（备选） */
  name?: string;
  /** 字段类型 */
  fieldType?: string;
  /** 字段类型（备选） */
  type?: string;
  /** 聚合函数 */
  aggregateFunc?: string;
  /** 是否为主键 */
  isPrimary?: boolean;
  /** 字段别名 */
  alias?: string;
  /** JSON路径 */
  jsonPath?: string;
}

/**
 * API请求字段配置
 */
interface APIField {
  param_id?: number;
  field_name: string;
  field_type: string;
  aggregate_func?: string;
  is_primary?: boolean;
  alias?: string;
  json_path?: string;
}

/**
 * 过滤条件字典
 */
interface FilterConditionsDict {
  custom_where: string;
  conditions: WhereCondition[];
}

/**
 * HQL预览请求数据
 */
interface HQLPreviewRequestData {
  game_gid: number;
  event_id: number;
  fields: APIField[];
  filter_conditions: FilterConditionsDict;
  sql_mode: string;
}

/**
 * SQL模式类型
 */
export type SQLMode = 'view' | 'procedure' | 'custom';

/**
 * 组件Props接口
 */
export interface HQLPreviewContainerProps {
  /** 游戏GID */
  gameGid: number;
  /** 事件对象 */
  event: Event | null;
  /** 字段列表 */
  fields: HQLPreviewContainerField[];
  /** 字段数组 */
  fields?: Field[];
  /** WHERE条件数组 */
  whereConditions?: WhereCondition[];
  /** 显示详情回调 */
  onShowDetails?: () => void;
}

// ============================================
// Component Implementation
// ============================================

/**
 * HQL预览容器组件
 *
 * @param props - 组件属性
 * @returns HQLPreview组件
 *
 * @example
 * ```tsx
 * <HQLPreviewContainer
 *   gameGid={10000147}
 *   event={selectedEvent}
 *   fields={fields}
 *   whereConditions={conditions}
 *   onShowDetails={() => setShowModal(true)}
 * />
 * ```
 */
const HQLPreviewContainer = React.memo(function HQLPreviewContainer({
  gameGid,
  event,
  fields = [],
  whereConditions = [],
  onShowDetails
}: HQLPreviewContainerProps): React.ReactElement {
  // ============================================
  // State Management
  // ============================================

  const [hqlContent, setHqlContent] = useState<string>('');
  const [sqlMode, setSqlMode] = useState<SQLMode>('view');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // ============================================
  // HQL Generation
  // ============================================

  /**
   * 生成HQL的核心逻辑
   */
  const generateHQLInternal = useCallback(async (): Promise<void> => {
    // Enhanced validation
    if (!gameGid) {
      console.warn('[HQLPreviewContainer] Missing gameGid');
      return;
    }

    if (!event || !event.id) {
      // 这是正常的初始状态，不需要显示为错误
      setHqlContent('-- 请选择事件');
      return;
    }

    if (!fields || fields.length === 0) {
      setHqlContent('-- 请添加字段');
      return;
    }

    // Debug logging
    
    setIsLoading(true);
    setError(null);

    try {
      // 转换 whereConditions 数组为后端期望的格式
      const filterConditionsDict: FilterConditionsDict = {
        custom_where: (whereConditions || []).length > 0
          ? (whereConditions || []).map(c => `${c.field || ''} ${c.operator || '='} '${c.value || ''}'`).join(' AND ')
          : '',
        conditions: whereConditions || []
      };

      // 转换字段为API期望的格式
      const apiFields: APIField[] = (fields || [])
        .map((f): APIField | null => ({
          param_id: f.paramId,
          field_name: f.fieldName || f.name || '',
          field_type: f.fieldType === 'basic' ? 'base' : (f.fieldType || f.type || 'base'),
          aggregate_func: f.aggregateFunc || '',
          is_primary: f.isPrimary || false,
          alias: f.alias || f.fieldName,
          json_path: f.jsonPath || f.jsonPath
        }))
        .filter((f): f is APIField => f !== null && f.field_name !== '');

      const requestData: HQLPreviewRequestData = {
        game_gid: typeof gameGid === 'string' ? parseInt(gameGid, 10) : gameGid,
        event_id: event.id,
        fields: apiFields,
        filter_conditions: filterConditionsDict,
        sql_mode: sqlMode
      };

      const result = await previewHQL(requestData);

      // previewHQL返回response.data，可能是HQL字符串或包含hql字段的对象
      if (typeof result === 'string') {
        // 后端直接返回HQL字符串
        setHqlContent(result);
      } else if (result.hql) {
        // 后端返回包含hql字段的对象
        setHqlContent(result.hql);
      } else {
        throw new Error(result.error || '生成HQL失败');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('[HQLPreviewContainer] Failed to generate HQL:', err);
      setError(errorMessage);
      setHqlContent(`-- 错误: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  }, [gameGid, event, fields, whereConditions, sqlMode]);

  // ============================================
  // Effects
  // ============================================

  /**
   * 当事件、字段、条件或模式变化时重新生成HQL
   */
  useEffect(() => {
    generateHQLInternal();
  }, [generateHQLInternal]);

  // ============================================
  // Event Handlers
  // ============================================

  /**
   * 处理SQL模式切换
   */
  const handleModeChange = useCallback((newMode: SQLMode): void => {
    setSqlMode(newMode);
  }, []);

  /**
   * 处理内容变化
   */
  const handleContentChange = useCallback((newContent: string): void => {
    setHqlContent(newContent);
  }, []);

  // ============================================
  // Render
  // ============================================

  return (
    <HQLPreview
      hqlContent={hqlContent}
      sqlMode={sqlMode}
      onModeChange={handleModeChange}
      onContentChange={handleContentChange}
      readOnly={true}  // ✅ 在事件节点构建器中隐藏View/Procedure按钮
      fields={fields}
      isLoading={isLoading}
      onShowDetails={onShowDetails}
    />
  );
});

HQLPreviewContainer.displayName = 'HQLPreviewContainer';

export default HQLPreviewContainer;

// ============================================
// Export Types
// ============================================

// Types are already exported above with their declarations
