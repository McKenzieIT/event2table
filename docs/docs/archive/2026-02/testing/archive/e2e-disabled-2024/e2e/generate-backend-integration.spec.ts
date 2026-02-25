import { test, expect } from '@playwright/test';

/**
 * Generate Backend Integration Test
 *
 * 验证Generate组件是否连接到真实后端HQL生成API
 * 而不是使用setTimeout模拟
 */

test.describe('Generate Backend Integration', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏上下文
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

  test('should NOT use setTimeout for HQL generation', async ({ page }) => {
    await page.goto('/#/generate');
    await page.waitForSelector('#app-root', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // 检查页面内容
    const pageText = await page.locator('body').textContent();

    // 如果使用setTimeout，会显示"登录事件"、"购买事件"等硬编码选项
    const hasHardcodedEvents =
      pageText?.includes('登录事件') ||
      pageText?.includes('购买事件');

    if (hasHardcodedEvents) {
      // 这是问题所在 - 使用硬编码而非真实API
      expect(hasHardcodedEvents, 'Should NOT have hardcoded event list').toBe(false);
    }

    // 检查是否有真实的API调用
    const apiRequests: string[] = [];
    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/hql') || url.includes('/hql')) {
        apiRequests.push(url);
      }
    });

    // 尝试点击生成按钮（如果存在）
    const generateButton = await page.locator('button:has-text("生成HQL"), button:has-text("生成")').count();

    if (generateButton > 0) {
      // 选择一个事件（如果存在）
      const eventItem = await page.locator('.event-item').count();
      if (eventItem > 0) {
        await page.locator('.event-item').first().click();
      }

      // 点击生成按钮
      await page.locator('button:has-text("生成HQL"), button:has-text("生成")').first().click();

      // 等待可能的API调用
      await page.waitForTimeout(3000);

      // 验证是否有真实API调用
      if (apiRequests.length === 0) {
        // 没有API调用 = 使用setTimeout模拟
        expect(apiRequests.length, 'Should call real HQL generation API').toBeGreaterThan(0);
      }
    }
  });

  test('should have real event list from backend', async ({ page }) => {
    await page.goto('/#/generate');
    await page.waitForSelector('#app-root', { timeout: 10000 });

    // 监听API请求
    const apiRequests: string[] = [];
    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/events') || url.includes('/api/hql')) {
        apiRequests.push(url);
      }
    });

    await page.waitForTimeout(2000);

    // 检查是否有调用/events API获取事件列表
    const hasEventsApiCall = apiRequests.some(url => url.includes('/api/events'));

    if (!hasEventsApiCall) {
      // 没有调用API = 使用硬编码事件列表
      expect(hasEventsApiCall, 'Should fetch event list from backend API').toBe(true);
    }
  });
});
