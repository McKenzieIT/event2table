import { Card, Checkbox, Radio } from '@shared/ui';
import React, { useState, useCallback, useMemo } from 'react';

interface RadioOption {
  value: string;
  label: string;
}

const CheckboxRadioShowcase: React.FC = () => {
  const [checkboxChecked, setCheckboxChecked] = useState(false);
  const [checkboxIndeterminate, setCheckboxIndeterminate] = useState(true);
  const [selectedRadio, setSelectedRadio] = useState('football');

  const radioOptions: RadioOption[] = useMemo(() => [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'baseball', label: 'Baseball' },
  ], []);

  const handleCheckboxChange = useCallback((checked: boolean) => {
    setCheckboxChecked(checked);
  }, []);

  const handleIndeterminateToggle = useCallback(() => {
    setCheckboxIndeterminate(!checkboxIndeterminate);
  }, [checkboxIndeterminate]);

  const handleRadioChange = useCallback((value: string) => {
    setSelectedRadio(value);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Checkbox & Radio</h2>
      <div className="inputs-grid">
        <Card>
          <Card.Header>
            <Card.Title>Checkboxes</Card.Title>
          </Card.Header>
          <Card.Body>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <Checkbox
                label="Enable notifications"
                checked={checkboxChecked}
                onChange={handleCheckboxChange}
              />
              <Checkbox
                label="Accept terms and conditions"
                required
              />
              <Checkbox
                label="Indeterminate state"
                checked={checkboxIndeterminate}
                indeterminate={checkboxIndeterminate}
                onChange={handleIndeterminateToggle}
                helperText="Click to toggle through states"
              />
              <Checkbox
                label="Disabled checkbox"
                disabled
                checked={true}
              />
              <Checkbox
                label="Error state"
                error="This field is required"
                required
              />
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Radio Buttons</Card.Title>
          </Card.Header>
          <Card.Body>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <p style={{ color: 'var(--text-secondary, #94A3B8)', marginBottom: '8px' }}>
                Select your favorite game:
              </p>
              {radioOptions.map((option) => (
                <Radio
                  key={option.value}
                  label={option.label}
                  name="game"
                  value={option.value}
                  checked={selectedRadio === option.value}
                  onChange={handleRadioChange}
                />
              ))}
              <div style={{ marginTop: '16px' }}>
                <Radio
                  label="Disabled option"
                  name="game"
                  value="tennis"
                  disabled
                />
              </div>
            </div>
          </Card.Body>
        </Card>
      </div>
    </section>
  );
};

export default CheckboxRadioShowcase;
