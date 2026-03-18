/**
 * 统一弹窗管理系统导出
 *
 * @module @shared/popup
 */

// Context Provider
export { PopupProvider, usePopupContext } from './PopupProvider';

// ZIndexManager
export { ZIndexManager, PopupType } from './ZIndexManager';

// Hooks
export { useUnifiedEscHandler } from './hooks/useUnifiedEscHandler';
export type { UseEscHandlerOptions } from './hooks/useUnifiedEscHandler';

export { useFocusManager } from './hooks/useFocusManager';
export type { UseFocusManagerOptions } from './hooks/useFocusManager';

// Types
export type {
  PopupConfig,
  PopupState,
  PopupContextValue,
  FocusStrategy,
  FOCUS_STRATEGIES,
} from './types';
