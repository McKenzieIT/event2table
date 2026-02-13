import React from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import './ParameterNetwork.css';

/**
 * 参数网络页面
 * 显示参数之间的关系网络图
 * 需要游戏上下文
 */
function ParameterNetwork() {
  const { currentGame } = useOutletContext();

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数关系网络需要先选择游戏" />;
  }

  return (
    <div className="parameter-network-container">
      <div className="page-header">
        <h1>参数关系网络</h1>
        <Link to="/parameters" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回
        </Link>
      </div>

      <div className="network-canvas glass-card">
        <div className="network-placeholder">
          <i className="bi bi-diagram-3"></i>
          <h3>参数关系网络图</h3>
          <p>此页面将显示参数之间的关系网络</p>
          <div className="network-info">
            <div className="info-item">
              <span className="dot primary"></span>
              <span>事件参数</span>
            </div>
            <div className="info-item">
              <span className="dot success"></span>
              <span>公共参数</span>
            </div>
            <div className="info-item">
              <span className="dot warning"></span>
              <span>关联参数</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParameterNetwork;
