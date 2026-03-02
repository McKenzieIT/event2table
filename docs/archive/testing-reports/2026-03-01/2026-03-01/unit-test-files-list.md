# Frontend Unit Tests - File Reference

**Generated**: 2026-03-01
**Project**: Event2Table
**Test Framework**: Vitest + React Testing Library

## 测试文件清单

### 新增测试文件 (6个)

#### 1. GraphQL性能监控测试

**文件**: `frontend/src/shared/utils/graphqlPerformanceMonitor.test.ts`
**测试用例数**: 60+
**测试类**: `GraphQLPerformanceMonitor`
**关键功能**:
- GraphQL请求追踪
- REST API请求追踪
- 缓存统计
- 性能报告生成
- 优化建议生成

```bash
# 运行测试
cd frontend && npm run test:unit -- graphqlPerformanceMonitor.test.ts
```

#### 2. 表单验证工具测试

**文件**: `frontend/src/shared/utils/validationUtils.test.ts`
**测试用例数**: 80+
**测试函数**:
- `validationRules` (required, minLength, maxLength, pattern, number, email)
- `validateField`
- `validateAll`
- `createFieldValidator`
- `gameValidationRules`

```bash
# 运行测试
cd frontend && npm run test:unit -- validationUtils.test.ts
```

#### 3. 组件工具函数测试

**文件**: `frontend/src/shared/utils/componentUtils.test.ts`
**测试用例数**: 50+
**测试函数**:
- `ensureArray`
- `safeLength`
- `safeFilter`
- `safeMap`
- `safeIsEmpty`

```bash
# 运行测试
cd frontend && npm run test:unit -- componentUtils.test.ts
```

#### 4. 数字格式化工具测试

**文件**: `frontend/src/shared/utils/formatNumber.test.ts`
**测试用例数**: 40+
**测试函数**:
- `formatNumber`
- `formatPercent`
- `formatBytes`

```bash
# 运行测试
cd frontend && npm run test:unit -- formatNumber.test.ts
```

#### 5. API验证工具测试

**文件**: `frontend/src/shared/utils/apiValidator.test.ts`
**测试用例数**: 60+
**测试函数**:
- `validateApiResponse`
- `validateArrayResponse`
- `assertApiResponse`
- `assertArrayResponse`
- `safeParseJSON`
- `validateRequiredFields`

```bash
# 运行测试
cd frontend && npm run test:unit -- apiValidator.test.ts
```

#### 6. 确认对话框组件测试

**文件**: `frontend/src/shared/ui/ConfirmDialog/ConfirmDialog.test.tsx`
**测试用例数**: 40+
**测试组件**: `ConfirmDialog`
**关键功能**:
- 打开/关闭状态
- 用户交互（确认/取消）
- 键盘交互（ESC键）
- Body滚动锁定
- 可访问性（ARIA属性）

```bash
# 运行测试
cd frontend && npm run test:unit -- ConfirmDialog.test.tsx
```

### 现有测试文件 (18个)

#### UI组件测试

| 组件 | 测试文件 | 测试用例数 | 估算覆盖率 |
|------|---------|-----------|-----------|
| Badge | `Badge/Badge.test.tsx` | 20+ | ~90% |
| Breadcrumb | `Breadcrumb/Breadcrumb.test.tsx` | 15+ | ~90% |
| Button | `Button/Button.test.tsx` | 40+ | ~95% |
| Card | `Card/Card.test.tsx` | 25+ | ~90% |
| Checkbox | `Checkbox/Checkbox.test.tsx` | 35+ | ~95% |
| EmptyState | `EmptyState/EmptyState.test.tsx` | 20+ | ~90% |
| ErrorState | `ErrorState/ErrorState.test.tsx` | 25+ | ~90% |
| Input | `Input/Input.test.tsx` | 45+ | ~95% |
| Loading | `Loading.test.tsx` | 15+ | ~85% |
| PageLoader | `PageLoader/PageLoader.test.tsx` | 20+ | ~90% |
| Radio | `Radio/Radio.test.tsx` | 35+ | ~95% |
| SearchInput | `SearchInput/SearchInput.test.tsx` | 30+ | ~90% |
| Select | `Select/Select.test.tsx` | 40+ | ~85% |
| Skeleton | `Skeleton/Skeleton.test.tsx` | 10+ | ~80% |
| Spinner | `Spinner/Spinner.test.tsx` | 20+ | ~90% |
| Switch | `Switch/Switch.test.tsx` | 35+ | ~95% |
| Table | `Table/Table.test.tsx` | 30+ | ~85% |
| TextArea | `TextArea/TextArea.test.tsx` | 25+ | ~90% |
| Toast | `Toast/Toast.test.tsx` | 25+ | ~90% |

## 运行测试的命令

### 全部测试

