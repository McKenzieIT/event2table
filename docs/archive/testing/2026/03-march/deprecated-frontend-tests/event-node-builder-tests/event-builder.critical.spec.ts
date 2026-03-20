import { test, expect, type Page, type Locator } from '@playwright/test';

/**
 * Event Builder Critical Tests
 * Phase 3: Automated E2E Testing
 *
 * Tests critical Event Builder functionality including:
 * - Event selection
 * - Field dragging to canvas
 * - WHERE conditions
 * - HQL preview updates
 *
 * Uses test GID 90000001 to avoid production data.
 */

// Type definitions
interface ConsoleError {
  text: string;
  location?: {
    url?: string;
    lineNumber?: number;
    columnNumber?: number;
  };
}

interface HQLPreview {
  initial: string | null;
  updated: string | null;
}

interface FieldCount {
  before: number;
  after: number;
}

// Test configuration
const TEST_GAME_GID = 90000001 as const;
const EVENT_NAME = /zmpvp|测试事件/i;
const TEST_FIELD = 'role_id' as const;

// Helper functions with types
async function navigateToEventBuilder(page: Page): Promise<void> {
  await page.goto('/#/event-node-builder?game_gid=90000001');

  // Wait for page to load
  await expect(
    page.locator('[data-testid="event-node-builder"], .event-node-builder')
  ).toBeVisible({ timeout: 10000 });
}

async function selectEvent(page: Page, eventName: RegExp): Promise<void> {
  await page.selectOption('#event-select, [data-testid="event-select"]', { label: eventName });
  await page.waitForTimeout(1000);
}

async function getFieldCount(page: Page): Promise<number> {
  return await page.locator('.canvas-field, .field-on-canvas').count();
}

async function dragFieldToCanvas(page: Page, fieldName: string): Promise<void> {
  const fieldToDrag = page.locator(`.field-list-item[data-field="${fieldName}"]`).first();
  const canvas = page.locator('.field-canvas, .canvas-drop-zone, [data-testid="canvas"]');
  await fieldToDrag.dragTo(canvas);
  await page.waitForTimeout(500);
}

async function getHQLPreview(page: Page): Promise<string | null> {
  const hqlPreview = page.locator('.hql-preview, [data-testid="hql-preview"]');
  return await hqlPreview.textContent();
}

async function collectConsoleErrors(page: Page): Promise<ConsoleError[]> {
  const errors: ConsoleError[] = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push({
        text: msg.text(),
        location: msg.location()
      });
    }
  });

  return errors;
}

function filterCriticalErrors(errors: ConsoleError[]): ConsoleError[] {
  return errors.filter(err =>
    !err.text.includes('DevTools') &&
    !err.text.includes('chrome-extension') &&
    !err.text.includes('Extension')
  );
}

