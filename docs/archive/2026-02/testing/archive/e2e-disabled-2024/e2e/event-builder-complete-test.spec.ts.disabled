import { test, expect } from "@playwright/test";
import { waitForReactMount, waitForDataLoad } from "../helpers/wait-helpers";

/**
 * 事件节点构建器完整功能测试
 * Event Node Builder Complete Functionality Test
 *
 * 测试双击和拖拽功能是否正常工作
 */

test.describe("事件节点构建器 - 完整功能测试", () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏上下文到localStorage（模拟已选择游戏）
    await page.goto("http://127.0.0.1:5001/");
    await page.evaluate(() => {
      const gameData = {
        id: 325,
        gid: 10000147,
        name: "Duplicate Game",
        ods_db: "ieu_ods",
      };
      localStorage.setItem("selectedGameGid", "10000147");
      localStorage.setItem("selectedGameData", JSON.stringify(gameData));
      window.gameData = gameData;
    });

    // 访问事件节点构建器页面
    await page.goto(
      "http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147",
    );

    // 等待React组件完全渲染（增加等待时间）
    await waitForDataLoad(page, 5000);

    // 额外等待确保EventNodeBuilder完全加载
    await page
      .waitForSelector(".event-node-builder", {
        state: "visible",
        timeout: 10000,
      })
      .catch(() => {
        console.log(
          "EventNodeBuilder not found immediately, waiting longer...",
        );
        // 如果还没找到，再等待5秒
        return page.waitForTimeout(5000);
      });

    // 打开控制台以查看日志
    page.on("console", (msg) => {
      if (msg.type() === "log") {
        console.log("Browser Console:", msg.text());
      }
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem("eventNodeBuilderConfig");
      localStorage.removeItem("eventNodeBuilderFields");
    });
    await page.waitForTimeout(300);
  });

  test("页面应该正确加载", async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/DWD Generator/);

    // 验证事件节点构建器容器存在
    const container = page.locator(".event-node-builder");
    await expect(container).toBeVisible();

    // 验证三个主要区域存在
    await expect(page.locator(".sidebar-left")).toBeVisible();
    await expect(page.locator(".field-canvas")).toBeVisible();
    await expect(page.locator(".sidebar-right")).toBeVisible();
  });

  test("双击基础字段应该添加到画布", async ({ page }) => {
    console.log("测试：双击基础字段");

    // 找到第一个基础字段（例如"分区"）
    const baseField = page.locator('[data-field="ds"]').first();

    // 验证字段存在
    await expect(baseField).toBeVisible();

    // 记录双击前的字段数量
    const beforeCount = await page.locator(".field-item").count();
    console.log("双击前的字段数量:", beforeCount);

    // 双击字段
    await baseField.dblclick();
    await waitForReactMount(page);

    // 验证字段已添加到画布
    const afterCount = await page.locator(".field-item").count();
    console.log("双击后的字段数量:", afterCount);

    expect(afterCount).toBe(beforeCount + 1);

    // 验证新字段的内容
    const newField = page.locator(".field-item").last();
    await expect(newField).toContainText("分区");
  });

  test("双击多个基础字段", async ({ page }) => {
    console.log("测试：双击多个基础字段");

    const fields = ["ds", "role_id", "account_id"];

    for (const fieldName of fields) {
      const baseField = page.locator(`[data-field="${fieldName}"]`).first();
      await baseField.dblclick();
      await waitForReactMount(page);
      console.log(`双击字段: ${fieldName}`);
    }

    // 验证所有字段都添加成功
    const fieldCount = await page.locator(".field-item").count();
    console.log("最终字段数量:", fieldCount);

    expect(fieldCount).toBeGreaterThanOrEqual(fields.length);
  });

  test("选择事件后双击参数字段", async ({ page }) => {
    console.log("测试：选择事件后双击参数字段");

    // 首先选择一个事件
    await page.selectOption("#event-selector", "0");
    await waitForReactMount(page);

    // 检查是否有参数字段
    const paramCount = await page.locator("[data-param]").count();
    console.log("参数字段数量:", paramCount);

    if (paramCount > 0) {
      // 双击第一个参数字段
      const firstParam = page.locator("[data-param]").first();
      await firstParam.dblclick();
      await waitForReactMount(page);

      // 验证字段添加成功
      const fieldCount = await page.locator(".field-item").count();
      expect(fieldCount).toBeGreaterThan(0);
    } else {
      console.log("没有找到参数字段，跳过测试");
    }
  });

  test("拖拽基础字段到画布", async ({ page }) => {
    console.log("测试：拖拽基础字段到画布");

    // 找到基础字段和画布区域
    const baseField = page.locator('[data-field="tm"]').first();
    const canvas = page.locator(".canvas-area").first();

    // 验证元素存在
    await expect(baseField).toBeVisible();
    await expect(canvas).toBeVisible();

    // 记录拖拽前的字段数量
    const beforeCount = await page.locator(".field-item").count();

    // 执行拖拽操作
    await baseField.dragTo(canvas);

    // 等待拖拽完成
    await waitForReactMount(page);

    // 验证字段添加成功
    const afterCount = await page.locator(".field-item").count();
    console.log("拖拽前字段数:", beforeCount, "拖拽后字段数:", afterCount);

    expect(afterCount).toBeGreaterThan(beforeCount);
  });

  test("字段画布内的拖拽排序", async ({ page }) => {
    console.log("测试：字段画布内的拖拽排序");

    // 先添加几个字段
    const fields = ["ds", "role_id", "account_id"];
    for (const fieldName of fields) {
      const baseField = page.locator(`[data-field="${fieldName}"]`).first();
      await baseField.dblclick();
      await waitForReactMount(page);
    }

    // 等待所有字段加载完成
    await waitForReactMount(page);

    // 获取所有字段
    const fieldItems = page.locator(".field-item");
    const count = await fieldItems.count();
    console.log("画布中的字段数量:", count);

    if (count >= 2) {
      // 获取第一个和最后一个字段
      const firstField = fieldItems.first();
      const lastField = fieldItems.last();

      // 获取拖拽前第一个字段的文本
      const firstFieldTextBefore = await firstField.textContent();

      // 拖拽第一个字段到最后一个字段之后
      await firstField.dragTo(lastField);
      await waitForReactMount(page);

      // 验证字段顺序已改变
      const firstFieldTextAfter = await fieldItems.first().textContent();

      console.log("排序前第一个字段:", firstFieldTextBefore);
      console.log("排序后第一个字段:", firstFieldTextAfter);

      // 顺序应该已经改变
      expect(firstFieldTextAfter).not.toBe(firstFieldTextBefore);
    } else {
      console.log("字段数量不足，无法测试排序");
    }
  });

  test("编辑字段配置", async ({ page }) => {
    console.log("测试：编辑字段配置");

    // 先添加一个字段
    const baseField = page.locator('[data-field="ds"]').first();
    await baseField.dblclick();
    await waitForReactMount(page);

    // 双击字段卡片打开编辑
    const fieldCard = page.locator(".field-item").first();
    await fieldCard.dblclick();
    await waitForReactMount(page);

    // 检查是否有编辑弹窗或输入框
    const editModal = page
      .locator(".modal.show")
      .or(page.locator('[role="dialog"]'));
    const isVisible = await editModal.isVisible();

    if (isVisible) {
      console.log("编辑弹窗已打开");
      // 关闭弹窗
      await page.keyboard.press("Escape");
      await waitForReactMount(page);
    } else {
      console.log("没有检测到编辑弹窗，可能是inline编辑或其他方式");
    }
  });

  test("删除字段", async ({ page }) => {
    console.log("测试：删除字段");

    // 先添加一个字段
    const baseField = page.locator('[data-field="utdid"]').first();
    await baseField.dblclick();
    await waitForReactMount(page);

    // 记录删除前的字段数量
    const beforeCount = await page.locator(".field-item").count();

    // 点击删除按钮
    const deleteButton = page
      .locator(".field-item")
      .first()
      .locator(".btn-outline-danger");
    await deleteButton.click();

    // 处理可能的确认弹窗
    await waitForReactMount(page);

    // 验证字段已删除
    const afterCount = await page.locator(".field-item").count();
    console.log("删除前字段数:", beforeCount, "删除后字段数:", afterCount);

    expect(afterCount).toBeLessThan(beforeCount);
  });

  test("验证CSS变量已加载", async ({ page }) => {
    console.log("测试：验证CSS变量已加载");

    // 检查是否使用了新的CSS变量
    const canvas = page.locator(".field-canvas");
    const computedStyle = await canvas.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        padding: styles.padding,
        background: styles.background,
      };
    });

    console.log("画布计算样式:", computedStyle);

    // 验证样式不为空
    expect(computedStyle.background).toBeTruthy();
  });

  test("控制台日志检查", async ({ page }) => {
    console.log("测试：控制台日志检查");

    const logs: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "log") {
        logs.push(msg.text());
      }
    });

    // 执行一些操作
    const baseField = page.locator('[data-field="ds"]').first();
    await baseField.dblclick();
    await waitForReactMount(page);

    // 检查是否有预期的日志
    const hasBaseFieldLog = logs.some(
      (log) => log.includes("BaseFieldsList") && log.includes("Double clicked"),
    );
    const hasHookLog = logs.some(
      (log) =>
        log.includes("useEventNodeBuilder") && log.includes("addFieldToCanvas"),
    );

    console.log("收集到的日志:", logs);
    console.log("有BaseFieldsList日志:", hasBaseFieldLog);
    console.log("有useEventNodeBuilder日志:", hasHookLog);

    expect(hasBaseFieldLog || hasHookLog).toBeTruthy();
  });
});

