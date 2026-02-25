import { test, expect } from '@playwright/test';

/**
 * React Error #321 Validation Test
 *
 * 验证选择性直接导入策略是否解决了 React Error #321
 * 测试所有高频页面（直接导入）是否无错误
 */

test.describe('React Error #321 Validation', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏数据（使用生产路径）
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      localStorage.setItem('selectedGameId', '16');
      localStorage.setItem('selectedGameName', '游戏 10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理
    await page.evaluate(() => {
      sessionStorage.clear();
    });
  });

  /**
   * 高频页面测试（直接导入）
   * 这些页面使用 React Query hooks，不能使用 lazy loading
   */
  test.describe('High-Frequency Pages (Direct Import)', () => {
    test('Dashboard should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000); // 等待 React 完全渲染

      const errors = await reactErrors;

      console.log('\n=== Dashboard Page ===');
      console.log('React Errors:', errors);

      // 检查是否有 React Error #321
      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      // 检查是否有 React Error #310
      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      // 检查是否有 removeChild 错误
      const hasRemoveChildError = errors.some(err =>
        err.includes('removeChild') ||
        err.includes('not a child of this node')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);
      expect(hasRemoveChildError, 'Should not have removeChild error').toBe(false);

      // 验证页面内容已渲染（只检查容器存在，不检查具体元素）
      const appRoot = await page.locator('#app-root').count();
      expect(appRoot, 'App root should exist').toBeGreaterThan(0);

      console.log('✅ Dashboard: No React errors');
    });

    test('Canvas should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/canvas?game_gid=10000147');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Canvas Page ===');
      console.log('React Errors:', errors);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);

      console.log('✅ Canvas: No React errors');
    });

    test('Event Node Builder should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/event-node-builder?game_gid=10000147');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Event Node Builder Page ===');
      console.log('React Errors:', errors);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);

      // 验证页面容器存在
      const appRoot = await page.locator('#app-root').count();
      expect(appRoot, 'App root should exist').toBeGreaterThan(0);

      console.log('✅ Event Node Builder: No React errors');
    });

    test('Event Nodes should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/event-nodes?game_gid=10000147');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Event Nodes Page ===');
      console.log('React Errors:', errors);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);

      console.log('✅ Event Nodes: No React errors');
    });

    test('Games List should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/games');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Games List Page ===');
      console.log('React Errors:', errors);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);

      console.log('✅ Games List: No React errors');
    });

    test('Events List should load without React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      await page.goto('/#/events?game_gid=10000147');
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Events List Page ===');
      console.log('React Errors:', errors);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasError310 = errors.some(err =>
        err.includes('React error #310') ||
        err.includes('invariant=310')
      );

      expect(hasError321, 'Should not have React Error #321').toBe(false);
      expect(hasError310, 'Should not have React Error #310').toBe(false);

      console.log('✅ Events List: No React errors');
    });
  });

  /**
   * 路由切换测试
   * 验证在页面之间快速切换时不会触发 React Error
   */
  test.describe('Route Navigation Tests', () => {
    test('Rapid navigation should not trigger React errors', async ({ page }) => {
      const reactErrors = await captureReactErrors(page);

      // 快速导航多个页面（使用生产路径）
      const routes = [
        '/#/',
        '/#/games',
        '/#/events?game_gid=10000147',
        '/#/canvas?game_gid=10000147',
        '/#/event-node-builder?game_gid=10000147',
        '/#/event-nodes?game_gid=10000147',
      ];

      for (const route of routes) {
        console.log(`\nNavigating to: ${route}`);
        await page.goto(route);
        await page.waitForSelector('#app-root', { timeout: 10000 });
        await page.waitForTimeout(1000); // 短暂等待
      }

      // 最后等待更长时间，确保所有异步操作完成
      await page.waitForTimeout(3000);

      const errors = await reactErrors;

      console.log('\n=== Rapid Navigation Test ===');
      console.log('Total Errors:', errors.length);

      const hasError321 = errors.some(err =>
        err.includes('React error #321') ||
        err.includes('invariant=321')
      );

      const hasRemoveChildError = errors.some(err =>
        err.includes('removeChild')
      );

      expect(hasError321, 'Should not have React Error #321 after rapid navigation').toBe(false);
      expect(hasRemoveChildError, 'Should not have removeChild error after rapid navigation').toBe(false);

      console.log('✅ Rapid Navigation: No React errors');
    });
  });
});

/**
 * 辅助函数：捕获 React 错误
 */
async function captureReactErrors(page: any): Promise<string[]> {
  const errors: string[] = [];

  // 监听 console 错误
  page.on('console', (msg: any) => {
    const text = msg.text();
    if (msg.type() === 'error') {
      errors.push(text);
    }
  });

  // 监听页面错误
  page.on('pageerror', (error: Error) => {
    errors.push(error.toString());
  });

  return errors;
}
