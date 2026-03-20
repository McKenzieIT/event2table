import { useUserStore } from '../userStore';

/**
 * 用户状态Hook
 * 
 * 提供类型安全的用户状态访问和操作
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { user, isAuthenticated, hasPermission, logout } = useUserStore();
 *   
 *   if (!isAuthenticated) {
 *     return <Login />;
 *   }
 *   
 *   if (!hasPermission('event:write')) {
 *     return <AccessDenied />;
 *   }
 *   
 *   return <div>欢迎, {user?.username}</div>;
 * }
 * ```
 */
export function useUserStore() {
  const store = useUserStore();
  
  return {
    // 用户信息
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    
    // 权限和角色
    permissions: store.permissions,
    roles: store.roles,
    
    // 用户操作
    setUser: store.setUser,
    updateUser: store.updateUser,
    
    // 认证操作
    login: store.login,
    logout: store.logout,
    
    // 权限检查
    hasPermission: store.hasPermission,
    hasAnyPermission: store.hasAnyPermission,
    hasAllPermissions: store.hasAllPermissions,
    hasRole: store.hasRole,
    hasAnyRole: store.hasAnyRole,
    
    // 权限和角色管理
    setPermissions: store.setPermissions,
    setRoles: store.setRoles,
    addPermission: store.addPermission,
    removePermission: store.removePermission,
    addRole: store.addRole,
    removeRole: store.removeRole,
    
    // 重置
    resetUserState: store.resetUserState,
  };
}

/**
 * 用户信息Hook - 只关注用户基本信息
 */
export function useUserInfo() {
  const { user, isAuthenticated, setUser, updateUser } = useUserStore();
  return { user, isAuthenticated, setUser, updateUser };
}

/**
 * 权限Hook - 只关注权限相关功能
 */
export function usePermissions() {
  const {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    addPermission,
    removePermission,
  } = useUserStore();
  
  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    addPermission,
    removePermission,
  };
}

/**
 * 角色Hook - 只关注角色相关功能
 */
export function useRoles() {
  const {
    roles,
    hasRole,
    hasAnyRole,
    setRoles,
    addRole,
    removeRole,
  } = useUserStore();
  
  return {
    roles,
    hasRole,
    hasAnyRole,
    setRoles,
    addRole,
    removeRole,
  };
}

/**
 * 认证Hook - 只关注认证相关功能
 */
export function useAuth() {
  const { isAuthenticated, user, login, logout } = useUserStore();
  return { isAuthenticated, user, login, logout };
}
