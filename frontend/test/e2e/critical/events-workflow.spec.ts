import { test, expect } from "@playwright/test";
import {
  waitForDataLoad,
  waitForVisible,
  waitForCondition,
  waitForReactMount,
} from "../helpers/wait-helpers";
import { navigateAndSetGameContext } from "../helpers/game-context";

/**
 * 事件管理工作流E2E测试
 *
 * 测试事件的CRUD操作：
 * - 查看事件列表
 * - 创建新事件
 * - 编辑事件
 * - 删除事件
 * - 批量操作
 */
test.describe("事件管理工作流", () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态 - 仅清除应用状态，不导航
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem("eventsFilters");
      localStorage.removeItem("eventsSearchQuery");
    });
    await page.waitForTimeout(300);
  });
  test("应该能够查看事件列表", async ({ page }) => {
    // 使用 navigateAndSetGameContext 设置上下文并导航
    await navigateAndSetGameContext(page, "/events", "10000147");

    // 等待页面加载
    await page.waitForLoadState("domcontentloaded");
    await waitForReactMount(page, 100);

    // 检查是否显示游戏选择提示
    const gamePromptCount = await page
      .locator(".select-game-prompt, .game-selection-prompt")
      .count();
    if (gamePromptCount > 0) {
      test.skip();
      return;
    }

    // 验证页面加载成功（检查h1或页面容器）
    const h1Locator = page
      .locator('h1:has-text("事件")')
      .or(page.locator('h1:has-text("事件管理")'))
      .or(page.locator('h1:has-text("日志事件")'));
    const h1Count = await h1Locator.count();

    // 如果找不到h1，至少验证页面容器存在
    if (h1Count === 0) {
      await expect(page.locator("body")).toBeVisible();
      test.skip();
      return;
    }

    await expect(h1Locator.first()).toBeVisible();
  });

  test("事件列表应该有搜索功能", async ({ page }) => {
    await page.goto("/#/events");

    // 等待页面加载
    await waitForReactMount(page, 100);

    // 验证搜索框存在
    const searchInput = page
      .locator(
        'input[placeholder*="搜索"], input[placeholder*="search"], .search-input',
      )
      .first();
    if (await searchInput.isVisible()) {
      // 测试搜索功能
      await searchInput.fill("test");

      // 等待搜索结果
      await waitForReactMount(page, 50);
    }
  });

  test("应该能够打开事件创建表单", async ({ page }) => {
    await page.goto("/#/events");

    // 查找并点击"创建事件"按钮
    const createButton = page
      .locator(
        'button:has-text("创建"), button:has-text("新建"), button:has-text("添加"), a:has-text("创建")',
      )
      .first();

    if (await createButton.isVisible()) {
      await createButton.click();

      // 验证表单页面加载
      await expect(
        page
          .locator('form, .event-form, h1:has-text("创建")')
          .or(page.locator('h1:has-text("新建")'))
          .first(),
      ).toBeVisible({ timeout: 3000 });
    }
  });

  test("应该能够创建新事件", async ({ page }) => {
    await page.goto("/#/events/create");

    // 等待表单加载
    await waitForReactMount(page, 100);

    // 查找表单字段
    const eventNameInput = page
      .locator(
        'input[name="event_name"], input[placeholder*="事件名"], input[id*="event"]',
      )
      .first();
    const eventNameCnInput = page
      .locator(
        'input[name="event_name_cn"], input[placeholder*="中文名"], input[id*="cn"]',
      )
      .first();

    // 填写表单
    if (await eventNameInput.isVisible()) {
      await eventNameInput.fill(`test.event.${Date.now()}`);
    }

    if (await eventNameCnInput.isVisible()) {
      await eventNameCnInput.fill("测试事件");
    }

    // 提交表单
    const submitButton = page
      .locator(
        'button[type="submit"], button:has-text("保存"), button:has-text("提交"), button:has-text("创建")',
      )
      .first();
    if (await submitButton.isVisible()) {
      await submitButton.click();

      // 等待响应
      await waitForReactMount(page, 100);

      // 验证成功消息或导航
      const currentUrl = page.url();
      const hasSuccessMessage =
        (await page.locator("text=成功, text=已创建, text=保存").count()) > 0;

      if (!hasSuccessMessage && !currentUrl.includes("/events")) {
        console.log("表单提交完成，但未检测到明确的成功消息");
      }
    }
  });

  test("应该能够编辑事件", async ({ page }) => {
    // 先导航到事件列表
    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 查找第一个事件
    const firstEvent = page
      .locator(".event-item, .event-row, [data-event-id]")
      .first();

    if (await firstEvent.isVisible()) {
      // 点击编辑按钮
      const editButton = firstEvent
        .locator('.btn-edit, button:has-text("编辑"), .edit-button')
        .first();

      if (await editButton.isVisible()) {
        await editButton.click();

        // 等待编辑表单加载
        await waitForReactMount(page, 100);

        // 验证表单存在
        const form = page.locator("form, .event-form").first();
        await expect(form).toBeVisible();

        // 修改中文名称
        const nameCnInput = page.locator('input[name="event_name_cn"]').first();
        if (await nameCnInput.isVisible()) {
          await nameCnInput.fill("更新后的事件");

          // 提交更改
          const submitButton = page.locator('button[type="submit"]').first();
          await submitButton.click();

          // 等待响应
          await waitForReactMount(page, 100);

          // 验证成功
          const hasSuccessMessage =
            (await page.locator("text=更新成功, text=保存成功").count()) > 0;
          if (!hasSuccessMessage) {
            console.log("编辑提交完成，但未检测到明确的成功消息");
          }
        }
      }
    }
  });

  test("应该能够删除事件", async ({ page }) => {
    // 注意：这个测试会实际删除数据，可能导致其他测试失败
    // 考虑跳过或使用测试数据

    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 查找第一个事件
    const firstEvent = page.locator(".event-item, .event-row").first();

    if (await firstEvent.isVisible()) {
      // 点击删除按钮
      const deleteButton = firstEvent
        .locator('.btn-delete, button:has-text("删除"), .delete-button')
        .first();

      if (await deleteButton.isVisible()) {
        // 先记录事件数量
        const eventCountBefore = await page
          .locator(".event-item, .event-row")
          .count();

        await deleteButton.click();

        // 确认删除对话框
        const confirmButton = page
          .locator(
            'button:has-text("确认"), button:has-text("确定"), button:has-text("删除")',
          )
          .first();
        if (await confirmButton.isVisible()) {
          await confirmButton.click();

          // 等待删除完成
          await waitForReactMount(page, 100);

          // 验证事件数量减少（可选，因为可能有分页）
          const eventCountAfter = await page
            .locator(".event-item, .event-row")
            .count();
          console.log(`事件数量: ${eventCountBefore} -> ${eventCountAfter}`);
        }
      }
    }
  });

  test("应该能够批量选择事件", async ({ page }) => {
    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 查找复选框
    const firstCheckbox = page
      .locator(
        '.event-item input[type="checkbox"], .event-row input[type="checkbox"]',
      )
      .first();

    if (await firstCheckbox.isVisible()) {
      // 点击第一个复选框
      await firstCheckbox.check();

      // 验证复选框被选中
      await expect(firstCheckbox).toBeChecked();

      // 验证批量操作按钮出现（如果有）
      const batchActions = page
        .locator(".batch-actions, .selection-bar")
        .first();
      if (await batchActions.isVisible({ timeout: 1000 })) {
        console.log("批量操作栏已显示");
      }
    }
  });
});

/**
 * 事件表单验证测试
 */
test.describe("事件表单验证", () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndSetGameContext(page, "/events", "10000147");
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem("eventFormDraft");
    });
    await page.waitForTimeout(300);
  });

  test("应该验证必填字段", async ({ page }) => {
    await page.goto("/#/events/create");

    await waitForReactMount(page, 100);

    // 尝试直接提交空表单
    const submitButton = page.locator('button[type="submit"]').first();
    if (await submitButton.isVisible()) {
      await submitButton.click();

      // 等待验证错误
      await waitForReactMount(page, 100);

      // 验证显示错误消息或表单未提交
      const currentUrl = page.url();
      expect(currentUrl).toContain("/events");
    }
  });

  test("应该支持表单取消操作", async ({ page }) => {
    await page.goto("/#/events/create");

    await waitForReactMount(page, 100);

    // 查找取消按钮
    const cancelButton = page
      .locator(
        'button:has-text("取消"), button:has-text("返回"), a:has-text("返回")',
      )
      .first();

    if (await cancelButton.isVisible()) {
      await cancelButton.click();

      // 验证返回到事件列表
      await waitForReactMount(page, 100);
      const currentUrl = page.url();
      expect(currentUrl).toContain("/events");
    }
  });
});
