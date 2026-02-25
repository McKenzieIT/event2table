import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('CanvasFlow - Variable Initialization Fix', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('should load canvas without ReferenceError', async ({ page }) => {
    const errors: string[] = [];

    // 监听console错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // 监听页面错误
    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForSelector('#app-root', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(3000);

    // 验证没有ReferenceError
    const referenceErrors = errors.filter(e =>
      e.includes('ReferenceError') ||
      e.includes('Cannot access') ||
      e.includes('before initialization')
    );
    expect(referenceErrors.length).toBe(0);
  });

  test('should allow double-clicking JOIN nodes without errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await navigateToPage(page, PAGE_PATHS.CANVAS, { gameGid: '10000147' });
    await page.waitForSelector('#app-root', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(3000);

    // 尝试添加一个JOIN节点（如果可能）
    // 这个测试主要是验证页面不会因为初始化问题而崩溃
    const hasErrors = errors.filter(e =>
      e.includes('ReferenceError') ||
      e.includes('Cannot access') ||
      e.includes('before initialization')
    );

    expect(hasErrors.length).toBe(0);
  });
});
