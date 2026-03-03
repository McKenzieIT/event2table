/**
 * TDD 测试：事件节点构建器 - 参数字段显示
 *
 * Bug: 选择事件后，参数字段列表显示"没有找到参数"
 * Expected: 选择事件后，应显示该事件的参数列表
 */

import { test, expect } from '@playwright/test';

test.describe('ParamSelector - 参数字段选择器 Bug', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏数据
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      window.gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });

    // 导航到事件节点构建器页面
    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('RED: 选择事件后应显示参数列表', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('.event-node-builder')).toBeVisible({ timeout: 10000 });

    // 等待事件选择器加载
    const eventSelector = page.locator('.event-selector .dropdown-list').first();
    await expect(eventSelector).toBeVisible({ timeout: 5000 });

    // 获取第一个事件的名称
    const firstEvent = eventSelector.locator('.dropdown-item').first();
    const eventName = await firstEvent.textContent();

    console.log(`[DEBUG] 选择事件: ${eventName}`);

    // 点击选择第一个事件
    await firstEvent.click();

    // 监听控制台日志
    page.on('console', msg => {
      if (msg.text().includes('[ParamSelector]') || msg.text().includes('[DEBUG]')) {
        console.log('[Browser Console]', msg.text());
      }
    });

    // 等待参数选择器加载（参数字段是异步获取的）
    await page.waitForTimeout(3000);

    // 检查参数选择器区域
    const paramSelector = page.locator('.sidebar-section').filter({
      hasText: '参数字段'
    });

    await expect(paramSelector).toBeVisible();

    // 等待参数加载完成（检查是否还显示"加载中..."）
    await page.waitForTimeout(2000);

    // 检查参数列表的内容
    const paramList = paramSelector.locator('.dropdown-list');

    // 关键断言：应该显示参数，而不是"没有找到参数"
    const placeholder = paramList.locator('.dropdown-placeholder');
    const hasPlaceholder = await placeholder.count();

    if (hasPlaceholder > 0) {
      const placeholderText = await placeholder.textContent();
      console.log(`[BUG CONFIRMED] 参数显示: "${placeholderText}"`);

      // 这是一个失败的测试 - 应该显示参数列表，而不是"没有找到参数"
      expect(placeholderText).not.toContain('没有找到参数');
    } else {
      // 如果没有占位符，检查是否有实际的参数项
      const paramItems = paramList.locator('.dropdown-item');
      const paramCount = await paramItems.count();

      console.log(`[SUCCESS] 找到 ${paramCount} 个参数`);

      // 至少应该有一些参数
      expect(paramCount).toBeGreaterThan(0);

      // 记录前几个参数的名称
      for (let i = 0; i < Math.min(3, paramCount); i++) {
        const paramName = await paramItems.nth(i).textContent();
        console.log(`  参数 ${i + 1}: ${paramName}`);
      }
    }
  });

  test('验证 API 返回参数数据', async ({ page }) => {
    // 直接调用 API 验证后端是否返回参数
    const response = await page.request.get('/event_node_builder/api/params?event_id=55');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log('[DEBUG] API Response:', JSON.stringify(data, null, 2));

    // 验证 API 返回格式
    expect(data).toHaveProperty('success');
    expect(data).toHaveProperty('data');

    if (data.success) {
      const params = data.data.params || data.data || [];
      console.log(`[DEBUG] API 返回 ${params.length} 个参数`);

      // 应该有参数数据
      expect(params.length).toBeGreaterThan(0);

      // 验证参数结构
      const firstParam = params[0];
      expect(firstParam).toHaveProperty('param_name');
      expect(firstParam).toHaveProperty('id');
    } else {
      console.log('[BUG] API 返回失败:', data);
      expect(data.success).toBe(true);
    }
  });
});
