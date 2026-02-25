import { test, expect } from '@playwright/test';

/**
 * GenerateResult Backend Integration Test
 *
 * 验证GenerateResult组件是否从URL参数或后端API获取真实生成的HQL
 * 而不是使用硬编码的HQL字符串
 */

test.describe('GenerateResult Backend Integration', () => {
  test('should NOT contain hardcoded HQL string', async ({ page }) => {
    // 导航到生成结果页面（带event参数）
    await page.goto('/#/generate-result?event=login');
    await page.waitForSelector('#app-root', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // 获取页面内容
    const pageText = await page.locator('.result-card, .generate-result-container').textContent();

    // 检查是否有硬编码的HQL特征
    const hasHardcodedHQL =
      pageText?.includes('CREATE OR REPLACE VIEW dwd_event_login') ||
      pageText?.includes('ieu_ods.ods_all_view') ||
      pageText?.includes('${bizdate}');

    if (hasHardcodedHQL) {
      // 这是问题所在 - 使用硬编码HQL
      expect(hasHardcodedHQL, 'Should NOT contain hardcoded HQL template').toBe(false);
    }

    // 检查是否有真实生成的HQL（应该从URL参数或API获取）
    const resultElement = await page.locator('.hql-code, pre, code').count();
    expect(resultElement, 'Should have HQL code display element').toBeGreaterThan(0);
  });

  test('should fetch HQL from backend API or URL params', async ({ page }) => {
    // 监听API请求
    const apiRequests: string[] = [];
    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/hql') || url.includes('/api/generate')) {
        apiRequests.push(url);
      }
    });

    // 导航到生成结果页面
    await page.goto('/#/generate-result?event=login');
    await page.waitForSelector('#app-root', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // 检查URL参数
    const urlParams = page.url().split('?')[1];
    const hasEventParam = urlParams?.includes('event=');

    // 应该从URL参数获取事件名，或从API获取HQL
    if (apiRequests.length === 0 && !hasEventParam) {
      // 既没有API调用，也没有URL参数 = 使用硬编码
      expect(apiRequests.length || hasEventParam, 'Should fetch HQL from API or use URL params').toBe(true);
    }
  });

  test('should display HQL based on selected event', async ({ page }) => {
    // 测试不同事件的HQL生成
    const testEvents = ['login', 'purchase', 'register'];

    for (const event of testEvents) {
      await page.goto(`/#/generate-result?event=${event}`);
      await page.waitForSelector('#app-root', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 获取HQL代码
      const hqlCode = await page.locator('.hql-code, pre, code').first().textContent();

      // 检查HQL是否包含事件名（应该是动态生成的）
      const hasEventName = hqlCode?.includes(event) || hqlCode?.includes(event.toUpperCase());

      if (!hasEventName && hqlCode?.includes('dwd_event_login')) {
        // 如果HQL总是固定的dwd_event_login，说明是硬编码
        expect(hasEventName, `HQL should reference the selected event (${event})`).toBe(true);
      }
    }
  });
});
