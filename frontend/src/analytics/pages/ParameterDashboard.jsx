import React from 'react';
import './ParameterDashboard.css';

function ParameterDashboard() {
  return (
    <div className="param-dashboard-container" data-testid="dashboard">
      <div className="page-header glass-card">
        <h1>参数统计</h1>
      </div>
      <div className="dashboard-cards">
        <div className="stat-card glass-card">
          <h3>参数分布</h3>
        </div>
      </div>
    </div>
  );
}
export default ParameterDashboard;
