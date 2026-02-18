/**
 * RightSidebar Component
 * 右侧栏组件（HQL预览、WHERE条件、统计信息）
 */
import React from 'react';
import PropTypes from 'prop-types';
import HQLPreviewContainer from './HQLPreviewContainer';
import WhereBuilder from './WhereBuilder';
import StatsPanel from './StatsPanel';

export default function RightSidebar({
  gameGid,
  selectedEvent = null,
  fields = [],
  whereConditions = [],
  onWhereConditionsChange,
  onShowWhereModal,
  onShowHQLDetails,
}) {
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

RightSidebar.propTypes = {
  gameGid: PropTypes.number.isRequired,
  selectedEvent: PropTypes.shape({
    id: PropTypes.number.isRequired,
    event_name: PropTypes.string,  // 英文事件名
    event_name_cn: PropTypes.string,  // 中文事件名
    display_name: PropTypes.string,  // 显示名称
  }),
  fields: PropTypes.arrayOf(PropTypes.object),
  whereConditions: PropTypes.arrayOf(PropTypes.object),
  onWhereConditionsChange: PropTypes.func.isRequired,
  onShowWhereModal: PropTypes.func.isRequired,
  onShowHQLDetails: PropTypes.func
};
