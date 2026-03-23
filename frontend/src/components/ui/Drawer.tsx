/**
 * Drawer Component
 *
 * 可复用的抽屉组件，用于侧边栏和面板
 * 赛博朋克实验室风格 - 玻璃态效果 + 霓虹边框
 *
 * 功能：
 * - 支持 left/right 方向
 * - 玻璃态背景效果
 * - 平滑的滑入/滑出动画
 * - 键盘 ESC 关闭
 * - 点击遮罩层关闭
 * - 焦点陷阱（focus trap）
 */

import React, { useEffect, useRef, useCallback, useState, type ReactNode } from 'react';
import { type DrawerDirection, type DrawerSize } from './types';

/**
 * 检测用户是否偏好减少动画
 */
const usePrefersReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return prefersReducedMotion;
};

/**
 * Drawer 组件属性
 */
export interface DrawerProps {
  /** 是否打开 */
  open: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 标题 */
  title?: ReactNode;
  /** 内容 */
  children: ReactNode;
  /** 方向（left/right） */
  direction?: DrawerDirection;
  /** 尺寸 */
  size?: DrawerSize;
  /** 是否显示遮罩层 */
  showOverlay?: boolean;
  /** 点击遮罩层是否关闭 */
  closeOnOverlayClick?: boolean;
  /** 按 ESC 是否关闭 */
  closeOnEscape?: boolean;
  /** 是否启用焦点陷阱 */
  enableFocusTrap?: boolean;
  /** 自定义宽度 */
  width?: string;
  /** 自定义类名 */
  className?: string;
  /** z-index */
  zIndex?: number;
}

/**
 * Drawer 组件
 *
 * @example
 * ```tsx
 * const [open, setOpen] = useState(false);
 *
 * return (
 *   <>
 *     <button onClick={() => setOpen(true)}>打开抽屉</button>
 *     <Drawer
 *       open={open}
 *       onClose={() => setOpen(false)}
 *       title="侧边栏"
 *       direction="right"
 *     >
 *       <p>抽屉内容</p>
 *     </Drawer>
 *   </>
 * );
 * ```
 */
