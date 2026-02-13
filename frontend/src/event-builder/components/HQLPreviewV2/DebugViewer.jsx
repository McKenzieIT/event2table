/**
 * DebugViewer - V2 API调试模式可视化组件
 *
 * 功能：
 * - 显示HQL生成的每个步骤
 * - 展示步骤结果
 * - 时间线视图
 */

import React from 'react';
import './DebugViewer.css';

export default function DebugViewer({ debugTrace }) {
  if (!debugTrace || !debugTrace.steps) {
    return null;
  }

  const { steps = [], events = [], fields = [] } = debugTrace;

  // 步骤图标映射
  const getStepIcon = (step) => {
    const icons = {
      'parse_input': '📥',
      'process_events': '📦',
      'build_fields': '🔧',
      'build_where': '🎯',
      'assemble': '🔨',
      'validate': '✅',
      'analyze_performance': '📊'
    };
    return icons[step] || '⚙️';
  };

  // 步骤名称映射
  const getStepLabel = (step) => {
    const labels = {
      'parse_input': '解析输入',
      'process_events': '处理事件',
      'build_fields': '构建字段',
      'build_where': '构建WHERE条件',
      'assemble': '组装HQL',
      'validate': '语法验证',
      'analyze_performance': '性能分析'
    };
    return labels[step] || step;
  };

  return (
    <div className="debug-viewer">
      <div className="debug-header">
        <h3>🔍 调试模式</h3>
        <span className="step-count">{steps.length} 个步骤</span>
      </div>

      {/* 输入概览 */}
      {(events.length > 0 || fields.length > 0) && (
        <div className="debug-overview">
          <div className="overview-item">
            <strong>事件:</strong> {events.length}
          </div>
          <div className="overview-item">
            <strong>字段:</strong> {fields.length}
          </div>
        </div>
      )}

      {/* 步骤时间线 */}
      <div className="steps-timeline">
        {steps.map((step, index) => (
          <div key={index} className="step-item">
            <div className="step-marker">
              <span className="step-number">{index + 1}</span>
              <div className="step-connector" />
            </div>

            <div className="step-content">
              <div className="step-header">
                <span className="step-icon">{getStepIcon(step.step)}</span>
                <h4 className="step-name">{getStepLabel(step.step)}</h4>
                {step.count !== undefined && (
                  <span className="step-count">({step.count} 项)</span>
                )}
              </div>

              {/* 步骤结果 */}
              {step.result && (
                <div className="step-result">
                  {typeof step.result === 'string' ? (
                    <pre className="result-text">{step.result}</pre>
                  ) : Array.isArray(step.result) ? (
                    <ul className="result-list">
                      {step.result.map((item, i) => (
                        <li key={i}>{String(item)}</li>
                      ))}
                    </ul>
                  ) : (
                    <pre className="result-json">{JSON.stringify(step.result, null, 2)}</pre>
                  )}
                </div>
              )}

              {/* 步骤时间 */}
              {step.duration && (
                <div className="step-duration">
                  ⏱️ {step.duration}ms
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
