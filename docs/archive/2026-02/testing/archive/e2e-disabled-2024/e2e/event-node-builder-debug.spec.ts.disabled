import { test, expect } from '@playwright/test';
import { navigateAndSetGameContext } from '../helpers/game-context';

/**
 * Event Node Builder 调试测试
 * 用于调试页面加载和元素可见性问题
 */
test.describe('Event Node Builder - 调试', () => {
  const TEST_CONFIG_ID = '7';
  const TEST_GAME_GID = '10000147';

  test.beforeEach(async ({ page }) => {
    await setGameContext(page, TEST_GAME_GID);
  });

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

  test('调试：查看页面实际加载的内容', async ({ page }) => {
    // 使用node_id参数访问
    const url = `http://127.0.0.1:5001/#/event-node-builder?node_id=${TEST_CONFIG_ID}`;
    console.log('Navigating to:', url);
    await page.goto(url);

    // 等待页面加载
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // 打印页面URL
    console.log('Current URL:', page.url());

    // 打印页面标题
    const title = await page.title();
    console.log('Page title:', title);

    // 打印页面的HTML结构（body部分）
    const bodyHTML = await page.locator('body').innerHTML();
    console.log('Body HTML length:', bodyHTML.length);

    // 检查是否有error或warning消息
    const errorLocator = page.locator('.error, .alert-danger');
    const errorCount = await errorLocator.count();
    if (errorCount > 0) {
      const errors = await errorLocator.allTextContents();
      console.log('Errors found:', errors);
    }

    // 检查关键元素是否存在
    const elementsToCheck = [
      '.event-node-builder',
      '.workspace',
      '.sidebar-right',
      '.field-canvas',
      '.hql-preview-container',
      '.where-builder',
      '.stats-grid'
    ];

    for (const selector of elementsToCheck) {
      const count = await page.locator(selector).count();
      console.log(`${selector}: ${count} element(s)`);
    }

    // 如果找到了sidebar-right，打印其内容
    const sidebarCount = await page.locator('.sidebar-right').count();
    if (sidebarCount > 0) {
      const sidebarHTML = await page.locator('.sidebar-right').first().innerHTML();
      console.log('Sidebar HTML (first 500 chars):', sidebarHTML.substring(0, 500));
    }

    // 截图
    await page.screenshot({ path: 'test-results/debug-screenshot.png', fullPage: true });
    console.log('Screenshot saved to test-results/debug-screenshot.png');
  });

  test('调试：检查API响应', async ({ page }) => {
    // 监听网络请求
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err));

    // 设置游戏上下文后访问
    await page.goto(`http://127.0.0.1:5001/#/event-node-builder?node_id=${TEST_CONFIG_ID}`);
    await page.waitForTimeout(3000);

    // 检查localStorage
    const localStorage = await page.evaluate(() => {
      return {
        selectedGameGid: localStorage.getItem('selectedGameGid'),
        selectedGameId: localStorage.getItem('selectedGameId'),
        selectedGameName: localStorage.getItem('selectedGameName')
      };
    });
    console.log('LocalStorage:', localStorage);

    // 检查React状态
    const reactState = await page.evaluate(() => {
      // 尝试获取React内部的state
      const rootElement = document.querySelector('#app-root');
      if (rootElement && '_reactRootContainer' in rootElement) {
        return 'React root found';
      }
      return 'React root not found';
    });
    console.log('React state:', reactState);
  });

  test('调试：测试数据库中的配置ID', async ({ page }) => {
    // 直接调用API来验证配置是否存在
    const apiUrl = `http://127.0.0.1:5001/#/event-node-builder/api/load/${TEST_CONFIG_ID}`;

    try {
      const response = await page.context().request.get(apiUrl);
      console.log('API Response status:', response.status());
      const data = await response.json();
      console.log('API Response data:', JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('API request failed:', error);
    }
  });
});
