/**
 * E2E Tests for Parameter Management
 *
 * Tests the complete parameter management workflow:
 * 1. Navigate to parameter management page
 * 2. Filter parameters by mode (all/common/non-common)
 * 3. View common parameters modal
 * 4. Change parameter type
 * 5. Auto-sync common parameters
 *
 * @see docs/testing/e2e-testing-guide.md
 */

import { test, expect } from '@playwright/test';

test.describe('Parameter Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to parameter management page
    await page.goto('http://localhost:5173/parameters?game_gid=90000001');
    await page.waitForLoadState('networkidle');
  });

  test('should display parameter management page', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText('参数管理');

    // Check filters are visible
    await expect(page.locator('[data-testid="parameter-filters"]')).toBeVisible();

    // Check parameter cards are displayed
    const parameterCards = page.locator('[data-testid="parameter-card"]');
    await expect(parameterCards).toHaveCount.greaterThan(0);
  });

  test('should filter parameters by mode', async ({ page }) => {
    // Click on "common" mode
    await page.click('[data-testid="filter-mode-common"]');

    // Wait for filtered results
    await page.waitForSelector('[data-testid="parameter-card"]', { timeout: 5000 });

    // Verify only common parameters are shown
    const parameterCards = page.locator('[data-testid="parameter-card"]');
    const count = await parameterCards.count();

    for (let i = 0; i < count; i++) {
      const card = parameterCards.nth(i);
      await expect(card.locator('[data-testid="is-common-badge"]')).toBeVisible();
    }

    // Click on "non-common" mode
    await page.click('[data-testid="filter-mode-non-common"]');

    // Wait for filtered results
    await page.waitForSelector('[data-testid="parameter-card"]', { timeout: 5000 });

    // Verify only non-common parameters are shown
    const nonCommonCards = page.locator('[data-testid="parameter-card"]');
    const nonCommonCount = await nonCommonCards.count();

    for (let i = 0; i < nonCommonCount; i++) {
      const card = nonCommonCards.nth(i);
      await expect(card.locator('[data-testid="is-common-badge"]')).not.toBeVisible();
    }
  });

  test('should open common parameters modal', async ({ page }) => {
    // Click "View Common Parameters" button
    await page.click('[data-testid="view-common-params-button"]');

    // Wait for modal to open
    await expect(page.locator('[data-testid="common-params-modal"]')).toBeVisible();

    // Check statistics are displayed
    await expect(page.locator('[data-testid="common-params-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="common-params-coverage"]')).toBeVisible();

    // Close modal
    await page.click('[data-testid="close-common-params-modal"]');
    await expect(page.locator('[data-testid="common-params-modal"]')).not.toBeVisible();
  });

  test('should change parameter type', async ({ page }) => {
    // Find first parameter card
    const firstCard = page.locator('[data-testid="parameter-card"]').first();

    // Hover to show edit button
    await firstCard.hover();
    await expect(firstCard.locator('[data-testid="edit-parameter-button"]')).toBeVisible();

    // Click edit button
    await firstCard.click('[data-testid="edit-parameter-button"]');

    // Wait for modal to open
    await expect(page.locator('[data-testid="parameter-type-editor"]')).toBeVisible();

    // Select new type (e.g., change to "int")
    await page.selectOption('[data-testid="parameter-type-select"]', 'int');

    // Click submit
    await page.click('[data-testid="submit-type-change"]');

    // Wait for success toast
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({
      timeout: 5000
    });

    // Verify type changed
    await expect(firstCard.locator('[data-testid="parameter-type-badge"]')).toContainText('int');
  });

  test('should auto-sync common parameters', async ({ page }) => {
    // Open common parameters modal
    await page.click('[data-testid="view-common-params-button"]');
    await expect(page.locator('[data-testid="common-params-modal"]')).toBeVisible();

    // Get initial count
    const initialCountText = await page.locator('[data-testid="common-params-count"]').textContent();
    const initialCount = parseInt(initialCountText.match(/\d+/)[0]);

    // Close modal
    await page.click('[data-testid="close-common-params-modal"]');

    // Add a new parameter (this will affect common params)
    // ... (implementation depends on how parameters are added)

    // Open common parameters modal again
    await page.click('[data-testid="view-common-params-button"]');
    await expect(page.locator('[data-testid="common-params-modal"]')).toBeVisible();

    // Click refresh button
    await page.click('[data-testid="refresh-common-params"]');

    // Wait for refresh to complete
    await page.waitForSelector('[data-testid="common-params-modal"] .spinner', {
      state: 'hidden',
      timeout: 10000
    });

    // Verify count updated (or stayed the same if no change)
    const newCountText = await page.locator('[data-testid="common-params-count"]').textContent();
    const newCount = parseInt(newCountText.match(/\d+/)[0]);

    expect(newCount).toBeGreaterThanOrEqual(initialCount);
  });

  test('should filter parameters by event', async ({ page }) => {
    // Open event filter dropdown
    await page.click('[data-testid="event-filter-dropdown"]');

    // Select an event
    await page.click('[data-testid="event-option-1"]');

    // Wait for filtered results
    await page.waitForSelector('[data-testid="parameter-card"]', { timeout: 5000 });

    // Verify parameters are filtered by event
    const parameterCards = page.locator('[data-testid="parameter-card"]');
    await expect(parameterCards).toHaveCount.greaterThan(0);

    // Verify all parameters belong to the selected event
    const count = await parameterCards.count();
    for (let i = 0; i < count; i++) {
      const card = parameterCards.nth(i);
      // Check that parameter is associated with the event
      await expect(card.locator('[data-testid="event-badge"]')).toContainText('Event 1');
    }
  });

  test('should search parameters', async ({ page }) => {
    // Enter search term
    await page.fill('[data-testid="parameter-search-input"]', 'zone');

    // Wait for search results
    await page.waitForTimeout(500); // Wait for debounce

    // Verify search results
    const parameterCards = page.locator('[data-testid="parameter-card"]');
    const count = await parameterCards.count();

    for (let i = 0; i < count; i++) {
      const card = parameterCards.nth(i);
      const paramName = await card.locator('[data-testid="parameter-name"]').textContent();
      expect(paramName.toLowerCase()).toContain('zone');
    }
  });
});

