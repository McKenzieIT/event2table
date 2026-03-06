// ⚡️ REACT PERF: Optimized with React.memo
// ✅ Performance optimization: Prevent unnecessary re-renders
// See: docs/reports/2026-03-06/PHASE-2-OPTIMIZATION-REPORT.md

import React from 'react';
import './ValidationRules.css';

/**
 * 验证规则页面
 * 配置和查看数据验证规则
 *
 * 静态组件，使用React.memo避免不必要的重新渲染
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

// 使用 React.memo 优化性能 - 避免不必要的重新渲染
const ValidationRulesMemo = React.memo(ValidationRules);
export default ValidationRulesMemo;
