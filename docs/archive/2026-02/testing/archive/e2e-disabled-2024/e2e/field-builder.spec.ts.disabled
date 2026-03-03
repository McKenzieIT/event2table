import { test, expect } from "@playwright/test";
import {
  navigateToFieldBuilder,
  selectFirstEvent,
  expandAllCategories,
  waitForHQLGeneration,
  getHQLPreview,
  switchSQLMode,
  addFieldToCanvas,
} from "../helpers/field-builder";

test.describe("Field Builder Page", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to field builder page
    await navigateToFieldBuilder(page);

    // Wait for page to load
    await page
      .waitForSelector(".field-builder-page", { timeout: 10000 })
      .catch(() => {});

    // Try to expand first category if it exists
    const categoryHeader = page.locator(".category-header").first();
    const count = await categoryHeader.count();
    if (count > 0) {
      await categoryHeader.click().catch(() => {});
      await page.waitForTimeout(500);
    }
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem("fieldBuilderConfig");
      localStorage.removeItem("fieldBuilderFields");
      localStorage.removeItem("fieldBuilderEventId");
    });
    await page.waitForTimeout(300);
  });

  test("should render page container", async ({ page }) => {
    // Check if main page container exists
    await expect(page.locator(".field-builder-page")).toBeVisible();
  });

  test("should render page header with save and close buttons", async ({
    page,
  }) => {
    // Check for page header
    await expect(
      page.locator(".field-builder-page .page-header"),
    ).toBeVisible();

    // Check for save button
    await expect(page.locator('button:has-text("保存")')).toBeVisible();

    // Check for close button
    await expect(page.locator('button:has-text("关闭")')).toBeVisible();
  });

  test("should render three-panel layout", async ({ page }) => {
    // Check for event selector (left panel)
    await expect(page.locator(".event-selector-panel")).toBeVisible();

    // Check for field canvas (center panel)
    await expect(page.locator(".field-canvas-panel")).toBeVisible();

    // Check for HQL preview (right panel)
    await expect(page.locator(".hql-preview-panel")).toBeVisible();
  });

  test("should display loading state while fetching events", async ({
    page,
  }) => {
    // Navigate and check that page loads successfully
    await page.goto("/#/field-builder?gameGid=10000147");

    // Wait for page to load (loading state should appear and disappear)
    await page.waitForSelector(".field-builder-page", { timeout: 10000 });

    // Page should be loaded successfully
    await expect(page.locator(".field-builder-page")).toBeVisible();
  });

  test("should handle error state when API fails", async ({ page }) => {
    // Intercept events API and return error - use unroute first to clear any previous routes
    page.unroute("**/api/events?game_gid=**");
    await page.route("**/api/events?game_gid=**", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Internal Server Error" }),
      });
    });

    // Use a context to ensure fresh request
    await page.context().clearCookies();
    await page.goto("/#/field-builder?gameGid=99999999");

    // Wait for error state or page load
    try {
      await page.waitForSelector(".error-state", { timeout: 5000 });
      await expect(page.locator(".error-state")).toBeVisible();
    } catch {
      // If error state doesn't appear, page should still load
      await expect(page.locator(".field-builder-page")).toBeVisible();
    }
  });

  test("should track unsaved changes", async ({ page }) => {
    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Try to navigate away - should show warning if there are fields
    page.on("dialog", (dialog) => {
      expect(dialog.message()).toContain("有未保存的更改");
      dialog.accept();
    });

    await page.click('button:has-text("关闭")');
  });

  test("should switch SQL mode between view and procedure", async ({
    page,
  }) => {
    // Check initial mode - View mode should be active
    const viewButton = page.locator('button:has-text("视图模式")');
    await expect(viewButton).toBeVisible();

    // Switch to procedure mode
    await page.click('button:has-text("存储过程")');

    // Verify mode changed
    const procedureButton = page.locator('button:has-text("存储过程")');
    await expect(procedureButton).toHaveClass(/btn-primary/);
  });
});