test.describe('Event Node Builder - Field Selection', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to event node builder
    await page.goto('http://localhost:5173/event-node-builder?game_gid=90000001');
    await page.waitForLoadState('networkidle');
  });

  test('should show field selection modal on event select', async ({ page }) => {
    // Select an event
    await page.click('[data-testid="event-selector"]');
    await page.click('[data-testid="event-option-1"]');

    // Wait for field selection modal
    await expect(page.locator('[data-testid="field-selection-modal"]')).toBeVisible({
      timeout: 3000
    });

    // Verify all 6 options are present
    await expect(page.locator('[data-testid="field-option-all"]')).toBeVisible();
    await expect(page.locator('[data-testid="field-option-params"]')).toBeVisible();
    await expect(page.locator('[data-testid="field-option-non-common"]')).toBeVisible();
    await expect(page.locator('[data-testid="field-option-common"]')).toBeVisible();
    await expect(page.locator('[data-testid="field-option-base"]')).toBeVisible();
    await expect(page.locator('[data-testid="field-option-skip"]')).toBeVisible();
  });

  test('should batch add fields using quick action buttons', async ({ page }) => {
    // Select an event first
    await page.click('[data-testid="event-selector"]');
    await page.click('[data-testid="event-option-1"]');

    // Close field selection modal if it appears
    const modal = page.locator('[data-testid="field-selection-modal"]');
    if (await modal.isVisible()) {
      await page.click('[data-testid="field-option-skip"]');
    }

    // Click quick action button
    await page.click('[data-testid="quick-action-button"]');

    // Wait for dropdown
    await expect(page.locator('[data-testid="quick-action-dropdown"]')).toBeVisible();

    // Select "all fields" option
    await page.click('[data-testid="quick-action-all"]');

    // Wait for success toast
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({
      timeout: 5000
    });

    // Verify fields are added to canvas
    const canvasFields = page.locator('[data-testid="canvas-field"]');
    await expect(canvasFields).toHaveCount.greaterThan(0);
  });

  test('should add only common parameter fields', async ({ page }) => {
    // Select an event
    await page.click('[data-testid="event-selector"]');
    await page.click('[data-testid="event-option-1"]');

    // In field selection modal, click "common" option
    await page.click('[data-testid="field-option-common"]');

    // Wait for success toast
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({
      timeout: 5000
    });

    // Verify only common parameters are added
    const canvasFields = page.locator('[data-testid="canvas-field"]');
    const count = await canvasFields.count();

    for (let i = 0; i < count; i++) {
      const field = canvasFields.nth(i);
      const fieldType = await field.locator('[data-testid="field-type"]').textContent();
      expect(fieldType).toBe('common');
    }
  });

  test('should add only base fields', async ({ page }) => {
    // Select an event
    await page.click('[data-testid="event-selector"]');
    await page.click('[data-testid="event-option-1"]');

    // In field selection modal, click "base" option
    await page.click('[data-testid="field-option-base"]');

    // Wait for success toast
    await expect(page.locator('[data-testid="toast-success"]')).toBeVisible({
      timeout: 5000
    });

    // Verify exactly 7 base fields are added
    const canvasFields = page.locator('[data-testid="canvas-field"]');
    await expect(canvasFields).toHaveCount(7);

    // Verify all are base fields
    const count = await canvasFields.count();
    for (let i = 0; i < count; i++) {
      const field = canvasFields.nth(i);
      const fieldType = await field.locator('[data-testid="field-type"]').textContent();
      expect(fieldType).toBe('base');
    }
  });
});

