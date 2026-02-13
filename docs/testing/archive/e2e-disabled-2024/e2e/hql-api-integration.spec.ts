import { test, expect } from '@playwright/test';

/**
 * HQL预览功能 - API集成E2E测试
 *
 * 这个测试直接验证HQL生成的正确性，通过调用API并检查响应。
 * 不依赖复杂的UI交互，更稳定可靠。
 */

test.describe('HQL预览 - API集成测试', () => {
  test.beforeEach(async ({ page }) => {
    // 设置游戏数据
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });

    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('应该通过API生成包含分区筛选的HQL', async ({ page }) => {
    // 直接调用API
    const response = await page.request.post('/event_node_builder/api/preview-hql', {
      data: {
        game_gid: 10000147,
        event_id: 55,  // 使用已知存在的事件ID
        name_en: 'test_node',
        name_cn: '测试节点',
        fields: [
          { field_name: 'ds', field_type: 'base', alias: 'ds' }
        ],
        filter_conditions: { custom_where: '', conditions: [] }
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data.hql).toBeDefined();

    // 验证分区筛选
    expect(data.data.hql).toContain("ds = '${ds}'");
  });

  test('应该使用正确的表名格式', async ({ page }) => {
    const response = await page.request.post('/event_node_builder/api/preview-hql', {
      data: {
        game_gid: 10000147,
        event_id: 55,
        name_en: 'test_node',
        name_cn: '测试节点',
        fields: [
          { field_name: 'ds', field_type: 'base', alias: 'ds' }
        ],
        filter_conditions: { custom_where: '', conditions: [] }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    // 验证表名格式
    expect(data.data.hql).toContain('ods_10000147_all_view');
  });

  test('应该使用event而非event_name', async ({ page }) => {
    const response = await page.request.post('/event_node_builder/api/preview-hql', {
      data: {
        game_gid: 10000147,
        event_id: 55,
        name_en: 'test_node',
        name_cn: '测试节点',
        fields: [
          { field_name: 'ds', field_type: 'base', alias: 'ds' }
        ],
        filter_conditions: { custom_where: '', conditions: [] }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    // 验证使用event而非event_name
    expect(data.data.hql).toContain("event = '");
    expect(data.data.hql).not.toContain('event_name');
  });

  test('应该支持参数字段的get_json_object', async ({ page }) => {
    const response = await page.request.post('/event_node_builder/api/preview-hql', {
      data: {
        game_gid: 10000147,
        event_id: 55,
        name_en: 'test_node',
        name_cn: '测试节点',
        fields: [
          { field_name: 'ds', field_type: 'base', alias: 'ds' },
          { field_name: 'level', field_type: 'param', alias: 'level', base_type: 'int' }
        ],
        filter_conditions: { custom_where: '', conditions: [] }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    // 验证参数字段使用get_json_object
    expect(data.data.hql).toContain("get_json_object(params, '$.level')");
  });
});
