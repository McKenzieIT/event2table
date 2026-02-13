import React from 'react';
import { useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import './ParameterHistory.css';

/**
 * 参数变更历史页面
 * 查看参数历史变更记录
 * 需要游戏上下文
 */
function ParameterHistory() {
  const { currentGame } = useOutletContext();

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数变更历史需要先选择游戏" />;
  }

  return (
    <div className="param-history-container">
      <div className="page-header glass-card">
        <h1>参数变更历史</h1>
      </div>
      <div className="history-card glass-card">
        <p>查看参数历史变更记录</p>
      </div>
    </div>
  );
}
export default ParameterHistory;
