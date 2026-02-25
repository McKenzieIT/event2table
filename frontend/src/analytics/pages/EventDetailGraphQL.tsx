import React from 'react';
import { useQuery } from '@apollo/client';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import { Button, Spinner, ErrorState } from '@shared/ui';
import { useGameContext } from '@shared/hooks/useGameContext';
import { GET_EVENT, GET_PARAMETERS } from '@/graphql/queries';
import './EventDetail.css';

/**
 * 事件详情组件 (GraphQL版本)
 *
 * 已迁移到GraphQL:
 * - 使用Apollo Client替代React Query + fetch
 * - 使用GraphQL查询GET_EVENT和GET_PARAMETERS
 * - 自动类型检查（通过GraphQL Code Generator）
 *
 * 最佳实践: 并行加载 + 提前返回
 */
function EventDetailGraphQL() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { currentGameGid } = useGameContext();

  // Priority: URL params > useGameContext > localStorage
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameGid = gameGidFromUrl || currentGameGid || localStorage.getItem('selectedGameGid');

  // 并行加载事件数据和参数数据
  const { data: eventData, loading: eventLoading, error: eventError } = useQuery(GET_EVENT, {
    variables: { id: parseInt(id) },
    skip: !id,
    fetchPolicy: 'cache-and-network',
  });

  const { data: parametersData, loading: paramsLoading, error: paramsError } = useQuery(GET_PARAMETERS, {
    variables: { eventId: parseInt(id), activeOnly: false },
    skip: !id,
    fetchPolicy: 'cache-and-network',
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
                  <span className="badge badge-info">{event.categoryName}</span>
                )}
              </p>
            </div>
          </div>
          <div className="header-actions">
            <Button
              variant="outline-secondary"
              onClick={() => navigate(-1)}
            >
              返回
            </Button>
            <Button
              variant="outline-primary"
              onClick={() => navigate(`/events/${id}/edit?game_gid=${gameGid}`)}
            >
              编辑
            </Button>
          </div>
        </div>
      </div>

      {/* Event Info */}
      <div className="detail-content">
        <div className="info-section glass-card">
          <h3>基本信息</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>事件ID</label>
              <span>{event.id}</span>
            </div>
            <div className="info-item">
              <label>游戏GID</label>
              <span>{event.gameGid}</span>
            </div>
            <div className="info-item">
              <label>事件名称</label>
              <code>{event.eventName}</code>
            </div>
            <div className="info-item">
              <label>中文名称</label>
              <span>{event.eventNameCn || '-'}</span>
            </div>
            <div className="info-item">
              <label>分类</label>
              <span>{event.categoryName || '未分类'}</span>
            </div>
            <div className="info-item">
              <label>源表</label>
              <code>{event.sourceTable || '-'}</code>
            </div>
            <div className="info-item">
              <label>目标表</label>
              <code>{event.targetTable || '-'}</code>
            </div>
            <div className="info-item">
              <label>参数数量</label>
              <span className="badge badge-primary">{event.paramCount || 0}</span>
            </div>
          </div>
        </div>

        {/* Parameters List */}
        <div className="parameters-section glass-card">
          <div className="section-header">
            <h3>参数列表</h3>
            <span className="badge badge-secondary">{parameters.length} 个参数</span>
          </div>

          {parameters.length === 0 ? (
            <div className="empty-state">
              <p>暂无参数</p>
              <Button
                variant="primary"
                onClick={() => navigate(`/events/${id}/parameters/create`)}
              >
                添加参数
              </Button>
            </div>
          ) : (
            <div className="parameters-table-container">
              <table className="parameters-table">
                <thead>
                  <tr>
                    <th>参数名</th>
                    <th>中文名</th>
                    <th>类型</th>
                    <th>JSON路径</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {parameters.map((param) => (
                    <tr key={param.id}>
                      <td>
                        <code>{param.paramName}</code>
                      </td>
                      <td>{param.paramNameCn || '-'}</td>
                      <td>
                        <span className={`badge badge-${getTypeBadgeVariant(param.paramType)}`}>
                          {param.paramType || 'unknown'}
                        </span>
                      </td>
                      <td>
                        <code className="json-path">{param.jsonPath || '-'}</code>
                      </td>
                      <td>
                        <span className={`badge badge-${param.isActive ? 'success' : 'secondary'}`}>
                          {param.isActive ? '启用' : '禁用'}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => navigate(`/parameters/${param.id}/edit`)}
                          >
                            编辑
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * 获取参数类型对应的Badge variant
 */
function getTypeBadgeVariant(type: string): string {
  const variantMap: Record<string, string> = {
    'string': 'info',
    'int': 'success',
    'bigint': 'warning',
    'float': 'primary',
    'boolean': 'danger',
    'datetime': 'info',
    'array': 'primary',
    'map': 'secondary'
  };
  return variantMap[type] || 'secondary';
}

export default EventDetailGraphQL;
