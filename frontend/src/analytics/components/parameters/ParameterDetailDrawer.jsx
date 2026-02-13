import React, { useState, useEffect } from 'react';
import { fetchParameterDetails } from '@shared/api/parameters';
import './ParameterDetailDrawer.css';

/**
 * 参数详情侧边抽屉组件
 * 类似模态框,从右侧滑出
 */
export default function ParameterDetailDrawer({ show, paramName, gameGid, onClose }) {
  const [details, setDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 加载参数详情
  useEffect(() => {
    if (!show || !paramName || !gameGid) return;

    setIsLoading(true);
    setError(null);

    fetchParameterDetails(paramName, gameGid)
      .then(response => {
        if (response.success) {
          setDetails(response.data);
        } else {
          setError(response.message || '加载失败');
        }
      })
      .catch(err => {
        console.error('Failed to fetch parameter details:', err);
        setError(err.message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [show, paramName, gameGid]);

  // ESC键关闭
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && show) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [show, onClose]);

  if (!show) return null;

  return (
    <>
      {/* 背景遮罩 */}
      <div
        className={`drawer-backdrop ${show ? 'show' : ''}`}
        onClick={onClose}
      ></div>

      {/* 抽屉内容 */}
      <div className={`drawer drawer-right ${show ? 'show' : ''}`}>
        <div className="drawer-header">
          <h4>
            <i className="bi bi-sliders"></i>
            参数详情
          </h4>
          <button className="drawer-close" onClick={onClose}>
            <i className="bi bi-x"></i>
          </button>
        </div>

        <div className="drawer-body">
          {isLoading && (
            <div className="drawer-loading">
              <div className="spinner-border spinner-border-sm text-primary"></div>
              <span>加载中...</span>
            </div>
          )}

          {error && (
            <div className="drawer-error">
              <i className="bi bi-exclamation-triangle"></i>
              <span>{error}</span>
            </div>
          )}

          {details && !isLoading && !error && (
            <>
              {/* 参数基本信息 */}
              <div className="drawer-section">
                <h5>基本信息</h5>
                <div className="info-grid">
                  <div className="info-item">
                    <label>参数名</label>
                    <code>{details.param_name}</code>
                  </div>
                  <div className="info-item">
                    <label>中文名</label>
                    <span>{details.param_name_cn || '-'}</span>
                  </div>
                  <div className="info-item">
                    <label>数据类型</label>
                    <span className={`badge type-${details.base_type}`}>
                      {details.base_type}
                    </span>
                  </div>
                  <div className="info-item">
                    <label>使用事件数</label>
                    <span>{details.events?.length || 0}</span>
                  </div>
                </div>
              </div>

              {/* 事件使用列表 */}
              <div className="drawer-section">
                <h5>事件使用情况</h5>
                {details.events && details.events.length > 0 ? (
                  <div className="events-list">
                    {details.events.map(event => (
                      <div key={event.id} className="event-item glass-card">
                        <div className="event-info">
                          <div>
                            <code>{event.event_name}</code>
                            <span className="event-cn-name">{event.event_name_cn}</span>
                          </div>
                          <div className="event-meta">
                            <span className="badge bg-secondary">{event.category || '未分类'}</span>
                            <span className="text-muted">版本: {event.version || 1}</span>
                          </div>
                        </div>
                        <div className="event-actions">
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => window.location.href = `/#/events/${event.event_id}`}
                          >
                            <i className="bi bi-arrow-right-circle"></i>
                            查看事件
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <i className="bi bi-inbox"></i>
                    <p>该参数未被任何事件使用</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        <div className="drawer-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            关闭
          </button>
        </div>
      </div>
    </>
  );
}