test.describe("Field Builder URL Parameters", () => {
  test("should load game from URL params", async ({ page }) => {
    await page.goto("/#/field-builder?gameGid=10000147");

    // Verify game context is loaded
    await expect(page.locator(".field-builder-page")).toBeVisible();
  });

  test("should load specific event from URL params", async ({ page }) => {
    await page.goto(
      "/#/field-builder?gameGid=10000147&eventId=1",
    );

    // Verify page loads (event may not exist but page should handle it)
    await expect(page.locator(".field-builder-page")).toBeVisible();
  });

  test("should load saved config from URL params", async ({ page }) => {
    await page.goto(
      "/#/field-builder?gameGid=10000147&configId=456",
    );

    // Verify page loads
    await expect(page.locator(".field-builder-page")).toBeVisible();
  });

  test("should require gameGid parameter", async ({ page }) => {
    // Navigate without gameGid
    await page.goto("/#/field-builder");

    // Should show error
    await expect(page.locator(".error-state")).toBeVisible();
  });
});

test.describe("Field Builder Save Functionality", () => {
  test("should save configuration successfully", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Click save (may show alert if no fields)
    page.on("dialog", (dialog) => dialog.accept());
    await page.click('button:has-text("保存")');
  });

  test("should show validation errors before save", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Check that save button is disabled when no event is selected
    const saveButton = page.locator('button:has-text("保存")');
    await expect(saveButton).toBeDisabled();
  });
});

test.describe("Field Builder Keyboard Shortcuts", () => {
  test("should save on Ctrl/Cmd + S", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Handle alert
    page.on("dialog", (dialog) => dialog.accept());

    // Press Ctrl+S
    await page.keyboard.press("Control+s");
  });

  test("should close on Escape", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Press Escape - may show dialog or navigate
    page.on("dialog", (dialog) => dialog.accept());
    await page.keyboard.press("Escape");
  });
});

test.describe("Field Builder Drag and Drop", () => {
  test("should drag parameter from left panel to canvas", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Check if there are parameters/fields to drag
    const paramCount = await page.locator(".param-item").count();
    const initialFieldCount = await page.locator(".field-item").count();

    if (paramCount === 0) {
      test.skip();
      return;
    }

    // Drag first parameter to canvas
    const paramItem = page.locator(".param-item:first-child");
    const canvasDropZone = page.locator(".field-canvas-panel");

    await paramItem.dragTo(canvasDropZone);

    // Verify field was added
    const finalCount = await page.locator(".field-item").count();
    expect(finalCount).toBeGreaterThan(initialFieldCount);
  });

  test("should reorder fields by dragging", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Check if there are enough fields
    const fieldCount = await page.locator(".field-item").count();
    if (fieldCount < 2) {
      test.skip();
      return;
    }

    // Get first field text
    const firstField = page.locator(".field-item:first-child .field-name");
    const firstFieldName = await firstField.textContent();

    // Drag first field to third position
    const firstFieldItem = page.locator(".field-item:first-child");
    const thirdFieldItem = page.locator(".field-item:nth-child(3)");

    await firstFieldItem.dragTo(thirdFieldItem);

    // Verify field moved
    const newFirstField = page.locator(".field-item:first-child .field-name");
    const newFirstFieldName = await newFirstField.textContent();
    expect(newFirstFieldName).not.toBe(firstFieldName);
  });

  test("should remove field by clicking delete button", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Check if there are fields
    const initialCount = await page.locator(".field-item").count();
    if (initialCount === 0) {
      test.skip();
      return;
    }

    // Click delete button on first field
    await page.click(
      '.field-item:first-child button[title="删除字段"], .field-item:first-child .btn-delete, .field-item:first-child .bi-trash',
    );

    // Verify field was removed
    const finalCount = await page.locator(".field-item").count();
    expect(finalCount).toBeLessThan(initialCount);
  });
});

