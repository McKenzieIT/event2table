// ⚡️ REACT PERF: Optimized with React.memo
// ✅ Performance optimization: Prevent unnecessary re-renders
// See: docs/reports/2026-03-06/REACT-PERFORMANCE-OPTIMIZATION-REPORT.md

import React, { memo } from 'react';
import './ApiDocs.css';

/**
 * API文档页面
 * 迁移自: templates/api_docs.html
 */

function ApiDocs(): React.JSX.Element {
  return (
    <div className="api-docs-container">
      <div className="page-header glass-card">
        <div className="header-content">
          <div className="icon-box">
            <i className="bi bi-book"></i>
          </div>
          <div>
            <h1>API文档</h1>
            <p>RESTful API接口文档</p>
          </div>
        </div>
      </div>

      <div className="docs-content">
        <div className="endpoint-card glass-card">
          <h3>GET /api/games</h3>
          <p>获取游戏列表</p>
        </div>

        <div className="endpoint-card glass-card">
          <h3>GET /api/events</h3>
          <p>获取事件列表</p>
        </div>

        <div className="endpoint-card glass-card">
          <h3>GET /api/categories</h3>
          <p>获取分类列表</p>
        </div>
      </div>
    </div>
  );
}

// ⚡️ REACT PERF: Export with React.memo optimization
const ApiDocsMemo = memo(ApiDocs);
export default ApiDocsMemo;
