import React from 'react';
import { useOutletContext, useSearchParams } from 'react-router-dom';
import { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import './CanvasPage.css';
import CanvasFlow from '../components/CanvasFlow';
import '../components/CanvasFlow.css';
import { Button, Spinner } from '@shared/ui';
import { useGameData } from '../hooks/useGameData';

export default function CanvasPage() {
  const { currentGame } = useOutletContext() || {};
  const [searchParams] = useSearchParams();

  // Determine targetGameGid from URL/context/window.gameData
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameIdFromUrl = searchParams.get('game_id');  // 向后兼容

  // 优先级: game_gid > game_id (legacy)
  let targetGameGid = gameGidFromUrl || gameIdFromUrl;

  if (!targetGameGid && currentGame) {
    targetGameGid = currentGame.gid || currentGame.id;
  }

  if (!targetGameGid && window.gameData) {
    targetGameGid = window.gameData.gid || window.gameData.id;
  }

  // Use React Query hook
  const { data: queryData, isLoading, error, refetch } = useGameData(targetGameGid);

  // Convert to expected format for backward compatibility
  const gameData = React.useMemo(() => {
    // Check if window.gameData already has the data
    if (window.gameData && window.gameData.gid == targetGameGid) {
      return window.gameData;
    }

    // Convert query data to expected format
    if (queryData) {
      const data = {
        id: queryData.id,      // 保留向后兼容
        gid: queryData.gid,    // 主键
        name: queryData.name,
        ods_db: queryData.ods_db
      };
      // Update window.gameData for backward compatibility
      window.gameData = data;
      console.log('[CanvasPage] Game data loaded:', data);
      return data;
    }

    return null;
  }, [queryData, targetGameGid]);

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
        <Button onClick={() => window.history.back()} variant="secondary" data-testid="back-button">
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
