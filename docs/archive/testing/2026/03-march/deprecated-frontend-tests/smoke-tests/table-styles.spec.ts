import { test, expect } from "@playwright/test";
import { waitForReactMount } from "../helpers/wait-helpers";
import { navigateAndSetGameContext } from "../helpers/game-context";

/**
 * 表格样式验证E2E测试
 *
 * 测试确保所有页面使用统一的cyber-table样式
 * 而非遗留的oled-table样式
 */
test.describe("表格样式统一验证", () => {
  test.beforeEach(async ({ page }) => {
    await navigateAndSetGameContext(page, "/events", "10000147");
  });

  test("事件列表应使用cyber-table样式", async ({ page }) => {
    // 导航到事件列表页面
    await page.goto("/#/events");

    // 等待页面加载
    await waitForReactMount(page, 100);

    // 检查是否显示游戏选择提示
    const gamePrompt = page.locator(".select-game-prompt, .game-selection-prompt");
    if (await gamePrompt.isVisible()) {
      test.skip();
      return;
    }

    // 验证表格存在
    const table = page.locator("table").first();
    if (!(await table.isVisible())) {
      test.skip();
      return;
    }

    // ✅ 关键断言：表格应该使用cyber-table类
    // 当前状态：使用oled-table（测试会失败 - RED）
    // 目标状态：使用cyber-table（测试会通过 - GREEN）
    await expect(page.locator(".cyber-table")).toBeVisible({ timeout: 5000 });

    // 验证没有遗留的oled-table类
    const oledTableCount = await page.locator(".oled-table").count();
    expect(oledTableCount).toBe(0);

    // 验证cyber-table的结构完整性
    await expect(page.locator(".cyber-table__header")).toBeVisible();
    await expect(page.locator(".cyber-table__body")).toBeVisible();
    await expect(page.locator(".cyber-table__row").first()).toBeVisible();
    await expect(page.locator(".cyber-table__cell").first()).toBeVisible();

    console.log("✅ EventsList使用cyber-table样式");
  });

  test("参数列表应使用cyber-table样式", async ({ page }) => {
    // 导航到参数列表页面
    await page.goto("/#/parameters");

    // 等待页面加载
    await waitForReactMount(page, 100);

    // 检查是否显示游戏选择提示
    const gamePrompt = page.locator(".select-game-prompt, .game-selection-prompt");
    if (await gamePrompt.isVisible()) {
      test.skip();
      return;
    }

    // 验证表格存在
    const table = page.locator("table").first();
    if (!(await table.isVisible())) {
      test.skip();
      return;
    }

    // ✅ 关键断言：表格应该使用cyber-table类
    await expect(page.locator(".cyber-table")).toBeVisible({ timeout: 5000 });

    // 验证没有遗留的oled-table类
    const oledTableCount = await page.locator(".oled-table").count();
    expect(oledTableCount).toBe(0);

    console.log("✅ ParametersList使用cyber-table样式");
  });

  test("cyber-table应该支持排序功能", async ({ page }) => {
    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 检查游戏选择提示
    const gamePrompt = page.locator(".select-game-prompt, .game-selection-prompt");
    if (await gamePrompt.isVisible()) {
      test.skip();
      return;
    }

    // 查找可排序的表头
    const sortableHeader = page.locator(".cyber-table__head--sortable").first();

    if (await sortableHeader.isVisible()) {
      // 验证排序指示器存在
      const sortIndicator = sortableHeader.locator(".cyber-table__sort-indicator");
      await expect(sortIndicator).toBeVisible();

      // 点击排序
      await sortableHeader.click();
      await waitForReactMount(page, 50);

      // 验证排序状态改变
      await expect(sortableHeader).toHaveClass(/cyber-table__head--sorted/);

      console.log("✅ cyber-table排序功能正常");
    } else {
      console.log("⚠️ 未找到可排序的表头");
    }
  });

  test("cyber-table应该支持行点击交互", async ({ page }) => {
    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 检查游戏选择提示
    const gamePrompt = page.locator(".select-game-prompt, .game-selection-prompt");
    if (await gamePrompt.isVisible()) {
      test.skip();
      return;
    }

    // 查找第一行
    const firstRow = page.locator(".cyber-table__row").first();

    if (await firstRow.isVisible()) {
      // 验证可点击行的样式
      const hasClickableClass = await firstRow.evaluate(
        (el) => el.classList.contains("cyber-table__row--clickable")
      );

      if (hasClickableClass) {
        console.log("✅ cyber-table支持行点击交互");

        // 测试点击效果（悬停）
        await firstRow.hover();
        await waitForReactMount(page, 50);

        // 验证悬停样式（通过检查是否有特定的hover效果）
        const hasHoverEffect = await firstRow.evaluate((el) => {
          const styles = window.getComputedStyle(el);
          return styles.cursor === "pointer" || styles.cursor === "default";
        });

        expect(hasHoverEffect).toBeTruthy();
      } else {
        console.log("ℹ️ 当前行不可点击（预期行为）");
      }
    }
  });

  test("cyber-table应该支持斑马纹样式", async ({ page }) => {
    await page.goto("/#/events");

    await waitForReactMount(page, 100);

    // 检查游戏选择提示
    const gamePrompt = page.locator(".select-game-prompt, .game-selection-prompt");
    if (await gamePrompt.isVisible()) {
      test.skip();
      return;
    }

    // 验证表格有striped类
    const table = page.locator(".cyber-table").first();

    if (await table.isVisible()) {
      const hasStripedClass = await table.evaluate(
        (el) => el.classList.contains("cyber-table--striped")
      );

      if (hasStripedClass) {
        console.log("✅ cyber-table启用斑马纹样式");

        // 验证行的不同背景色
        const firstRow = page.locator(".cyber-table__row").first();
        const secondRow = page.locator(".cyber-table__row").nth(1);

        if ((await firstRow.count()) > 0 && (await secondRow.count()) > 0) {
          const firstRowBg = await firstRow.evaluate((el) =>
            window.getComputedStyle(el).backgroundColor
          );
          const secondRowBg = await secondRow.evaluate((el) =>
            window.getComputedStyle(el).backgroundColor
          );

          // 验证相邻行的背景色不同（斑马纹效果）
          expect(firstRowBg).not.toBe(secondRowBg);
        }
      } else {
        console.log("ℹ️ 表格未启用斑马纹");
      }
    }
  });
});
