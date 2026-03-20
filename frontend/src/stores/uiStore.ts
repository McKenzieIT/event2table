import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * UI主题类型
 */
export type ThemeMode = 'light' | 'dark' | 'auto';

/**
 * UI状态管理Store (Zustand)
 * UI State Management Store (Zustand)
 * 
 * 管理所有UI相关的全局状态：
 * - 主题模式
 * - 侧边栏状态
 * - 模态框状态
 * - 其他UI交互状态
 */
interface UIStore {
  // ========== 主题状态 ==========
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;

  // ========== 侧边栏状态 ==========
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // 侧边栏分组展开状态
  sidebarGroupStates: Record<string, boolean>;
  toggleSidebarGroup: (groupId: string) => void;
  expandAllSidebarGroups: (groupIds: string[]) => void;
  collapseAllSidebarGroups: (groupIds: string[]) => void;

  // ========== 模态框状态 ==========
  // 通用模态框注册表（用于管理多个模态框的开启状态）
  modalStates: Record<string, boolean>;
  openModal: (modalId: string) => void;
  closeModal: (modalId: string) => void;
  toggleModal: (modalId: string) => void;
  setModalState: (modalId: string, isOpen: boolean) => void;

  // ========== 全屏状态 ==========
  isFullscreen: boolean;
  toggleFullscreen: () => void;
  setFullscreen: (isFullscreen: boolean) => void;

  // ========== 加载状态 ==========
  globalLoading: boolean;
  setGlobalLoading: (loading: boolean) => void;

  // ========== 重置UI状态 ==========
  resetUIState: () => void;
}

const defaultUIState = {
  themeMode: 'auto' as ThemeMode,
  sidebarCollapsed: false,
  sidebarGroupStates: {},
  modalStates: {},
  isFullscreen: false,
  globalLoading: false,
};

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      // ========== 初始状态 ==========
      ...defaultUIState,

      // ========== 主题操作 ==========
      setThemeMode: (mode) => set({ themeMode: mode }),

      // ========== 侧边栏操作 ==========
      toggleSidebar: () => set((state) => {
        const newState = !state.sidebarCollapsed;
        // 触发自定义事件，用于通知其他组件
        window.dispatchEvent(new CustomEvent('sidebarToggled', { detail: newState }));
        return { sidebarCollapsed: newState };
      }),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      toggleSidebarGroup: (groupId) => set((state) => ({
        sidebarGroupStates: {
          ...state.sidebarGroupStates,
          [groupId]: !state.sidebarGroupStates[groupId]
        }
      })),

      expandAllSidebarGroups: (groupIds) => set({
        sidebarGroupStates: Object.fromEntries(groupIds.map(id => [id, true]))
      }),

      collapseAllSidebarGroups: (groupIds) => set({
        sidebarGroupStates: Object.fromEntries(groupIds.map(id => [id, false]))
      }),

      // ========== 模态框操作 ==========
      openModal: (modalId) => set((state) => ({
        modalStates: { ...state.modalStates, [modalId]: true }
      })),

      closeModal: (modalId) => set((state) => ({
        modalStates: { ...state.modalStates, [modalId]: false }
      })),

      toggleModal: (modalId) => set((state) => ({
        modalStates: { ...state.modalStates, [modalId]: !state.modalStates[modalId] }
      })),

      setModalState: (modalId, isOpen) => set((state) => ({
        modalStates: { ...state.modalStates, [modalId]: isOpen }
      })),

      // ========== 全屏操作 ==========
      toggleFullscreen: () => set((state) => {
        const newState = !state.isFullscreen;
        // 实际切换浏览器全屏
        if (newState) {
          document.documentElement.requestFullscreen?.();
        } else {
          document.exitFullscreen?.();
        }
        return { isFullscreen: newState };
      }),

      setFullscreen: (isFullscreen) => set({ isFullscreen }),

      // ========== 加载状态操作 ==========
      setGlobalLoading: (loading) => set({ globalLoading: loading }),

      // ========== 重置操作 ==========
      resetUIState: () => set(defaultUIState),
    }),
    {
      name: 'ui-storage',
      // 只持久化需要保存的状态
      partialize: (state) => ({
        themeMode: state.themeMode,
        sidebarCollapsed: state.sidebarCollapsed,
        sidebarGroupStates: state.sidebarGroupStates,
      }),
    }
  )
);
