// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import { ReactNode } from 'react';
import './SidebarGroup.css';

export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  path?: string;
  shortLabel?: string;
  tooltip?: string;
  children?: MenuItem[];
}

export interface MenuGroup {
  id: string;
  title: string;
  defaultExpanded?: boolean;
  items: MenuItem[];
}

interface SidebarGroupProps {
  group: MenuGroup;
  isSidebarCollapsed: boolean;
  isExpanded: boolean;
  onToggle: (groupId: string, newState: boolean) => void;
  children: ReactNode;
}

export function SidebarGroup({
  group,
  isSidebarCollapsed,
  isExpanded,
  onToggle,
  children
}: SidebarGroupProps): React.JSX.Element {
  const handleToggle = (): void => {
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
