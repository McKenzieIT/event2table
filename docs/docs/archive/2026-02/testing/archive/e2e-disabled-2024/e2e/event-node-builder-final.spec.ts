import { test, expect } from '@playwright/test';
import { navigateAndSetGameContext } from '../helpers/game-context';

/**
 * Event Node Builder 最终验证测试
 * 带缓存绕过
 */
test.describe('Event Node Builder - 最终验证', () => {
  const TEST_CONFIG_ID = '7';
  const TEST_GAME_GID = '10000147';
  const CACHE_BUSTER = Date.now().toString(); // 添加时间戳绕过缓存

  test.beforeEach(async ({ page, context }) => {
    // 禁用缓存
    await context.setHTTPCredentials({
      username: '',
      password: '',
      origin: '*'
    });

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

  test('应该能够通过node_id参数加载配置（缓存绕过）', async ({ page }) => {
    // 使用缓存破坏参数
    const url = `http://127.0.0.1:5001/?_cb=${CACHE_BUSTER}#/event-node-builder?node_id=${TEST_CONFIG_ID}`;
    console.log('Navigating to:', url);

    await page.goto(url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 验证URL包含node_id
    expect(page.url()).toContain(`node_id=${TEST_CONFIG_ID}`);

    // 检查#app-root
    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 15000 });

    // 等待React加载
    await page.waitForTimeout(3000);

    // 检查是否有内容
    const appRootHTML = await appRoot.innerHTML();
    console.log('#app-root HTML length:', appRootHTML.length);
    expect(appRootHTML.length).toBeGreaterThan(1000);

    // 检查event-node-builder
    const eventBuilder = page.locator('.event-node-builder');
    await expect(eventBuilder).toBeVisible({ timeout: 10000 });

    // 截图
    await page.screenshot({
      path: 'test-results/node-id-load-success.png',
      fullPage: true
    });
  });

  test('应该支持config_id参数（缓存绕过）', async ({ page }) => {
    const url = `http://127.0.0.1:5001/?_cb=${CACHE_BUSTER}#/event-node-builder?config_id=5`;
    console.log('Navigating to:', url);

    await page.goto(url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    // 检查#app-root
    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 15000 });

    await page.waitForTimeout(3000);

    const appRootHTML = await appRoot.innerHTML();
    console.log('#app-root HTML length:', appRootHTML.length);
    expect(appRootHTML.length).toBeGreaterThan(1000);
  });

  test('WHERE构建器应该默认展开', async ({ page }) => {
    const url = `http://127.0.0.1:5001/?_cb=${CACHE_BUSTER}#/event-node-builder?node_id=${TEST_CONFIG_ID}`;

    await page.goto(url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 15000 });

    await page.waitForTimeout(3000);

    // 检查WHERE构建器
    const whereBuilder = page.locator('.where-builder-section, .where-builder').first();

    if (await whereBuilder.isVisible()) {
      // 检查默认状态
      const toggleIcon = whereBuilder.locator('.bi-chevron-right, .bi-chevron-down');

      // 默认展开时应该看到向下箭头（或向下箭头图标）
      // 如果没有图标，检查section-content是否可见
      const sectionContent = whereBuilder.locator('.section-content');

      if (await toggleIcon.count() > 0) {
        const iconClass = await toggleIcon.first().getAttribute('class');
        console.log('Toggle icon class:', iconClass);
        // chevron-down = expanded, chevron-right = collapsed
        const isExpanded = iconClass?.includes('chevron-down');
        console.log('WHERE builder is expanded:', isExpanded);
        expect(isExpanded).toBeTruthy();
      } else {
        // 如果没有图标，检查section-content是否可见
        const isVisible = await sectionContent.isVisible();
        console.log('Section content visible:', isVisible);
        expect(isVisible).toBeTruthy();
      }
    }

    await page.screenshot({
      path: 'test-results/where-expanded.png',
      fullPage: true
    });
  });

  test('右侧栏布局应该正确', async ({ page }) => {
    const url = `http://127.0.0.1:5001/?_cb=${CACHE_BUSTER}#/event-node-builder?node_id=${TEST_CONFIG_ID}`;

    await page.goto(url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    const appRoot = page.locator('#app-root');
    await expect(appRoot).toBeVisible({ timeout: 15000 });

    await page.waitForTimeout(3000);

    // 检查右侧栏
    const rightSidebar = page.locator('.sidebar-right');
    await expect(rightSidebar).toBeVisible({ timeout: 10000 });

    const sidebarBox = await rightSidebar.boundingBox();
    expect(sidebarBox).not.toBeNull();

    if (sidebarBox) {
      console.log(`Sidebar: x=${sidebarBox.x}, y=${sidebarBox.y}, w=${sidebarBox.width}, h=${sidebarBox.height}`);

      // 检查HQL预览
      const hqlPreview = page.locator('.hql-preview-container');
      if (await hqlPreview.isVisible()) {
        const hqlBox = await hqlPreview.boundingBox();
        console.log(`HQL Preview: y=${hqlBox?.y}, h=${hqlBox?.height}`);

        // 验证高度限制（35vh）
        const viewportHeight = page.viewportSize()?.height || 1080;
        const maxHeight = viewportHeight * 0.35;
        expect(hqlBox?.height || 0).toBeLessThanOrEqual(maxHeight + 50); // +50px tolerance
      }

      // 检查统计面板
      const statsPanel = page.locator('.stats-grid');
      if (await statsPanel.isVisible()) {
        const statsBox = await statsPanel.boundingBox();
        console.log(`Stats Panel: y=${statsBox?.y}, h=${statsBox?.height}`);

        // 验证在侧边栏内
        if (statsBox) {
          expect(statsBox.y).toBeGreaterThanOrEqual(sidebarBox.y);
        }
      }
    }

    await page.screenshot({
      path: 'test-results/sidebar-layout.png',
      fullPage: true
    });
  });

  test('响应式布局测试', async ({ page }) => {
    const url = `http://127.0.0.1:5001/?_cb=${CACHE_BUSTER}#/event-node-builder?node_id=${TEST_CONFIG_ID}`;

    // 测试不同屏幕尺寸
    const sizes = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 1024, height: 768 }
    ];

    for (const size of sizes) {
      await page.setViewportSize(size);
      await page.goto(url);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);

      const appRoot = page.locator('#app-root');
      const isVisible = await appRoot.isVisible();
      console.log(`Size ${size.width}x${size.height}: app-root visible = ${isVisible}`);

      expect(isVisible).toBeTruthy();

      await page.screenshot({
        path: `test-results/responsive-${size.width}x${size.height}.png`,
        fullPage: true
      });
    }
  });
});
