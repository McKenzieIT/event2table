# Testing Documentation - 测试文档索引

> **维护者**: Event2Table Development Team
> **最后更新**: 2026-03-23

---

## 核心测试文档

| 文档 | 描述 | 状态 |
|------|------|------|
| [test-specification.md](./test-specification.md) | **测试规范文档** ⭐ - 组件导出/导入规范、测试文件规范、GraphQL Mock规范 | 活跃 |
| [test-failure-analysis-2026-03-23.md](./test-failure-analysis-2026-03-23.md) | 测试失败分析报告 - 87.6%通过率，错误模式分析 | 参考 |
| [e2e-testing-guide.md](./e2e-testing-guide.md) | E2E测试指南 | 活跃 |
| [complete-e2e-test-plan.md](./complete-e2e-test-plan.md) | 完整E2E测试计划 | 活跃 |
| [quick-test-guide.md](./quick-test-guide.md) | 快速测试指南 | 活跃 |

---

## 测试规范文档 (test-specification.md)

### 核心内容

1. **组件导出/导入规范**
   - 推荐模式：Named Export + Default Export
   - 避免仅 Default Export
   - 统一导出入口 (`@shared/ui/index.ts`)

2. **测试文件规范**
   - 使用 `@test/test-utils` 导入 render
   - useOutletContext Mock 方法
   - 测试文件命名规范

3. **GraphQL Mock 规范**
   - 字段命名：camelCase (非 snake_case)
   - 枚举值：UPPER_SNAKE_CASE
   - 字段映射参考表

4. **ESLint 配置**
   - `import/export` - 检查重复导出
   - `import/named` - 检查 named import 是否存在
   - `import/default` - 检查 default import 是否存在
   - `import/no-duplicates` - 禁止重复导入
   - `import/order` - 导入顺序规范

### 快速参考

```typescript
// ✅ 正确：组件导出
export const MyComponent: React.FC<Props> = (props) => {...}
export default MyComponent

// ✅ 正确：测试导入
import { render, screen, waitFor } from '@test/test-utils';

// ✅ 正确：GraphQL Mock 数据
const mockGames = [
  { id: 1, gid: 10000147, name: 'STAR001', odsDb: 'ieu_ods' }
];

// ✅ 正确：useOutletContext Mock
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => createMockGameContext(),
  };
});
```

---

## 测试失败分析 (test-failure-analysis-2026-03-23.md)

### 关键发现

| 错误类型 | 出现次数 | 优先级 |
|---------|---------|--------|
| Element type is invalid | 1,467 | P0 |
| useOutletContext null | 41 | P1 |
| GraphQL field naming | 14 | P2 |
| act() warnings | 20+ | P2 |

### 修复策略

1. **P0 - 立即修复**
   - 修复组件导入/导出不匹配
   - 排除E2E测试目录

2. **P1 - 高优先级**
   - 添加 OutletContext mock
   - 添加 PromiseConfirmProvider

3. **P2 - 中等优先级**
   - 修复 GraphQL 字段命名
   - 修复 act() 警告

---

## 相关文档

- [测试经验文档](../lessons-learned/testing-guide.md) - 测试最佳实践
- [React最佳实践](../lessons-learned/react-best-practices.md) - React开发规范
- [GraphQL开发指南](../development/graphql-development-guide.md) - GraphQL开发规范

---

## 测试命令

```bash
# 运行单元测试
cd frontend
npm run test:unit

# 运行E2E测试
npm run test:e2e

# 运行ESLint检查
npm run lint

# 运行类型检查
npm run type-check
```

---

## 更新历史

| 日期 | 变更内容 |
|------|---------|
| 2026-03-23 | 创建测试文档索引，添加测试规范文档 |
