import React from 'react';
import { Link } from 'react-router-dom';
import { Card, Button } from '@shared/ui';
import './NotFound.css';

/**
 * 404 Not Found Page
 *
 * Displayed when user navigates to a non-existent route
 */
function NotFound() {
  return (
    <div className="not-found-container">
      <Card className="not-found-content glass-card">
        <div className="cyber-card__body">
          <div className="error-code">404</div>
          <h1>页面未找到</h1>
          <p className="text-secondary">抱歉，您访问的页面不存在。</p>

          <div className="not-found-actions">
            <Button variant="primary" onClick={() => window.location.href = '/'}>
              <i className="bi bi-house" aria-hidden="true"></i>
              返回首页
            </Button>
            <Button variant="secondary" onClick={() => window.location.href = '/games'}>
              <i className="bi bi-controller" aria-hidden="true"></i>
              游戏管理
            </Button>
          </div>

          <div className="help-text">
            <p>需要帮助？</p>
            <ul>
              <li>检查URL拼写是否正确</li>
              <li>使用导航菜单浏览可用页面</li>
              <li>联系管理员报告此问题</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default React.memo(NotFound);
