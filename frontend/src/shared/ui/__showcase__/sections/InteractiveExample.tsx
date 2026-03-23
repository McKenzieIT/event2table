import { Button, Card, Input } from '@shared/ui';
import React, { useState, useCallback } from 'react';

const InteractiveExample: React.FC = () => {
  const [isloading, setIsLoading] = useState(false);

  const handleClick = useCallback(() => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Interactive Example</h2>
      <Card>
        <Card.Header>
          <Card.Title>Generate HQL</Card.Title>
        </Card.Header>
        <Card.Body>
          <div style={{ marginBottom: '16px' }}>
            <Input
              label="Game Name"
              placeholder="Enter game name..."
            />
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <Button variant="primary" onClick={handleClick} loading={isloading}>
              {isloading ? 'Generating...' : 'Generate'}
            </Button>
            <Button variant="ghost">Cancel</Button>
          </div>
        </Card.Body>
      </Card>
    </section>
  );
};

export default InteractiveExample;
