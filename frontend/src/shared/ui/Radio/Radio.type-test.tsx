/**
 * Type Test for Radio Component
 *
 * This file verifies that the TypeScript types for Radio component are correct.
 * It will be compiled by TypeScript during the build process.
 */

import { Radio } from './Radio';

// Test 1: Basic usage with minimal props
const test1 = () => {
  return <Radio name="game" value="football" label="Football" />;
};

// Test 2: Controlled radio with value and onChange
const test2 = () => {
  const [selectedGame, setSelectedGame] = React.useState('football');

  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      checked={selectedGame === 'football'}
      onChange={(value) => setSelectedGame(value)}
    />
  );
};

// Test 3: All optional props
const test3 = () => {
  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      checked={true}
      disabled={false}
      required={true}
      error="This field is required"
      className="custom-radio"
      id="football-radio"
    />
  );
};

// Test 4: Radio group
const test4 = () => {
  const [selectedGame, setSelectedGame] = React.useState('football');

  const options = [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'tennis', label: 'Tennis' }
  ];

  return (
    <div>
      {options.map(option => (
        <Radio
          key={option.value}
          name="game"
          value={option.value}
          label={option.label}
          checked={selectedGame === option.value}
          onChange={(value) => setSelectedGame(value)}
        />
      ))}
    </div>
  );
};

// Test 5: Ref forwarding
const test5 = () => {
  const ref = React.useRef<HTMLInputElement>(null);

  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      ref={ref}
    />
  );
};

// Test 6: Different states
const test6 = () => {
  return (
    <>
      <Radio name="test1" value="1" label="Checked" checked />
      <Radio name="test2" value="2" label="Unchecked" checked={false} />
      <Radio name="test3" value="3" label="Disabled" disabled />
      <Radio name="test4" value="4" label="Required" required />
    </>
  );
};

// Test 7: Error states
const test7 = () => {
  return (
    <>
      <Radio name="test1" value="1" label="Valid" />
      <Radio name="test2" value="2" label="Invalid" error="This field is required" />
      <Radio name="test3" value="3" label="Disabled" disabled />
    </>
  );
};

// Test 8: Event handlers should have correct types
const test8 = () => {
  const handleChange = (value: string, event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Selected value:', value);
    console.log('Event target checked:', event.target.checked);
    console.log('Event target value:', event.target.value);
  };

  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      onChange={handleChange}
    />
  );
};

// Test 9: All standard HTML input attributes should work
const test9 = () => {
  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      disabled={false}
      form="my-form"
      required={true}
      autoFocus={false}
    />
  );
};

// Test 10: Without label
const test10 = () => {
  return (
    <Radio
      name="game"
      value="football"
      checked={true}
    />
  );
};

// Test 11: Custom onChange with event access
const test11 = () => {
  const handleChange = (value: string, event: React.ChangeEvent<HTMLInputElement>) => {
    // Access to the full event object
    const radio = event.target as HTMLInputElement;
    console.log('Radio checked:', radio.checked);
    console.log('Radio value:', radio.value);
    console.log('Radio name:', radio.name);
  };

  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      onChange={handleChange}
    />
  );
};

// Test 12: Auto-generated ID
const test12 = () => {
  return (
    <Radio
      name="game"
      value="football"
      label="Football"
      // No id provided - should auto-generate
    />
  );
};

// Import React for the tests
import React from 'react';
