// ✅ React Performance Optimization: Added React.memo, useMemo
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React, { useMemo, memo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import './FlowBuilder.css';

/**
 * FlowBuilder Component
 *
 * Visual HQL flow builder page
 *
 * URL Parameters:
 * - game_gid (optional): Game GID for flow context
 *
 * @returns JSX.Element
 */
const FlowBuilder: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { currentGameGid } = useGameContext();

  // Priority: URL parameter > useGameContext > localStorage > default
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameGidFromStorage = typeof window !== 'undefined'
    ? localStorage.getItem('selectedGameGid')
    : null;
  const gameGid = useMemo(
    () => gameGidFromUrl || currentGameGid || gameGidFromStorage || '10000147',
    [gameGidFromUrl, currentGameGid, gameGidFromStorage]
  );

  return (
    <div className="flow-builder-container">
      <Card className="page-header glass-card">
        <Card.Body>
          <h1>流程构建器</h1>
          {gameGid && (
            <p className="text-muted">游戏 GID: {gameGid}</p>
          )}
        </Card.Body>
      </Card>
      <Card className="builder-card glass-card">
        <Card.Body>
          <p>可视化流程构建功能</p>
          <p className="text-muted">当前游戏上下文: GID {gameGid}</p>
        </Card.Body>
      </Card>
    </div>
  );
};

// ✅ 添加 React.memo 优化渲染性能
const FlowBuilderMemo = memo(FlowBuilder);

export default FlowBuilderMemo;
