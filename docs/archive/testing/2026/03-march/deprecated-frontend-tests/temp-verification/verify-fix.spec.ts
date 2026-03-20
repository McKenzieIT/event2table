import { test, expect } from '@playwright/test';

/**
 * E2E测试 - 验证require错误修复
 *
 * 测试目标:
 * 1. 页面成功加载，不再显示"LOADING EVENT2TABLE..."
 * 2. React应用成功挂载
 * 3. 游戏列表页面正常显示
 * 4. "管理游戏"按钮存在且可点击
 */

test.describe('React应用启动验证', () => {
  test('页面成功加载且React挂载', async ({ page }) => {
    // 导航到首页
    await page.goto('http://localhost:5173');

    // 等待页面加载
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // 检查：不应该再显示"LOADING EVENT2TABLE..."
    const loadingText = await page.textContent('body');
    expect(loadingText).not.toContain('LOADING EVENT2TABLE...');

    // 检查：#app-root应该有内容
    const appRoot = page.locator('#app-root');
    await expect(appRoot).toHaveCount(1);

    // 检查：initial-loader应该被移除
    const loader = page.locator('#initial-loader');
    await expect(loader).toHaveCount(0);

    console.log('✅ React应用成功挂载');
  });

  test('游戏列表页面正常显示', async ({ page }) => {
    // 导航到游戏页面
    await page.goto('http://localhost:5173/#/games');
    await page.waitForTimeout(3000);

    // 等待React挂载
    await page.waitForSelector('#app-root > *', { timeout: 10000 });

    // 检查：页面标题
    const title = await page.title();
    expect(title).toContain('Event2Table');

    // 检查：不应该显示loading
    const bodyText = await page.textContent('body');
    expect(bodyText).not.toContain('LOADING');

    console.log('✅ 游戏列表页面正常显示');
  });

  test('管理游戏按钮存在且可见', async ({ page }) => {
    await page.goto('http://localhost:5173/#/games');
    await page.waitForTimeout(3000);

    // 等待React挂载
    await page.waitForSelector('#app-root > *', { timeout: 10000 });

    // 查找"管理游戏"按钮
    const manageButton = page.locator('button').filter({ hasText: '管理游戏' });

    // 检查：按钮应该存在
    await expect(manageButton).toHaveCount(1);

    // 检查：按钮应该可见
    await expect(manageButton).toBeVisible();

    console.log('✅ 管理游戏按钮存在且可见');
  });

  test('控制台无require错误', async ({ page }) => {
    const errors: string[] = [];

    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('http://localhost:5173/#/games');
    await page.waitForTimeout(3000);

    // 检查：不应该有"require is not defined"错误
    const requireErrors = errors.filter(err => err.includes('require is not defined'));
    expect(requireErrors.length).toBe(0);

    console.log('✅ 控制台无require错误');
  });
});