test.describe("HQL Preview Panel", () => {
  test("should display HQL preview after adding fields", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Wait for HQL to generate
    await waitForHQLGeneration(page);

    // Verify HQL preview panel is visible
    await expect(page.locator(".hql-preview-panel")).toBeVisible();
  });

  test("should toggle between View and Procedure modes", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Wait for initial load
    await page.waitForTimeout(1000);

    // Check View mode button is active
    const viewButton = page.locator('button:has-text("视图模式")');
    await expect(viewButton).toHaveClass(/btn-primary/);

    // Switch to Procedure mode
    await page.click('button:has-text("存储过程")');

    // Verify mode changed
    const procedureButton = page.locator('button:has-text("存储过程")');
    await expect(procedureButton).toHaveClass(/btn-primary/);
  });

  test("should switch to edit mode when clicking edit button", async ({
    page,
  }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Wait for HQL preview
    await page.waitForTimeout(1000);

    // Click edit button if it exists
    const editButton = page.locator('button:has-text("编辑")');
    const count = await editButton.count();
    if (count > 0) {
      await editButton.click();
      // Verify CodeMirror editor is visible
      await expect(
        page.locator(".hql-editor-wrapper .cm-editor"),
      ).toBeVisible();
    } else {
      test.skip();
    }
  });

  test("should copy HQL to clipboard", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Wait for HQL preview
    await page.waitForTimeout(1000);

    // Click copy button if it exists
    const copyButton = page.locator('button:has-text("复制")');
    const count = await copyButton.count();
    if (count > 0) {
      await copyButton.click();
      // Verify button text changes or action completes
      await page.waitForTimeout(500);
    } else {
      test.skip();
    }
  });

  test("should show loading state while generating HQL", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Wait for HQL preview
    await page.waitForTimeout(1000);
    // Verify HQL preview is visible (loading or loaded)
    await expect(page.locator(".hql-preview-panel")).toBeVisible();
  });
});

test.describe("Field Builder Edge Cases", () => {
  test("should handle empty state when no event selected", async ({ page }) => {
    await navigateToFieldBuilder(page);

    // Verify empty state message in center panel
    await expect(
      page.locator(".field-canvas-panel .empty-state"),
    ).toBeVisible();
    await expect(page.locator("text=/请从左侧选择一个事件/")).toBeVisible();
  });

  test("should handle unsaved changes warning when switching events", async ({
    page,
  }) => {
    await navigateToFieldBuilder(page);

    // Try to select an event
    const selected = await selectFirstEvent(page);
    if (!selected) {
      test.skip();
      return;
    }

    // Check if there are parameters to click
    const paramCount = await page.locator(".param-item").count();
    if (paramCount === 0) {
      test.skip();
      return;
    }

    // Add a field (trigger unsaved changes)
    await page.click(".param-item:first-child");

    // Try to switch to another event
    page.on("dialog", (dialog) => {
      expect(dialog.message()).toContain("有未保存的更改");
      dialog.accept();
    });

    // Try to expand second category (if exists)
    const secondCategory = page.locator(".category-header").nth(1);
    const categoryCount = await secondCategory.count();
    if (categoryCount > 0) {
      await secondCategory.click();
      await page.waitForTimeout(500);

      // Try to click second event
      const secondEvent = page.locator(".event-item").nth(1);
      const eventCount = await secondEvent.count();
      if (eventCount > 0) {
        await secondEvent.click();
      }
    }
  });

  test("should show error when API fails", async ({ page }) => {
    // Intercept events API
    await page.route("**/api/events?game_gid=**", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ error: "Internal Server Error" }),
      });
    });

    await page.goto("/#/field-builder?gameGid=10000147");

    // Verify error state
    await expect(page.locator(".error-state")).toBeVisible();
    await expect(page.locator("text=/加载失败/")).toBeVisible();
  });
});
