import { expect, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';
import '@testing-library/jest-dom';
import React from 'react';

// Make React globally available for components that use React.memo without explicit import
(global as any).React = React;

// Mock localStorage before any tests run
const localStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// Mock sessionStorage as well
const sessionStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(global, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
});

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  // Reset localStorage mock
  localStorageMock.getItem.mockReturnValue(null);
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
});

// Add custom matchers
expect.extend(matchers);

// Mock global fetch for API tests with proper response handling
const originalFetch = global.fetch;
beforeAll(() => {
  global.fetch = vi.fn((url: string) => {
    // Handle different API endpoints
    if (url.includes('/api/params')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: [] }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: [] })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/events')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { events: [], has_more: false, page: 1 } }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: { events: [], has_more: false, page: 1 } })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/preview-hql')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { hql: '', fields: [], preview_count: 0 } }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: { hql: '', fields: [], preview_count: 0 } })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/save') || url.includes('/api/update')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { id: 1 } }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: { id: 1 } })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/load') || url.includes('/api/list')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: [] }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: [] })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/delete')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, message: 'Deleted successfully' }),
        text: () => Promise.resolve(JSON.stringify({ success: true, message: 'Deleted successfully' })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    if (url.includes('/api/copy')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { id: 1 } }),
        text: () => Promise.resolve(JSON.stringify({ success: true, data: { id: 1 } })),
        status: 200,
        headers: new Headers(),
      } as Response);
    }
    // Default response for other requests
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ success: true, data: [] }),
      text: () => Promise.resolve(''),
      status: 200,
      headers: new Headers(),
    } as Response);
  }) as any;
});

afterAll(() => {
  global.fetch = originalFetch;
});

// Mock IntersectionObserver
(global as any).IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver as a proper constructor class
class MockResizeObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
(global as any).ResizeObserver = MockResizeObserver;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock URL constructor for relative URLs
const originalURL = global.URL;
beforeAll(() => {
  global.URL = class URL {
    href: string;
    origin: string;
    protocol: string;
    host: string;
    hostname: string;
    port: string;
    pathname: string;
    search: string;
    hash: string;

    constructor(url: string, base?: string) {
      // If it's a relative URL, prepend a base URL
      if (url.startsWith('/') && !base) {
        base = 'http://localhost:3000';
      }
      
      if (base) {
        const baseObj = new originalURL(base);
        this.href = baseObj.origin + url;
        this.origin = baseObj.origin;
        this.protocol = baseObj.protocol;
        this.host = baseObj.host;
        this.hostname = baseObj.hostname;
        this.port = baseObj.port;
        this.pathname = url;
        this.search = '';
        this.hash = '';
      } else {
        const parsed = new originalURL(url);
        this.href = parsed.href;
        this.origin = parsed.origin;
        this.protocol = parsed.protocol;
        this.host = parsed.host;
        this.hostname = parsed.hostname;
        this.port = parsed.port;
        this.pathname = parsed.pathname;
        this.search = parsed.search;
        this.hash = parsed.hash;
      }
    }

    toString() {
      return this.href;
    }

    toJSON() {
      return this.href;
    }

    static createObjectURL = originalURL.createObjectURL;
    static revokeObjectURL = originalURL.revokeObjectURL;
    static canParse = originalURL.canParse;
    static parse = originalURL.parse;
  };
});

afterAll(() => {
  global.URL = originalURL;
});
