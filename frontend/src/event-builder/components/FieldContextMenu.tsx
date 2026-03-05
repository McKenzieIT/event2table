// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * FieldContextMenu Component
 * 右键上下文菜单 - 在画布空白处右键显示
 */
import React, { useEffect, useRef } from 'react';

/**
 * 组件Props接口
 */
export interface FieldContextMenuProps {
  isOpen: boolean;
  x: number;
  y: number;
  onClose: () => void;
  onAddBaseField: () => void;
  onAddCustomField: () => void;
  onAddFixedField: () => void;
  onQuickAddCommon: () => void;
}

/**
 * FieldContextMenu Component
 */
export default function FieldContextMenu({
  isOpen,
  x,
  y,
  onClose,
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon
}: FieldContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // 点击菜单外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  // ESC键关闭
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const menuStyle: React.CSSProperties = {
    position: 'fixed',
    left: `${x}px`,
    top: `${y}px`,
    zIndex: 1000,
  };

  return (
    <div
      ref={menuRef}
      className="field-context-menu"
      style={menuStyle}
    >
      <div className="context-menu-header">
        <i className="bi bi-plus-circle"></i>
        <span>添加字段</span>
      </div>

      <div className="context-menu-divider" />

      <ul className="context-menu-list">
        <li className="context-menu-item" onClick={() => { onAddBaseField(); onClose(); }}>
          <i className="bi bi-type"></i>
          <span>基础字段</span>
          <span className="shortcut">Cmd+B</span>
        </li>

        <li className="context-menu-item" onClick={() => { onAddCustomField(); onClose(); }}>
          <i className="bi bi-code"></i>
          <span>自定义字段</span>
          <span className="shortcut">Cmd+Shift+C</span>
        </li>

        <li className="context-menu-item" onClick={() => { onAddFixedField(); onClose(); }}>
          <i className="bi bi-pin"></i>
          <span>固定值字段</span>
          <span className="shortcut">Cmd+Shift+F</span>
        </li>
      </ul>

      <div className="context-menu-divider" />

      <ul className="context-menu-list">
        <li className="context-menu-item" onClick={() => { onQuickAddCommon(); onClose(); }}>
          <i className="bi bi-bolt"></i>
          <span>快速添加常用字段</span>
          <span className="shortcut">Cmd+Shift+B</span>
        </li>
      </ul>
    </div>
  );
}
