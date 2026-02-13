/**
 * HQL预览V2 API E2E测试
 *
 * 测试新的V2 API功能：
 * 1. 性能分析评分
 * 2. 调试模式跟踪
 * 3. 智能字段推荐
 * 4. HQL语法校验
 * 5. V1 vs V2输出一致性
 *
 * 遵循TDD原则：先写测试，看测试失败，再实现功能
 */

import { test, expect } from '@playwright/test';

const API_BASE = '/hql-preview-v2/api';

test.describe('HQL Preview V2 API - Performance Analysis', () => {
  test.beforeEach(async ({ request }) => {
    // 设置游戏上下文
    await request.post('/api/set-game', {
      data: { game_gid: 10000147 }
    });
  });

  test('should return performance score with HQL', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate`, {
      data: {
        events: [
          { game_gid: 10000147, event_id: 55 }
        ],
        fields: [
          { fieldName: 'role_id', fieldType: 'base' },
          { fieldName: 'zone_id', fieldType: 'param', jsonPath: '$.zone_id' }
        ],
        options: {
          mode: 'single',
          include_performance: true
        }
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('hql');
    expect(data.data).toHaveProperty('performance');

    // 验证性能评分存在
    expect(data.data.performance).toHaveProperty('score');
    expect(data.data.performance.score).toBeGreaterThanOrEqual(0);
    expect(data.data.performance.score).toBeLessThanOrEqual(100);

    // 验证问题列表
    expect(data.data.performance).toHaveProperty('issues');
    expect(Array.isArray(data.data.performance.issues)).toBeTruthy();
  });

  test('should detect missing partition filter', async ({ request }) => {
    // 使用 validate 端点测试缺少分区过滤的HQL
    const response = await request.post(`${API_BASE}/validate`, {
      data: {
        hql: "SELECT role_id FROM table WHERE zone_id = 1"
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    const result = data.data;

    // 应该检测到缺少分区过滤
    const syntaxErrors = result.syntax_errors;
    const hasPartitionError = syntaxErrors.some(
      error => error.includes('partition') || error.includes('ds')
    );

    expect(hasPartitionError).toBe(true);
  });

  test('should detect SELECT * performance issue', async ({ request }) => {
    // 使用 validate 端点测试包含 SELECT * 的HQL
    const response = await request.post(`${API_BASE}/validate`, {
      data: {
        hql: "SELECT * FROM table WHERE ds = '${ds}'"
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    const result = data.data;

    // 应该检测到SELECT *问题
    const syntaxErrors = result.syntax_errors;
    const hasStarError = syntaxErrors.some(
      error => error.includes('SELECT *') || error.includes('select *')
    );

    expect(hasStarError).toBe(true);
  });
});

test.describe('HQL Preview V2 API - Debug Mode', () => {
  test('should return debug trace with steps', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate-debug`, {
      data: {
        events: [
          { game_gid: 10000147, event_id: 55 }
        ],
        fields: [
          { fieldName: 'role_id', fieldType: 'base' }
        ],
        debug: true
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('hql');
    expect(data.data).toHaveProperty('steps');

    // 验证调试步骤
    expect(Array.isArray(data.data.steps)).toBeTruthy();
    expect(data.data.steps.length).toBeGreaterThan(0);

    // 验证每个步骤包含必要信息
    const firstStep = data.data.steps[0];
    expect(firstStep).toHaveProperty('step');
    expect(firstStep).toHaveProperty('result');
  });

  test('should include event and field info in debug trace', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate-debug`, {
      data: {
        events: [
          { game_gid: 10000147, event_id: 55 }
        ],
        fields: [
          { fieldName: 'role_id', fieldType: 'base' }
        ],
        debug: true
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    const debugTrace = data.data;

    // 验证包含事件信息
    expect(debugTrace).toHaveProperty('events');
    expect(Array.isArray(debugTrace.events)).toBeTruthy();
    expect(debugTrace.events[0]).toHaveProperty('name');

    // 验证包含字段信息
    expect(debugTrace).toHaveProperty('fields');
    expect(Array.isArray(debugTrace.fields)).toBeTruthy();
  });
});

test.describe('HQL Preview V2 API - Validation', () => {
  test('should validate HQL syntax', async ({ request }) => {
    const response = await request.post(`${API_BASE}/validate`, {
      data: {
        hql: "SELECT role_id, account_id FROM table WHERE ds = '${ds}'"
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('is_valid');
    expect(data.data).toHaveProperty('syntax_errors');

    // 有效的HQL
    expect(data.data.is_valid).toBe(true);
    expect(data.data.syntax_errors.length).toBe(0);
  });

  test('should detect missing SELECT clause', async ({ request }) => {
    const response = await request.post(`${API_BASE}/validate`, {
      data: {
        hql: "FROM table WHERE ds = '${ds}'"
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    const result = data.data;

    // 无效的HQL
    expect(result.is_valid).toBe(false);

    // 应该检测到缺少SELECT
    const syntaxErrors = result.syntax_errors;
    const hasSelectError = syntaxErrors.some(
      error => error.includes('SELECT') || error.includes('select')
    );

    expect(hasSelectError).toBe(true);
  });

  test('should detect missing partition filter', async ({ request }) => {
    const response = await request.post(`${API_BASE}/validate`, {
      data: {
        hql: "SELECT role_id FROM table WHERE zone_id = 1"
      }
    });

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    const result = data.data;

    // 无效的HQL
    expect(result.is_valid).toBe(false);

    // 应该检测到缺少分区过滤
    const syntaxErrors = result.syntax_errors;
    const hasPartitionError = syntaxErrors.some(
      error => error.includes('partition') || error.includes('ds')
    );

    expect(hasPartitionError).toBe(true);
  });
});

test.describe('HQL Preview V2 API - Field Recommendations', () => {
  test('should return field suggestions', async ({ request }) => {
    const response = await request.get(`${API_BASE}/recommend-fields`);

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('suggestions');

    // 验证包含常用字段
    const suggestions = data.data.suggestions;
    expect(suggestions.length).toBeGreaterThan(0);

    // 验证包含基础字段
    const hasDsField = suggestions.some(s => s.name === 'ds');
    const hasRoleIdField = suggestions.some(s => s.name === 'role_id');

    expect(hasDsField).toBe(true);
    expect(hasRoleIdField).toBe(true);
  });

  test('should support partial search', async ({ request }) => {
    const response = await request.get(`${API_BASE}/recommend-fields?partial=zone`);

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);

    // 验证返回的字段包含'zone'
    const suggestions = data.data.suggestions;
    suggestions.forEach(s => {
      expect(s.name.toLowerCase()).toContain('zone');
    });
  });
});

test.describe('HQL Preview V2 - V1 vs V2 Consistency', () => {
  // 注意：V1和V2 API契约不同，这些测试暂时跳过
  // V1: 单事件API，参数为 game_gid, event_id
  // V2: 多事件API，参数为 events: [{game_gid, event_id}]
  test.skip('V2 should generate same HQL structure as V1', async ({ request }) => {
    const requestData = {
      events: [
        { game_gid: 10000147, event_id: 55 }
      ],
      fields: [
        { fieldName: 'role_id', fieldType: 'base' },
        { fieldName: 'zone_id', fieldType: 'param', jsonPath: '$.zone_id' }
      ],
      where_conditions: [
        { field: 'zone_id', operator: '=', value: 1, logicalOp: 'AND' }
      ],
      options: {
        mode: 'single',
        include_comments: true
      }
    };

    // 调用V2 API
    const v2Response = await request.post(`${API_BASE}/generate`, {
      data: requestData
    });

    // 调用V1 API（假设还有/event_node_builder/api/preview-hql）
    const v1Response = await request.post('/event_node_builder/api/preview-hql', {
      data: requestData
    });

    expect(v2Response.ok()).toBeTruthy();
    expect(v1Response.ok()).toBeTruthy();

    const v2Data = await v2Response.json();
    const v1Data = await v1Response.json();

    expect(v2Data.success).toBe(true);
    expect(v1Data.success).toBe(true);

    const v2HQL = v2Data.data.hql;
    const v1HQL = v1Data.data.hql;

    // 验证基本结构一致
    expect(v2HQL).toContain('SELECT');
    expect(v2HQL).toContain('FROM');
    expect(v2HQL).toContain('WHERE');
    expect(v2HQL).toContain("ds = '${ds}'");

    // V2应该包含注释
    expect(v2HQL).toContain('--');

    // 两者都应该包含相同的核心字段
    expect(v2HQL).toContain('role_id');
    expect(v1HQL).toContain('role_id');
  });

  test.skip('V2 should have additional features that V1 lacks', async ({ request }) => {
    const requestData = {
      events: [
        { game_gid: 10000147, event_id: 55 }
      ],
      fields: [
        { fieldName: 'role_id', fieldType: 'base' }
      ],
      options: {
        mode: 'single',
        include_performance: true,
        debug: true
      }
    };

    const v2Response = await request.post(`${API_BASE}/generate-debug`, {
      data: requestData
    });

    expect(v2Response.ok()).toBeTruthy();

    const v2Data = await v2Response.json();
    expect(v2Data.success).toBe(true);

    // V2特有的功能
    expect(v2Data.data).toHaveProperty('performance');
    expect(v2Data.data).toHaveProperty('steps');

    // 性能分析
    expect(v2Data.data.performance).toHaveProperty('score');

    // 调试步骤
    expect(Array.isArray(v2Data.data.steps)).toBeTruthy();
  });
});

test.describe('HQL Preview V2 API - Error Handling', () => {
  test('should return 400 when events is missing', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate`, {
      data: {
        fields: [{ fieldName: 'role_id', fieldType: 'base' }]
      }
    });

    expect(response.status()).toBe(400);

    const data = await response.json();
    expect(data.success).toBe(false);
    expect(data.error).toContain('events is required');
  });

  test('should return 404 when event does not exist', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate`, {
      data: {
        events: [
          { game_gid: 10000147, event_id: 99999 }  // 不存在的事件
        ],
        fields: [{ fieldName: 'role_id', fieldType: 'base' }]
      }
    });

    expect(response.status()).toBe(404);

    const data = await response.json();
    expect(data.success).toBe(false);
    expect(data.error).toContain('not found');
  });

  // 注意：Playwright的request.post自动序列化数据，难以测试原始malformed JSON
  // 在真实浏览器场景中，这由浏览器和Fetch API处理
  test.skip('should handle malformed JSON gracefully', async ({ request }) => {
    const response = await request.post(`${API_BASE}/generate`, {
      data: 'invalid json'
    });

    expect(response.status()).toBe(400);
  });
});

test.describe('HQL Preview V2 - API Status', () => {
  test('should return API status and features', async ({ request }) => {
    const response = await request.get(`${API_BASE}/status`);

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('version');
    expect(data.data).toHaveProperty('status');
    expect(data.data.status).toBe('running');

    // 验证功能列表
    expect(data.data).toHaveProperty('features');
    expect(Array.isArray(data.data.features)).toBeTruthy();

    const expectedFeatures = [
      'single_event_hql',
      'param_fields',
      'custom_fields',
      'where_conditions'
    ];

    expectedFeatures.forEach(feature => {
      expect(data.data.features).toContain(feature);
    });
  });
});
