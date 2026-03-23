/**
 * Simple test to verify ToastProvider works correctly
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ToastProvider, useToast } from '@shared/ui/Toast/Toast';
import { createElement } from 'react';

// Simple test component
function TestComponent() {
  const toast = useToast();
  return createElement('div', null, 'Test Component');
}

describe('ToastProvider Diagnostics', () => {
  it('should render ToastProvider without errors', () => {
    const { container } = render(
      createElement(ToastProvider, null, createElement(TestComponent))
    );

    expect(container).toBeDefined();
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });
});
