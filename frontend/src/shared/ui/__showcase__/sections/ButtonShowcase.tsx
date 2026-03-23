import { Button } from '@shared/ui';
import React from 'react';

const ButtonShowcase: React.FC = React.memo(() => {
  return (
    <section className="showcase-section">
      <h2 className="section-title">Buttons</h2>
      <div className="showcase-row">
        <Button variant="primary">Primary Button</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost Button</Button>
        <Button variant="danger">Danger Button</Button>
      </div>
      <div className="showcase-row">
        <Button size="sm">Small Primary</Button>
        <Button size="md">Medium Primary</Button>
        <Button size="lg">Large Primary</Button>
      </div>
      <div className="showcase-row">
        <Button loading>Loading...</Button>
        <Button disabled>Disabled</Button>
      </div>
    </section>
  );
});

ButtonShowcase.displayName = 'ButtonShowcase';

export default ButtonShowcase;
