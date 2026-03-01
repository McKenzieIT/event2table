import { memo, useCallback } from 'react';
import { NavLink } from 'react-router-dom';

export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  path?: string;
  shortLabel?: string;
  tooltip?: string;
  children?: MenuItem[];
}

export interface GameData {
  id: number;
  gid: number;
  name: string;
  ods_db?: string;
}

interface SidebarMenuItemProps {
  item: MenuItem;
  isSidebarCollapsed: boolean;
  currentGame?: GameData | null;
  routesRequiringGameContext?: string[];
}

// FIX 1.1: Use React.memo to optimize and avoid unnecessary re-renders
function SidebarMenuItem({
  item,
  isSidebarCollapsed,
  currentGame,
  routesRequiringGameContext = []
}: SidebarMenuItemProps): React.JSX.Element {
  // Dynamically build path: if route requires game context and a game is selected, add game_gid parameter
  const getPath = useCallback((): string => {
    if (routesRequiringGameContext.includes(item.path || '') && currentGame?.gid) {
      return `${item.path}?game_gid=${currentGame.gid}`;
    }
    return item.path || '';
  }, [item.path, currentGame?.gid, routesRequiringGameContext]);

  // Use short label (collapsed state) or full label (expanded state)
  const displayLabel = isSidebarCollapsed && item.shortLabel ? item.shortLabel : item.label;

  return (
    <li className="sidebar-menu-item">
      <NavLink
        to={getPath()}
        className={({ isActive }) => `sidebar-menu-link ${isActive ? 'active' : ''}`}
        data-tooltip={isSidebarCollapsed ? item.tooltip || item.label : undefined}
      >
        <i className={`bi ${item.icon} sidebar-menu-icon`}></i>
        <span className="sidebar-menu-text">{displayLabel}</span>
      </NavLink>
    </li>
  );
}

// Wrap with memo and define comparison function
export const SidebarMenuItemMemo = memo(SidebarMenuItem, (prevProps, nextProps) => {
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.item.path === nextProps.item.path &&
    prevProps.item.label === nextProps.item.label &&
    prevProps.isSidebarCollapsed === nextProps.isSidebarCollapsed &&
    prevProps.currentGame?.gid === nextProps.currentGame?.gid
  );
});
