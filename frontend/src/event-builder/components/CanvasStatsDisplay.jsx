/**
 * CanvasStatsDisplay Component
 * 字段画布统计信息显示组件（纯显示，无交互功能）
 * 样式参照"⚡ 基础字段 0/7"的btn-quick-add样式
 * 优化：添加赛博朋克玻璃拟态视觉效果
 */
import React from 'react';
import PropTypes from 'prop-types';
import './CanvasStatsDisplay.css';

export default function CanvasStatsDisplay({ stats = {} }) {
  const { total = 0, baseFields = 0, paramFields = 0 } = stats;

  return (
    <div className="field-canvas-stats">
      <span className="stats-icon">📊</span>
      <span className="stats-text">累计 {total}</span>
      <span className="stats-text">参数 {paramFields}</span>
      <span className="stats-text">基础 {baseFields}</span>
    </div>
  );
}

CanvasStatsDisplay.propTypes = {
  stats: PropTypes.shape({
    total: PropTypes.number.isRequired,
    baseFields: PropTypes.number.isRequired,
    paramFields: PropTypes.number.isRequired,
  }),
};
