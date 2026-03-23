import { Button, Card, useToast } from '@shared/ui';
import React from 'react';

const ToastShowcase: React.FC = () => {
  const { success, error, warning, info } = useToast();

  const handleSuccessToast = () => {
    success('Operation completed successfully!');
  };

  const handleErrorToast = () => {
    error('An error occurred. Please try again.');
  };

  const handleWarningToast = () => {
    warning('Warning: This action cannot be undone.');
  };

  const handleInfoToast = () => {
    info('Here is some useful information for you.');
  };

  return (
    <section className="showcase-section">
      <h2 className="section-title">Toast Notifications</h2>
      <Card>
        <Card.Body>
          <p style={{ marginBottom: '16px', color: 'var(--text-secondary, #94A3B8)' }}>
            Click the buttons below to see toast notifications with different variants.
          </p>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <Button variant="primary" onClick={handleSuccessToast}>
              Success Toast
            </Button>
            <Button variant="danger" onClick={handleErrorToast}>
              Error Toast
            </Button>
            <Button variant="warning" onClick={handleWarningToast}>
              Warning Toast
            </Button>
            <Button variant="ghost" onClick={handleInfoToast}>
              Info Toast
            </Button>
          </div>
        </Card.Body>
      </Card>
    </section>
  );
};

export default ToastShowcase;
