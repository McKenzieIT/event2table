import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import { NavLinkWithGameContext } from '@shared/components';
import './ParameterAnalysis.css';

/**
 * 参数分析页面
 * 分析参数的使用情况和统计信息
 * 需要游戏上下文
 */
function ParameterAnalysis() {
  const { currentGame } = useOutletContext();

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数分析需要先选择游戏" />;
  }

  const { data: stats = {}, isLoading } = useQuery({
    queryKey: ['parameter-stats', currentGame.gid],
    queryFn: async () => {
      const response = await fetch(`/api/parameters/stats?game_gid=${currentGame.gid}`);
      if (!response.ok) throw new Error('加载失败');
      return response.json();
    },
    enabled: !!currentGame // Only execute when currentGame exists
  });

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
        <div className="stat-card glass-card">
          <div className="stat-icon">
            <i className="bi bi-list-check"></i>
          </div>
          <div className="stat-content">
            <h3>{stats.total || 0}</h3>
            <p>总参数数</p>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon success">
            <i className="bi bi-stars"></i>
          </div>
          <div className="stat-content">
            <h3>{stats.common || 0}</h3>
            <p>公共参数</p>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon warning">
            <i className="bi bi-calendar"></i>
          </div>
          <div className="stat-content">
            <h3>{stats.thisMonth || 0}</h3>
            <p>本月新增</p>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-icon danger">
            <i className="bi bi-exclamation-triangle"></i>
          </div>
          <div className="stat-content">
            <h3>{stats.unused || 0}</h3>
            <p>未使用参数</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParameterAnalysis;
