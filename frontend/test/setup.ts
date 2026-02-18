import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Add custom matchers
expect.extend(matchers);
