/**
 * TDD 单元测试：ParamSelector 组件 - API 数据解析
 *
 * 测试 fetchParams 返回的数据是否能正确解析
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { fetchParams } from '@shared/api/eventNodeBuilderApi';

// Mock fetch
global.fetch = jest.fn();

describe('ParamSelector - API 数据解析', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('RED: 应正确解析 API 返回的参数数据', async () => {
    // 模拟 API 返回的数据结构（实际的后端响应）
    const mockApiResponse = {
      success: true,
      data: [
        {
          id: 51,
          param_name: 'serverName',
          param_name_cn: '游戏服名字',
          param_type: 'string',
          is_active: 1,
          description: '',
          created_at: '2026-02-02 12:05:52',
          updated_at: '2026-02-02 12:05:52'
        },
        {
          id: 52,
          param_name: 'roleName',
          param_name_cn: '角色名',
          param_type: 'string',
          is_active: 1,
          description: '',
          created_at: '2026-02-02 12:05:52',
          updated_at: '2026-02-02 12:05:52'
        }
      ],
      timestamp: '2026-02-06T03:05:46.033968+00:00'
    };

    // Mock fetch 返回
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockApiResponse
    });

    // 调用 API
    const result = await fetchParams(55);

    console.log('[DEBUG] API 返回:', JSON.stringify(result, null, 2));

    // 验证基本结构
    expect(result).toBeDefined();
    expect(result.success).toBe(true);

    // 验证数据结构 - 参数数组应该在 data 字段下
    expect(result.data).toBeDefined();
    expect(Array.isArray(result.data)).toBe(true);

    // 验证参数数量
    expect(result.data.length).toBe(2);

    // 验证第一个参数的字段
    expect(result.data[0].param_name).toBe('serverName');
    expect(result.data[0].id).toBe(51);
  });

  it('验证前端代码如何使用 API 响应', async () => {
    const mockApiResponse = {
      success: true,
      data: [
        { id: 1, param_name: 'test1', param_name_cn: '测试1' },
        { id: 2, param_name: 'test2', param_name_cn: '测试2' }
      ]
    };

    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockApiResponse
    });

    const result = await fetchParams(1);

    // 这是 ParamSelector.jsx 中的原始代码（错误版本）:
    // const params = data?.data?.params || [];
    const wrongWay = result?.data?.params || [];
    console.log('[DEBUG] 错误方式 (data?.data?.params):', wrongWay);

    // 这是修复后的代码:
    // const params = data?.data || [];
    const correctWay = result?.data || [];
    console.log('[DEBUG] 正确方式 (data?.data):', correctWay);

    // 验证
    expect(wrongWay.length).toBe(0); // 错误方式会得到空数组
    expect(correctWay.length).toBe(2); // 正确方式会得到参数数组
  });
});
