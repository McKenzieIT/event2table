import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import './CanvasPage.css';
import CanvasFlow from '../components/CanvasFlow';
import '../components/CanvasFlow.css';
import { Button, Spinner } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import { useGameData } from '../hooks/useGameData';

export default function CanvasPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const gameGidFromUrl = searchParams.get('game_gid');
  const gameIdFromUrl = searchParams.get('game_id');  // 向后兼容

  // 使用 useGameContext 获取游戏上下文
  const { currentGame, currentGameGid: storeGameGid } = useGameContext();

  // 简化优先级逻辑
  const targetGameGid = gameGidFromUrl || gameIdFromUrl || storeGameGid;

  // Use React Query hook
  const { data: queryData, isLoading, error, refetch } = useGameData(targetGameGid);

  // 简化 gameData：优先使用查询数据，回退到当前游戏
  const gameData = queryData || currentGame;

  // Determine error message
  const errorMessage = React.useMemo(() => {
    if (!targetGameGid) {
      return '请先选择游戏';
    }
    if (error) {
      return error.message || '加载游戏数据失败';
    }
    return null;
  }, [error, targetGameGid]);

  // 加载状态
  if (isLoading) {
    return (
      <div className="canvas-page-loading" data-testid="canvas-loading">
        <Spinner size="lg" label="正在加载游戏数据..." />
      </div>
    );
  }

  // 错误状态
  if (errorMessage) {
    return (
      <div className="canvas-page-error" data-testid="canvas-error">
        <h2>加载失败</h2>
        <p>{errorMessage}</p>
        <Button onClick={() => refetch()} variant="primary" data-testid="retry-button">
          重试
        </Button>
        <Button onClick={() => navigate(-1)} variant="secondary" data-testid="back-button">
          返回
        </Button>
      </div>
    );
  }

  // 正常状态
  return (
    <ReactFlowProvider>
      <div className="canvas-page" data-testid="canvas-page">
        <CanvasFlow gameData={gameData} />
      </div>
    </ReactFlowProvider>
  );
}
