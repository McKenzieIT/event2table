import React, { useState, useCallback, useMemo } from 'react';
import { Select } from '@shared/ui';

interface GameOption {
  value: string;
  label: string;
}

const SelectShowcase: React.FC = () => {
  const [selectedGame, setSelectedGame] = useState('');

  const gameOptions: GameOption[] = useMemo(() => [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'baseball', label: 'Baseball' },
    { value: 'hockey', label: 'Hockey' },
    { value: 'soccer', label: 'Soccer' },
  ], []);

  const handleGameChange = useCallback((value: string) => {
    setSelectedGame(value);
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Select</h2>
      <div className="inputs-grid">
        <div>
          <Select
            label="Game Type"
            options={gameOptions}
            value={selectedGame}
            onChange={handleGameChange}
            placeholder="Select a game..."
          />
          <Select
            label="With Helper Text"
            options={gameOptions}
            placeholder="Choose game type..."
            helperText="Select the primary game type for this event."
          />
          <Select
            label="Error State"
            options={gameOptions}
            placeholder="Select an option..."
            error="Please select a game type"
            required
          />
        </div>
        <div>
          <Select
            label="Searchable Select"
            options={gameOptions}
            placeholder="Search games..."
            searchable
            helperText="Type to search through options."
          />
          <Select
            label="Disabled Select"
            options={gameOptions}
            value="football"
            disabled
            helperText="This field is disabled."
          />
        </div>
      </div>
    </section>
  );
};

export default SelectShowcase;
