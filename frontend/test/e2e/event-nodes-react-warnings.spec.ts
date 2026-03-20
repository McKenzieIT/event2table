import { test, expect } from '@playwright/test';

test.describe('Event Nodes Page - React State Management', () => {
  test('should not have concurrent state update warnings', async ({ page }) => {
    // Collect all console messages
    const consoleMessages: Array<{type: string, text: string}> = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // Navigate to event-nodes page
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Wait for page to fully load
    await page.waitForTimeout(3000);

    // Check for "Cannot update a component" warnings
    const stateWarnings = consoleMessages.filter(msg =>
      msg.type === 'warning' &&
      msg.text.includes('Cannot update a component') &&
      (msg.text.includes('MainLayout') || msg.text.includes('Sidebar'))
    );

    expect(stateWarnings.length).toBe(0);
  });

  test('should not trigger setState during render', async ({ page }) => {
    const consoleMessages: Array<{type: string, text: string}> = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // Navigate to event-nodes page
    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Wait for initial render
    await page.waitForTimeout(2000);

    // Trigger a game change to test state updates
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('gameChanged', {
        detail: { id: 1, name: 'Test Game', gid: 10000147 }
      }));
    });

    // Wait for state to update
    await page.waitForTimeout(1000);

    // Should not have "Cannot update a component" warnings
    const stateWarnings = consoleMessages.filter(msg =>
      msg.type === 'warning' &&
      msg.text.includes('Cannot update a component')
    );

    expect(stateWarnings.length).toBe(0);
  });

  test('should load without React errors or warnings', async ({ page }) => {
    const consoleMessages: Array<{type: string, text: string}> = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await page.goto('http://localhost:5173/#/event-nodes?game_gid=10000147');

    // Wait for page to fully stabilize
    await page.waitForTimeout(3000);

    // Count errors and warnings
    const errors = consoleMessages.filter(m => m.type === 'error');
    const warnings = consoleMessages.filter(m => m.type === 'warning');

    // Should have no React errors
    expect(errors.length).toBe(0);

    // Warnings should only be about future flags, not state management
    const stateWarnings = warnings.filter(w =>
      !w.text.includes('Future Flag')
    );

    expect(stateWarnings.length).toBe(0);
  });
});
