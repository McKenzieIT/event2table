/**
 * LeftSidebar Component
 * 左侧栏组件（事件选择、参数字段、基础字段）
 */
import React from 'react';
import EventSelector from './EventSelector';
import ParamSelector from './ParamSelector';
import BaseFieldsList from './BaseFieldsList';

export default function LeftSidebar({
  gameGid,
  selectedEvent,
  onEventSelect,
  onAddField,
}) {
  return (
    <aside className="sidebar-left">
      <EventSelector
        gameGid={gameGid}
        selectedEvent={selectedEvent}
        onSelect={onEventSelect}
      />
      <ParamSelector
        eventId={selectedEvent?.id}
        onAddField={onAddField}
        disabled={!selectedEvent}
      />
      <BaseFieldsList onAddField={onAddField} />
    </aside>
  );
}
