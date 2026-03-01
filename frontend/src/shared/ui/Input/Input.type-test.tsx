/**
 * Type Test for Input Component
 *
 * This file verifies that the TypeScript types for Input component are correct.
 * It will be compiled by TypeScript during the build process.
 */

import { Input } from './Input';

// Test 1: Basic usage with minimal props
const test1 = () => {
  return <Input type="text" />;
};

// Test 2: Controlled input with value and onChange
const test2 = () => {
  const [value, setValue] = React.useState('');

  return (
    <Input
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      label="Game Name"
    />
  );
};

// Test 3: All optional props
const test3 = () => {
  return (
    <Input
      type="email"
      label="Email"
      placeholder="Enter email"
      error="Invalid email"
      disabled={false}
      required={true}
      helperText="We'll never share your email"
      className="custom-input"
      name="email"
      id="email-input"
      readOnly={false}
      autoFocus={false}
      maxLength={100}
      minLength={5}
      onBlur={(e) => console.log('Blur', e.target.value)}
      onFocus={(e) => console.log('Focus', e.target.value)}
    />
  );
};

// Test 4: With icon component
const test4 = () => {
  const SearchIcon = () => <span>🔍</span>;

  return (
    <Input
      type="search"
      label="Search"
      placeholder="Search games..."
      icon={SearchIcon}
    />
  );
};

// Test 5: Ref forwarding
const test5 = () => {
  const ref = React.useRef<HTMLInputElement>(null);

  return (
    <Input
      type="text"
      label="With Ref"
      ref={ref}
    />
  );
};

// Test 6: Different input types
const test6 = () => {
  return (
    <>
      <Input type="text" label="Text" />
      <Input type="password" label="Password" />
      <Input type="email" label="Email" />
      <Input type="number" label="Number" />
      <Input type="tel" label="Phone" />
      <Input type="url" label="Website" />
      <Input type="search" label="Search" />
      <Input type="date" label="Date" />
      <Input type="time" label="Time" />
    </>
  );
};

// Test 7: Error states
const test7 = () => {
  return (
    <>
      <Input type="text" label="Valid" />
      <Input type="text" label="Invalid" error="This field is required" />
      <Input type="text" label="Disabled" disabled />
    </>
  );
};

// Test 8: Event handlers should have correct types
const test8 = () => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value: string = e.target.value;
    console.log('Value:', value);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const value: string = e.target.value;
    console.log('Blurred with value:', value);
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    const value: string = e.target.value;
    console.log('Focused with value:', value);
  };

  return (
    <Input
      type="text"
      label="Events"
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
    />
  );
};

// Test 9: Value can be string or number
const test9 = () => {
  const [textValue, setTextValue] = React.useState('text');
  const [numberValue, setNumberValue] = React.useState(42);

  return (
    <>
      <Input
        type="text"
        value={textValue}
        onChange={(e) => setTextValue(e.target.value)}
      />
      <Input
        type="number"
        value={numberValue}
        onChange={(e) => setNumberValue(Number(e.target.value))}
      />
    </>
  );
};

// Test 10: All standard HTML input attributes should work
const test10 = () => {
  return (
    <Input
      type="text"
      label="Complete"
      placeholder="Placeholder"
      autoComplete="on"
      autoFocus={false}
      disabled={false}
      form="my-form"
      list="options"
      max={100}
      maxLength={10}
      min={0}
      minLength={5}
      multiple={false}
      name="field"
      pattern="[A-Za-z]{3}"
      readOnly={false}
      required={true}
      size={20}
      step={1}
      title="Help text"
    />
  );
};

// Import React for the tests
import React from 'react';
