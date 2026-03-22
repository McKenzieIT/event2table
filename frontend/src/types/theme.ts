/**
 * Theme Type Definitions
 *
 * 主题相关类型定义
 * 支持赛博朋克实验室风格的深色主题
 */

// ============================================================================
// Theme Mode
// ============================================================================

/**
 * 主题模式
 * - dark: 深色主题（默认，赛博朋克风格）
 * - light: 浅色主题（预留，暂未实现）
 */
export type ThemeMode = 'dark' | 'light';

/**
 * 主题配置
 */
export interface ThemeConfig {
  /** 当前主题模式 */
  mode: ThemeMode;
  /** 是否启用赛博朋克特效 */
  cyberpunkEffects: boolean;
}

/**
 * 主题状态
 */
export interface ThemeState {
  /** 当前主题模式 */
  theme: ThemeMode;
  /** 切换主题 */
  toggleTheme: () => void;
  /** 设置主题 */
  setTheme: (mode: ThemeMode) => void;
}

// ============================================================================
// Theme Constants
// ============================================================================

/**
 * 默认主题
 */
export const DEFAULT_THEME: ThemeMode = 'dark';

/**
 * 可用主题列表
 */
export const AVAILABLE_THEMES: ThemeMode[] = ['dark', 'light'];

/**
 * localStorage 存储键
 */
export const THEME_STORAGE_KEY = 'event2table-theme';

/**
 * data-theme 属性名
 */
export const DATA_THEME_ATTRIBUTE = 'data-theme';

// ============================================================================
// Theme Colors (Cyberpunk Lab Style)
// ============================================================================

/**
 * 主题颜色配置
 */
export interface ThemeColors {
  /** 主色调 - 青色 */
  primary: string;
  /** 辅助色 - 电光紫 */
  secondary: string;
  /** 背景色 */
  background: string;
  /** 表面色 */
  surface: string;
  /** 文本色 */
  text: string;
  /** 边框色 */
  border: string;
  /** 成功色 */
  success: string;
  /** 警告色 */
  warning: string;
  /** 错误色 */
  error: string;
}

/**
 * 赛博朋克主题颜色配置
 */
export const CYBERPUNK_DARK_COLORS: ThemeColors = {
  primary: '#06B6D4',      // 青色
  secondary: '#8B5CF6',    // 电光紫
  background: '#0A0A0F',   // 深黑背景
  surface: '#1A1A2E',      // 深蓝表面
  text: '#E0E0E0',         // 浅灰文本
  border: '#2A2A4E',       // 深蓝边框
  success: '#10B981',      // 绿色
  warning: '#F59E0B',      // 橙色
  error: '#EF4444',        // 红色
};

/**
 * 浅色主题颜色配置（预留）
 */
export const LIGHT_COLORS: ThemeColors = {
  primary: '#06B6D4',
  secondary: '#8B5CF6',
  background: '#FFFFFF',
  surface: '#F5F5F5',
  text: '#1A1A1A',
  border: '#E0E0E0',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
};

/**
 * 根据主题模式获取颜色配置
 */
export function getThemeColors(mode: ThemeMode): ThemeColors {
  return mode === 'dark' ? CYBERPUNK_DARK_COLORS : LIGHT_COLORS;
}
