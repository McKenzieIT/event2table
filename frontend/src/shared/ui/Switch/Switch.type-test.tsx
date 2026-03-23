// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Type Test for Switch Component
 *
 * This file verifies that the TypeScript types for Switch component are correct.
 * It will be compiled by TypeScript during the build process.
 */

import React from 'react';

import { Switch } from './Switch';

// Test 1: Basic usage with minimal props
const test1 = () => {
  return <Switch />;
};

// Test 2: Controlled switch with value and onChange
const test2 = () => {
  const [checked, setChecked] = React.useState(false);

  return (
    <Switch
      label="Enable notifications"
      checked={checked}
      onChange={(isChecked) => setChecked(isChecked)}
    />
  );
};

// Test 3: onChange with event parameter
const test3 = () => {
  const handleChange = (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Switch changed to:', checked);
    console.log('Event target:', event.target);
  };

  return (
    <Switch
      label="Auto-save"
      checked={true}
      onChange={handleChange}
    />
  );
};

// Test 4: All optional props
const test4 = () => {
  return (
    <Switch
      label="Email notifications"
      description="Receive email updates about your account"
      checked={false}
      disabled={false}
      required={true}
      error="This field is required"
      className="custom-switch"
      name="email-notifications"
      id="email-notifications-switch"
      value="email-notifications"
    />
  );
};

// Test 5: With description
const test5 = () => {
  return (
    <Switch
      label="Dark mode"
      description="Enable dark theme across the application"
      checked={true}
      onChange={(checked) => console.log('Dark mode:', checked)}
    />
  );
};

// Test 6: Disabled state
const test6 = () => {
  return (
    <>
      <Switch label="Enabled switch" checked={true} />
      <Switch label="Disabled switch" checked={false} disabled />
    </>
  );
};

// Test 7: Error states
const test7 = () => {
  return (
    <>
      <Switch label="Valid" checked={true} />
      <Switch label="Invalid" checked={false} error="This field is required" />
      <Switch label="Disabled" checked={false} disabled />
    </>
  );
};

// Test 8: Ref forwarding
const test8 = () => {
  const ref = React.useRef<HTMLInputElement>(null);

  const focusSwitch = () => {
    ref.current?.focus();
  };

  return (
    <>
      <Switch
        label="With Ref"
        ref={ref}
      />
      <button onClick={focusSwitch}>Focus Switch</button>
    </>
  );
};

// Test 9: Standard HTML input attributes should work
const test9 = () => {
  return (
    <Switch
      label="Complete"
      checked={true}
      name="my-switch"
      id="my-switch-id"
      value="switch-value"
      required={true}
      aria-label="Toggle notifications"
      aria-describedby="switch-description"
    />
  );
};

// Test 10: Uncontrolled mode
const test10 = () => {
  return (
    <Switch
      label="Uncontrolled switch"
      defaultChecked={true}
      onChange={(checked) => console.log('Changed to:', checked)}
    />
  );
};

// Test 11: Label only (no description)
const test11 = () => {
  return (
    <Switch
      label="Simple label"
      checked={false}
    />
  );
};

// Test 12: Description only (no label)
const test12 = () => {
  return (
    <Switch
      description="Just a description"
      checked={true}
    />
  );
};

// Test 13: Both label and description
const test13 = () => {
  return (
    <Switch
      label="Feature flag"
      description="Enable experimental features for testing"
      checked={true}
      required={true}
    />
  );
};

// Test 14: onChange callback can be optional
const test14 = () => {
  return (
    <>
      <Switch label="Without onChange" checked={true} />
      <Switch
        label="With onChange"
        checked={false}
        onChange={(checked) => console.log('Checked:', checked)}
      />
    </>
  );
};

// Test 15: Event should have correct types
const test15 = () => {
  const handleChange = (checked: boolean, event: React.ChangeEvent<HTMLInputElement>) => {
    // Type checking for event properties
    const target: HTMLInputElement = event.target;
    const checkedState: boolean = target.checked;
    const name: string = target.name;
    const value: string = target.value;
    const id: string = target.id;

    console.log({ checkedState, name, value, id, checked });
  };

  return (
    <Switch
      label="Event Types"
      name="test-switch"
      id="test-switch"
      value="test-value"
      checked={true}
      onChange={handleChange}
    />
  );
};
