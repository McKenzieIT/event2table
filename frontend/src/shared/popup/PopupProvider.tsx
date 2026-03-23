/**
 * PopupProvider - 统一弹窗管理Provider
 *
 * 提供全局弹窗状态管理和z-index协调
 */

import React, { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react';

import { ZIndexManager } from './ZIndexManager';
import { PopupConfig, PopupContextValue, PopupState } from './types';

// Context
const PopupContext = createContext<PopupContextValue | null>(null);

/**
 * PopupProvider组件
 */
export function PopupProvider({ children }: { children: ReactNode }) {
  const zManager = useMemo(() => new ZIndexManager(), []);
  const [popups, setPopups] = useState<Map<string, PopupConfig>>(new Map());

  // 注册弹窗
  const register = useCallback((config: PopupConfig) => {
    const zIndex = zManager.getNext(config.type);

    setPopups(prev => {
      const newMap = new Map(prev);
      newMap.set(config.id, { ...config, zIndex });
      return newMap;
    });
  }, [zManager]);

  // 注销弹窗
  const unregister = useCallback((id: string) => {
    setPopups(prev => {
      const popup = prev.get(id);
      if (popup) {
        zManager.release(popup.type);
      }

      const newMap = new Map(prev);
      newMap.delete(id);
      return newMap;
    });
  }, [zManager]);

  // 获取z-index
  const getZIndex = useCallback((id: string) => {
    return popups.get(id)?.zIndex || 1050;
  }, [popups]);

  // 获取最顶层弹窗ID
  const getTopmostId = useCallback((): string | null => {
    let maxZ = 0;
    let topId = null;

    popups.forEach((popup, id) => {
      if (popup.zIndex && popup.zIndex > maxZ) {
        maxZ = popup.zIndex;
        topId = id;
      }
    });

    return topId;
  }, [popups]);

  const value: PopupContextValue = useMemo(() => ({
    register,
    unregister,
    getZIndex,
    getTopmostId,
  }), [register, unregister, getZIndex, getTopmostId]);

  return (
    <PopupContext.Provider value={value}>
      {children}
    </PopupContext.Provider>
  );
}

/**
 * usePopupContext Hook
 */
export function usePopupContext(): PopupContextValue {
  const context = useContext(PopupContext);

  if (!context) {
    throw new Error('usePopupContext must be used within PopupProvider');
  }

  return context;
}

export default PopupProvider;
