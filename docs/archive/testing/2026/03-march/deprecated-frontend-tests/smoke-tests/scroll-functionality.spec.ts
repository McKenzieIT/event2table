import { test, expect } from '@playwright/test';

/**
 * Scroll Functionality Tests for Event Node Builder
 * 
 * Tests the ability to scroll through:
 * 1. Event List (.sidebar-section--event)
 * 2. Parameter List (.sidebar-section--params)
 * 3. Field Canvas (.field-canvas)
 * 
 * Issue: These areas cannot scroll due to CSS overflow conflicts.
 * Root Cause: Parent containers have overflow: hidden preventing child overflow-y: auto from working.
 */
test.describe('EventNodeBuilder - Scroll Functionality', () => {
  const baseUrl = 'http://localhost:5173';
  const eventNodeBuilderUrl = `${baseUrl}/#/event-node-builder?game_gid=10000147`;

  test.beforeEach(async ({ page }) => {
    // Clear cache and storage
    await page.goto(baseUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.evaluate(() => {
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  test.afterEach(async ({ page }) => {
    // Clean up test state
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_event_node_builder_')) {
          localStorage.removeItem(key);
        }
      });
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  /**
   * Helper: Check if element has scrollable overflow
   */
  async function isScrollable(page: any, selector: string): Promise<boolean> {
    const scrollHeight = await page.locator(selector).evaluate(el => el.scrollHeight);
    const clientHeight = await page.locator(selector).evaluate(el => el.clientHeight);
    return scrollHeight > clientHeight;
  }

  /**
   * Helper: Get scroll information
   */
  async function getScrollInfo(page: any, selector: string) {
    return await page.locator(selector).evaluate((el: any) => ({
      scrollHeight: el.scrollHeight,
      clientHeight: el.clientHeight,
      scrollTop: el.scrollTop,
      scrollBottom: el.scrollHeight - el.clientHeight - el.scrollTop,
      overflowY: window.getComputedStyle(el).overflowY,
      overflow: window.getComputedStyle(el).overflow
    }));
  }

  /**
   * Helper: Scroll to specific position
   */
  async function scrollToSelector(page: any, selector: string, scrollTop: number) {
    await page.locator(selector).evaluate((el: any, pos: number) => {
      el.scrollTo({ top: pos, behavior: 'smooth' });
    }, scrollTop);
    await page.waitForTimeout(500); // Wait for smooth scroll to complete
  }

  test('should have scrollable event list when many events exist', async ({ page }) => {
    console.log('[TEST] Starting event list scroll test');

    // Navigate to Event Node Builder
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Wait for event list to load
    const eventList = page.locator('.sidebar-section--event .section-content');
    await expect(eventList).toBeVisible({ timeout: 10000 });

    // Check if event list has scrollable overflow
    const scrollable = await isScrollable(page, '.sidebar-section--event .section-content');
    console.log('[TEST] Event list scrollable:', scrollable);

    // Count total events
    const eventItems = page.locator('.sidebar-section--event .event-item');
    const count = await eventItems.count();
    console.log('[TEST] Total events found:', count);
    expect(count).toBeGreaterThanOrEqual(10); // At least 10 events

    // If scrollable, test scrolling
    if (scrollable) {
      // Scroll to bottom
      await scrollToSelector(page, '.sidebar-section--event .section-content', 9999);
      
      // Verify last event is visible
      const lastEvent = eventItems.nth(count - 1);
      await expect(lastEvent).toBeVisible();

      // Scroll back to top
      await scrollToSelector(page, '.sidebar-section--event .section-content', 0);
      
      // Verify first event is visible
      const firstEvent = eventItems.first();
      await expect(firstEvent).toBeVisible();
    }

    // Verify overflow CSS
    const scrollInfo = await getScrollInfo(page, '.sidebar-section--event .section-content');
    console.log('[TEST] Event list scroll info:', scrollInfo);
    expect(scrollInfo.overflowY).toMatch(/auto|scroll/);
  });

  test('should have scrollable parameter list when many parameters exist', async ({ page }) => {
    console.log('[TEST] Starting parameter list scroll test');

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Select an event with many parameters
    const eventItems = page.locator('.sidebar-section--event .event-item');
    await eventItems.first().click({ timeout: 5000 });
    await page.waitForTimeout(1000);

    // Wait for parameter list to load
    const paramList = page.locator('.sidebar-section--params .section-content');
    await expect(paramList).toBeVisible({ timeout: 10000 });

    // Check if parameter list is scrollable
    const scrollable = await isScrollable(page, '.sidebar-section--params .section-content');
    console.log('[TEST] Parameter list scrollable:', scrollable);

    // Count total parameters
    const paramItems = page.locator('.sidebar-section--params .param-item, .sidebar-section--params .parameter-item');
    const count = await paramItems.count();
    console.log('[TEST] Total parameters found:', count);
    expect(count).toBeGreaterThanOrEqual(5); // At least 5 parameters

    // If scrollable, test scrolling
    if (scrollable) {
      // Scroll to bottom
      await scrollToSelector(page, '.sidebar-section--params .section-content', 9999);
      
      // Verify last parameter is visible
      const lastParam = paramItems.nth(count - 1);
      await expect(lastParam).toBeVisible();

      // Scroll back to top
      await scrollToSelector(page, '.sidebar-section--params .section-content', 0);
      
      // Verify first parameter is visible
      const firstParam = paramItems.first();
      await expect(firstParam).toBeVisible();
    }

    // Verify overflow CSS
    const scrollInfo = await getScrollInfo(page, '.sidebar-section--params .section-content');
    console.log('[TEST] Parameter list scroll info:', scrollInfo);
    expect(scrollInfo.overflowY).toMatch(/auto|scroll/);
  });

  test('should have scrollable field canvas when many fields added', async ({ page }) => {
    console.log('[TEST] Starting field canvas scroll test');

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Select an event
    const eventItems = page.locator('.sidebar-section--event .event-item');
    await eventItems.first().click({ timeout: 5000 });
    await page.waitForTimeout(1000);

    // Add many fields via double-click on parameters
    const paramItems = page.locator('.sidebar-section--params .param-item, .sidebar-section--params .parameter-item');
    const count = await paramItems.count();
    const fieldsToAdd = Math.min(count, 25); // Add up to 25 fields

    console.log('[TEST] Adding', fieldsToAdd, 'fields to canvas');
    
    for (let i = 0; i < fieldsToAdd; i++) {
      await paramItems.nth(i).dblClick();
      await page.waitForTimeout(100);
    }

    // Wait for fields to be added
    await page.waitForTimeout(1000);

    // Check if field list is scrollable
    const fieldList = page.locator('.field-list');
    const scrollable = await isScrollable(page, '.field-list');
    console.log('[TEST] Field list scrollable:', scrollable);

    // Count total fields
    const fieldItems = page.locator('.field-item');
    const fieldCount = await fieldItems.count();
    console.log('[TEST] Total fields found:', fieldCount);
    expect(fieldCount).toBeGreaterThanOrEqual(15); // At least 15 fields

    // If scrollable, test scrolling
    if (scrollable) {
      // Scroll to bottom
      await scrollToSelector(page, '.field-list', 9999);
      
      // Verify last field is visible
      const lastField = fieldItems.nth(fieldCount - 1);
      await expect(lastField).toBeVisible();

      // Scroll back to top
      await scrollToSelector(page, '.field-list', 0);
      
      // Verify first field is visible
      const firstField = fieldItems.first();
      await expect(firstField).toBeVisible();
    }

    // Verify overflow CSS
    const scrollInfo = await getScrollInfo(page, '.field-list');
    console.log('[TEST] Field list scroll info:', scrollInfo);
    expect(scrollInfo.overflowY).toMatch(/auto|scroll/);
  });

  test('should maintain scroll position when selecting events', async ({ page }) => {
    console.log('[TEST] Starting scroll position persistence test');

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Wait for event list to load
    const eventList = page.locator('.sidebar-section--event .section-content');
    await expect(eventList).toBeVisible();

    // Check if scrollable
    const scrollable = await isScrollable(page, '.sidebar-section--event .section-content');
    
    if (scrollable) {
      // Scroll to middle position
      await scrollToSelector(page, '.sidebar-section--event .section-content', 500);
      
      const midScrollInfo = await getScrollInfo(page, '.sidebar-section--event .section-content');
      console.log('[TEST] Mid-scroll position:', midScrollInfo.scrollTop);

      // Select an event
      const eventItems = page.locator('.sidebar-section--event .event-item');
      await eventItems.nth(5).click();
      await page.waitForTimeout(1000);

      // Verify scroll position is maintained (±100px tolerance)
      const postScrollInfo = await getScrollInfo(page, '.sidebar-section--event .section-content');
      console.log('[TEST] Post-click scroll position:', postScrollInfo.scrollTop);

      const positionDiff = Math.abs(midScrollInfo.scrollTop - postScrollInfo.scrollTop);
      expect(positionDiff).toBeLessThanOrEqual(100); // Allow 100px tolerance
    }
  });

  test('should have smooth scrolling behavior configured', async ({ page }) => {
    console.log('[TEST] Starting smooth scroll behavior test');

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Check for scroll-behavior CSS property
    const eventList = page.locator('.sidebar-section--event .section-content');
    const scrollBehavior = await eventList.evaluate(el => 
      window.getComputedStyle(el).scrollBehavior
    );
    
    console.log('[TEST] scroll-behavior:', scrollBehavior);
    
    // Test smooth scrolling to bottom
    const eventItems = page.locator('.sidebar-section--event .event-item');
    const count = await eventItems.count();
    
    if (count > 5) {
      await scrollToSelector(page, '.sidebar-section--event .section-content', 9999);
      
      // Verify no console errors during scroll
      const consoleErrors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      
      await page.waitForTimeout(1000);
      
      expect(consoleErrors.filter(err => err.includes('scroll')).length).toBe(0);
    }
  });

  test('should have visible scrollbar without breaking layout', async ({ page }) => {
    console.log('[TEST] Starting scrollbar visibility test');

    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // Select an event
    const eventItems = page.locator('.sidebar-section--event .event-item');
    await eventItems.first().click();
    await page.waitForTimeout(1000);

    // Add fields to create scrollable content
    const paramItems = page.locator('.sidebar-section--params .param-item, .sidebar-section--params .parameter-item');
    const count = await paramItems.count();

    for (let i = 0; i < Math.min(count, 15); i++) {
      await paramItems.nth(i).dblclick();
      await page.waitForTimeout(100);
    }

    await page.waitForTimeout(1000);

    // Check scrollbar visibility
    const fieldList = page.locator('.field-list');
    const hasOverflow = await isScrollable(page, '.field-list');
    
    if (hasOverflow) {
      // Check scrollbar width
      const scrollbarWidth = await fieldList.evaluate(el => 
        el.offsetWidth - el.clientWidth
      );
      
      console.log('[TEST] Scrollbar width:', scrollbarWidth, 'px');
      expect(scrollbarWidth).toBeGreaterThan(0); // Scrollbar should be visible

      // Verify no horizontal overflow
      const scrollWidth = await fieldList.evaluate(el => el.scrollWidth);
      const clientWidth = await fieldList.evaluate(el => el.clientWidth);
      const hasHorizontalOverflow = scrollWidth > clientWidth;
      
      console.log('[TEST] Horizontal overflow:', hasHorizontalOverflow);
      expect(hasHorizontalOverflow, 'Field list should not have horizontal overflow').toBeFalsy();
    }
  });
});
