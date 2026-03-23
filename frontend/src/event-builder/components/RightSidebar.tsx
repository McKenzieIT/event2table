/**
 * RightSidebar Component
 * 右侧栏组件（HQL预览、WHERE条件、统计信息）
 */
import type { CanvasField, WhereCondition } from '@shared/hooks/useEventNodeBuilder';
import React, { memo } from 'react';

import HQLPreviewContainer from './HQLPreviewContainer';
import StatsPanel from './StatsPanel';
import WhereBuilder, { type WhereCondition as BuilderWhereCondition } from './WhereBuilder';

interface EventData {
  id: number;
  event_name?: string;  // 英文事件名
  event_name_cn?: string;  // 中文事件名
  display_name?: string;  // 显示名称
}

interface RightSidebarProps {
  gameGid: number;
  selectedEvent?: EventData | null;
  fields?: CanvasField[];
  whereConditions?: WhereCondition[];
  onWhereConditionsChange: (conditions: WhereCondition[]) => void;
  onShowWhereModal: () => void;
  onShowHQLDetails?: () => void;
}

function RightSidebarInner({
  gameGid,
  selectedEvent = null,
  fields = [],
  whereConditions = [],
  onWhereConditionsChange,
  onShowWhereModal,
  onShowHQLDetails,
}: RightSidebarProps) {
  // Convert CanvasField[] to HQLPreviewContainerField[] format
  const hqlFields = fields.map(f => ({
    paramId: f.paramId ?? undefined,
    fieldName: f.fieldName || f.name || '',
    name: f.name,
    fieldType: f.fieldType,
    type: f.type,
    alias: f.alias,
    jsonPath: f.jsonPath ?? undefined,
  }));

  // Convert WhereCondition to HQLPreviewContainer format
  const hqlWhereConditions = whereConditions.map(c => ({
    id: c.id,
    field: c.field || '',
    operator: c.operator || '=',
    value: c.value,
    logical_operator: c.logicalOp,
  }));

  // Convert WhereCondition to WhereBuilder format (simplified - no nested conditions)
  const builderConditions: BuilderWhereCondition[] = whereConditions.map(c => ({
    id: c.id,
    field: c.field || '',
    operator: c.operator || '=',
    value: c.value,
    logicalOperator: c.logicalOp,
    type: c.type,
  }));

  const handleWhereChange = (conditions: BuilderWhereCondition[]) => {
    const converted: WhereCondition[] = conditions.map(c => ({
      id: c.id,
      type: (c.type || 'condition') as 'condition' | 'group',
      field: c.field,
      operator: c.operator,
      value: c.value,
      logicalOp: c.logicalOperator as 'AND' | 'OR' | undefined,
    }));
    onWhereConditionsChange(converted);
  };

  // Convert CanvasField[] to StatsPanel Field[] format
  const statsFields = fields.map(f => ({
    id: f.id,
    fieldType: f.fieldType as 'base' | 'param' | 'basic' | 'custom' | 'fixed',
    name: f.name,
    alias: f.alias,
    dataType: f.dataType,
  }));

  // Convert WhereCondition to StatsPanel format
  const statsWhereConditions = whereConditions.map(c => ({
    id: c.id,
    field: c.field || '',
    operator: c.operator || '=',
    value: c.value,
  }));

  return (
    <aside className="sidebar-right">
      <HQLPreviewContainer
        gameGid={gameGid}
        event={selectedEvent}
        fields={hqlFields}
        whereConditions={hqlWhereConditions}
        onShowDetails={onShowHQLDetails}
      />
      <WhereBuilder
        conditions={builderConditions}
        onChange={handleWhereChange}
        onOpenModal={onShowWhereModal}
      />
      <StatsPanel
        fields={statsFields}
        whereConditions={statsWhereConditions}
      />
    </aside>
  );
}

export const RightSidebar = memo(RightSidebarInner);