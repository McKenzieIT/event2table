import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';

test.describe('Debug: Event Nodes Page Load', () => {
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
      localStorage.removeItem('selectedGameData');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('Debug: Check what renders on event-nodes page', async ({ page }) => {
    // 先设置localStorage模拟游戏选择（在React应用加载之前）
    await navigateToPage(page, PAGE_PATHS.HOME);

    // 设置游戏上下文到localStorage
    await page.evaluate(() => {
      const mockGameData = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'ieu_ods',
        dwd_prefix: 'ieu_dwd'
      };
      localStorage.setItem('selectedGameGid', '10000147');
      localStorage.setItem('selectedGameData', JSON.stringify(mockGameData));
    });

    console.log('已设置游戏上下文到localStorage');

    // 重新加载页面以触发GameContext重新读取localStorage
    await page.reload();
    await page.waitForSelector('#app-root', { state: 'visible', timeout: 10000 });

    // 现在访问事件节点页面
    await navigateToPage(page, PAGE_PATHS.EVENT_NODES);

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Take a screenshot
    await page.screenshot({ path: 'test-results/debug-page-load-with-game.png', fullPage: true });

    // Check for any React error boundaries
    const errorBoundary = page.locator('text=/error|error|Error').first();
    const errorCount = await errorBoundary.count();
    console.log(`Error elements found: ${errorCount}`);

    // Check for app-root
    const appRoot = page.locator('#app-root');
    const appRootExists = await appRoot.count();
    console.log(`#app-root elements found: ${appRootExists}`);

    // Check for any text content in the body
    const bodyText = await page.locator('body').textContent();
    console.log(`Body text length: ${bodyText?.length || 0}`);
    console.log(`Body text preview: ${bodyText?.substring(0, 200) || 'empty'}`);

    // Check for game selection prompt
    const gamePrompt = page.locator('text=请先选择游戏');
    const gamePromptCount = await gamePrompt.count();
    console.log(`Game selection prompt found: ${gamePromptCount > 0}`);

    // Check for event nodes page elements
    const pageTitle = page.locator('h2:has-text("事件节点管理")');
    const pageTitleCount = await pageTitle.count();
    console.log(`Event nodes page title found: ${pageTitleCount > 0}`);

    // Check for search input
    const searchInput = page.locator('input[placeholder="搜索节点名称、别名..."]');
    const searchInputCount = await searchInput.count();
    console.log(`Search input found: ${searchInputCount > 0}`);

    // Check for any glass-card elements
    const glassCards = page.locator('.glass-card');
    const glassCardCount = await glassCards.count();
    console.log(`Glass cards found: ${glassCardCount}`);

    // Check for any h2 elements
    const h2Elements = page.locator('h2');
    const h2Count = await h2Elements.count();
    console.log(`H2 elements found: ${h2Count}`);

    // Check page title
    const title = await page.title();
    console.log(`Page title: ${title}`);

    // Get page HTML
    const html = await page.content();
    console.log(`HTML length: ${html.length}`);
  });
});
