import React from 'react';
import { Badge } from '@shared/ui';

const BadgeShowcase: React.FC = React.memo(() => {
  return (
    <section className="showcase-section">
      <h2 className="section-title">Badges</h2>
      <div className="showcase-row">
        <Badge variant="default">Default</Badge>
        <Badge variant="primary">Primary</Badge>
        <Badge variant="success">Success</Badge>
        <Badge variant="warning">Warning</Badge>
        <Badge variant="danger">Danger</Badge>
        <Badge variant="info">Info</Badge>
      </div>
      <div className="showcase-row">
        <Badge variant="success" dot>Active</Badge>
        <Badge variant="warning" dot>Draft</Badge>
        <Badge variant="default" dot>Archived</Badge>
      </div>
      <div className="showcase-row">
        <Badge variant="primary" pill>Pill Badge</Badge>
        <Badge variant="success" pill>Success Pill</Badge>
      </div>
    </section>
  );
});

BadgeShowcase.displayName = 'BadgeShowcase';

export default BadgeShowcase;
