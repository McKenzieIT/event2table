import { useEffect, useRef, useState } from 'react';
import { useSidebar } from '@shared/hooks/useSidebar';
import { SIDEBAR_GROUPS, GAME_CHIP_CONFIG } from '@shared/config/sidebarConfig';
import { SidebarGroup } from './SidebarGroup';
import { SidebarMenuItem } from './SidebarMenuItem';
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
  const [currentGame, setCurrentGame] = useState({
    id: null,
    name: GAME_CHIP_CONFIG.defaultText,
    gid: null
  });

  // 需要游戏上下文的路由（这些路由会动态添加 game_gid 参数）
  const routesRequiringGameContext = ['/event-node-builder', '/canvas'];

  // 响应式处理：小屏幕默认折叠
  useEffect(() => {
    const handleResize = () => {
      const screenWidth = window.innerWidth;
      if (screenWidth < 768 && !collapsed) {
        toggleCollapsed();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
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

  // 加载当前游戏信息
  useEffect(() => {
    const loadCurrentGame = () => {
      const gameId = localStorage.getItem('selectedGameId');
      const gameName = localStorage.getItem('selectedGameName');
      const gameGid = localStorage.getItem('selectedGameGid');

      if (gameId && gameName && gameGid) {
        setCurrentGame({
          id: gameId,
          name: gameName,
          gid: gameGid
        });
      }
    };

    loadCurrentGame();

    // 监听游戏切换事件
    const handleGameChange = () => {
      loadCurrentGame();
    };

    window.addEventListener('gameChanged', handleGameChange);
    return () => window.removeEventListener('gameChanged', handleGameChange);
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
          <span className="sidebar-brand-text">DWD Generator</span>
        </a>
        <button
          className="sidebar-toggle"
          onClick={toggleCollapsed}
          aria-label="切换侧边栏"
          title={collapsed ? "展开侧边栏" : "折叠侧边栏"}
        >
          <i className={`bi bi-chevron-${collapsed ? 'right' : 'left'}`}></i>
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
              <SidebarMenuItem
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
              {currentGame.name}
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
            <span className="game-management-btn-text">游戏管理</span>
          </div>
        </button>
      </div>
    </aside>
  );
}
