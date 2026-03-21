import React from 'react';
import { Card, Spinner } from '@shared/ui';

const SpinnerShowcase: React.FC = React.memo(() => {
  return (
    <section className="showcase-section">
      <h2 className="section-title">Spinner</h2>
      <Card>
        <Card.Body>
          <p style={{ marginBottom: '24px', color: 'var(--text-secondary, #94A3B8)' }}>
            Loading indicators in different sizes:
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '48px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <Spinner size="sm" />
              <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Small</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <Spinner size="md" />
              <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Medium</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <Spinner size="lg" />
              <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Large</span>
            </div>
          </div>
          <div style={{ marginTop: '32px' }}>
            <Spinner size="md" label="Loading data..." />
          </div>
        </Card.Body>
      </Card>
    </section>
  );
});

SpinnerShowcase.displayName = 'SpinnerShowcase';

export default SpinnerShowcase;
