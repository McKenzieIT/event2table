/**
 * LeftSidebar Component
 * 左侧栏组件（事件选择、参数字段）
 * 优化：移除BaseFieldsList，释放空间给ParamSelector
 */
import React from 'react';
import EventSelector from './EventSelector';
import ParamSelector from './ParamSelector';

export default function LeftSidebar({
  gameGid,
  selectedEvent,
  onEventSelect,
  onAddField,
}) {
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
