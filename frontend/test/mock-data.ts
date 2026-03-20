/**
 * Mock数据生成器
 * Mock Data Generator
 * 
 * 提供统一的测试Mock数据
 */

// ========== 游戏相关Mock数据 ==========

export const mockGames = [
  {
    gid: '10000147',
    name: '测试游戏1',
    ods_db: 'ieu_ods',
    description: '这是一个测试游戏',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    is_active: true,
  },
  {
    gid: '10000148',
    name: '测试游戏2',
    ods_db: 'hdyl_data_sg',
    description: '这是另一个测试游戏',
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
    is_active: true,
  },
  {
    gid: '10000149',
    name: '测试游戏3',
    ods_db: 'ieu_ods',
    description: '这是第三个测试游戏',
    created_at: '2026-01-03T00:00:00Z',
    updated_at: '2026-01-03T00:00:00Z',
    is_active: false,
  },
];

// ========== 事件相关Mock数据 ==========

export const mockEvents = [
  {
    id: 1,
    game_gid: '10000147',
    event_name: 'user_login',
    event_name_cn: '用户登录',
    category_name: '用户行为',
    param_count: 5,
    game_name: '测试游戏1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    game_gid: '10000147',
    event_name: 'user_logout',
    event_name_cn: '用户登出',
    category_name: '用户行为',
    param_count: 3,
    game_name: '测试游戏1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 3,
    game_gid: '10000147',
    event_name: 'purchase_item',
    event_name_cn: '购买道具',
    category_name: '交易',
    param_count: 8,
    game_name: '测试游戏1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

// ========== 参数相关Mock数据 ==========

export const mockParameters = [
  {
    id: 1,
    event_id: 1,
    param_name: 'user_id',
    param_name_cn: '用户ID',
    base_type: 'string',
    events_count: 10,
    usage_count: 100,
    is_common: 1,
  },
  {
    id: 2,
    event_id: 1,
    param_name: 'login_time',
    param_name_cn: '登录时间',
    base_type: 'datetime',
    events_count: 5,
    usage_count: 50,
    is_common: 0,
  },
  {
    id: 3,
    event_id: 1,
    param_name: 'device_type',
    param_name_cn: '设备类型',
    base_type: 'string',
    events_count: 8,
    usage_count: 80,
    is_common: 1,
  },
  {
    id: 4,
    event_id: 2,
    param_name: 'logout_time',
    param_name_cn: '登出时间',
    base_type: 'datetime',
    events_count: 3,
    usage_count: 30,
    is_common: 0,
  },
  {
    id: 5,
    event_id: 3,
    param_name: 'item_id',
    param_name_cn: '道具ID',
    base_type: 'int',
    events_count: 12,
    usage_count: 120,
    is_common: 1,
  },
];

// ========== 分类相关Mock数据 ==========

export const mockCategories = [
  {
    id: 1,
    name: '用户行为',
    description: '用户行为相关事件',
    event_count: 15,
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: '交易',
    description: '交易相关事件',
    event_count: 8,
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 3,
    name: '系统',
    description: '系统相关事件',
    event_count: 5,
    created_at: '2026-01-01T00:00:00Z',
  },
];

// ========== HQL相关Mock数据 ==========

export const mockHQLRequest = {
  game_gid: '10000147',
  event_name: 'user_login',
  fields: [
    { name: 'user_id', type: 'parameter' },
    { name: 'login_time', type: 'parameter' },
  ],
  where_conditions: [
    { field: 'user_id', operator: '=', value: '12345' },
  ],
  sql_mode: 'single',
};

export const mockHQLResponse = {
  success: true,
  data: {
    result: 'SELECT user_id, login_time FROM user_login WHERE user_id = \'12345\'',
    mode: 'single',
    event_count: 1,
    field_count: 2,
    generated_at: '2026-01-01T00:00:00Z',
  },
};

// ========== API响应Mock数据 ==========

export const mockAPIResponse = {
  success: true,
  data: null as any,
  message: '操作成功',
  timestamp: '2026-01-01T00:00:00Z',
};

export const mockPaginatedResponse = {
  success: true,
  data: [] as any[],
  pagination: {
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0,
  },
};

// ========== 工具函数 ==========

/**
 * 创建Mock游戏数据
 */
export function createMockGame(overrides = {}) {
  return {
    gid: '10000150',
    name: '新测试游戏',
    ods_db: 'ieu_ods',
    description: '这是一个新的测试游戏',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    ...overrides,
  };
}

/**
 * 创建Mock事件数据
 */
export function createMockEvent(overrides = {}) {
  return {
    id: Math.floor(Math.random() * 10000),
    game_gid: '10000147',
    event_name: 'test_event',
    event_name_cn: '测试事件',
    category_name: '测试分类',
    param_count: 0,
    game_name: '测试游戏1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

/**
 * 创建Mock参数数据
 */
export function createMockParameter(overrides = {}) {
  return {
    id: Math.floor(Math.random() * 10000),
    event_id: 1,
    param_name: 'test_param',
    param_name_cn: '测试参数',
    base_type: 'string',
    events_count: 1,
    usage_count: 1,
    is_common: 0,
    ...overrides,
  };
}

/**
 * 创建Mock API响应
 */
export function createMockAPIResponse(data: any, success = true, message = '操作成功') {
  return {
    success,
    data,
    message,
    timestamp: new Date().toISOString(),
  };
}

/**
 * 创建Mock分页响应
 */
export function createMockPaginatedResponse(
  items: any[],
  page = 1,
  perPage = 20,
  total?: number
) {
  const totalCount = total || items.length;
  const totalPages = Math.ceil(totalCount / perPage);
  
  return {
    success: true,
    data: items,
    pagination: {
      page,
      per_page: perPage,
      total: totalCount,
      total_pages: totalPages,
    },
  };
}

/**
 * 生成大量Mock数据
 */
export function generateMockEvents(count: number) {
  return Array.from({ length: count }, (_, i) => 
    createMockEvent({
      id: i + 1,
      event_name: `event_${i + 1}`,
      event_name_cn: `事件${i + 1}`,
    })
  );
}

export function generateMockParameters(count: number) {
  return Array.from({ length: count }, (_, i) => 
    createMockParameter({
      id: i + 1,
      param_name: `param_${i + 1}`,
      param_name_cn: `参数${i + 1}`,
    })
  );
}
