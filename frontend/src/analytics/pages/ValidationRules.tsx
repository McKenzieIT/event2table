import React from 'react';
import './ValidationRules.css';

/**
 * 验证规则页面
 * 配置和查看数据验证规则
 */

function ValidationRules(): React.JSX.Element {
  return (
    <div className="validation-rules-container">
      <div className="page-header glass-card">
        <h1>验证规则</h1>
      </div>
      <div className="rules-card glass-card">
        <p>配置和查看数据验证规则</p>
      </div>
    </div>
  );
}

export default ValidationRules;
