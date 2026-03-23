// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * RequireGameContext Component
 *
 * A wrapper component that checks if a game context exists.
 * If no game is selected, displays a prompt to navigate to the games list.
 *
 * @example
 * // In Event Node Builder
 * <RequireGameContext gameId={currentGame?.gid}>
 *   <EventNodeBuilderContent />
 * </RequireGameContext>
 *
 * @example
 * // In Canvas
 * <RequireGameContext gameId={currentGame?.gid}>
 *   <CanvasContent />
 * </RequireGameContext>
 */

import { Button } from '@shared/ui';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './RequireGameContext.css';

interface RequireGameContextProps {
  children: React.ReactNode;
  gameId?: string | number | null;
}

/**
 * RequireGameContext Component
 *
 * Renders children if gameId exists, otherwise shows a prompt
 * to navigate to the games list.
 */
export function RequireGameContext({ children, gameId }: RequireGameContextProps): React.JSX.Element {
  const navigate = useNavigate();

  if (!gameId) {
    return (
      <div className="require-game-context">
        <div className="prompt-container glass-card">
          <h2>🎮 请先选择游戏</h2>
          <p>您需要先选择一个游戏才能使用此功能。</p>
          <Button
            variant="primary"
            onClick={() => navigate('/games')}
          >
            前往游戏列表
          </Button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default RequireGameContext;
