// dwd_generator/static/js/react-app-shell/src/components/sidebar/SidebarGroup.jsx
import { useState } from 'react';
import './SidebarGroup.css';

export function SidebarGroup({ group, isSidebarCollapsed, isExpanded, onToggle, children }) {
  const handleToggle = () => {
    const newState = !isExpanded;
    onToggle(group.id, newState);
  };

  return (
    <div className={`menu-group ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <button
        className="menu-group-header"
        onClick={handleToggle}
        aria-expanded={isExpanded}
        aria-label={`切换 ${group.title} 分组`}
      >
        <span className="menu-group-title">{group.title}</span>
        <span className="menu-group-icon">▼</span>
      </button>
      <div className="menu-group-content">
        <div className="sidebar-group">
          <ul className="sidebar-menu">
            {children}
          </ul>
        </div>
      </div>
    </div>
  );
}
