import React from 'react';
import { Button } from '@shared/ui';

const AnimationDemo: React.FC = () => {
  const handleReload = () => {
    window.location.reload();
  };

  return (
    <section className="showcase-section">
      <h2 className="section-title">Animations</h2>
      <Button onClick={handleReload}>
        Reload Page to See Entrance Animations
      </Button>
      <p className="text-sm text-gray-400" style={{ marginTop: '8px' }}>
        Cards will animate in with staggered delay.
      </p>
    </section>
  );
};

export default AnimationDemo;
