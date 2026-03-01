import React from 'react';
import './LogDetail.css';

/**
 * 日志详情页面组件
 * 显示日志的详细信息
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

export default LogDetail;
