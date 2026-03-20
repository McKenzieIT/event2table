import { test, expect } from '@playwright/test';

/**
 * Event Node Builder API 路由修复验证测试
 *
 * 验证以下修复:
 * 1. /event_node_builder/api/preview-hql 返回 200（非 404）
 * 2. /event_node_builder/api/params 返回有效 JSON（非 HTML）
 * 3. PropTypes 警告：selectedEvent.name 和 event.name 匹配后端返回的 event_name/event_name_cn
 *
 * TDD 流程:
 * - RED: 这个测试应该先失败（API 路由不存在）
 * - GREEN: 实现后端路由 + 修复 PropTypes
 * - REFACTOR: 清理代码
 */

test.describe('EventNodeBuilder - API Routes (TDD)', () => {
  const baseUrl = 'http://localhost:5173';
  const eventNodeBuilderUrl = `${baseUrl}/#/event-node-builder?game_gid=10000147`;

  test.beforeEach(async ({ page }) => {
    // 清除缓存数据
    await page.goto(baseUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.evaluate(() => {
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.clear();
    });
  });

  test('GREEN Phase: /event_node_builder/api/preview-hql 应该返回 200', async ({ page }) => {
    // 导航到 EventNodeBuilder 页面
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // 直接调用 API
    const response = await page.request.post('/event_node_builder/api/preview-hql', {
      data: {
        game_gid: 10000147,
        event_id: 1,
        fields: [],
        where_conditions: []
      }
    });

    // 在 GREEN 阶段，这个断言应该通过（路由已实现）
    expect(response.status()).toBe(200);

    // 验证返回的是 JSON
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');

    // 验证响应格式
    const json = await response.json();
    expect(json).toHaveProperty('success', true);
  });

  test('GREEN Phase: /event_node_builder/api/params 应该返回 JSON', async ({ page }) => {
    // 导航到 EventNodeBuilder 页面
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });
    await page.waitForTimeout(2000);

    // 直接调用 API
    const response = await page.request.get('/event_node_builder/api/params?event_id=1');

    // 在 GREEN 阶段，这个断言应该通过
    expect(response.status()).toBe(200);

    // 验证返回的是 JSON（非 HTML）
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');

    // 验证响应格式
    const json = await response.json();
    expect(json).toHaveProperty('success', true);
  });

  test('GREEN Phase: PropTypes 不应该警告 event.name undefined', async ({ page }) => {
    // 监听控制台警告
    const propWarnings: string[] = [];

    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('Invalid prop') && text.includes('name') && text.includes('required')) {
        propWarnings.push(text);
      }
    });

    // 导航到 EventNodeBuilder 页面
    await page.goto(eventNodeBuilderUrl, { timeout: 60000, waitUntil: 'commit' });

    // 等待页面加载
    await page.waitForTimeout(3000);

    // 在 GREEN 阶段，这个断言应该通过（PropTypes 已修复为 event_name/event_name_cn）
    expect(propWarnings.length, 'PropTypes 不应该有警告').toBe(0);
  });
});
