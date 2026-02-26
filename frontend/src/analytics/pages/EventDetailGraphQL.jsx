/**
 * EventDetailGraphQL - 事件详情页面(GraphQL版本)
 *
 * 完整迁移自EventDetail.jsx,保留所有功能:
 * - 事件基本信息展示
 * - 参数列表展示
 * - 编辑和生成HQL操作
 *
 * 使用GraphQL API替代REST API
 */

import React from 'react';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Button, Spinner, ErrorState, EmptyState } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import { useEvent, useParameters } from '@/graphql/hooks';
import './EventDetail.css';

/**
 * 事件详情组件(GraphQL版本)
 * 显示事件的详细信息
 * 最佳实践: 并行加载 + 提前返回
 *
 * 按钮设计规范:
 * - 纯文字标签（无图标）
 * - 语义化颜色匹配操作类型
 * - 使用统一的Button组件
 */
function EventDetailGraphQL() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { currentGameGid } = useGameContext();

  // Priority: URL params > useGameContext > localStorage
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameGid = gameGidFromUrl || currentGameGid || localStorage.getItem('selectedGameGid');

  // GraphQL queries - 并行加载事件数据和参数数据
  const { data: eventData, loading: eventLoading, error: eventError } = useEvent(Number(id));

  const { data: parametersData, loading: paramsLoading, error: paramsError } = useParameters(Number(id), true);

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

  const event = eventData?.event;
  const parameters = parametersData?.parameters || [];

  if (!event) {
    const isMissingGameContext = !gameGid;
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
              <h2 className="event-title">{event.eventNameCn}</h2>
              <p className="event-subtitle">
                <code>{event.eventName}</code>
                {event.categoryName && (
                  <span className="badge badge-info">
                    {event.categoryName}
                  </span>
                )}
                <span className="badge badge-secondary" style={{ marginLeft: '8px' }}>
                  GraphQL
                </span>
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
                  <strong>{event.eventName}</strong>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">事件中文名</div>
                <div className="info-value">
                  {event.eventNameCn}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">事件分类</div>
                <div className="info-value">
                  {event.categoryName ? (
                    <span className="badge badge-info">
                      {event.categoryName}
                    </span>
                  ) : (
                    <span className="badge badge-secondary">未分类</span>
                  )}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">所属游戏</div>
                <div className="info-value">
                  <span className="font-semibold">GID: {event.gameGid}</span>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">源表</div>
                <div className="info-value">
                  <code>{event.sourceTable || '-'}</code>
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">目标表</div>
                <div className="info-value">
                  <code>{event.targetTable || '-'}</code>
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
                        <th style={{ width: '80px' }}>状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parameters.map(param => (
                        <tr key={param.id}>
                          <td><code>{param.paramName}</code></td>
                          <td>{param.paramNameCn}</td>
                          <td><span className="badge badge-secondary text-xs">{param.paramType}</span></td>
                          <td className="text-muted text-sm">{param.paramDescription || '-'}</td>
                          <td>
                            {param.isActive ? (
                              <span className="badge badge-success text-xs">
                                ✓ 活跃
                              </span>
                            ) : (
                              <span className="badge badge-secondary text-xs">停用</span>
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

export default EventDetailGraphQL;
