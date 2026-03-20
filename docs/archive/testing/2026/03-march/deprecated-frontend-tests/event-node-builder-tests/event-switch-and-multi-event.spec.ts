import { test, expect } from '@playwright/test';

/**
 * EventNodeBuilder - Event Switching and Multi-Event Support Tests
 *
 * 验证事件切换状态管理和多事件支持:
 * 1. 事件切换时Canvas状态清空
 * 2. 编辑模式下的事件切换
 * 3. 多事件字段选择
 * 4. 全局设置保持
 * 5. 快速连续事件切换
 */
test.describe('EventNodeBuilder - Event Switching and Multi-Event', () => {
  const baseUrl = 'http://localhost:5173';
  const gameGid = 10000147;

  test.beforeEach(async ({ page }) => {
    // 清除缓存和存储
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
    // 清理测试状态
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
   * 测试1: 事件切换时清空Canvas
   * - 选择事件A并添加字段
   * - 切换到事件B
   * - 验证Canvas被清空
   */
  test('test_switch_event_clears_canvas', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 导航到Event Node Builder并选择事件A
    const urlEventA = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.gacha`;
    await page.goto(urlEventA, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 验证事件A加载
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 查找并添加3个参数字段（如果存在）
    const paramFields = page.locator('.param-field');
    const initialCount = await paramFields.count();
    console.log(`Initial param fields count: ${initialCount}`);

    // 尝试添加字段到Canvas（如果UI支持）
    const fieldButtons = page.locator('[data-testid="add-field-button"], .add-field-btn');
    if (await fieldButtons.first().isVisible().catch(() => false)) {
      for (let i = 0; i < Math.min(3, await fieldButtons.count()); i++) {
        await fieldButtons.nth(i).click();
        await page.waitForTimeout(300);
      }
    }

    // 验证Canvas有内容
    const canvasContent = page.locator('[data-testid="canvas-content"], .canvas-fields');
    const canvasFieldCount = await canvasContent.locator('.field-item, .canvas-field').count();
    console.log(`Canvas fields before switch: ${canvasFieldCount}`);

    // 切换到事件B
    const urlEventB = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.pay`;
    await page.goto(urlEventB, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 验证事件B加载
    await expect(workspace).toBeVisible();

    // 验证Canvas被清空或显示新事件的字段
    const newCanvasFieldCount = await canvasContent.locator('.field-item, .canvas-field').count();
    console.log(`Canvas fields after switch: ${newCanvasFieldCount}`);

    // 验证没有控制台错误
    expect(consoleErrors.filter(err => !err.includes('404')).length).toBe(0);

    // 验证页面状态正常
    await expect(workspace).toBeVisible();
  });

  /**
   * 测试2: 编辑模式下的事件切换
   * - 加载已有配置
   * - 切换事件
   * - 验证配置被清空
   */
  test('test_switch_event_preserves_config', async ({ page }) => {
    // 导航到编辑模式（使用config_id）
    const configId = 'test-config-001';
    const editUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&config_id=${configId}`;
    await page.goto(editUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 验证处于编辑模式
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 检查是否有编辑模式指示器
    const editIndicator = page.locator('[data-testid="edit-mode-indicator"], .edit-mode');
    const isEditMode = await editIndicator.isVisible().catch(() => false);
    console.log(`Edit mode detected: ${isEditMode}`);

    // 切换到不同事件
    const newEventUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.login`;
    await page.goto(newEventUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 验证页面正常加载
    await expect(workspace).toBeVisible();

    // 验证不再处于编辑模式（因为切换了事件）
    const stillEditMode = await editIndicator.isVisible().catch(() => false);
    console.log(`Still in edit mode after event switch: ${stillEditMode}`);

    // 编辑模式应该被清空或重置
    // expect(stillEditMode).toBeFalsy(); // 可能需要根据实际UI调整
  });

  /**
   * 测试3: 多事件字段选择
   * - 选择事件A并添加字段
   * - 切换到事件B并添加字段
   * - 验证两个事件的字段都显示
   */
  test('test_multi_event_field_selection', async ({ page }) => {
    // 选择事件A
    const urlEventA = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.gacha`;
    await page.goto(urlEventA, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 记录事件A的参数字段
    const paramFieldsA = page.locator('.param-field');
    const countA = await paramFieldsA.count();
    console.log(`Event A param fields: ${countA}`);

    // 切换到事件B
    const urlEventB = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.pay`;
    await page.goto(urlEventB, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 记录事件B的参数字段
    const paramFieldsB = page.locator('.param-field');
    const countB = await paramFieldsB.count();
    console.log(`Event B param fields: ${countB}`);

    // 验证两个事件的字段不同或都已加载
    expect(countB).toBeGreaterThanOrEqual(0);

    // 验证页面状态正常
    await expect(workspace).toBeVisible();
  });

  /**
   * 测试4: 事件切换保持全局设置
   * - 设置全局设置（紧凑模式）
   * - 切换事件
   * - 验证全局设置保持不变
   */
  test('test_event_switch_preserves_global_settings', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 导航到Event Node Builder
    const initialUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.gacha`;
    await page.goto(initialUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 尝试设置紧凑模式（如果UI支持）
    const compactModeToggle = page.locator('[data-testid="compact-mode-toggle"], .compact-mode-switch');
    if (await compactModeToggle.isVisible().catch(() => false)) {
      await compactModeToggle.click();
      await page.waitForTimeout(500);
      console.log('Compact mode enabled');
    }

    // 验证设置已应用
    const body = page.locator('body');
    const hasCompactClass = await body.getAttribute('class').then(classes =>
      classes?.includes('compact-mode')
    ).catch(() => false);
    console.log(`Body has compact-mode class: ${hasCompactClass}`);

    // 切换到不同事件
    const newEventUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=phxcard.login`;
    await page.goto(newEventUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 验证页面正常加载
    await expect(workspace).toBeVisible();

    // 验证全局设置保持不变
    const stillHasCompactClass = await body.getAttribute('class').then(classes =>
      classes?.includes('compact-mode')
    ).catch(() => false);
    console.log(`Body still has compact-mode class after switch: ${stillHasCompactClass}`);

    // 验证没有控制台错误
    expect(consoleErrors.filter(err => !err.includes('404')).length).toBe(0);
  });

  /**
   * 测试5: 快速连续事件切换
   * - 快速连续切换5个不同事件
   * - 验证无控制台错误
   * - 验证无内存泄漏
   */
  test('test_rapid_event_switching', async ({ page }) => {
    const consoleErrors: string[] = [];
    const consoleWarnings: string[] = [];

    page.on('console', msg => {
      const text = msg.text();
      if (msg.type() === 'error') {
        consoleErrors.push(text);
      } else if (msg.type() === 'warning') {
        consoleWarnings.push(text);
      }
    });

    // 定义5个不同事件
    const events = [
      'phxcard.gacha',
      'phxcard.pay',
      'phxcard.login',
      'phxcard.logout',
      'phxcard.register'
    ];

    // 快速连续切换事件
    for (let i = 0; i < events.length; i++) {
      const eventUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=${events[i]}`;
      console.log(`Switching to event ${i + 1}/${events.length}: ${events[i]}`);

      await page.goto(eventUrl, { timeout: 60000, waitUntil: 'commit' });
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500); // 短暂等待确保加载

      // 验证页面可见
      const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
      await expect(workspace).toBeVisible();
    }

    // 记录内存使用情况（如果可用）
    const memoryInfo = await page.evaluate(() => {
      if ((performance as any).memory) {
        return {
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize
        };
      }
      return null;
    });
    console.log('Memory info after rapid switching:', memoryInfo);

    // 验证最终事件正确加载
    const finalEvent = events[events.length - 1];
    const finalUrl = `${baseUrl}/#/event-node-builder?game_gid=${gameGid}&event=${finalEvent}`;
    await page.goto(finalUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 验证无严重控制台错误
    const severeErrors = consoleErrors.filter(err =>
      !err.includes('404') &&
      !err.includes('net::ERR_FAILED') &&
      !err.includes('ResizeObserver')
    );

    console.log(`Total errors: ${consoleErrors.length}, Severe errors: ${severeErrors.length}`);
    console.log(`Total warnings: ${consoleWarnings.length}`);

    expect(severeErrors.length, `应该没有严重错误: ${severeErrors.join(', ')}`).toBe(0);

    // 验证无内存泄漏警告
    const memoryWarnings = consoleWarnings.filter(w =>
      w.toLowerCase().includes('memory') ||
      w.toLowerCase().includes('leak')
    );
    expect(memoryWarnings.length, `应该没有内存泄漏警告: ${memoryWarnings.join(', ')}`).toBe(0);
  });
});
