# Event2Table 测试体系完善方案

> **版本**: 1.0.0 | **创建日期**: 2026-02-19 | **状态**: 设计完成

## 📋 目录

1. [现状分析](#现状分析)
2. [测试体系架构](#测试体系架构)
3. [实施计划](#实施计划)
4. [测试策略](#测试策略)
5. [工具和配置](#工具和配置)
6. [质量指标](#质量指标)

---

## 现状分析

### 当前测试状态

| 测试类型 | 文件数 | 覆盖率 | 状态 |
|---------|--------|--------|------|
| **单元测试** | 7个 | ~15% | ⚠️ 不足 |
| **E2E测试** | 22个 | ~40% | ✅ 良好 |
| **集成测试** | 0个 | 0% | ❌ 缺失 |
| **性能测试** | 1个 | - | ⚠️ 不足 |

### 现有测试工具

- ✅ **Vitest** - 单元测试框架（已配置）
- ✅ **Playwright** - E2E测试框架（已配置）
- ✅ **Testing Library** - React组件测试（已安装）
- ✅ **覆盖率工具** - V8 coverage（已配置）

### 主要问题

1. **单元测试覆盖率低** - 仅15%，关键组件缺少测试
2. **集成测试缺失** - API集成和页面集成测试为0
3. **测试工具未充分利用** - 已有工具但使用不充分
4. **测试文档不完善** - 缺少测试指南和最佳实践

---

## 测试体系架构

### 测试金字塔

```
        /\
       /  \
      / E2E \          10% - 关键用户流程
     /______\
    /        \
   / Integration \      30% - API集成、页面集成
  /______________\
 /                \
/   Unit Tests     \    60% - 组件、Hooks、工具函数
/__________________\
```

### 测试层次结构

#### 1. 单元测试 (Unit Tests) - 60%

**目标覆盖率**: 80%

**测试范围**:
- ✅ React组件（UI组件、业务组件）
- ✅ Custom Hooks
- ✅ 工具函数
- ✅ Store（Zustand）
- ✅ API客户端
- ✅ 类型定义验证

**测试文件组织**:
```
src/
├── shared/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   └── Button.test.tsx
│   │   └── VirtualList/
│   │       ├── VirtualList.jsx
│   │       └── VirtualList.test.jsx
│   ├── hooks/
│   │   ├── useGameContext.ts
│   │   └── useGameContext.test.ts
│   └── utils/
│       ├── formatters.ts
│       └── formatters.test.ts
├── features/
│   ├── games/
│   │   ├── GameManagementModal.tsx
│   │   └── GameManagementModal.test.tsx
│   └── events/
│       ├── EventsList.jsx
│       └── EventsList.test.jsx
└── analytics/
    └── pages/
        ├── EventsList.jsx
        └── EventsList.test.jsx
```

#### 2. 集成测试 (Integration Tests) - 30%

**目标覆盖率**: 70%

**测试范围**:
- ✅ API集成（前后端交互）
- ✅ 页面集成（多组件协作）
- ✅ 数据流集成（React Query + Store）
- ✅ 路由集成

**测试文件组织**:
```
test/
├── integration/
│   ├── api/
│   │   ├── games-api.test.ts
│   │   ├── events-api.test.ts
│   │   └── parameters-api.test.ts
│   ├── pages/
│   │   ├── games-page.test.tsx
│   │   ├── events-page.test.tsx
│   │   └── parameters-page.test.tsx
│   └── data-flow/
│       ├── react-query-integration.test.ts
│       └── store-integration.test.ts
```

#### 3. E2E测试 (End-to-End Tests) - 10%

**目标覆盖率**: 关键流程100%

**测试范围**:
- ✅ 用户关键流程
- ✅ 跨页面交互
- ✅ 真实浏览器环境

**测试文件组织**:
```
test/e2e/
├── critical/
│   ├── game-management.spec.ts
│   ├── event-management.spec.ts
│   ├── hql-generation.spec.ts
│   └── canvas-workflow.spec.ts
├── smoke/
│   ├── smoke-tests.spec.ts
│   └── quick-smoke.spec.ts
└── api-contract/
    ├── api-contract-tests.spec.ts
    └── contract-validation.spec.ts
```

---

## 实施计划

### 阶段1: 基础设施完善 (1-2天)

#### 任务清单

1. **测试配置优化**
   - ✅ 更新vitest.config.ts
   - ✅ 更新playwright.config.ts
   - ✅ 创建测试工具库
   - ✅ 配置测试覆盖率报告

2. **测试工具创建**
   - ✅ 创建测试工具函数（test-utils.tsx）
   - ✅ 创建Mock数据生成器
   - ✅ 创建API Mock工具
   - ✅ 创建测试Fixtures

3. **测试文档编写**
   - ✅ 测试指南
   - ✅ 最佳实践文档
   - ✅ Mock数据使用指南

### 阶段2: 单元测试实施 (3-5天)

#### 优先级1: 核心组件测试

**并行任务组A - UI组件**:
- Button组件测试
- Input组件测试
- Modal组件测试
- Badge组件测试
- Spinner组件测试

**并行任务组B - 业务组件**:
- VirtualList组件测试
- VirtualTable组件测试
- SearchInput组件测试
- ConfirmDialog组件测试

**并行任务组C - 页面组件**:
- EventsList页面测试
- ParametersList页面测试
- GameManagementModal测试
- CategoryManagementModal测试

#### 优先级2: Hooks测试

**并行任务组D - 核心Hooks**:
- useGameContext测试
- useToast测试
- useQuery相关Hooks测试

#### 优先级3: 工具函数测试

**并行任务组E - 工具函数**:
- formatters测试
- validators测试
- api客户端测试

### 阶段3: 集成测试实施 (2-3天)

#### 并行任务组F - API集成

- Games API集成测试
- Events API集成测试
- Parameters API集成测试
- HQL API集成测试

#### 并行任务组G - 页面集成

- Games页面集成测试
- Events页面集成测试
- Parameters页面集成测试
- Canvas页面集成测试

### 阶段4: E2E测试补充 (1-2天)

#### 并行任务组H - 关键流程

- 游戏管理流程E2E测试
- 事件管理流程E2E测试
- HQL生成流程E2E测试
- Canvas工作流E2E测试

### 阶段5: 验证和优化 (1天)

- 运行完整测试套件
- 分析测试覆盖率
- 优化测试性能
- 生成测试报告

---

## 测试策略

### 单元测试策略

#### React组件测试

```typescript
// 示例: Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('应该正确渲染按钮文本', () => {
    render(<Button>点击我</Button>);
    expect(screen.getByText('点击我')).toBeInTheDocument();
  });

  it('应该支持点击事件', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>点击我</Button>);
    fireEvent.click(screen.getByText('点击我'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('应该在禁用状态下不可点击', () => {
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick}>禁用按钮</Button>);
    fireEvent.click(screen.getByText('禁用按钮'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

#### Hooks测试

```typescript
// 示例: useGameContext.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useGameContext } from './useGameContext';

describe('useGameContext', () => {
  it('应该返回游戏上下文', () => {
    const { result } = renderHook(() => useGameContext());
    expect(result.current).toBeDefined();
  });

  it('应该支持设置当前游戏', () => {
    const { result } = renderHook(() => useGameContext());
    act(() => {
      result.current.setCurrentGame({ gid: '10000147', name: '测试游戏' });
    });
    expect(result.current.currentGame?.gid).toBe('10000147');
  });
});
```

### 集成测试策略

#### API集成测试

```typescript
// 示例: games-api.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { fetchGames } from '@/api/games';

const server = setupServer(
  rest.get('/api/games', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: [
        { gid: '10000147', name: '测试游戏1' },
        { gid: '10000148', name: '测试游戏2' }
      ]
    }));
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());

describe('Games API', () => {
  it('应该成功获取游戏列表', async () => {
    const games = await fetchGames();
    expect(games).toHaveLength(2);
    expect(games[0].name).toBe('测试游戏1');
  });
});
```

#### 页面集成测试

```typescript
// 示例: games-page.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect } from 'vitest';
import { GamesList } from '@/features/games/GamesList';

describe('GamesList Page', () => {
  it('应该正确渲染游戏列表', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    });

    render(
      <QueryClientProvider client={queryClient}>
        <GamesList />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('测试游戏1')).toBeInTheDocument();
    });
  });
});
```

### E2E测试策略

#### 关键流程测试

```typescript
// 示例: game-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('游戏管理流程', () => {
  test('应该能够创建新游戏', async ({ page }) => {
    await page.goto('/games');
    await page.click('text=创建游戏');
    await page.fill('input[name="gid"]', '10000149');
    await page.fill('input[name="name"]', 'E2E测试游戏');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=E2E测试游戏')).toBeVisible();
  });

  test('应该能够删除游戏', async ({ page }) => {
    await page.goto('/games');
    const gameRow = page.locator('tr:has-text("E2E测试游戏")');
    await gameRow.locator('button:has-text("删除")').click();
    await page.click('text=确认');
    await expect(page.locator('text=E2E测试游戏')).not.toBeVisible();
  });
});
```

---

## 工具和配置

### 测试工具库

#### test-utils.tsx

```typescript
// test/test-utils.tsx
import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// 创建测试用的QueryClient
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
    },
  });
}

