import { Input } from '@shared/ui';
import React, { useState, useCallback } from 'react';

const InputShowcase: React.FC = () => {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Inputs</h2>
      <div className="inputs-grid">
        <div>
          <Input
            label="Text Input"
            placeholder="Enter game name..."
            value={inputValue}
            onChange={handleInputChange}
          />
          <Input
            label="With Helper Text"
            placeholder="Enter description..."
            helperText="This field supports markdown formatting."
          />
          <Input
            label="Error State"
            placeholder="This field has an error..."
            error="This field is required"
            required
          />
          <Input
            label="Disabled Input"
            placeholder="Cannot edit..."
            disabled
          />
        </div>

        <div>
          <Input
            type="password"
            label="Password Input"
            placeholder="Enter password..."
          />
          <Input
            type="number"
            label="Number Input"
            placeholder="Enter number..."
          />
        </div>
      </div>
    </section>
  );
};

export default InputShowcase;
