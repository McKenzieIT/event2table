/**
 * ThemeProvider Component
 *
 * 主题提供者组件
 * 使用 Zustand 管理主题状态，支持主题切换和持久化
 * 赛博朋克实验室风格 - 深色主题为主
 */

import { useEffect, type ReactNode } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  ThemeMode,
  ThemeState,
  DEFAULT_THEME,
  THEME_STORAGE_KEY,
  DATA_THEME_ATTRIBUTE,
} from '@/types/theme';

// ============================================================================
// Theme Store
// ============================================================================

interface ThemeStore extends ThemeState {
  /** 内部状态 - 当前主题 */
  _theme: ThemeMode;
  /** 内部方法 - 设置主题 */
  _setTheme: (mode: ThemeMode) => void;
}

/**
 * 创建主题 Store
 * 使用 persist 中间件实现 localStorage 持久化
 */
const createThemeStore = () =>
  create<ThemeStore>()(
    persist(
      (set) => ({
        _theme: DEFAULT_THEME,
        theme: DEFAULT_THEME,
        
        setTheme: (mode: ThemeMode) => {
          set({ _theme: mode, theme: mode });
          // 更新 DOM 属性
          if (typeof document !== 'undefined') {
            document.documentElement.setAttribute(DATA_THEME_ATTRIBUTE, mode);
          }
        },
        
        toggleTheme: () => {
          set((state) => {
            const newTheme: ThemeMode = state._theme === 'dark' ? 'light' : 'dark';
            // 更新 DOM 属性
            if (typeof document !== 'undefined') {
              document.documentElement.setAttribute(DATA_THEME_ATTRIBUTE, newTheme);
            }
            return { _theme: newTheme, theme: newTheme };
          });
        },
        
        _setTheme: (mode: ThemeMode) => {
          set({ _theme: mode, theme: mode });
        },
      }),
      {
        name: THEME_STORAGE_KEY,
        // 只持久化 _theme，避免循环引用
        partialize: (state) => ({ _theme: state._theme }),
      }
    )
  );

// 创建单例 store
let themeStore: ReturnType<typeof createThemeStore> | null = null;

/**
 * 获取主题 Store 实例
 */
export const getThemeStore = () => {
  if (!themeStore) {
    themeStore = createThemeStore();
  }
  return themeStore;
};

/**
 * 重置主题 Store（仅供测试使用）
 * 清除 store 实例和 localStorage
 */
export const resetThemeStore = () => {
  themeStore = null;
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(THEME_STORAGE_KEY);
  }
};

// ============================================================================
// useTheme Hook
// ============================================================================

/**
 * 使用主题 Hook
 * 提供主题状态和操作方法
 * 
 * @returns 主题状态和方法
 * 
 * @example
 * function MyComponent() {
 *   const { theme, toggleTheme, setTheme } = useTheme();
 *   
 *   return (
 *     <div>
 *       <p>Current theme: {theme}</p>
 *       <button onClick={toggleTheme}>Toggle Theme</button>
 *       <button onClick={() => setTheme('dark')}>Dark Mode</button>
 *       <button onClick={() => setTheme('light')}>Light Mode</button>
 *     </div>
 *   );
 * }
 */
export function useTheme(): ThemeState {
  const store = getThemeStore();
  return {
    theme: store((state) => state.theme),
    toggleTheme: store((state) => state.toggleTheme),
    setTheme: store((state) => state.setTheme),
  };
}

// ============================================================================
// ThemeProvider Component
// ============================================================================

interface ThemeProviderProps {
  /** 子组件 */
  children: ReactNode;
  /** 初始主题（可选，默认从 localStorage 读取） */
  initialTheme?: ThemeMode;
}

/**
 * ThemeProvider 组件
 * 
 * 功能：
 * - 包装应用，提供主题上下文
 * - 初始化时从 localStorage 读取主题偏好
 * - 将主题应用到 document.documentElement 的 data-theme 属性
 * - 支持主题切换和持久化
 * 
 * @example
 * function App() {
 *   return (
 *     <ThemeProvider>
 *       <YourApp />
 *     </ThemeProvider>
 *   );
 * }
 * 
 * @example
 * // 使用自定义初始主题
 * function App() {
 *   return (
 *     <ThemeProvider initialTheme="dark">
 *       <YourApp />
 *     </ThemeProvider>
 *   );
 * }
 */
export function ThemeProvider({ children, initialTheme }: ThemeProviderProps) {
  const store = getThemeStore();
  
  useEffect(() => {
    // 初始化主题
    const currentTheme = store.getState()._theme;
    const themeToApply = initialTheme || currentTheme;
    
    // 应用主题到 DOM
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute(DATA_THEME_ATTRIBUTE, themeToApply);
    }
    
    // 如果提供了初始主题，更新 store
    if (initialTheme && initialTheme !== currentTheme) {
      store.getState()._setTheme(initialTheme);
    }
  }, [initialTheme, store]);
  
  return <>{children}</>;
}

/**
 * 导出默认组件
 */
export default ThemeProvider;
