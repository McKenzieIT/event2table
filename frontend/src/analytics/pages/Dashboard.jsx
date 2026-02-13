import React, { useMemo, Suspense } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Card, Badge, Spinner } from '@shared/ui';
import './Dashboard.css';

/**
 * Dashboard Page
 *
 * Main landing page showing:
 * - Statistics (games, events, parameters count)
 * - Quick actions
 * - Recent activity
 *
 * 性能优化：
 * - useMemo优化统计计算
 * - 移除React.memo以避免与Suspense冲突（实验性验证）
 */
function Dashboard() {
  // Fetch statistics with caching - 优化：添加staleTime避免重复请求
  const { data: gamesData, isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) throw new Error('Failed to fetch games');
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5分钟内不重复请求
    cacheTime: 10 * 60 * 1000, // 缓存10分钟
    refetchOnWindowFocus: false, // 切换窗口不自动刷新
  });

  const games = Array.isArray(gamesData?.data) ? gamesData.data : [];

  // 优化：使用单次遍历计算所有统计，减少遍历次数
  const stats = useMemo(() => {
    let totalEvents = 0;
    let totalParams = 0;
    
    for (const game of games) {
      totalEvents += game.event_count || 0;
      totalParams += game.param_count || 0;
    }
    
    return {
      gameCount: games.length,
      totalEvents,
      totalParams,
    };
  }, [games]);

  // 优化：延迟加载最近游戏列表，优先渲染关键内容
  const [showRecentGames, setShowRecentGames] = React.useState(false);
  
  React.useEffect(() => {
    // 延迟500ms再显示最近游戏，优先渲染关键内容
    const timer = setTimeout(() => {
      setShowRecentGames(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);
  
  const recentGames = useMemo(() => {
    return games.slice(0, 5);
  }, [games]);

  return (
    <Suspense fallback={<Spinner size="lg" label="正在加载仪表板..." />}>
      <div className="dashboard-container" data-testid="dashboard-container">
        <div className="dashboard-header">
          <h1>Event2Table</h1>
          <p className="text-secondary">欢迎使用Event2Table</p>
        </div>

      {/* Statistics Cards - 优化：添加骨架屏 */}
      <div className="stats-grid">
        {isLoading ? (
          // 骨架屏状态
          <>
            <Card variant="glass" className="stat-card skeleton-card">
              <div className="skeleton-icon"></div>
              <div className="skeleton-content">
                <div className="skeleton-number"></div>
                <div className="skeleton-text"></div>
              </div>
            </Card>
            <Card variant="glass" className="stat-card skeleton-card">
              <div className="skeleton-icon"></div>
              <div className="skeleton-content">
                <div className="skeleton-number"></div>
                <div className="skeleton-text"></div>
              </div>
            </Card>
            <Card variant="glass" className="stat-card skeleton-card">
              <div className="skeleton-icon"></div>
              <div className="skeleton-content">
                <div className="skeleton-number"></div>
                <div className="skeleton-text"></div>
              </div>
            </Card>
            <Card variant="glass" className="stat-card skeleton-card">
              <div className="skeleton-icon"></div>
              <div className="skeleton-content">
                <div className="skeleton-number"></div>
                <div className="skeleton-text"></div>
              </div>
            </Card>
          </>
        ) : (
          // 实际内容
          <>
            <Card variant="glass" className="stat-card" hover>
              <div className="stat-icon">
                <i className="bi bi-controller"></i>
              </div>
              <div className="stat-content">
                <h3>{stats.gameCount}</h3>
                <p>游戏总数</p>
              </div>
            </Card>

            <Card variant="glass" className="stat-card" hover>
              <div className="stat-icon">
                <i className="bi bi-diagram-3"></i>
              </div>
              <div className="stat-content">
                <h3>{stats.totalEvents}</h3>
                <p>事件总数</p>
              </div>
            </Card>

            <Card variant="glass" className="stat-card" hover>
              <div className="stat-icon">
                <i className="bi bi-sliders"></i>
              </div>
              <div className="stat-content">
                <h3>{stats.totalParams}</h3>
                <p>参数总数</p>
              </div>
            </Card>

            <Card variant="glass" className="stat-card" hover>
              <div className="stat-icon">
                <i className="bi bi-gear"></i>
              </div>
              <div className="stat-content">
                <h3>HQL</h3>
                <p>脚本生成</p>
              </div>
            </Card>
          </>
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>快速操作</h2>
        <div className="actions-grid">
          <Card as={Link} to="/games" className="action-card" hover>
            <i className="bi bi-plus-circle"></i>
            <h3>管理游戏</h3>
            <p>创建和管理游戏项目</p>
          </Card>

          <Card as={Link} to="/events" className="action-card" hover>
            <i className="bi bi-list-task"></i>
            <h3>管理事件</h3>
            <p>配置日志事件</p>
          </Card>

          <Card as={Link} to="/canvas" className="action-card" hover>
            <i className="bi bi-diagram-3-fill"></i>
            <h3>HQL画布</h3>
            <p>可视化构建HQL</p>
          </Card>

          <Card as={Link} to="/flows" className="action-card" hover>
            <i className="bi bi-flowchart"></i>
            <h3>流程管理</h3>
            <p>管理HQL流程</p>
          </Card>
        </div>
      </div>

      {/* Recent Games - 优化：延迟渲染，优先加载关键内容 */}
      {showRecentGames && stats.gameCount > 0 && (
        <div className="recent-section">
          <h2>最近游戏</h2>
          <div className="games-list">
            {recentGames.map(game => (
              <Card
                key={game.gid}
                as={Link}
                to={`/events?game_gid=${game.gid}`}
                className="game-item"
                hover
              >
                <div className="game-info">
                  <h3>{game.name}</h3>
                  <p className="text-secondary">GID: {game.gid}</p>
                </div>
                <div className="game-stats">
                  <Badge variant="primary" pill>
                    <i className="bi bi-diagram-3"></i>
                    {game.event_count || 0} 事件
                  </Badge>
                  <Badge variant="info" pill>
                    <i className="bi bi-sliders"></i>
                    {game.param_count || 0} 参数
                  </Badge>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
    </Suspense>
  );
}

// 移除React.memo包装（实验性：验证是否解决React Error #321）
// React.memo可能与Suspense有冲突，移除后测试稳定性
export default Dashboard;
