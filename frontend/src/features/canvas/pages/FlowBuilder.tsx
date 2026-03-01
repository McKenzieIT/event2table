import React from 'react';
import './FlowBuilder.css';
import { Card } from '@shared/ui';

/**
 * FlowBuilder Component
 *
 * Visual HQL flow builder page
 *
 * @returns JSX.Element
 */
function FlowBuilder(): JSX.Element {
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
