import { Card, Switch } from '@shared/ui';
import React, { useState, useCallback } from 'react';

const SwitchShowcase: React.FC = () => {
  const [switchEnabled, setSwitchEnabled] = useState(false);
  const [switchAutoSave, setSwitchAutoSave] = useState(true);

  const handleSwitchEnabledChange = useCallback((checked: boolean) => {
    setSwitchEnabled(checked);
  }, []);

  const handleSwitchAutoSaveChange = useCallback((checked: boolean) => {
    setSwitchAutoSave(checked);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Switch</h2>
      <Card>
        <Card.Body>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <Switch
              label="Enable Notifications"
              checked={switchEnabled}
              onChange={handleSwitchEnabledChange}
            />
            <Switch
              label="Auto-save"
              description="Automatically save changes every 30 seconds"
              checked={switchAutoSave}
              onChange={handleSwitchAutoSaveChange}
            />
            <Switch
              label="Dark Mode"
              description="Enable dark theme for the application"
              checked={true}
            />
            <Switch
              label="Disabled Switch"
              description="This switch is disabled"
              disabled
              checked={false}
            />
            <Switch
              label="Required Setting"
              required
              checked={true}
            />
          </div>
        </Card.Body>
      </Card>
    </section>
  );
};

export default SwitchShowcase;
