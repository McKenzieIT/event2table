import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@shared/ui';

interface LoadingStateProps {
  onNavigateToDashboard?: () => void;
}

export const LoadingState = React.memo(function LoadingState({ onNavigateToDashboard }: LoadingStateProps): React.JSX.Element {
  const navigate = useNavigate();

  const handleNavigate = () => {
    if (onNavigateToDashboard) {
      onNavigateToDashboard();
    } else {
      navigate('/');
    }
  };

  return (
    <div className="event-node-builder-loading" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>
        <i className="bi bi-controller"></i>
      </div>
      <h2>请先选择游戏</h2>
      <p style={{ color: 'rgba(255,255,255,0.6)', marginBottom: '1.5rem' }}>
        事件节点构建器需要游戏上下文才能正常工作
      </p>
      <Button variant="primary" onClick={handleNavigate}>
        前往仪表板
      </Button>
    </div>
  );
});

LoadingState.displayName = 'LoadingState';