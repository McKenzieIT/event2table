import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 应用状态管理Store (Zustand)
 * App State Management Store (Zustand)
 * 
 * 管理应用级别的全局状态：
 * - 应用初始化状态
 * - 全局配置
 * - 应用版本信息
 * - 错误状态
 * - 通知消息
 */
interface AppStore {
  // ========== 应用初始化 ==========
  isAppInitialized: boolean;
  setAppInitialized: (initialized: boolean) => void;

  // ========== 应用配置 ==========
  appVersion: string;
  apiBaseUrl: string;
  environment: 'development' | 'staging' | 'production';
  
  setAppVersion: (version: string) => void;
  setApiBaseUrl: (url: string) => void;
  setEnvironment: (env: 'development' | 'staging' | 'production') => void;

  // ========== 错误状态 ==========
  globalError: Error | null;
  setGlobalError: (error: Error | null) => void;
  clearGlobalError: () => void;

  // ========== 通知消息 ==========
  notifications: Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    message: string;
    timestamp: number;
  }>;
  
  addNotification: (notification: Omit<AppStore['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;

  // ========== 应用状态 ==========
  isOnline: boolean;
  setOnlineStatus: (online: boolean) => void;

  // ========== 功能开关 ==========
  featureFlags: Record<string, boolean>;
  setFeatureFlag: (flag: string, enabled: boolean) => void;
  getFeatureFlag: (flag: string) => boolean;

  // ========== 缓存管理 ==========
  clearAllCache: () => void;

  // ========== 重置应用状态 ==========
  resetAppState: () => void;
}

const defaultAppState = {
  isAppInitialized: false,
  appVersion: '1.0.0',
  apiBaseUrl: '/api',
  environment: 'development' as const,
  globalError: null,
  notifications: [],
  isOnline: true,
  featureFlags: {},
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // ========== 初始状态 ==========
      ...defaultAppState,

      // ========== 应用初始化操作 ==========
      setAppInitialized: (initialized) => set({ isAppInitialized: initialized }),

      // ========== 应用配置操作 ==========
      setAppVersion: (version) => set({ appVersion: version }),

      setApiBaseUrl: (url) => set({ apiBaseUrl: url }),

      setEnvironment: (env) => set({ environment: env }),

      // ========== 错误状态操作 ==========
      setGlobalError: (error) => set({ globalError: error }),

      clearGlobalError: () => set({ globalError: null }),

      // ========== 通知消息操作 ==========
      addNotification: (notification) => set((state) => ({
        notifications: [
          ...state.notifications,
          {
            ...notification,
            id: Math.random().toString(36).substring(7),
            timestamp: Date.now(),
          }
        ]
      })),

      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id)
      })),

      clearNotifications: () => set({ notifications: [] }),

      // ========== 应用状态操作 ==========
      setOnlineStatus: (online) => set({ isOnline: online }),

      // ========== 功能开关操作 ==========
      setFeatureFlag: (flag, enabled) => set((state) => ({
        featureFlags: { ...state.featureFlags, [flag]: enabled }
      })),

      getFeatureFlag: (flag) => {
        const { featureFlags } = get();
        return featureFlags[flag] ?? false;
      },

      // ========== 缓存管理 ==========
      clearAllCache: () => {
        // 清除localStorage
        try {
          localStorage.clear();
        } catch (error) {
          console.error('[AppStore] Failed to clear localStorage:', error);
        }
        // 清除sessionStorage
        try {
          sessionStorage.clear();
        } catch (error) {
          console.error('[AppStore] Failed to clear sessionStorage:', error);
        }
      },

      // ========== 重置操作 ==========
      resetAppState: () => set(defaultAppState),
    }),
    {
      name: 'app-storage',
      // 只持久化必要的配置状态
      partialize: (state) => ({
        appVersion: state.appVersion,
        apiBaseUrl: state.apiBaseUrl,
        environment: state.environment,
        featureFlags: state.featureFlags,
      }),
    }
  )
);

// ========== 初始化应用状态 ==========
// 从环境变量读取配置
if ((import.meta as { env?: Record<string, string> }).env.VITE_APP_VERSION) {
  useAppStore.getState().setAppVersion((import.meta as { env?: Record<string, string> }).env.VITE_APP_VERSION);
}

if ((import.meta as { env?: Record<string, string> }).env.VITE_API_BASE_URL) {
  useAppStore.getState().setApiBaseUrl((import.meta as { env?: Record<string, string> }).env.VITE_API_BASE_URL);
}

if ((import.meta as { env?: Record<string, string> }).env.MODE) {
  const env = (import.meta as { env?: Record<string, string> }).env.MODE as 'development' | 'staging' | 'production';
  useAppStore.getState().setEnvironment(env);
}

// 监听在线/离线状态
window.addEventListener('online', () => {
  useAppStore.getState().setOnlineStatus(true);
});

window.addEventListener('offline', () => {
  useAppStore.getState().setOnlineStatus(false);
});