test.describe('Event Builder Critical Tests', () => {
  test.beforeEach(async ({ page }: { page: Page }) => {
    await navigateToEventBuilder(page);
  });

  test('Event Builder page loads successfully', async ({ page }: { page: Page }) => {
    // Verify main components are visible
    await expect(page.locator('#event-select, [data-testid="event-select"]')).toBeVisible();
    await expect(page.locator('.field-canvas, .canvas-area, [data-testid="canvas"]')).toBeVisible();
    await expect(page.locator('.hql-preview, [data-testid="hql-preview"]')).toBeVisible();
  });

  test('User can select an event', async ({ page }: { page: Page }) => {
    // Select an event from dropdown
    await selectEvent(page, EVENT_NAME);

    // Verify field list is populated
    await expect(page.locator('.field-list-item, [data-testid*="field"]')).toHaveCount({ min: 1 });
  });

  test('User can drag field to canvas', async ({ page }: { page: Page }) => {
    // Select an event first
    await selectEvent(page, /zmpvp/i);

    // Get initial field count on canvas
    const initialCanvasFields: number = await getFieldCount(page);

    // Drag field to canvas
    await dragFieldToCanvas(page, TEST_FIELD);

    // Verify field was added to canvas
    await expect(page.locator('.canvas-field, .field-on-canvas')).toHaveCount(initialCanvasFields + 1);

    // Verify the specific field is on canvas
    await expect(
      page.locator(`.canvas-field[data-field="${TEST_FIELD}"], [data-testid*="${TEST_FIELD}"][data-on-canvas="true"]`)
    ).toBeVisible();
  });

  test('HQL preview updates when field is added', async ({ page }: { page: Page }) => {
    // Select event
    await selectEvent(page, /zmpvp/i);

    // Get initial HQL preview
    const initialHQL: string | null = await getHQLPreview(page);

    // Drag field to canvas
    await dragFieldToCanvas(page, TEST_FIELD);

    // Get updated HQL preview
    const updatedHQL: string | null = await getHQLPreview(page);

    // Verify HQL preview changed
    expect(updatedHQL).not.toBe(initialHQL);

    // Verify field name appears in HQL
    expect(updatedHQL).toMatch(/role_id/i);
  });

  test('User can add WHERE condition', async ({ page }: { page: Page }) => {
    // Select event
    await selectEvent(page, /zmpvp/i);

    // Click "Add WHERE Condition" button
    await page.click('text=/添加.*WHERE|Add.*WHERE/i');

    // Verify WHERE condition modal opens
    await expect(
      page.locator('.where-builder-modal, .modal, [data-testid="where-modal"]')
    ).toBeVisible();

    // Fill WHERE condition
    await page.selectOption('.condition-field-select, [name="field"]', 'zone_id');
    await page.selectOption('.condition-operator-select, [name="operator"]', '>');
    await page.fill('.condition-value-input, [name="value"]', '100');

    // Apply condition
    await page.click('text=/应用|apply|确定/i');

    // Verify modal closes
    await expect(page.locator('.where-builder-modal, .modal')).not.toBeVisible();

    // Verify condition appears in HQL preview
    await expect(
      page.locator('.hql-preview, [data-testid="hql-preview"]')
    ).toContainText(/zone_id\s*>\s*100/i);
  });

  test('User can remove field from canvas', async ({ page }: { page: Page }) => {
    // Select event and add field
    await selectEvent(page, /zmpvp/i);
    await dragFieldToCanvas(page, TEST_FIELD);

    // Get field count before removal
    const fieldsBefore: number = await getFieldCount(page);

    // Click remove button on the field
    await page.locator(
      `.canvas-field[data-field="${TEST_FIELD}"] .remove-button, [data-testid*="remove"][data-field="${TEST_FIELD}"]`
    ).click();

    // Wait for removal
    await page.waitForTimeout(500);

    // Verify field was removed
    const fieldsAfter: number = await getFieldCount(page);
    expect(fieldsAfter).toBe(fieldsBefore - 1);
  });

  test('HQL Generate button works', async ({ page }: { page: Page }) => {
    // Select event and add field
    await selectEvent(page, /zmpvp/i);
    await dragFieldToCanvas(page, TEST_FIELD);

    // Click Generate HQL button
    await page.click('text=/生成.*HQL|Generate/i');

    // Verify HQL output is displayed
    await expect(
      page.locator('.hql-output, .generated-hql, [data-testid="hql-output"]')
    ).toBeVisible();

    // Verify HQL contains SELECT statement
    const hqlText = await page.locator('.hql-output, .generated-hql, [data-testid="hql-output"]').textContent();
    expect(hqlText).toMatch(/SELECT/i);
    expect(hqlText).toMatch(/role_id/i);
  });

  test('Event Builder has no console errors', async ({ page }: { page: Page }) => {
    // Collect console errors
    const errors: ConsoleError[] = await collectConsoleErrors(page);

    // Select event and interact with canvas
    await selectEvent(page, /zmpvp/i);
    await dragFieldToCanvas(page, TEST_FIELD);

    // Filter out non-critical errors
    const criticalErrors = filterCriticalErrors(errors);

    expect(criticalErrors).toHaveLength(0);
  });
});
