// Diagnose import issues
import { describe, it, expect } from 'vitest';
import React from 'react';

describe('Import Diagnosis', () => {
  it('should import ToastProvider', async () => {
    const { ToastProvider } = await import('@shared/ui/Toast/Toast');
    expect(ToastProvider).toBeDefined();
    expect(typeof ToastProvider).toBe('function');
  });

  it('should import ErrorBoundary', async () => {
    const { ErrorBoundary } = await import('@shared/ui/ErrorBoundary/ErrorBoundary');
    expect(ErrorBoundary).toBeDefined();
    console.log('ErrorBoundary type:', typeof ErrorBoundary);
    console.log('ErrorBoundary:', ErrorBoundary);
    console.log('ErrorBoundary.displayName:', ErrorBoundary?.displayName);
    // React.memo returns an object with $$typeof property
    expect(ErrorBoundary).toBeTruthy();
  });

  it('should import from @shared/ui', async () => {
    const ui = await import('@shared/ui');
    console.log('@shared/ui exports:', Object.keys(ui));
    expect(ui.ToastProvider).toBeDefined();
    expect(ui.ErrorBoundary).toBeDefined();
  });

  it('should check React.memo behavior', () => {
    const TestComponent = () => React.createElement('div', null, 'test');
    const Memoized = React.memo(TestComponent);
    console.log('Memoized type:', typeof Memoized);
    console.log('Memoized:', Memoized);
    expect(typeof Memoized).toBe('object');
  });
});
