/**
 * 统一状态管理Store导出
 * 
 * @module @stores
 * 
 * Event2Table统一状态管理架构
 * 
 * 架构说明：
 * - Zustand: 用于管理客户端状态（UI、用户、应用配置）
 * - React Query: 用于管理服务端状态（API数据、缓存）
 * 
 * Store分类：
 * - uiStore: UI状态（主题、侧边栏、模态框等）
 * - userStore: 用户状态（用户信息、权限、角色）
 * - appStore: 应用全局状态（配置、错误、通知）
 * - gameStore: 游戏相关状态（已存在）
 */

// ========== Stores ==========
export { useUIStore } from './uiStore';
export type { ThemeMode } from './uiStore';

export { useUserStore } from './userStore';
export type { UserInfo, Permission, Role } from './userStore';

export { useAppStore } from './appStore';

export { useGameStore } from './gameStore';

// ========== Hooks ==========
export * from './hooks';
