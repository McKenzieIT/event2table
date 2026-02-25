import { test, expect } from '@playwright/test';

/**
 * ImportEvents Backend Integration Test
 *
 * 验证ImportEvents组件是否连接到真实后端API
 * 而不是使用模拟数据
 */

test.describe('ImportEvents Backend Integration', () => {
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

  test('should call real backend API when previewing Excel file', async ({ page }) => {
    // 监听所有网络请求
    const apiRequests: string[] = [];
    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/api/preview-excel') || url.includes('/events/import')) {
        apiRequests.push(url);
      }
    });

    // 导航到导入页面
    await page.goto('/#/import-events');
    await page.waitForSelector('#app-root', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // 检查页面是否加载
    const importPage = await page.locator('.import-events-container').count();
    expect(importPage, 'Import events page should exist').toBeGreaterThan(0);

    // 尝试上传文件（如果存在文件输入）
    const fileInput = await page.locator('input[type="file"]').count();
    if (fileInput > 0) {
      // 创建测试Excel文件
      const testFile = Buffer.from(
        'PK\x03\x04\x14\x00\x00\x00\x08\x00' // 简化的zip文件头（Excel格式）
      );

      // 尝试上传
      await page.locator('input[type="file"]').setInputFiles({
        name: 'test.xlsx',
        mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        buffer: testFile,
      });

      // 等待可能的API调用
      await page.waitForTimeout(3000);
    }

    // 验证是否调用了真实API
    // 如果使用模拟数据，不会有任何API请求
    console.log('API Requests made:', apiRequests);

    // CRITICAL: 如果使用模拟数据，测试会失败
    // 这是期望的行为 - 测试应该失败来证明问题存在
    const hasMockData = await page.locator('text=/mock|模拟|placeholder/i').count();

    if (apiRequests.length === 0) {
      // 没有API调用 = 使用模拟数据 = 测试失败（这是RED phase的期望）
      expect(true, 'Component uses mock data instead of real API - THIS IS EXPECTED TO FAIL').toBe(false);
    }
  });

  test('should have real backend integration indicators', async ({ page }) => {
    await page.goto('/#/import-events');
    await page.waitForSelector('#app-root', { timeout: 10000 });

    // 检查组件是否有真实的表单元素
    const hasFileUpload = await page.locator('input[type="file"]').count() > 0;
    const hasPreviewButton = await page.locator('button:has-text("预览")').count() > 0;
    const hasImportButton = await page.locator('button:has-text("导入")').count() > 0;

    // 至少应该有基本的UI元素
    expect(hasFileUpload || hasPreviewButton || hasImportButton, 'Should have some UI elements').toBe(true);
  });

  test('should NOT contain hardcoded mock data', async ({ page }) => {
    await page.goto('/#/import-events');
    await page.waitForSelector('#app-root', { timeout: 10000 });

    // 获取页面文本内容
    const pageText = await page.locator('body').textContent();

    // 检查是否有明显的模拟数据标记
    const hasMockIndicators =
      pageText?.includes('mockParameters') ||
      pageText?.includes('accountId') && pageText?.includes('roleId') && pageText?.includes('1507') ||
      pageText?.includes('模拟数据') ||
      pageText?.includes('Mock');

    if (hasMockIndicators) {
      // 如果发现模拟数据，这是问题所在
      expect(hasMockIndicators, 'Component should NOT use mock data').toBe(false);
    }
  });
});
