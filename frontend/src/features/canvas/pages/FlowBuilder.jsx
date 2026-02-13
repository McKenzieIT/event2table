import React from 'react';
import './FlowBuilder.css';
import { Card } from '@shared/ui';

/**
 * 流程构建器页面
 * 可视化构建HQL流程
 */
function FlowBuilder() {
  return (
    <div className="flow-builder-container">
      <Card className="page-header glass-card">
        <Card.Body>
          <h1>流程构建器</h1>
        </Card.Body>
      </Card>
      <Card className="builder-card glass-card">
        <Card.Body>
          <p>可视化流程构建功能</p>
        </Card.Body>
      </Card>
    </div>
  );
}
export default FlowBuilder;
