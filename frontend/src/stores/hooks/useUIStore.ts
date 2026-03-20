import { useUIStore } from '../uiStore';

/**
 * UI状态Hook
 * 
 * 提供类型安全的UI状态访问和操作
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { themeMode, setThemeMode, sidebarCollapsed, toggleSidebar } = useUIStore();
 *   
 *   return (
 *     <div>
 *       <p>当前主题: {themeMode}</p>
 *       <button onClick={() => setThemeMode('dark')}>切换到暗色主题</button>
 *       <button onClick={toggleSidebar}>切换侧边栏</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useUIStore() {
  const store = useUIStore();
  
  return {
    // 主题状态
    themeMode: store.themeMode,
    setThemeMode: store.setThemeMode,
    
    // 侧边栏状态
    sidebarCollapsed: store.sidebarCollapsed,
    toggleSidebar: store.toggleSidebar,
    setSidebarCollapsed: store.setSidebarCollapsed,
    
    // 侧边栏分组状态
    sidebarGroupStates: store.sidebarGroupStates,
    toggleSidebarGroup: store.toggleSidebarGroup,
    expandAllSidebarGroups: store.expandAllSidebarGroups,
    collapseAllSidebarGroups: store.collapseAllSidebarGroups,
    
    // 模态框状态
    modalStates: store.modalStates,
    openModal: store.openModal,
    closeModal: store.closeModal,
    toggleModal: store.toggleModal,
    setModalState: store.setModalState,
    
    // 全屏状态
    isFullscreen: store.isFullscreen,
    toggleFullscreen: store.toggleFullscreen,
    setFullscreen: store.setFullscreen,
    
    // 加载状态
    globalLoading: store.globalLoading,
    setGlobalLoading: store.setGlobalLoading,
    
    // 重置
    resetUIState: store.resetUIState,
  };
}

/**
 * 主题Hook - 只关注主题相关状态
 */
export function useTheme() {
  const { themeMode, setThemeMode } = useUIStore();
  return { themeMode, setThemeMode };
}

/**
 * 侧边栏Hook - 只关注侧边栏相关状态
 */
export function useSidebar() {
  const {
    sidebarCollapsed,
    toggleSidebar,
    setSidebarCollapsed,
    sidebarGroupStates,
    toggleSidebarGroup,
    expandAllSidebarGroups,
    collapseAllSidebarGroups,
  } = useUIStore();
  
  return {
    collapsed: sidebarCollapsed,
    toggleCollapsed: toggleSidebar,
    setCollapsed: setSidebarCollapsed,
    groupStates: sidebarGroupStates,
    toggleGroup: toggleSidebarGroup,
    expandAllGroups: expandAllSidebarGroups,
    collapseAllGroups: collapseAllSidebarGroups,
  };
}

/**
 * 模态框Hook - 只关注模态框相关状态
 */
export function useModal(modalId: string) {
  const {
    modalStates,
    openModal,
    closeModal,
    toggleModal,
    setModalState,
  } = useUIStore();
  
  return {
    isOpen: modalStates[modalId] ?? false,
    open: () => openModal(modalId),
    close: () => closeModal(modalId),
    toggle: () => toggleModal(modalId),
    setState: (isOpen: boolean) => setModalState(modalId, isOpen),
  };
}

/**
 * 全屏Hook - 只关注全屏相关状态
 */
export function useFullscreen() {
  const { isFullscreen, toggleFullscreen, setFullscreen } = useUIStore();
  return { isFullscreen, toggleFullscreen, setFullscreen };
}
