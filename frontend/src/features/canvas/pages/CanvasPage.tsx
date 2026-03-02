// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import './CanvasPage.css';
import CanvasFlow from '../components/CanvasFlow';
import '../components/CanvasFlow.css';
import { Button, Spinner } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import { useGameData } from '../hooks/useGameData';

/**
 * CanvasPage Component
 *
 * Main page for the Canvas flow builder with game context management
 *
 * @returns JSX.Element
 */
export default function CanvasPage(): JSX.Element {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const gameGidFromUrl = searchParams.get('game_gid');
  const gameIdFromUrl = searchParams.get('game_id');  // Backward compatibility

  // Use useGameContext to get game context
  const { currentGame, currentGameGid: storeGameGid } = useGameContext();

  // Simplified priority logic
  const targetGameGid = gameGidFromUrl || gameIdFromUrl || storeGameGid;

  // Use React Query hook
  const { data: queryData, isLoading, error, refetch } = useGameData(targetGameGid);

  // Simplify gameData: prefer query data, fallback to current game
  const gameData = queryData || currentGame;

  // Determine error message
  const errorMessage = useMemo(() => {
    if (!targetGameGid) {
      return '请先选择游戏';
    }
    if (error?.message === '请先创建游戏') {
      return '暂无游戏，请先创建游戏';
    }
    if (error) {
      return error.message || '加载游戏数据失败';
    }
    return null;
  }, [error, targetGameGid]);

  // Check if this is a "no games" state
  const isNoGamesState = error?.message === '请先创建游戏' || errorMessage === '暂无游戏，请先创建游戏';

  // Loading state
  if (isLoading) {
    return (
      <div className="canvas-page-loading" data-testid="canvas-loading">
        <Spinner size="lg" label="正在加载游戏数据..." />
      </div>
    );
  }

  // Error state
  if (errorMessage) {
    return (
      <div className="canvas-page-error" data-testid="canvas-error">
        <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>
          <i className="bi bi-exclamation-triangle-fill"></i>
        </div>
        <h2>{isNoGamesState ? '暂无游戏' : '加载失败'}</h2>
        <p>{errorMessage}</p>
        {isNoGamesState ? (
          <Button
            onClick={() => navigate('/')}
            variant="primary"
            data-testid="create-game-button"
          >
            前往创建游戏
          </Button>
        ) : (
          <>
            <Button onClick={() => refetch()} variant="primary" data-testid="retry-button">
              重试
            </Button>
            <Button onClick={() => navigate(-1)} variant="secondary" data-testid="back-button">
              返回
            </Button>
          </>
        )}
      </div>
    );
  }

  // Normal state
  return (
    <ReactFlowProvider>
      <div className="canvas-page" data-testid="canvas-page">
        <CanvasFlow gameData={gameData} />
      </div>
    </ReactFlowProvider>
  );
}
