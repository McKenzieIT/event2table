// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from 'react';
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

export default ApiDocs;
