/**
 * EdgeToolbarButton Component
 * 边缘工具栏按钮
 */
import React from 'react';

// 组件Props接口
interface EdgeToolbarButtonProps {
  icon: string;
  label: string;
  title?: string;
  active?: boolean;
  onClick: () => void;
}

export default function EdgeToolbarButton({
  icon,
  label,
  title,
  active = false,
  onClick
}: EdgeToolbarButtonProps) {
  return (
    <button
      className={`edge-toolbar-button ${active ? 'active' : ''}`}
      onClick={onClick}
      title={title}
      aria-label={label}
      aria-pressed={active}
      type="button"
    >
      <i className={`bi ${icon}`} aria-hidden="true"></i>
      <span className="button-label">{label}</span>
    </button>
  );
}
