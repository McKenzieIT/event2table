import { useEffect, useRef } from 'react';
import { useSidebar } from '@shared/hooks/useSidebar';
import { SIDEBAR_GROUPS, GAME_CHIP_CONFIG } from '@shared/config/sidebarConfig';
import { SidebarGroup } from './SidebarGroup';
import { SidebarMenuItemMemo } from './SidebarMenuItem';
import { useGameStore } from '../../../stores/gameStore';
import './Sidebar.css';

export function Sidebar() {
  const {
    collapsed,
    groupStates,
    toggleCollapsed,
    toggleGroup,
    collapseAllGroups
  } = useSidebar();

  const sidebarRef = useRef(null);
  const { openGameManagementModal } = useGameStore();
  const { currentGame, setCurrentGame } = useGameStore();

  // 需要游戏上下文的路由（这些路由会动态添加 game_gid 参数）
  const routesRequiringGameContext = [
    '/event-node-builder',
    '/event-nodes',
    '/events',
    '/canvas',
    '/parameters',
    '/categories',
    '/common-params',
    '/flows'
  ];

  // 响应式处理：小屏幕默认折叠
  useEffect(() => {
    let timeoutId;
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

  // 键盘快捷键支持
  useEffect(() => {
    const handleKeyPress = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
        event.preventDefault();
        toggleCollapsed();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [toggleCollapsed]);

  // 初始化分组状态（使用配置的默认值）
  useEffect(() => {
    const initialState = {};
    SIDEBAR_GROUPS.forEach(group => {
      initialState[group.id] = group.defaultExpanded ?? true;
    });

    // 只在首次加载时设置（如果 localStorage 为空）
    const hasSavedState = localStorage.getItem('sidebarGroupStates');
    if (!hasSavedState) {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(initialState));
    }
  }, []);

  // 处理游戏选择点击
  const handleGameChipClick = () => {
    // 触发游戏选择模态框（需要与全局游戏选择系统集成）
    const event = new CustomEvent('toggleGameSheet');
    window.dispatchEvent(event);
  };

  // 处理游戏管理点击
  const handleGameManagementClick = () => {
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
