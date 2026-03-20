/**
 * API Mock工具
 * API Mock Utilities
 * 
 * 提供API Mock功能，用于测试
 */

import { vi } from 'vitest';

/**
 * Mock API响应类型
 */
interface MockAPIConfig {
  success?: boolean;
  data?: any;
  message?: string;
  delay?: number;
  status?: number;
}

/**
 * 创建Mock Fetch函数
 */
export function createMockFetch() {
  const mockResponses = new Map<string, MockAPIConfig>();
  
  const mockFetch = vi.fn(async (url: string, options?: RequestInit) => {
    const config = mockResponses.get(url) || { success: true, data: null };
    const { success = true, data = null, message = '操作成功', delay = 0, status = 200 } = config;
    
    // 模拟网络延迟
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    return {
      ok: success,
      status,
      json: async () => ({
        success,
        data,
        message,
        timestamp: new Date().toISOString(),
      }),
      text: async () => JSON.stringify({
        success,
        data,
        message,
        timestamp: new Date().toISOString(),
      }),
    } as Response;
  });
  
  // 添加设置响应的方法
  (mockFetch as any).setResponse = (url: string, config: MockAPIConfig) => {
    mockResponses.set(url, config);
  };
  
  // 添加清除响应的方法
  (mockFetch as any).clearResponses = () => {
    mockResponses.clear();
  };
  
  return mockFetch;
}

/**
 * Mock Games API
 */
export function mockGamesAPI() {
  const mockFetch = createMockFetch();
  
  // 设置默认响应
  mockFetch.setResponse('/api/games', {
    success: true,
    data: [
      { gid: '10000147', name: '测试游戏1', ods_db: 'ieu_ods' },
      { gid: '10000148', name: '测试游戏2', ods_db: 'hdyl_data_sg' },
    ],
  });
  
  mockFetch.setResponse('/api/games/10000147', {
    success: true,
    data: { gid: '10000147', name: '测试游戏1', ods_db: 'ieu_ods' },
  });
  
  return mockFetch;
}

/**
 * Mock Events API
 */
export function mockEventsAPI() {
  const mockFetch = createMockFetch();
  
  // 设置默认响应
  mockFetch.setResponse('/api/events?game_gid=10000147', {
    success: true,
    data: {
      events: [
        { id: 1, event_name: 'user_login', event_name_cn: '用户登录' },
        { id: 2, event_name: 'user_logout', event_name_cn: '用户登出' },
      ],
      pagination: { page: 1, per_page: 20, total: 2, total_pages: 1 },
    },
  });
  
  mockFetch.setResponse('/api/events/1', {
    success: true,
    data: { id: 1, event_name: 'user_login', event_name_cn: '用户登录' },
  });
  
  return mockFetch;
}

/**
 * Mock Parameters API
 */
export function mockParametersAPI() {
  const mockFetch = createMockFetch();
  
  // 设置默认响应
  mockFetch.setResponse('/api/parameters?game_gid=10000147', {
    success: true,
    data: {
      parameters: [
        { id: 1, param_name: 'user_id', param_name_cn: '用户ID', base_type: 'string' },
        { id: 2, param_name: 'login_time', param_name_cn: '登录时间', base_type: 'datetime' },
      ],
      total: 2,
    },
  });
  
  return mockFetch;
}

/**
 * Mock HQL API
 */
export function mockHQLAPI() {
  const mockFetch = createMockFetch();
  
  // 设置默认响应
  mockFetch.setResponse('/api/hql/generate', {
    success: true,
    data: {
      result: 'SELECT user_id, login_time FROM user_login WHERE user_id = \'12345\'',
      mode: 'single',
      event_count: 1,
      field_count: 2,
    },
  });
  
  return mockFetch;
}

/**
 * Mock所有API
 */
export function mockAllAPIs() {
  const originalFetch = global.fetch;
  
  beforeAll(() => {
    const mockFetch = createMockFetch();
    
    // 设置所有API的默认响应
    mockFetch.setResponse('/api/games', {
      success: true,
      data: [],
    });
    
    mockFetch.setResponse('/api/events', {
      success: true,
      data: { events: [], pagination: { page: 1, per_page: 20, total: 0, total_pages: 0 } },
    });
    
    mockFetch.setResponse('/api/parameters', {
      success: true,
      data: { parameters: [], total: 0 },
    });
    
    mockFetch.setResponse('/api/hql/generate', {
      success: true,
      data: { result: '', mode: 'single', event_count: 0, field_count: 0 },
    });
    
    global.fetch = mockFetch;
  });
  
  afterAll(() => {
    global.fetch = originalFetch;
  });
}

/**
 * 创建错误响应
 */
export function createErrorResponse(message: string, status = 500) {
  return {
    success: false,
    data: null,
    message,
    timestamp: new Date().toISOString(),
    status,
  };
}

/**
 * 创建网络错误
 */
export function createNetworkError() {
  return new Error('Network Error');
}

/**
 * 创建超时错误
 */
export function createTimeoutError() {
  return new Error('Timeout Error');
}
