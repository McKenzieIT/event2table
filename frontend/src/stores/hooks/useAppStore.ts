import { useAppStore } from '../appStore';

/**
 * 应用状态Hook
 * 
 * 提供类型安全的应用状态访问和操作
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { 
 *     appVersion, 
 *     environment, 
 *     isOnline, 
 *     addNotification,
 *     getFeatureFlag 
 *   } = useAppStore();
 *   
 *   return (
 *     <div>
 *       <p>版本: {appVersion}</p>
 *       <p>环境: {environment}</p>
 *       <p>状态: {isOnline ? '在线' : '离线'}</p>
 *       {getFeatureFlag('newFeature') && <NewFeature />}
 *     </div>
 *   );
 * }
 * ```
 */
export function useAppStore() {
  const store = useAppStore();
  
  return {
    // 应用初始化
    isAppInitialized: store.isAppInitialized,
    setAppInitialized: store.setAppInitialized,
    
    // 应用配置
    appVersion: store.appVersion,
    apiBaseUrl: store.apiBaseUrl,
    environment: store.environment,
    setAppVersion: store.setAppVersion,
    setApiBaseUrl: store.setApiBaseUrl,
    setEnvironment: store.setEnvironment,
    
    // 错误状态
    globalError: store.globalError,
    setGlobalError: store.setGlobalError,
    clearGlobalError: store.clearGlobalError,
    
    // 通知消息
    notifications: store.notifications,
    addNotification: store.addNotification,
    removeNotification: store.removeNotification,
    clearNotifications: store.clearNotifications,
    
    // 应用状态
    isOnline: store.isOnline,
    setOnlineStatus: store.setOnlineStatus,
    
    // 功能开关
    featureFlags: store.featureFlags,
    setFeatureFlag: store.setFeatureFlag,
    getFeatureFlag: store.getFeatureFlag,
    
    // 缓存管理
    clearAllCache: store.clearAllCache,
    
    // 重置
    resetAppState: store.resetAppState,
  };
}

/**
 * 应用配置Hook - 只关注应用配置
 */
export function useAppConfig() {
  const {
    appVersion,
    apiBaseUrl,
    environment,
    setAppVersion,
    setApiBaseUrl,
    setEnvironment,
  } = useAppStore();
  
  return {
    appVersion,
    apiBaseUrl,
    environment,
    setAppVersion,
    setApiBaseUrl,
    setEnvironment,
  };
}

/**
 * 错误状态Hook - 只关注错误处理
 */
export function useGlobalError() {
  const {
    globalError,
    setGlobalError,
    clearGlobalError,
  } = useAppStore();
  
  return {
    globalError,
    setGlobalError,
    clearGlobalError,
  };
}

/**
 * 通知Hook - 只关注通知消息
 */
export function useNotifications() {
  const {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
  } = useAppStore();
  
  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
  };
}

/**
 * 功能开关Hook - 只关注功能开关
 */
export function useFeatureFlags() {
  const {
    featureFlags,
    setFeatureFlag,
    getFeatureFlag,
  } = useAppStore();
  
  return {
    featureFlags,
    setFeatureFlag,
    getFeatureFlag,
  };
}

/**
 * 在线状态Hook - 只关注在线状态
 */
export function useOnlineStatus() {
  const { isOnline, setOnlineStatus } = useAppStore();
  return { isOnline, setOnlineStatus };
}
