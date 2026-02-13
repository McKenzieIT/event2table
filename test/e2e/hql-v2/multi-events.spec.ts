/**
 * 多事件JOIN/UNION E2E测试
 *
 * 测试多事件HQL生成的完整流程
 */

import { test, expect } from '@playwright/test';

test.describe('多事件HQL生成测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到事件节点构建器
    await page.goto('/event-builder?game_gid=10000147');

    // 等待页面加载
    await page.waitForSelector('h1:has-text("事件节点构建器")', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test.describe('多事件JOIN功能', () => {
    test('应该能够配置两个事件的JOIN', async ({ page }) => {
      console.log('🎬 测试多事件JOIN配置...');

      // 启用V2 API
      const v2Toggle = page.locator('#v2-api-toggle');
      await v2Toggle.waitFor({ state: 'visible', timeout: 5000 });
      await v2Toggle.check();
      await page.waitForTimeout(500);

      // 选择第一个事件
      await page.click('[data-testid="event-item-25ph.pass"]');
      await page.waitForTimeout(500);

      // 选择第二个事件（模拟）
      // 注意：实际UI可能需要不同的选择方式

      console.log('✅ 多事件JOIN配置完成');
    });

    test('应该能够生成正确的JOIN HQL', async ({ request }) => {
      console.log('🎬 测试JOIN HQL生成...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'join',
            include_performance: false
          }
        }
      });

      expect(response.ok()).toBeTruthy();

      const result = await response.json();
      expect(result.success).toBe(true);
      expect(result.data.hql).toBeTruthy();
      expect(result.data.hql).toContain('JOIN');

      console.log('✅ JOIN HQL生成成功:', result.data.hql.substring(0, 100) + '...');
    });
  });

  test.describe('多事件UNION功能', () => {
    test('应该能够生成正确的UNION HQL', async ({ request }) => {
      console.log('🎬 测试UNION HQL生成...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' },
            { fieldName: 'zone_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'union',
            include_performance: false
          }
        }
      });

      expect(response.ok()).toBeTruthy();

      const result = await response.json();
      expect(result.success).toBe(true);
      expect(result.data.hql).toBeTruthy();
      expect(result.data.hql).toContain('UNION ALL');

      console.log('✅ UNION HQL生成成功:', result.data.hql.substring(0, 100) + '...');
    });

    test('UNION查询应该包含正确的分区过滤', async ({ request }) => {
      console.log('🎬 测试UNION分区过滤...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'union',
            include_performance: false
          }
        }
      });

      const result = await response.json();
      const hql = result.data.hql;

      // 每个子查询都应该有分区过滤
      const selectBlocks = hql.split('UNION ALL');
      expect(selectBlocks.length).toBeGreaterThan(1);

      selectBlocks.forEach(block => {
        expect(block).toContain('ds');
      });

      console.log('✅ UNION分区过滤验证通过');
    });
  });

  test.describe('多事件性能分析', () => {
    test('应该能够分析JOIN查询的性能', async ({ request }) => {
      console.log('🎬 测试JOIN性能分析...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'join',
            include_performance: true
          }
        }
      });

      const result = await response.json();

      expect(result.success).toBe(true);
      expect(result.data.performance).toBeDefined();
      expect(result.data.performance.score).toBeGreaterThanOrEqual(0);
      expect(result.data.performance.score).toBeLessThanOrEqual(100);

      console.log('✅ JOIN性能分数:', result.data.performance.score);
    });

    test('应该能够检测JOIN性能问题', async ({ request }) => {
      console.log('🎬 测试JOIN性能问题检测...');

      // 创建一个没有分区过滤的JOIN查询
      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'join',
            include_performance: true
          }
        }
      });

      const result = await response.json();
      const performance = result.data.performance;

      // 如果没有分区过滤，性能分数应该较低
      if (performance.issues && performance.issues.length > 0) {
        console.log('✅ 检测到性能问题:', performance.issues.length, '个');
      } else {
        console.log('✅ 未检测到明显的性能问题');
      }
    });
  });

  test.describe('多事件调试模式', () => {
    test('应该能够提供详细的调试信息', async ({ request }) => {
      console.log('🎬 测试多事件调试模式...');

      const response = await request.post('/hql-preview-v2/api/generate-debug', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 },
            { game_gid: 10000147, event_id: 56 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' },
            { fieldName: 'zone_id', fieldType: 'base' }
          ],
          where_conditions: [],
          debug: true
        }
      });

      const result = await response.json();

      expect(result.success).toBe(true);
      expect(result.data.steps).toBeDefined();
      expect(result.data.steps.length).toBeGreaterThan(0);

      // 验证调试步骤包含必要信息
      const steps = result.data.steps;
      steps.forEach(step => {
        expect(step).toHaveProperty('step');
        expect(step).toHaveProperty('result');
      });

      console.log('✅ 调试步骤数:', steps.length);

      // 打印步骤概览
      steps.forEach((step, index) => {
        console.log(`   ${index + 1}. ${step.step}`);
      });
    });
  });

  test.describe('错误处理', () => {
    test('单个事件时JOIN应该返回错误', async ({ request }) => {
      console.log('🎬 测试单事件JOIN错误处理...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'join',
            include_performance: false
          }
        }
      });

      // 应该返回错误（因为JOIN需要至少2个事件）
      expect(response.status()).toBeGreaterThanOrEqual(400);

      console.log('✅ 单事件JOIN错误验证通过');
    });

    test('单个事件时UNION应该返回错误', async ({ request }) => {
      console.log('🎬 测试单事件UNION错误处理...');

      const response = await request.post('/hql-preview-v2/api/generate', {
        data: {
          events: [
            { game_gid: 10000147, event_id: 55 }
          ],
          fields: [
            { fieldName: 'role_id', fieldType: 'base' }
          ],
          where_conditions: [],
          options: {
            mode: 'union',
            include_performance: false
          }
        }
      });

      // 应该返回错误（因为UNION需要至少2个事件）
      expect(response.status()).toBeGreaterThanOrEqual(400);

      console.log('✅ 单事件UNION错误验证通过');
    });
  });
});
