// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * LeftSidebar Component
 * 左侧栏组件（事件选择、参数字段）
 * 优化：移除BaseFieldsList，释放空间给ParamSelector
 */
import React from 'react';
import EventSelector from './EventSelector';
import ParamSelector from './ParamSelector';
import type { Event } from '@/shared/types/event-types';

/**
 * 组件Props接口
 */
export interface LeftSidebarProps {
  gameGid: number;
  selectedEvent?: Event | null;
  onEventSelect: (event: Event) => void;
  onAddField: (fieldType: string, fieldName: string, displayName: string, paramId?: number, jsonPath?: string) => void;
}

/**
 * LeftSidebar Component
 */
export function LeftSidebar({
  gameGid,
  selectedEvent,
  onEventSelect,
  onAddField,
}: LeftSidebarProps) {
  return (
    <aside className="sidebar-left optimized">
      <div className="sidebar-section--event">
        <EventSelector
          gameGid={gameGid}
          selectedEvent={selectedEvent}
          onSelect={onEventSelect}
        />
      </div>
      <div className="sidebar-section--params">
        <ParamSelector
          eventId={selectedEvent?.id}
          onAddField={onAddField}
          disabled={!selectedEvent}
        />
      </div>
    </aside>
  );
}
