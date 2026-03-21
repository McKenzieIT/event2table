import React, { useState, useCallback } from 'react';
import { TextArea } from '@shared/ui';

const TextAreaShowcase: React.FC = () => {
  const [textAreaValue, setTextAreaValue] = useState('');

  const handleTextAreaChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextAreaValue(e.target.value);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">TextArea</h2>
      <div className="inputs-grid">
        <div>
          <TextArea
            label="Description"
            placeholder="Enter game description..."
            value={textAreaValue}
            onChange={handleTextAreaChange}
            rows={4}
          />
          <TextArea
            label="With Character Count"
            placeholder="Enter description (max 200 chars)..."
            maxLength={200}
            showCount
            rows={3}
            helperText="This field has a character limit."
          />
          <TextArea
            label="Error State"
            placeholder="This field has an error..."
            error="Description is required"
            required
            rows={3}
          />
        </div>
        <div>
          <TextArea
            label="Disabled TextArea"
            placeholder="Cannot edit..."
            disabled
            rows={4}
          />
          <TextArea
            label="Non-resizable"
            placeholder="This textarea cannot be resized..."
            resize="none"
            rows={3}
            helperText="Resize handle is disabled."
          />
        </div>
      </div>
    </section>
  );
};

export default TextAreaShowcase;
