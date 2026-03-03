/**
 * 事件数据验证测试
 *
 * 演示如何使用数据验证替代元素验证
 * 聚焦于验证API返回的数据正确性，而非UI元素存在性
 */

import { test, expect } from '@playwright/test';
import {
  getValidatedData,
  waitForDataLoad,
  fetchAndValidate,
  guards,
  validateRequiredFields
} from '../helpers/dataValidation';
import { navigateAndSetGameContext } from '../helpers/game-context';

test.describe('Events - Data Validation', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏上下文
    await navigateAndSetGameContext(page, '/events', '10000147');
  });

  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('eventsFilters');
      localStorage.removeItem('eventsSearchQuery');
    });
  });

  test('应该加载有效的事件数据', async ({ page }) => {
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 方法1：从window对象获取并验证数据
    const dataLoaded = await waitForDataLoad(page, 'eventsData', 10000);

    if (!dataLoaded) {
      // 如果window.eventsData不存在，尝试直接调用API
      const events = await fetchAndValidate(
        page,
        '/api/events?game_gid=10000147',
        { method: 'GET' }
      );

      // 验证数据结构
      expect(Array.isArray(events)).toBe(true);
      expect(events.length).toBeGreaterThan(0);

      // 验证第一个事件的数据结构
      const firstEvent = events[0];
      expect(validateRequiredFields(firstEvent, ['id', 'event_name', 'display_name', 'game_gid'])).toEqual({
        valid: true,
        missing: []
      });

      // 验证字段类型
      expect(typeof firstEvent.id === 'number').toBe(true);
      expect(typeof firstEvent.event_name === 'string').toBe(true);
      expect(typeof firstEvent.display_name === 'string').toBe(true);
      expect(typeof firstEvent.game_gid === 'number').toBe(true);
    } else {
      // 使用类型守卫验证数据
      const events = await getValidatedData(
        page,
        'eventsData',
        guards.isEventArray
      );

      // 验证数据数组不为空
      expect(events.length).toBeGreaterThan(0);

      // 验证第一个事件的数据结构
      expect(events[0].id).toBeTypeOf('number');
      expect(events[0].event_name).toBeTypeOf('string');
      expect(events[0].display_name).toBeTypeOf('string');
      expect(events[0].game_gid).toBeTypeOf('number');
    }
  });

  test('应该验证API响应结构', async ({ page }) => {
    // 直接调用API并验证响应结构
    const response = await page.evaluate(async () => {
      try {
        const res = await fetch('/api/events?game_gid=10000147');
        const data = await res.json();
        return { success: true, data, status: res.status };
      } catch (error) {
        return { success: false, error: String(error) };
      }
    });

    // 验证响应成功
    expect(response.success).toBe(true);
    expect(response.status).toBe(200);

    // 验证响应包含必要字段
    expect(response.data).toHaveProperty('data');
    expect(response.data).toHaveProperty('success');
    expect(response.data.success).toBe(true);

    // 验证data.data是数组
    expect(Array.isArray(response.data.data)).toBe(true);

    // 如果有数据，验证第一个元素的结构
    if (response.data.data.length > 0) {
      const firstEvent = response.data.data[0];
      expect(firstEvent).toHaveProperty('id');
      expect(firstEvent).toHaveProperty('event_name');
      expect(firstEvent).toHaveProperty('display_name');
      expect(typeof firstEvent.id === 'number').toBe(true);
      expect(typeof firstEvent.event_name === 'string').toBe(true);
    }
  });

  test('应该验证事件创建API', async ({ page }) => {
    // 创建测试事件
    const testEvent = {
      event_name: `test_event_${Date.now()}`,
      display_name: 'E2E Test Event',
      event_type: 'user',
      game_gid: 10000147
    };

    // 调用创建API
    const createResponse = await page.evaluate(async (eventData) => {
      try {
        const res = await fetch('/api/events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(eventData)
        });
        const data = await res.json();
        return { success: res.ok, status: res.status, data };
      } catch (error) {
        return { success: false, error: String(error) };
      }
    }, testEvent);

    // 验证创建成功
    expect(createResponse.success).toBe(true);
    expect(createResponse.status).toBe(200);
    expect(createResponse.data.success).toBe(true);

    // 验证返回的事件数据
    const createdEvent = createResponse.data.data;
    expect(createdEvent).toHaveProperty('id');
    expect(createdEvent.event_name).toBe(testEvent.event_name);
    expect(createdEvent.display_name).toBe(testEvent.display_name);
    expect(typeof createdEvent.id === 'number').toBe(true);
  });

  test('应该处理API错误', async ({ page }) => {
    // Mock API失败
    await page.route('/api/events*', route => route.abort());

    // 尝试加载数据
    const hasError = await page.evaluate(async () => {
      try {
        const res = await fetch('/api/events?game_gid=10000147');
        await res.json();
        return false;
      } catch (error) {
        return true;
      }
    });

    // 验证错误被捕获
    expect(hasError).toBe(true);
  });

  test('应该验证游戏上下文数据', async ({ page }) => {
    // 验证游戏上下文已设置
    const gameData = await page.evaluate(() => window.gameData);

    if (gameData) {
      // 验证游戏数据结构
      expect(validateRequiredFields(gameData, ['id', 'gid', 'name', 'ods_db'])).toEqual({
        valid: true,
        missing: []
      });

      // 验证数据类型
      expect(typeof gameData.id === 'number').toBe(true);
      expect(typeof gameData.gid === 'number').toBe(true);
      expect(typeof gameData.name === 'string').toBe(true);
      expect(typeof gameData.ods_db === 'string').toBe(true);

      // 验证游戏GID匹配
      expect(gameData.gid).toBe(10000147);
    }
  });

  test('应该验证事件数据完整性', async ({ page }) => {
    // 获取事件数据
    const events = await fetchAndValidate(
      page,
      '/api/events?game_gid=10000147',
      { method: 'GET' }
    );

    // 验证数据完整性
    expect(events.length).toBeGreaterThan(0);

    // 检查每个事件的必填字段
    events.forEach((event, index) => {
      const validation = validateRequiredFields(event, ['id', 'event_name', 'display_name', 'game_gid']);

      if (!validation.valid) {
        throw new Error(
          `Event at index ${index} is missing required fields: ${validation.missing.join(', ')}`
        );
      }

      // 验证game_gid一致性
      if (event.game_gid !== 10000147) {
        throw new Error(
          `Event at index ${index} has incorrect game_gid: ${event.game_gid}, expected 10000147`
        );
      }
    });
  });
});

/**
 * 对比示例：元素验证 vs 数据验证
 *
 * 这个测试展示了两种方法的区别
 */
test.describe('对比: 元素验证 vs 数据验证', () => {
  test('❌ 元素验证（旧方法）', async ({ page }) => {
    await navigateAndSetGameContext(page, '/events', '10000147');

    // 仅检查UI元素存在
    await expect(page.locator('.events-list-page')).toBeVisible();
    await expect(page.locator('h1:has-text("事件")')).toBeVisible();

    // 问题：即使元素存在，数据可能为空或错误
    // 这个测试无法验证实际的数据正确性
  });

  test('✅ 数据验证（新方法）', async ({ page }) => {
    await navigateAndSetGameContext(page, '/events', '10000147');

    // 验证实际的数据正确性
    const events = await fetchAndValidate(
      page,
      '/api/events?game_gid=10000147',
      { method: 'GET' }
    );

    // 验证数据存在且结构正确
    expect(events.length).toBeGreaterThan(0);
    expect(events[0].id).toBeDefined();
    expect(events[0].event_name).toBeTruthy();

    // 优势：即使UI改变，只要数据正确，测试就会通过
  });
});
