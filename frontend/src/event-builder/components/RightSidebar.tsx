/**
 * RightSidebar Component
 * 右侧栏组件（HQL预览、WHERE条件、统计信息）
 */
import React from 'react';
import HQLPreviewContainer from './HQLPreviewContainer';
import WhereBuilder from './WhereBuilder';
import StatsPanel from './StatsPanel';

interface EventData {
  id: number;
  event_name?: string;  // 英文事件名
  event_name_cn?: string;  // 中文事件名
  display_name?: string;  // 显示名称
}

type FieldType = 'base' | 'param' | 'basic' | 'custom' | 'fixed';

interface Field {
  id: string;
  fieldType: FieldType;
  name: string;
  fieldName?: string;
  displayName?: string;
  alias?: string;
  dataType: string;
}

interface WhereCondition {
  id: string;
  field: string;
  operator: string;
  value: unknown;
}

interface RightSidebarProps {
  gameGid: number;
  selectedEvent?: EventData | null;
  fields?: Field[];
  whereConditions?: WhereCondition[];
  onWhereConditionsChange: (conditions: WhereCondition[]) => void;
  onShowWhereModal: () => void;
  onShowHQLDetails?: () => void;
}

export default function RightSidebar({
  gameGid,
  selectedEvent = null,
  fields = [],
  whereConditions = [],
  onWhereConditionsChange,
  onShowWhereModal,
  onShowHQLDetails,
}: RightSidebarProps) {
  return (
    <aside className="sidebar-right">
      <HQLPreviewContainer
        gameGid={gameGid}
        event={selectedEvent}
        fields={fields}
        whereConditions={whereConditions}
        onShowDetails={onShowHQLDetails}
      />
      <WhereBuilder
        conditions={whereConditions}
        onChange={onWhereConditionsChange}
        onOpenModal={onShowWhereModal}
      />
      <StatsPanel
        fields={fields}
        whereConditions={whereConditions}
      />
    </aside>
  );
}
