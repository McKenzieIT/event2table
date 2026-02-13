// dwd_generator/static/js/react-app-shell/src/components/sidebar/SidebarMenuItem.jsx
import { NavLink } from 'react-router-dom';

export function SidebarMenuItem({ item, isSidebarCollapsed, currentGame, routesRequiringGameContext = [] }) {
  // 动态构建路径：如果路由需要游戏上下文且有选中的游戏，添加 game_gid 参数
  const getPath = () => {
    if (routesRequiringGameContext.includes(item.path) && currentGame?.gid) {
      return `${item.path}?game_gid=${currentGame.gid}`;
    }
    return item.path;
  };

  return (
    <li className="sidebar-menu-item">
      <NavLink
        to={getPath()}
        className={({ isActive }) => `sidebar-menu-link ${isActive ? 'active' : ''}`}
        data-tooltip={isSidebarCollapsed ? item.tooltip || item.label : undefined}
      >
        <i className={`bi ${item.icon} sidebar-menu-icon`}></i>
        <span className="sidebar-menu-text">{item.label}</span>
      </NavLink>
    </li>
  );
}
