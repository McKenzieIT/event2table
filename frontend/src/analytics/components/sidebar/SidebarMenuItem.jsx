// dwd_generator/static/js/react-app-shell/src/components/sidebar/SidebarMenuItem.jsx
import { memo, useCallback } from 'react';
import { NavLink } from 'react-router-dom';

// FIX 1.1: 使用React.memo优化避免不必要的重渲染
function SidebarMenuItem({ item, isSidebarCollapsed, currentGame, routesRequiringGameContext = [] }) {
  // 动态构建路径：如果路由需要游戏上下文且有选中的游戏，添加 game_gid 参数
  const getPath = useCallback(() => {
    if (routesRequiringGameContext.includes(item.path) && currentGame?.gid) {
      return `${item.path}?game_gid=${currentGame.gid}`;
    }
    return item.path;
  }, [item.path, currentGame?.gid, routesRequiringGameContext]);

  // 使用短标签（折叠状态）或完整标签（展开状态）
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

// 使用memo包装，并定义比较函数
export const SidebarMenuItemMemo = memo(SidebarMenuItem, (prevProps, nextProps) => {
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.item.path === nextProps.item.path &&
    prevProps.item.label === nextProps.item.label &&
    prevProps.isSidebarCollapsed === nextProps.isSidebarCollapsed &&
    prevProps.currentGame?.gid === nextProps.currentGame?.gid
  );
});
