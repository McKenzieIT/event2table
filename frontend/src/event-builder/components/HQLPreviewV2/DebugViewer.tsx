/**
 * DebugViewer组件
 *
 * 显示HQL生成的调试信息
 */

import React from 'react';
import './DebugViewer.css';

interface DebugStep {
  step: string;
  result: any;
  count?: number;
}

interface DebugTrace {
  hql: string;
  steps: DebugStep[];
  events: any[];
  fields: any[];
}

interface DebugViewerProps {
  trace: DebugTrace;
}

export const DebugViewer: React.FC<DebugViewerProps> = ({ trace }) => {
  return (
    <div className="debug-viewer">
      <div className="debug-header">
        <h4>Debug Information</h4>
      </div>

      {/* Steps */}
      <div className="debug-section">
        <h5>Generation Steps</h5>
        <div className="debug-steps">
          {trace.steps.map((step, index) => (
            <div key={index} className="debug-step">
              <div className="step-number">Step {index + 1}</div>
              <div className="step-name">{step.step}</div>
              <div className="step-result">
                {typeof step.result === 'string' ? (
                  <pre>{step.result}</pre>
                ) : Array.isArray(step.result) ? (
                  <div className="result-array">
                    {step.result.map((item, i) => (
                      <div key={i} className="array-item">
                        {typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)}
                      </div>
                    ))}
                    {step.count !== undefined && (
                      <div className="array-count">Total: {step.count} items</div>
                    )}
                  </div>
                ) : (
                  <pre>{JSON.stringify(step.result, null, 2)}</pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Input Data */}
      <div className="debug-section">
        <h5>Input Data</h5>
        <div className="debug-inputs">
          <div className="debug-input">
            <strong>Events ({trace.events.length})</strong>
            <pre>{JSON.stringify(trace.events, null, 2)}</pre>
          </div>
          <div className="debug-input">
            <strong>Fields ({trace.fields.length})</strong>
            <pre>{JSON.stringify(trace.fields, null, 2)}</pre>
          </div>
        </div>
      </div>

      {/* Final HQL */}
      <div className="debug-section">
        <h5>Final HQL</h5>
        <pre className="debug-hql">{trace.hql}</pre>
      </div>
    </div>
  );
};

export default DebugViewer;
