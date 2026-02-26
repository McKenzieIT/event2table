import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Button, Spinner, ErrorState, EmptyState } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import './EventDetail.css';

/**
 * 事件详情组件
 * 显示事件的详细信息
 * 最佳实践: 并行加载 + 提前返回
 *
 * 按钮设计规范:
 * - 纯文字标签（无图标）
 * - 语义化颜色匹配操作类型
 * - 使用统一的Button组件
 */
function EventDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { currentGameGid } = useGameContext();

  // Priority: URL params > useGameContext > localStorage
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameGid = gameGidFromUrl || currentGameGid || localStorage.getItem('selectedGameGid');

  // 并行加载事件数据和参数数据
  const { data: eventData, isLoading: eventLoading, error: eventError } = useQuery({
    queryKey: ['event', id, gameGid],
    queryFn: async () => {
      // API需要game_gid参数或从session获取
      const url = gameGid
        ? `/api/events/${id}?game_gid=${gameGid}`
        : `/api/events/${id}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('加载事件失败');
      return response.json();
    },
    enabled: !!id
  });

  const { data: parametersData, isLoading: paramsLoading, error: paramsError } = useQuery({
    queryKey: ['event', id, 'parameters'],
    queryFn: async () => {
      const response = await fetch(`/api/events/${id}/parameters`);
      if (!response.ok) throw new Error('加载参数失败');
      return response.json();
    },
    enabled: !!id
  });

  // 合并加载和错误状态
  const isLoading = eventLoading || paramsLoading;
  const loadingError = eventError || paramsError;

  // 提前返回优化
  if (isLoading) {
    return (
      <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  if (loadingError) {
    return <ErrorState message={loadingError.message} onRetry={() => window.location.reload()} />;
  }

  const event = eventData?.data;
  const parameters = parametersData?.data || [];

  if (!event) {
    const isMissingGameContext = eventData?.error === 'Game context required' || !gameGid;
    return (
      <div className="error">
        <p>{isMissingGameContext ? '请先选择游戏' : '事件不存在'}</p>
        <Button variant="primary" onClick={() => navigate(-1)}>
          返回
        </Button>
      </div>
    );
  }

  return (
    <div className="event-detail-container">
      {/* Page Header */}
      <div className="detail-header glass-card">
        <div className="detail-header-gradient"></div>
        <div className="detail-header-content">
          <div className="header-left">
            <div className="detail-header-icon">
              <span>事件</span>
            </div>
            <div>
              <h2 className="event-title">{event.event_name_cn}</h2>
              <p className="event-subtitle">
                <code>{event.event_name}</code>
                {event.category_name && (
                  <span className="badge badge-info">
                    {event.category_name}
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="header-actions">
            <Link to={`/events/${id}/edit`}>
              <Button variant="outline-primary">
                编辑
              </Button>
            </Link>
            <Link to="/hql/generate">
              <Button variant="primary">
                生成HQL
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Two-Column Detail Grid */}
      <div className="detail-grid-two-col">
        {/* Left Column: Basic Info */}
        <div className="left-column">
          {/* Basic Info Card */}
          <div className="glass-card basic-info-card">
            <div className="card-header">
              <div className="header-icon">
                <span>📋</span>
                <h5>基本信息</h5>
              </div>
            </div>
            <div className="card-content">
              <div className="info-item">
                <div className="info-label">事件名</div>
                <div className="info-value">
                  <strong>{event.event_name}</strong>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">事件中文名</div>
                <div className="info-value">
                  {event.event_name_cn}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">事件分类</div>
                <div className="info-value">
                  {event.category_name ? (
                    <span className="badge badge-info">
                      {event.category_name}
                    </span>
                  ) : (
                    <span className="badge badge-secondary">未分类</span>
                  )}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">所属游戏</div>
                <div className="info-value">
                  <span className="font-semibold">{event.game_name}</span>
                  <span className="text-muted text-sm">(GID: {event.gid})</span>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">源表</div>
                <div className="info-value">
                  <code>{event.source_table}</code>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">目标表</div>
                <div className="info-value">
                  <code>{event.target_table}</code>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">创建时间</div>
                <div className="info-value text-muted">
                  {event.created_at}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions Card */}
          <div className="glass-card quick-actions-card">
            <div className="card-header">
              <div className="header-icon">
                <span>⚡</span>
                <h5>快速操作</h5>
              </div>
            </div>
            <div className="card-content">
              <div className="actions-list">
                <Link to={`/events/${id}/edit`}>
                  <Button variant="primary" style={{ width: '100%', marginBottom: 'var(--space-2)' }}>
                    编辑事件信息
                  </Button>
                </Link>
                <Link to="/hql/generate">
                  <Button variant="success" style={{ width: '100%', marginBottom: 'var(--space-2)' }}>
                    生成此事件的HQL
                  </Button>
                </Link>
                <Link to="/events">
                  <Button variant="outline-secondary" style={{ width: '100%' }}>
                    返回事件列表
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Parameters */}
        <div className="right-column">
          <div className="glass-card parameters-card">
            <div className="card-header">
              <div className="header-left">
                <div className="header-icon">
                  <span>📊</span>
                  <h5>参数字段列表</h5>
                  <span className="badge badge-primary">{parameters.length} 个字段</span>
                </div>
              </div>
            </div>
            <div className="card-content">
              {parameters.length > 0 ? (
                <div className="table-responsive-wrapper">
                  <table className="oled-table">
                    <thead>
                      <tr>
                        <th>参数名</th>
                        <th>参数中文名</th>
                        <th>类型</th>
                        <th>描述</th>
                        <th style={{ width: '80px' }}>公参</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parameters.map(param => (
                        <tr key={param.id}>
                          <td><code>{param.param_name}</code></td>
                          <td>{param.param_name_cn}</td>
                          <td><span className="badge badge-secondary text-xs">{param.param_type}</span></td>
                          <td className="text-muted text-sm">{param.param_description || '-'}</td>
                          <td>
                            {param.is_common_param ? (
                              <span className="badge badge-success text-xs">
                                ✓ 是
                              </span>
                            ) : (
                              <span className="badge badge-secondary text-xs">否</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <EmptyState
                  icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
                  title="此事件暂无参数字段"
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EventDetail;