```bash
# 进入前端目录
cd /Users/mckenzie/Documents/event2table/frontend

# 运行所有单元测试
npm run test:unit

# 运行测试并生成覆盖率报告
npm run test:coverage

# 监视模式（开发时使用）
npm run test:watch

# UI模式（可视化测试结果）
npm run test:ui
```

### 单个测试文件

```bash
# 运行特定测试文件
npm run test:unit -- graphqlPerformanceMonitor.test.ts
npm run test:unit -- validationUtils.test.ts
npm run test:unit -- componentUtils.test.ts
npm run test:unit -- formatNumber.test.ts
npm run test:unit -- apiValidator.test.ts
npm run test:unit -- ConfirmDialog.test.tsx
```

### 按模式匹配运行

```bash
# 运行所有utils测试
npm run test:unit -- src/shared/utils

# 运行所有UI组件测试
npm run test:unit -- src/shared/ui

# 运行特定组件测试
npm run test:unit -- Button
npm run test:unit -- Input
```

## 测试覆盖率命令

### 生成覆盖率报告

```bash
# 生成完整覆盖率报告
npm run test:coverage

# 报告生成在
# frontend/coverage/index.html
```

### 查看覆盖率

```bash
# 在浏览器中打开覆盖率报告
open frontend/coverage/index.html
```

## 测试调试技巧

### 调试单个测试

```bash
# 使用 -t 参数运行特定测试
npm run test:unit -- -t "should calculate cache hit rate"

# 使用 --grep 参数运行匹配的测试
npm run test:unit -- --grep "GraphQL"
```

### 调试模式

```bash
# 使用 Node.js 调试器
node --inspect-brk node_modules/.bin/vitest run

# 在 Chrome 中打开
# chrome://inspect
```

### 仅运行失败的测试

```bash
# 仅运行上次失败的测试
npm run test:unit -- --reporter=verbose --bail=1
```

## 测试文件模板

### 工具函数测试模板

```typescript
/**
 * Utility Function Tests
 */

import { describe, it, expect } from 'vitest';
import { functionToTest } from './utilName';

describe('functionToTest', () => {
  describe('with valid input', () => {
    it('should return expected result', () => {
      const result = functionToTest('input');
      expect(result).toBe('expected');
    });
  });

  describe('with invalid input', () => {
    it('should handle edge case', () => {
      const result = functionToTest(null);
      expect(result).toBe('default');
    });
  });
});
```

### 组件测试模板

```typescript
/**
 * Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Component } from './Component';

describe('Component', () => {
  const defaultProps = {
    // default props here
  };

  describe('Rendering', () => {
    it('should render correctly', () => {
      render(<Component {...defaultProps} />);
      expect(screen.getByText('Content')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should handle click', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();
      render(<Component {...defaultProps} onClick={handleClick} />);

      await user.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalled();
    });
  });
});
```

## 测试最佳实践

### DO ✅

- ✅ 使用描述性的测试名称（`should do something`）
- ✅ 遵循 AAA 模式（Arrange-Act-Assert）
- ✅ 测试用户行为而非实现细节
- ✅ 使用 `@testing-library/user-event` 模拟用户操作
- ✅ 测试边界情况和错误处理
- ✅ 测试可访问性（ARIA属性、键盘导航）
- ✅ 保持测试独立性和可重复性

### DON'T ❌

- ❌ 测试CSS样式（除非是动态类名）
- ❌ 测试第三方库的内部实现
- ❌ 在测试中使用 `console.log`（使用断言代替）
- ❌ 测试过于细粒度的实现细节
- ❌ 在测试中硬编码选择器（使用查询API）
- ❌ 忽略异步操作（使用 await/async）
- ❌ 在测试间共享状态

## 常用断言示例

### DOM断言

```typescript
// 元素存在
expect(screen.getByText('Content')).toBeInTheDocument();
expect(screen.queryByText('Content')).not.toBeInTheDocument();

// 属性断言
expect(element).toHaveAttribute('href', '/path');
expect(element).toHaveClass('active');
expect(element).toHaveStyle({ display: 'none' });

// 可访问性
expect(screen.getByRole('button')).toBeInTheDocument();
expect(screen.getByLabelText('Username')).toBeInTheDocument();
```

### 函数断言

```typescript
// 函数被调用
expect(handleClick).toHaveBeenCalled();
expect(handleClick).toHaveBeenCalledTimes(1);
expect(handleClick).toHaveBeenCalledWith('arg1', 'arg2');

// 函数未被调用
expect(handleClick).not.toHaveBeenCalled();
```

### 数值断言

```typescript
// 数值比较
expect(count).toBe(10);
expect(count).toBeGreaterThan(5);
expect(count).toBeLessThan(20);
expect(count).toBeCloseTo(10.5, 1);

// 数组断言
expect(array).toHaveLength(3);
expect(array).toContain('item');
expect(array).toEqual([1, 2, 3]);
```

---

**最后更新**: 2026-03-01
**维护者**: Event2Table Development Team
