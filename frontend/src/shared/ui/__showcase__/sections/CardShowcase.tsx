import { Card } from '@shared/ui';
import React from 'react';

const CardShowcase: React.FC = React.memo(() => {
  return (
    <section className="showcase-section">
      <h2 className="section-title">Cards</h2>
      <div className="cards-grid">
        <Card>
          <Card.Header>
            <Card.Title>Default Card</Card.Title>
          </Card.Header>
          <Card.Body>
            <p>Default glassmorphism card with subtle border.</p>
          </Card.Body>
        </Card>

        <Card hoverable>
          <Card.Header>
            <Card.Title>Hoverable Card</Card.Title>
          </Card.Header>
          <Card.Body>
            <p>Hover to see the lift effect and cyan glow.</p>
          </Card.Body>
        </Card>

        <Card glowing>
          <Card.Header>
            <Card.Title>Glowing Card</Card.Title>
          </Card.Header>
          <Card.Body>
            <p>Continuous cyan glow effect.</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Header>
            <Card.Title>Outlined Card</Card.Title>
          </Card.Header>
          <Card.Body>
            <p>Minimal style with stronger border.</p>
          </Card.Body>
        </Card>
      </div>
    </section>
  );
});

CardShowcase.displayName = 'CardShowcase';

export default CardShowcase;
