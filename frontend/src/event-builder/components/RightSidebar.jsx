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
  selectedEvent,
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
    name: PropTypes.string.isRequired
  }),
  fields: PropTypes.arrayOf(PropTypes.object),
  whereConditions: PropTypes.arrayOf(PropTypes.object),
  onWhereConditionsChange: PropTypes.func.isRequired,
  onShowWhereModal: PropTypes.func.isRequired,
  onShowHQLDetails: PropTypes.func
};

RightSidebar.defaultProps = {
  fields: [],
  whereConditions: [],
  selectedEvent: null
};
