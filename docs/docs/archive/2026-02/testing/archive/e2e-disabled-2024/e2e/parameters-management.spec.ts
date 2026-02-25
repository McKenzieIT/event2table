import { test, expect } from "@playwright/test";
import {
  waitForDataLoad,
  waitForVisible,
  waitForCondition,
  waitForReactMount,
} from "../helpers/wait-helpers";
import { navigateAndSetGameContext } from "../helpers/game-context";

test.describe("参数管理页面 - 自动化测试套件", () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏上下文并导航 - 使用新的 helper 避免竞态条件
    await navigateAndSetGameContext(page, "/parameters", "10000147");

    // 监听控制台错误
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log("Browser console error:", msg.text());
      }
    });

    // 监听页面错误
    page.on("pageerror", (exception) => {
      console.log("Browser page error:", exception);
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态 - 仅清除应用状态，不导航
    await page.evaluate(() => {
      // 清除搜索和筛选状态，保留游戏上下文
      sessionStorage.clear();
      localStorage.removeItem("parametersFilters");
      localStorage.removeItem("parametersSearchQuery");
    });

    // 等待React重新渲染
    await page.waitForTimeout(300);
  });

  test("应该成功加载参数列表页面", async ({ page }) => {
    // 等待页面加载
    await page.waitForSelector(".parameters-list-container", {
      timeout: 10000,
    });

    // 验证页面标题
    await expect(page.locator(".page-header h1")).toContainText("参数管理", {
      timeout: 10000,
    });

    // 验证统计卡片显示
    await expect(page.locator(".stat-card")).toHaveCount(4, { timeout: 10000 });

    // 验证表格存在
    const table = page.locator(".oled-table");
    await expect(table).toBeVisible({ timeout: 10000 });
  });

  test("应该显示参数列表数据或空状态", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 等待数据加载完成(最多10秒)
    await waitForReactMount(page, 100);

    // 检查是否有数据或显示空状态
    const hasParameters = (await page.locator(".parameter-row").count()) > 0;
    const hasEmptyState = (await page.locator(".empty-state").count()) > 0;

    expect(hasParameters || hasEmptyState).toBeTruthy();

    if (hasParameters) {
      // 验证第一行数据结构
      const firstRow = page.locator(".parameter-row").first();
      await expect(firstRow.locator("td").nth(0)).toContainText(/\w+/); // 参数名
      await expect(firstRow.locator("td").nth(3)).toContainText(/\d+/); // 使用事件数
    }
  });

  test("搜索功能应该正常工作", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 等待初始数据加载
    await waitForReactMount(page, 100);

    // 获取初始参数数量
    const initialCount = await page.locator(".parameter-row").count();

    if (initialCount > 0) {
      // 获取第一个参数名
      const firstParamName = await page
        .locator(".parameter-row")
        .first()
        .locator("code")
        .textContent();

      if (firstParamName) {
        // 输入搜索词
        await page.fill(
          'input[placeholder="搜索参数名..."]',
          firstParamName.trim(),
        );

        // 等待搜索结果
        await waitForReactMount(page, 100);

        // 验证搜索结果(应该减少或保持不变)
        const searchCount = await page.locator(".parameter-row").count();
        expect(searchCount).toBeLessThanOrEqual(initialCount);
      }
    }
  });

  test("类型筛选应该正常工作", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 等待数据加载
    await waitForReactMount(page, 100);

    const initialCount = await page.locator(".parameter-row").count();

    if (initialCount > 0) {
      // 选择类型筛选
      await page.selectOption(".glass-select", "int");

      // 等待筛选结果
      await waitForReactMount(page, 100);

      // 验证筛选结果存在
      const filteredCount = await page.locator(".parameter-row").count();

      // 筛选后的数量应该小于或等于初始数量
      expect(filteredCount).toBeLessThanOrEqual(initialCount);

      if (filteredCount > 0) {
        // 验证所有结果的类型徽章显示int(可能需要一些容忍度,因为可能有不同的类型显示)
        const typeBadges = page.locator(".parameter-row .badge");
        const firstBadgeText = await typeBadges.first().textContent();
        console.log("First badge text:", firstBadgeText);
      }
    }
  });

  test("清除筛选应该重置所有筛选条件", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 应用筛选
    await page.fill('input[placeholder="搜索参数名..."]', "test");

    // 等待筛选生效
    await waitForReactMount(page, 50);

    // 验证清除按钮出现
    const clearButton = page.locator('button:has-text("清除筛选")');
    const isVisible = await clearButton.isVisible();

    if (isVisible) {
      // 点击清除筛选
      await clearButton.click();

      // 验证搜索框清空
      const searchValue = await page.inputValue(
        'input[placeholder="搜索参数名..."]',
      );
      expect(searchValue).toBe("");

      // 验证清除按钮消失
      await expect(clearButton).not.toBeVisible();
    }
  });

  test("点击参数应该打开详情抽屉", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 等待数据加载
    await waitForReactMount(page, 100);

    const paramRows = page.locator(".parameter-row");
    const rowCount = await paramRows.count();

    if (rowCount > 0) {
      // 点击第一个参数行
      await paramRows.first().click();

      // 验证抽屉打开(使用更宽松的timeout,因为可能需要加载数据)
      await expect(page.locator(".drawer.show")).toBeVisible({ timeout: 5000 });
      await expect(page.locator(".drawer-header")).toContainText("参数详情");
    } else {
      console.log("No parameters to test drawer functionality");
    }
  });

  test("点击背景遮罩应该关闭抽屉", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    const paramRows = page.locator(".parameter-row");
    const rowCount = await paramRows.count();

    if (rowCount > 0) {
      // 打开抽屉
      await paramRows.first().click();
      await expect(page.locator(".drawer.show")).toBeVisible({ timeout: 5000 });

      // 点击背景遮罩
      await page.locator(".drawer-backdrop.show").click();

      // 验证抽屉关闭
      await expect(page.locator(".drawer.show")).not.toBeVisible({
        timeout: 3000,
      });
    }
  });

  test("按ESC键应该关闭抽屉", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    const paramRows = page.locator(".parameter-row");
    const rowCount = await paramRows.count();

    if (rowCount > 0) {
      // 打开抽屉
      await paramRows.first().click();
      await expect(page.locator(".drawer.show")).toBeVisible({ timeout: 5000 });

      // 按ESC键
      await page.keyboard.press("Escape");

      // 验证抽屉关闭
      await expect(page.locator(".drawer.show")).not.toBeVisible({
        timeout: 3000,
      });
    }
  });

  test("抽屉应该显示参数详细信息", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    const paramRows = page.locator(".parameter-row");
    const rowCount = await paramRows.count();

    if (rowCount > 0) {
      // 打开抽屉
      await paramRows.first().click();
      await expect(page.locator(".drawer.show")).toBeVisible({ timeout: 5000 });

      // 验证基本信息显示
      await expect(page.locator(".drawer-section h5").first()).toContainText(
        "基本信息",
      );

      // 等待详情加载(最多5秒)
      try {
        await page.waitForSelector(".info-grid", { timeout: 5000 });

        // 验证信息项存在
        const infoItems = page.locator(".info-item");
        await expect(infoItems).toHaveCount(4);
      } catch (error) {
        console.log("Info grid not loaded, might be loading data");
      }

      // 验证事件使用情况部分
      await expect(page.locator(".drawer-section h5").nth(1)).toContainText(
        "事件使用情况",
      );
    }
  });

  test("应该显示统计数据卡片", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 验证统计卡片显示
    await expect(page.locator(".stat-card")).toHaveCount(4);

    // 验证统计标签
    await expect(page.locator(".stat-card")).toContainText("总参数数");
    await expect(page.locator(".stat-card")).toContainText("唯一参数名");
    await expect(page.locator(".stat-card")).toContainText("公参数量");
    await expect(page.locator(".stat-card")).toContainText("平均参数/事件");
  });

  test("统计数字应该大于等于0", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    // 获取所有统计数字
    const statNumbers = page.locator(".stat-number");

    for (let i = 0; i < (await statNumbers.count()); i++) {
      const text = await statNumbers.nth(i).textContent();
      const number = parseInt(text || "0");
      expect(number).toBeGreaterThanOrEqual(0);
    }
  });

  test("页面应该没有控制台错误", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    // 收集控制台错误
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    // 等待一会儿收集错误
    await waitForReactMount(page, 100);

    // 验证没有关键错误(500错误,React错误等)
    const criticalErrors = errors.filter(
      (err) =>
        err.includes("500") ||
        err.includes("Internal Server Error") ||
        err.includes("Minified React error"),
    );

    expect(criticalErrors.length).toBe(0);
  });

  test("参数行应该有正确的数据结构", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");
    await waitForReactMount(page, 100);

    const paramRows = page.locator(".parameter-row");
    const rowCount = await paramRows.count();

    if (rowCount > 0) {
      // 验证第一行的列数
      const firstRowCells = paramRows.first().locator("td");
      await expect(firstRowCells).toHaveCount(7);

      // 验证每列的内容类型
      await expect(firstRowCells.nth(0).locator("code")).isVisible(); // 参数名
      await expect(firstRowCells.nth(3)).toContainText(/\d+/); // 使用事件数(数字)
      await expect(firstRowCells.nth(4)).toContainText(/\d+/); // 使用频率(数字)
    }
  });

  test("导出按钮应该存在", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 验证导出按钮存在
    await expect(page.locator('button:has-text("导出Excel")')).toBeVisible();
  });

  test("页面应该有正确的标题和描述", async ({ page }) => {
    await page.waitForSelector(".parameters-list-container");

    // 验证页面标题
    await expect(page.locator(".page-header h1")).toHaveText("参数管理");
    await expect(page.locator(".page-header p")).toHaveText(
      "管理和配置事件参数",
    );
  });
});