export const Drawer = React.memo(({
  open,
  onClose,
  title,
  children,
  direction = 'right',
  size = 'md',
  showOverlay = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  enableFocusTrap = true,
  width,
  className = '',
  zIndex = 1000,
}: DrawerProps) => {
  const drawerRef = useRef<HTMLDivElement>(null);
  const previousActiveElementRef = useRef<HTMLElement | null>(null);
  const prefersReducedMotion = usePrefersReducedMotion();
  
  // 动画持续时间：用户偏好减少动画时为 0ms，否则为 250ms
  const transitionDuration = prefersReducedMotion ? '0ms' : '250ms';

  /**
   * 处理 ESC 键关闭
   */
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (closeOnEscape && event.key === 'Escape') {
      onClose();
    }
  }, [closeOnEscape, onClose]);

  /**
   * 处理遮罩层点击
   */
  const handleOverlayClick = useCallback((event: React.MouseEvent) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  }, [closeOnOverlayClick, onClose]);

  /**
   * 焦点陷阱实现
   */
  const trapFocus = useCallback((event: KeyboardEvent) => {
    if (!enableFocusTrap || !drawerRef.current) return;

    if (event.key !== 'Tab') return;

    const focusableElements = drawerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement?.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement?.focus();
      }
    }
  }, [enableFocusTrap]);

  /**
   * 保存和恢复焦点
   */
  useEffect(() => {
    if (open) {
      // 保存当前焦点元素
      previousActiveElementRef.current = document.activeElement as HTMLElement;

      // 监听键盘事件
      document.addEventListener('keydown', handleKeyDown);
      if (enableFocusTrap) {
        document.addEventListener('keydown', trapFocus);
      }

      // 禁用背景滚动
      document.body.style.overflow = 'hidden';

      // 聚焦到抽屉内的第一个可聚焦元素
      setTimeout(() => {
        if (drawerRef.current && enableFocusTrap) {
          const focusableElement = drawerRef.current.querySelector(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          ) as HTMLElement;
          focusableElement?.focus();
        }
      }, 100);
    } else {
      // 恢复焦点
      if (previousActiveElementRef.current) {
        previousActiveElementRef.current.focus();
      }

      // 移除监听器
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keydown', trapFocus);

      // 恢复背景滚动
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keydown', trapFocus);
      document.body.style.overflow = '';
    };
  }, [open, handleKeyDown, trapFocus, enableFocusTrap]);

  /**
   * 获取宽度样式
   */
  const getWidthStyle = (): React.CSSProperties => {
    if (width) {
      return { width };
    }

    const sizeMap: Record<DrawerSize, string> = {
      sm: '320px',
      md: '480px',
      lg: '640px',
      full: '100%',
    };

    return { width: sizeMap[size] };
  };

  /**
   * 获取抽屉容器样式
   */
  const getDrawerStyle = (): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      position: 'fixed',
      top: 0,
      bottom: 0,
      zIndex: zIndex + 1,
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      border: '1px solid rgba(6, 182, 212, 0.3)',
      boxShadow: direction === 'right'
        ? '-4px 0 24px rgba(0, 0, 0, 0.5), -2px 0 12px rgba(6, 182, 212, 0.2)'
        : '4px 0 24px rgba(0, 0, 0, 0.5), 2px 0 12px rgba(6, 182, 212, 0.2)',
      transition: 'transform 250ms ease-out, opacity 250ms ease-out',
      opacity: open ? 1 : 0,
      transform: open
        ? 'translateX(0)'
        : direction === 'right'
        ? 'translateX(100%)'
        : 'translateX(-100%)',
      ...getWidthStyle(),
    };

    return baseStyle;
  };

  /**
   * 获取遮罩层样式
   */
  const getOverlayStyle = (): React.CSSProperties => {
    return {
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      backdropFilter: 'blur(4px)',
      WebkitBackdropFilter: 'blur(4px)',
      zIndex,
      opacity: open ? 1 : 0,
      transition: `opacity ${transitionDuration} ease-out`,
      pointerEvents: open ? 'auto' : 'none',
    };
  };

  if (!open) {
    return null;
  }

  return (
    <>
      {/* 遮罩层 */}
      {showOverlay && (
        <div
          style={getOverlayStyle()}
          onClick={handleOverlayClick}
          data-testid="drawer-overlay"
          aria-hidden="true"
        />
      )}

      {/* 抽屉主体 */}
      <div
        ref={drawerRef}
        style={getDrawerStyle()}
        className={className}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'drawer-title' : undefined}
        data-testid="drawer"
        data-direction={direction}
      >
        {/* 标题栏 */}
        {title && (
          <div
            style={{
              padding: '20px 24px',
              borderBottom: '1px solid rgba(6, 182, 212, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
            }}
          >
            <h2
              id="drawer-title"
              style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: 600,
                color: '#e2e8f0',
                fontFamily: 'var(--font-display, system-ui, -apple-system, sans-serif)',
                background: 'linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: '8px',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: `all ${transitionDuration} ease`,
                fontSize: '20px',
                lineHeight: 1,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(6, 182, 212, 0.1)';
                e.currentTarget.style.color = '#22d3ee';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#94a3b8';
              }}
              aria-label="关闭"
              data-testid="drawer-close-button"
            >
              ×
            </button>
          </div>
        )}

        {/* 内容区域 */}
        <div
          style={{
            padding: '24px',
            overflowY: 'auto',
            height: title ? 'calc(100% - 73px)' : '100%',
          }}
          data-testid="drawer-content"
        >
          {children}
        </div>
      </div>
    </>
  );
});

Drawer.displayName = 'Drawer';

export default Drawer;
