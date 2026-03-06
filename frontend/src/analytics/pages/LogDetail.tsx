// ⚡️ REACT PERF: Optimized with React.memo
// ✅ Performance optimization: Prevent unnecessary re-renders
// See: docs/reports/2026-03-06/PHASE-2-OPTIMIZATION-REPORT.md

import React from 'react';
import './LogDetail.css';

/**
 * 日志详情页面组件
 * 显示日志的详细信息
 *
 * 静态组件，使用React.memo避免不必要的重新渲染
 */
function LogDetail() {
  return (
    <div className="log-detail-container">
      <div className="page-header glass-card">
        <h1>日志详情</h1>
      </div>
      <div className="log-card glass-card">
        <p>查看详细日志信息</p>
      </div>
    </div>
  );
}

// 使用 React.memo 优化性能 - 避免不必要的重新渲染
const LogDetailMemo = React.memo(LogDetail);
export default LogDetailMemo;
