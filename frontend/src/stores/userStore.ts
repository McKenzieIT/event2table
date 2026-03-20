import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 用户信息接口
 */
export interface UserInfo {
  id: string;
  username: string;
  email?: string;
  displayName?: string;
  avatar?: string;
  department?: string;
  position?: string;
}

/**
 * 权限类型
 */
export type Permission = string;

/**
 * 角色类型
 */
export type Role = string;

/**
 * 用户状态管理Store (Zustand)
 * User State Management Store (Zustand)
 * 
 * 管理用户认证、授权和相关信息：
 * - 用户基本信息
 * - 登录状态
 * - 权限列表
 * - 角色列表
 */
interface UserStore {
  // ========== 用户信息 ==========
  user: UserInfo | null;
  isAuthenticated: boolean;
  
  // ========== 权限和角色 ==========
  permissions: Permission[];
  roles: Role[];
  
  // ========== 用户操作 ==========
  setUser: (user: UserInfo | null) => void;
  updateUser: (updates: Partial<UserInfo>) => void;
  
  // ========== 认证操作 ==========
  login: (user: UserInfo, permissions?: Permission[], roles?: Role[]) => void;
  logout: () => void;
  
  // ========== 权限检查 ==========
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  hasRole: (role: Role) => boolean;
  hasAnyRole: (roles: Role[]) => boolean;
  
  // ========== 权限和角色管理 ==========
  setPermissions: (permissions: Permission[]) => void;
  setRoles: (roles: Role[]) => void;
  addPermission: (permission: Permission) => void;
  removePermission: (permission: Permission) => void;
  addRole: (role: Role) => void;
  removeRole: (role: Role) => void;
  
  // ========== 重置用户状态 ==========
  resetUserState: () => void;
}

const defaultUserState = {
  user: null,
  isAuthenticated: false,
  permissions: [],
  roles: [],
};

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      // ========== 初始状态 ==========
      ...defaultUserState,

      // ========== 用户信息操作 ==========
      setUser: (user) => set({ 
        user, 
        isAuthenticated: user !== null 
      }),

      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),

      // ========== 认证操作 ==========
      login: (user, permissions = [], roles = []) => set({
        user,
        isAuthenticated: true,
        permissions,
        roles,
      }),

      logout: () => set(defaultUserState),

      // ========== 权限检查 ==========
      hasPermission: (permission) => {
        const { permissions } = get();
        return permissions.includes(permission);
      },

      hasAnyPermission: (permissions) => {
        const { permissions: userPermissions } = get();
        return permissions.some(p => userPermissions.includes(p));
      },

      hasAllPermissions: (permissions) => {
        const { permissions: userPermissions } = get();
        return permissions.every(p => userPermissions.includes(p));
      },

      hasRole: (role) => {
        const { roles } = get();
        return roles.includes(role);
      },

      hasAnyRole: (roles) => {
        const { roles: userRoles } = get();
        return roles.some(r => userRoles.includes(r));
      },

      // ========== 权限和角色管理 ==========
      setPermissions: (permissions) => set({ permissions }),

      setRoles: (roles) => set({ roles }),

      addPermission: (permission) => set((state) => ({
        permissions: state.permissions.includes(permission) 
          ? state.permissions 
          : [...state.permissions, permission]
      })),

      removePermission: (permission) => set((state) => ({
        permissions: state.permissions.filter(p => p !== permission)
      })),

      addRole: (role) => set((state) => ({
        roles: state.roles.includes(role) 
          ? state.roles 
          : [...state.roles, role]
      })),

      removeRole: (role) => set((state) => ({
        roles: state.roles.filter(r => r !== role)
      })),

      // ========== 重置操作 ==========
      resetUserState: () => set(defaultUserState),
    }),
    {
      name: 'user-storage',
      // 只持久化用户基本信息，不持久化敏感信息
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        permissions: state.permissions,
        roles: state.roles,
      }),
    }
  )
);
