import { test, expect } from '@playwright/test';
import { navigateToPage, PAGE_PATHS } from '../helpers/url-helper';
import { setGameContext } from '../helpers/game-context';

/**
 * 对比测试：找出React加载的差异
 */
test.describe('加载对比测试', () => {
  test.afterEach(async ({ page }) => {
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

  test('测试1：不带任何参数访问根路径', async ({ page }) => {
    console.log('=== Test 1: Root path without params ===');
    await navigateToPage(page, PAGE_PATHS.HOME);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    const appRootHTML = await page.locator('#app-root').innerHTML();
    console.log('#app-root length:', appRootHTML.length);
    console.log('Has content:', appRootHTML.length > 100);
  });

  test('测试2：先设置游戏上下文，再访问', async ({ page }) => {
    console.log('=== Test 2: Set game context FIRST ===');
    await setGameContext(page, '10000147');

    // 等待一下确保localStorage设置完成
    await page.waitForTimeout(1000);

    await navigateToPage(page, PAGE_PATHS.HOME);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    const appRootHTML = await page.locator('#app-root').innerHTML();
    console.log('#app-root length:', appRootHTML.length);
    console.log('Has content:', appRootHTML.length > 100);
  });

  test('测试3：使用hash路由访问event-node-builder', async ({ page }) => {
    console.log('=== Test 3: Hash route to event-node-builder ===');

    // 先访问根路径，等待React加载
    await navigateToPage(page, PAGE_PATHS.HOME);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // 检查React是否加载
    const appRootBefore = await page.locator('#app-root').innerHTML();
    console.log('#app-root length BEFORE hash change:', appRootBefore.length);

    // 通过JavaScript改变hash
    await page.evaluate(() => {
      window.location.hash = '#/event-node-builder?node_id=7';
    });

    await page.waitForTimeout(5000);

    const appRootAfter = await page.locator('#app-root').innerHTML();
    console.log('#app-root length AFTER hash change:', appRootAfter.length);
  });

  test('测试4：完整流程 - 设置上下文后使用hash路由', async ({ page }) => {
    console.log('=== Test 4: Full flow - game context + hash ===');

    // 先访问根路径
    await navigateToPage(page, PAGE_PATHS.HOME);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 设置游戏上下文
    await setGameContext(page, '10000147');
    await page.waitForTimeout(1000);

    // 改变hash
    await page.evaluate(() => {
      window.location.hash = '#/event-node-builder?node_id=7';
    });

    await page.waitForTimeout(5000);

    const appRootHTML = await page.locator('#app-root').innerHTML();
    console.log('#app-root length:', appRootHTML.length);

    // 检查event-node-builder
    const eventBuilderCount = await page.locator('.event-node-builder').count();
    console.log('.event-node-builder count:', eventBuilderCount);

    // 截图
    await page.screenshot({ path: 'test-results/full-flow-test.png', fullPage: true });
  });

  test('测试5：检查JavaScript加载状态', async ({ page }) => {
    console.log('=== Test 5: Check JavaScript loading ===');

    await navigateToPage(page, PAGE_PATHS.HOME);

    // 等待所有资源加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 检查React是否可用
    const reactLoaded = await page.evaluate(() => {
      return typeof window.React !== 'undefined' ||
             typeof window.ReactDOM !== 'undefined' ||
             document.querySelector('[data-reactroot]') !== null;
    });

    console.log('React loaded:', reactLoaded);

    // 检查是否有script标签
    const scripts = await page.evaluate(() => {
      const scriptTags = Array.from(document.querySelectorAll('script'));
      return scriptTags
        .filter(s => s.src.includes('/frontend/dist/'))
        .map(s => ({
          src: s.src,
          loaded: s.onload !== null,
          error: s.onerror !== null
        }));
    });

    console.log('React scripts:', scripts);
  });
});
