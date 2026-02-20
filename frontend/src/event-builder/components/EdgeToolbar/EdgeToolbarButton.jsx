/**
 * EdgeToolbarButton Component
 * 边缘工具栏按钮
 */
import React from 'react';
import PropTypes from 'prop-types';

export default function EdgeToolbarButton({
  icon,
  label,
  title,
  active = false,
  onClick
}) {
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

EdgeToolbarButton.propTypes = {
  icon: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  title: PropTypes.string,
  active: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
};
