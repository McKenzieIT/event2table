// ⚡ REACT PERF: Component fully optimized
// - React.memo: Prevents unnecessary re-renders when props don't change
// - useMemo: Caches stats grid rendering
// - useCallback: Stabilizes retry handler

import { NavLinkWithGameContext } from '@shared/components';
import { SelectGamePrompt, ErrorState } from '@shared/ui';
import { useQuery } from '@tanstack/react-query';
import React, { useMemo, useCallback } from 'react';
import { useOutletContext } from 'react-router-dom';
import './ParameterAnalysis.css';

/**
 * 参数分析页面
 * 分析参数的使用情况和统计信息
 * 需要游戏上下文
 */

interface ParameterStats {
  total: number;
  common: number;
  thisMonth: number;
  unused: number;
}

interface GameContext {
  currentGame: {
    gid: number;
    name: string;
  } | null;
}

interface StatCard {
  icon: string;
  iconClass: string;
  value: number;
  label: string;
}

const ParameterAnalysis: React.FC = () => {
  const { currentGame } = useOutletContext<GameContext>();

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数分析需要先选择游戏" />;
  }

  const { data: stats = {} as ParameterStats, isLoading, error } = useQuery<ParameterStats>({
    queryKey: ['parameter-stats', currentGame.gid],
    queryFn: async () => {
      const response = await fetch(`/api/parameters/stats?game_gid=${currentGame.gid}`);
      if (!response.ok) throw new Error('加载失败');
      return response.json();
    },
    enabled: !!currentGame // Only execute when currentGame exists
  });

  // useCallback: Stabilize retry handler
  const handleRetry = useCallback(() => {
    window.location.reload();
  }, []);

  // useMemo: Cache stats cards configuration
  const statsCards = useMemo<StatCard[]>(() => [
    {
      icon: 'bi-list-check',
      iconClass: '',
      value: stats.total || 0,
      label: '总参数数'
    },
    {
      icon: 'bi-stars',
      iconClass: 'success',
      value: stats.common || 0,
      label: '公共参数'
    },
    {
      icon: 'bi-calendar',
      iconClass: 'warning',
      value: stats.thisMonth || 0,
      label: '本月新增'
    },
    {
      icon: 'bi-exclamation-triangle',
      iconClass: 'danger',
      value: stats.unused || 0,
      label: '未使用参数'
    }
  ], [stats]);

  // useMemo: Cache skeleton loading cards
  const loadingCards = useMemo(() =>
    [1, 2, 3, 4].map(i => (
      <div key={i} className="stat-card glass-card" style={{ opacity: 0.5 }}>
        <div className="stat-icon">
          <i className="bi bi-list-check"></i>
        </div>
        <div className="stat-content">
          <h3>--</h3>
          <p>加载中...</p>
        </div>
      </div>
    )),
  []);

  if (isLoading) {
    return (
      <div className="parameter-analysis-container">
        <div className="page-header">
          <h1>参数分析</h1>
        </div>
        <div className="stats-grid">
          {loadingCards}
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState message={(error as Error).message} onRetry={handleRetry} />;
  }

  return (
    <div className="parameter-analysis-container">
      <div className="page-header">
        <h1>参数分析</h1>
        <NavLinkWithGameContext to="/parameters" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回
        </NavLinkWithGameContext>
      </div>

      <div className="stats-grid">
        {statsCards.map((card, index) => (
          <div key={index} className="stat-card glass-card">
            <div className={`stat-icon ${card.iconClass}`}>
              <i className={`bi ${card.icon}`}></i>
            </div>
            <div className="stat-content">
              <h3>{card.value}</h3>
              <p>{card.label}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default React.memo(ParameterAnalysis);
