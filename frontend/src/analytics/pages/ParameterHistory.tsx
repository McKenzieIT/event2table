// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from 'react';
import { useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import './ParameterHistory.css';

/**
 * 参数变更历史页面
 * 查看参数历史变更记录
 * 需要游戏上下文
 */

interface GameContext {
  currentGame: {
    gid: number;
    name: string;
  } | null;
}

function ParameterHistory(): React.JSX.Element {
  const { currentGame } = useOutletContext<GameContext>();

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
