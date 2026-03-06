// ⚡️ REACT PERF: Optimized with React.memo, useCallback
// ✅ Performance optimization: Prevent unnecessary re-renders
// See: docs/reports/2026-03-06/PHASE-2-OPTIMIZATION-REPORT.md

import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button } from '@shared/ui';
import './NotFound.css';

/**
 * 404 Not Found Page
 *
 * Displayed when user navigates to a non-existent route
 *
 * @example
 * import { NotFound } from '@analytics/pages';
 *
 * <Route path="*" element={<NotFound />} />
 *
 * 性能优化:
 * - React.memo: 避免父组件更新时重新渲染
 * - useCallback: 稳定导航函数引用
 */
function NotFound(): React.JSX.Element {
  // 使用 useCallback 稳定导航函数引用
  const handleGoHome = useCallback(() => {
    window.location.href = '/';
  }, []);

  const handleGoToGames = useCallback(() => {
    window.location.href = '/games';
  }, []);

  return (
    <div className="not-found-container">
      <Card className="not-found-content glass-card">
        <div className="cyber-card__body">
          <div className="error-code">404</div>
          <h1>页面未找到</h1>
          <p className="text-secondary">抱歉，您访问的页面不存在。</p>

          <div className="not-found-actions">
            <Button variant="primary" onClick={handleGoHome}>
              <i className="bi bi-house" aria-hidden="true"></i>
              返回首页
            </Button>
            <Button variant="secondary" onClick={handleGoToGames}>
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

// 使用 React.memo 优化性能 - 避免不必要的重新渲染
const NotFoundMemo = React.memo(NotFound);
export default NotFoundMemo;