// 测试包装器
interface WrapperProps {
  children: React.ReactNode;
}

export function AllProviders({ children }: WrapperProps) {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

// 自定义render函数
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllProviders, ...options });
}

// 重新导出所有testing-library工具
export * from '@testing-library/react';
export { renderWithProviders as render };
```

#### mock-data.ts

```typescript
// test/mock-data.ts
import { Game, Event, Parameter } from '@/types';

export const mockGames: Game[] = [
  {
    gid: '10000147',
    name: '测试游戏1',
    ods_db: 'ieu_ods',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    is_active: true,
  },
  {
    gid: '10000148',
    name: '测试游戏2',
    ods_db: 'hdyl_data_sg',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    is_active: true,
  },
];

export const mockEvents: Event[] = [
  {
    id: 1,
    game_gid: '10000147',
    event_name: 'test_event_1',
    event_name_cn: '测试事件1',
    category_name: '用户行为',
    param_count: 5,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

export const mockParameters: Parameter[] = [
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
];
```

### Vitest配置优化

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        'test/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        '**/*.d.ts',
      ],
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80,
      },
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 10000,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@canvas': path.resolve(__dirname, './src/canvas'),
      '@features': path.resolve(__dirname, './src/features'),
      '@event-builder': path.resolve(__dirname, './src/event-builder'),
      '@analytics': path.resolve(__dirname, './src/analytics'),
    },
  },
});
```

---

## 质量指标

### 测试覆盖率目标

| 测试类型 | 当前覆盖率 | 目标覆盖率 | 提升幅度 |
|---------|-----------|-----------|----------|
| **单元测试** | 15% | 80% | +65% |
| **集成测试** | 0% | 70% | +70% |
| **E2E测试** | 40% | 100% | +60% |
| **总体覆盖率** | 20% | 80% | +60% |

### 质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **测试通过率** | > 95% | 所有测试的通过率 |
| **测试执行时间** | < 5分钟 | 完整测试套件执行时间 |
| **单元测试执行时间** | < 30秒 | 单元测试套件执行时间 |
| **E2E测试执行时间** | < 10分钟 | E2E测试套件执行时间 |
| **测试维护成本** | < 10% | 测试代码维护时间占比 |

### 成功标准

1. ✅ **覆盖率达标**: 总体覆盖率 ≥ 80%
2. ✅ **测试通过**: 所有测试通过率 ≥ 95%
3. ✅ **性能达标**: 测试执行时间 < 5分钟
4. ✅ **文档完善**: 测试指南和最佳实践文档完整
5. ✅ **CI集成**: 测试集成到CI/CD流程

---

## 实施时间表

| 阶段 | 任务 | 时间 | 并行度 |
|------|------|------|--------|
| **阶段1** | 基础设施完善 | 1-2天 | 串行 |
| **阶段2** | 单元测试实施 | 3-5天 | 5个并行任务组 |
| **阶段3** | 集成测试实施 | 2-3天 | 2个并行任务组 |
| **阶段4** | E2E测试补充 | 1-2天 | 1个并行任务组 |
| **阶段5** | 验证和优化 | 1天 | 串行 |
| **总计** | - | **8-13天** | - |

---

## 风险和缓解

### 主要风险

1. **时间风险**: 测试编写耗时可能超出预期
   - **缓解**: 优先测试核心功能，使用并行开发

2. **维护成本**: 测试代码维护成本高
   - **缓解**: 编写可维护的测试，使用测试工具库

3. **测试稳定性**: E2E测试可能不稳定
   - **缓解**: 增加重试机制，优化等待策略

4. **覆盖率目标**: 80%覆盖率可能难以达到
   - **缓解**: 优先核心模块，逐步提升覆盖率

---

## 总结

本测试体系完善方案旨在将测试覆盖率从20%提升到80%，通过：

1. ✅ **分层测试策略** - 单元测试60%、集成测试30%、E2E测试10%
2. ✅ **并行实施** - 8个并行任务组，提高效率
3. ✅ **工具支持** - 完善的测试工具库和配置
4. ✅ **质量保障** - 明确的质量指标和成功标准

预期在8-13天内完成，显著提升项目质量和可维护性。

---

**方案创建日期**: 2026-02-19
**方案版本**: v1.0.0
**预计完成日期**: 2026-03-01
