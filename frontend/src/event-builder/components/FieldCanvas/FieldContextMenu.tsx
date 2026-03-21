import React, { useEffect } from 'react';

/**
 * Props for FieldContextMenu component
 */
export interface FieldContextMenuProps {
  /** Is open */
  isOpen: boolean;
  /** X position */
  x: number;
  /** Y position */
  y: number;
  /** Close callback */
  onClose: () => void;
  /** Add base field callback */
  onAddBaseField: () => void;
  /** Add custom field callback */
  onAddCustomField: () => void;
  /** Add fixed field callback */
  onAddFixedField: () => void;
  /** Quick add common fields callback */
  onQuickAddCommon: () => void;
}

/**
 * FieldContextMenu Component
 */
export const FieldContextMenu: React.FC<FieldContextMenuProps> = ({
  isOpen,
  x,
  y,
  onClose,
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
}) => {
  // Close menu on click outside
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.context-menu')) {
        onClose();
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="context-menu"
      style={{
        position: 'fixed',
        left: x,
        top: y,
        zIndex: 1000,
      }}
    >
      <div className="context-menu-item" onClick={() => { onAddBaseField(); onClose(); }}>
        <i className="bi bi-plus-circle"></i>
        添加基础字段
      </div>
      <div className="context-menu-item" onClick={() => { onAddCustomField(); onClose(); }}>
        <i className="bi bi-code"></i>
        添加自定义字段
      </div>
      <div className="context-menu-item" onClick={() => { onAddFixedField(); onClose(); }}>
        <i className="bi bi-pin"></i>
        添加固定值
      </div>
      <div className="context-menu-divider"></div>
      <div className="context-menu-item" onClick={() => { onQuickAddCommon(); onClose(); }}>
        <i className="bi bi-lightning"></i>
        快速添加常用字段
      </div>
    </div>
  );
};

FieldContextMenu.displayName = 'FieldContextMenu';
