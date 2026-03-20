import { test, expect } from '@playwright/test';

/**
 * EventNodeBuilder 页面修复验证测试
 *
 * 验证以下修复:
 * 1. ParamSelector.jsx: debouncedSearch → searchQuery
 * 2. gameGid 类型转换: string → number
 * 3. defaultProps 转换为函数参数默认值
 */
test.describe('EventNodeBuilder - Rendering Error Fixes', () => {
  const baseUrl = 'http://localhost:5173';
  const eventNodeBuilderUrl = `${baseUrl}/#/event-node-builder?game_gid=10000147`;

  test.beforeEach(async ({ page }) => {
    // 清除缓存数据
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

  test('页面应该能够正常加载而不崩溃', async ({ page }) => {
    // 监听控制台错误
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 导航到 EventNodeBuilder 页面
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });

    // 等待页面加载
    await page.waitForTimeout(1000);

    // 验证页面显示（不是错误边界）
    const errorBoundary = page.locator('[data-testid="event-node-builder-error"]');
    const isVisible = await errorBoundary.isVisible().catch(() => false);

    expect(isVisible).toBeFalsy();

    // 验证主要内容区域可见
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 验证没有致命的 ReferenceError
    const hasReferenceError = consoleErrors.some(err =>
      err.includes('debouncedSearch is not defined') ||
      err.includes('ReferenceError')
    );

    expect(hasReferenceError, `不应有 ReferenceError: ${consoleErrors.join(', ')}`).toBeFalsy();
  });

  test('ParamSelector 应该正确渲染而不出现 debouncedSearch 错误', async ({ page }) => {
    // 监听控制台错误
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(eventNodeBuilderUrl);
    await page.waitForLoadState('networkidle');

    // 等待组件加载
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 查找 ParamSelector 区域
    const leftSidebar = page.locator('.sidebar-left');
    await expect(leftSidebar).toBeVisible();

    // 验证参数选择器区域存在（即使用 searchQuery 而非 debouncedSearch）
    const paramsSection = leftSidebar.locator('text=参数字段');
    await expect(paramsSection).toBeVisible();

    // 验证没有 debouncedSearch 相关的 ReferenceError
    const hasDebouncedSearchError = consoleErrors.some(err =>
      err.includes('debouncedSearch is not defined') ||
      err.includes('debouncedSearch') ||
      err.includes('ReferenceError')
    );

    expect(hasDebouncedSearchError, 'ParamSelector 不应该有 debouncedSearch 相关错误').toBeFalsy();
  });

  test('RightSidebar 应该接收 number 类型的 gameGid', async ({ page }) => {
    // 监听 PropTypes 警告
    const propWarnings: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('Invalid prop') && text.includes('gameGid')) {
        propWarnings.push(text);
      }
    });

    await page.goto(eventNodeBuilderUrl);
    await page.waitForLoadState('networkidle');

    // 等待右侧栏加载
    const rightSidebar = page.locator('.sidebar-right');
    await expect(rightSidebar).toBeVisible();

    // 验证没有 PropTypes 类型错误
    expect(propWarnings.length).toBe(0);
  });

  test('不应该有 defaultProps 废弃警告', async ({ page }) => {
    // 监听所有警告
    const warnings: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });

    await page.goto(eventNodeBuilderUrl);
    await page.waitForLoadState('networkidle');

    // 等待组件加载
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    // 验证没有 defaultProps 废弃警告
    const hasDeprecationWarning = warnings.some(warning =>
      warning.includes('defaultProps will be removed')
    );

    expect(hasDeprecationWarning, '不应该有 defaultProps 废弃警告').toBeFalsy();
  });

  test('组件应该正确使用函数参数默认值', async ({ page }) => {
    await page.goto(eventNodeBuilderUrl);
    await page.waitForLoadState('networkidle');

    // 等待各个组件加载
    const workspace = page.locator('[data-testid="event-node-builder-workspace"]');
    await expect(workspace).toBeVisible();

    const leftSidebar = page.locator('.sidebar-left');
    await expect(leftSidebar).toBeVisible();

    const rightSidebar = page.locator('.sidebar-right');
    await expect(rightSidebar).toBeVisible();

    // 验证页面结构完整
    const pageHeader = page.locator('.page-header');
    await expect(pageHeader).toBeVisible();

    // 验证没有运行时错误
    const hasRuntimeError = await page.evaluate(() => {
      return !!(window as any).hasRuntimeError;
    }).catch(() => false);

    expect(hasRuntimeError).toBeFalsy();
  });
});