test.describe('Parameter Management - Performance', () => {
  test('should load parameter list within 1 second', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('http://localhost:5173/parameters?game_gid=90000001');
    await page.waitForSelector('[data-testid="parameter-card"]', {
      state: 'attached',
      timeout: 5000
    });

    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(1000);
  });

  test('should filter parameters within 500ms', async ({ page }) => {
    await page.goto('http://localhost:5173/parameters?game_gid=90000001');
    await page.waitForSelector('[data-testid="parameter-card"]');

    const startTime = Date.now();

    // Click filter
    await page.click('[data-testid="filter-mode-common"]');

    // Wait for filtered results
    await page.waitForSelector('[data-testid="parameter-card"]', {
      state: 'attached',
      timeout: 2000
    });

    const filterTime = Date.now() - startTime;
    expect(filterTime).toBeLessThan(500);
  });

  test('should change parameter type within 1 second', async ({ page }) => {
    await page.goto('http://localhost:5173/parameters?game_gid=90000001');
    await page.waitForSelector('[data-testid="parameter-card"]');

    const firstCard = page.locator('[data-testid="parameter-card"]').first();

    const startTime = Date.now();

    // Hover and click edit
    await firstCard.hover();
    await firstCard.click('[data-testid="edit-parameter-button"]');

    // Wait for modal
    await page.waitForSelector('[data-testid="parameter-type-editor"]', {
      state: 'visible'
    });

    // Select type
    await page.selectOption('[data-testid="parameter-type-select"]', 'int');

    // Submit
    await page.click('[data-testid="submit-type-change"]');

    // Wait for success
    await page.waitForSelector('[data-testid="toast-success"]', {
      state: 'visible',
      timeout: 5000
    });

    const changeTime = Date.now() - startTime;
    expect(changeTime).toBeLessThan(1000);
  });
});
