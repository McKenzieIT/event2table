// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import { SIDEBAR_GROUPS, GAME_CHIP_CONFIG } from '@shared/config/sidebarConfig';
import { useSidebar } from '@shared/hooks/useSidebar';
import { useEffect, useRef } from 'react';

import { useGameStore } from '../../../stores/gameStore';

import { SidebarGroup } from './SidebarGroup';
import { SidebarMenuItemMemo } from './SidebarMenuItem';
import './Sidebar.css';

interface GameData {
  id: number;
  gid: number;
  name: string;
  ods_db?: string;
}

export function Sidebar(): React.JSX.Element {
  const {
    collapsed,
    groupStates,
    toggleCollapsed,
    toggleGroup,
    collapseAllGroups
  } = useSidebar();

  const sidebarRef = useRef<HTMLDivElement>(null);
  const { openGameManagementModal } = useGameStore();
  const { currentGame } = useGameStore();

  // Routes that require game context (these routes will dynamically add game_gid parameter)
  const routesRequiringGameContext: string[] = [
    '/event-node-builder',
    '/event-nodes',
    '/events',
    '/canvas',
    '/parameters',
    '/categories',
    '/common-params',
    '/flows'
  ];

  // Responsive handling: collapse by default on small screens
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const screenWidth = window.innerWidth;
        if (screenWidth < 768 && !collapsed) {
          toggleCollapsed();
        }
      }, 100);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', handleResize);
    };
  }, [collapsed, toggleCollapsed]);

  // Keyboard shortcut support
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
        event.preventDefault();
        toggleCollapsed();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [toggleCollapsed]);

  // Initialize group states (using configured defaults)
  useEffect(() => {
    const initialState: Record<string, boolean> = {};
    SIDEBAR_GROUPS.forEach(group => {
      initialState[group.id] = group.defaultExpanded ?? true;
    });

    // Only set on first load if localStorage is empty
    const hasSavedState = localStorage.getItem('sidebarGroupStates');
    if (!hasSavedState) {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(initialState));
    }
  }, []);

  // Handle game selection click
  const handleGameChipClick = (): void => {
    // Trigger game selection modal (needs integration with global game selection system)
    const event = new CustomEvent('toggleGameSheet');
    window.dispatchEvent(event);
  };

  // Handle game management click
  const handleGameManagementClick = (): void => {
    openGameManagementModal();
  };

  return (
    <aside
      ref={sidebarRef}
      className={`sidebar ${collapsed ? 'collapsed' : ''}`}
      id="sidebar"
    >
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <a href="/react-app-shell#/" className="sidebar-brand">
          <i className="bi bi-database-fill sidebar-brand-icon"></i>
          <span className="sidebar-brand-text">Event2Table</span>
        </a>
        <button
          className="sidebar-toggle"
          onClick={toggleCollapsed}
          aria-label={collapsed ? "展开侧边栏" : "折叠侧边栏"}
          title={collapsed ? "展开侧边栏" : "折叠侧边栏"}
        >
          {collapsed ? (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M10 4l-4 4 4 4" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      </div>

      {/* Sidebar Content */}
      <div className="sidebar-content">
        {SIDEBAR_GROUPS.map((group) => (
          <SidebarGroup
            key={group.id}
            group={group}
            isSidebarCollapsed={collapsed}
            isExpanded={groupStates[group.id] ?? group.defaultExpanded ?? true}
            onToggle={toggleGroup}
          >
            {group.items.map((item) => (
              <SidebarMenuItemMemo
                key={item.id}
                item={item}
                isSidebarCollapsed={collapsed}
                currentGame={currentGame}
                routesRequiringGameContext={routesRequiringGameContext}
              />
            ))}
          </SidebarGroup>
        ))}
      </div>

      {/* Sidebar Footer - Game Selection */}
      <div className="sidebar-footer">
        <button
          className="game-chip-sidebar"
          onClick={handleGameChipClick}
          aria-label="切换游戏"
        >
          <div className="game-chip-sidebar-content">
            <i className={`bi ${GAME_CHIP_CONFIG.icon} game-chip-sidebar-icon`}></i>
            <span className="game-chip-sidebar-text">
              {collapsed && GAME_CHIP_CONFIG.shortLabel
                ? GAME_CHIP_CONFIG.shortLabel
                : (currentGame?.name || '选择游戏')}
            </span>
          </div>
          <i className="bi bi-chevron-down game-chip-sidebar-chevron"></i>
        </button>

        {/* Game Management Button */}
        <button
          className="game-management-btn"
          onClick={handleGameManagementClick}
          aria-label="游戏管理"
          title="游戏管理"
        >
          <div className="game-management-btn-content">
            <i className="bi bi-gear game-management-btn-icon"></i>
            <span className="game-management-btn-text">
              {collapsed ? '管理' : '游戏管理'}
            </span>
          </div>
        </button>
      </div>
    </aside>
  );
}
