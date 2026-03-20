/**
 * 统一状态管理Hooks导出
 * 
 * @module @stores/hooks
 * 
 * 提供所有store的hooks，用于在组件中访问和操作状态
 */

// UI Store Hooks
export {
  useUIStore,
  useTheme,
  useSidebar,
  useModal,
  useFullscreen,
} from './useUIStore';

// User Store Hooks
export {
  useUserStore,
  useUserInfo,
  usePermissions,
  useRoles,
  useAuth,
} from './useUserStore';

// App Store Hooks
export {
  useAppStore,
  useAppConfig,
  useGlobalError,
  useNotifications,
  useFeatureFlags,
  useOnlineStatus,
} from './useAppStore';
