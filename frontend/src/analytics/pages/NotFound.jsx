import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '@shared/ui';
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
        <Card.Body>
          <div className="error-code">404</div>
          <h1>页面未找到</h1>
          <p className="text-secondary">抱歉，您访问的页面不存在。</p>

          <div className="not-found-actions">
            <Link to="/">
              <Button variant="primary">
                <i className="bi bi-house"></i>
                返回首页
              </Button>
            </Link>
            <Link to="/games">
              <Button variant="ghost">
                <i className="bi bi-controller"></i>
                游戏管理
              </Button>
            </Link>
          </div>

          <div className="help-text">
            <p>需要帮助？</p>
            <ul>
              <li>检查URL拼写是否正确</li>
              <li>使用导航菜单浏览可用页面</li>
              <li>联系管理员报告此问题</li>
            </ul>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
}

export default React.memo(NotFound);