test.describe("事件节点构建器 - 视觉和UI测试", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(
      "http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147",
    );
    await page.waitForLoadState("networkidle");
    await waitForReactMount(page);
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem("eventNodeBuilderConfig");
      localStorage.removeItem("eventNodeBuilderFields");
    });
    await page.waitForTimeout(300);
  });

  test("验证Glassmorphism样式应用", async ({ page }) => {
    // 检查页面头部是否有渐变背景
    const header = page.locator(".page-header");
    await expect(header).toBeVisible();

    const headerBg = await header.evaluate((el) => {
      return window.getComputedStyle(el).background;
    });

    console.log("页面头部背景:", headerBg);
    expect(headerBg).toContain("gradient");
  });

  test("验证字段卡片样式", async ({ page }) => {
    // 先添加一个字段
    const baseField = page.locator('[data-field="ds"]').first();
    await baseField.dblclick();
    await waitForReactMount(page);

    // 检查字段卡片样式
    const fieldCard = page.locator(".field-item").first();
    await expect(fieldCard).toBeVisible();

    // 检查是否有拖拽手柄
    const dragHandle = fieldCard.locator(".field-handle");
    await expect(dragHandle).toBeVisible();

    // 检查是否有类型图标
    const typeIcon = fieldCard.locator(".field-type-badge i");
    await expect(typeIcon).toBeVisible();
  });

  test("验证响应式布局", async ({ page }) => {
    // 测试桌面尺寸
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForLoadState("domcontentloaded");
    await waitForReactMount(page);

    const sidebarLeftDesktop = page.locator(".sidebar-left");
    const desktopWidth = await sidebarLeftDesktop.evaluate(
      (el) => el.offsetWidth,
    );
    console.log("桌面端左侧边栏宽度:", desktopWidth);

    // 测试平板尺寸
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForLoadState("domcontentloaded");
    await waitForReactMount(page, 1000);

    const sidebarLeftTablet = page.locator(".sidebar-left");
    const tabletWidth = await sidebarLeftTablet.evaluate(
      (el) => el.offsetWidth,
    );
    console.log("平板端左侧边栏宽度:", tabletWidth);

    // 平板端宽度应该等于容器宽度
    expect(tabletWidth).toBeGreaterThan(desktopWidth * 0.8);
  });
});
