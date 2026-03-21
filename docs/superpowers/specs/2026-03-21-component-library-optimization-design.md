# Event2Table 组件库全面优化设计文档

**文档版本**: v1.0  
**创建日期**: 2026-03-21  
**作者**: Aone Copilot  
**状态**: 设计阶段

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [现状分析](#现状分析)
3. [优化目标](#优化目标)
4. [四阶段渐进式优化方案](#四阶段渐进式优化方案)
5. [详细实施计划](#详细实施计划)
6. [风险评估与缓解策略](#风险评估与缓解策略)
7. [验收标准](#验收标准)
8. [附录](#附录)

---

## 执行摘要

### 项目背景

Event2Table 项目的前端组件库经过长期迭代，积累了以下问题：
- **架构问题**：新旧组件并存，职责划分不清晰
- **代码质量问题**：部分文件过大，性能优化不完整
- **测试覆盖问题**：测试文件分散，部分组件测试不足

### 优化策略

采用 **四阶段渐进式优化方案**，确保：
- ✅ 解决所有已知问题
- ✅ 不遗留任何技术债务
- ✅ 每个阶段独立验证，风险可控
- ✅ 最终实现组件库的全面现代化

### 预期成果

- 🎯 **架构清晰**：统一组件目录结构，消除双轨组件
- 🎯 **代码优质**：所有组件符合 React 最佳实践
- 🎯 **测试完善**：测试覆盖率达到 80% 以上
- 🎯 **性能优化**：所有关键组件完成性能优化
- 🎯 **文档完善**：完整的组件文档和使用指南

---

## 现状分析

### 1. 组件目录结构分析

#### 1.1 当前目录结构

```
frontend/src/shared/ui/
├── components/          # 新组件目录（推荐）
│   ├── DatePicker/
│   ├── Form/
│   ├── Modal/
│   ├── Select/
│   └── Table/
├── BaseModal/          # 旧组件目录（已废弃）
├── Select/             # 旧组件目录（已废弃）
├── Table/              # 旧组件目录（已废弃）
├── Button/
├── Card/
├── Checkbox/
├── ... (其他30+个组件)
├── hooks/
├── utils/
└── __tests__/
```

#### 1.2 问题识别

| 问题类型 | 具体问题 | 影响范围 | 严重程度 |
|---------|---------|---------|---------|
| **双轨组件** | BaseModal vs Modal | 5处使用 | 🔴 高 |
| **双轨组件** | Select (旧) vs Select (新) | 3处使用 | 🔴 高 |
| **双轨组件** | Table (旧) vs Table (新) | 3处使用 | 🔴 高 |
| **目录混乱** | 新旧组件并存 | 全局 | 🟡 中 |
| **职责不清** | 部分组件职责重叠 | 局部 | 🟡 中 |

### 2. 代码质量分析

#### 2.1 大文件问题

| 文件路径 | 行数 | 问题描述 | 优先级 |
|---------|------|---------|-------|
| `Form/Form.test.tsx` | 1095 | 测试文件过大，难以维护 | 🔴 P0 |
| `Table/Table.tsx` | 854 | 组件逻辑复杂，需要拆分 | 🔴 P0 |
| `Modal/Modal.test.tsx` | 692 | 测试文件过大，难以维护 | 🟡 P1 |
| `Select/Select.tsx` | 590 | 组件逻辑较复杂 | 🟡 P1 |
| `FormTable.integration.test.tsx` | 843 | 集成测试文件过大 | 🟡 P1 |

#### 2.2 性能优化覆盖

- **已优化组件**: 41个组件使用了 `React.memo`、`useCallback`、`useMemo`
- **未优化组件**: 部分组件缺少性能优化
- **优化覆盖率**: 约 60%

#### 2.3 代码质量问题

| 问题类型 | 数量 | 描述 |
|---------|------|------|
| 缺少 TypeScript 类型 | 待统计 | 部分组件使用 `@ts-nocheck` |
| 缺少错误边界 | 待统计 | 关键组件缺少错误处理 |
| 缺少可访问性支持 | 待统计 | 部分组件 ARIA 属性不完整 |
| 缺少性能优化 | 待统计 | 部分组件未使用 memo/callback |

### 3. 测试覆盖分析

#### 3.1 测试文件分布

- **总测试文件数**: 282 个
- **shared/ui 测试**: 36 个
- **__tests__ 目录数**: 20 个

#### 3.2 测试文件位置

```
frontend/src/
├── features/
│   ├── canvas/__tests__/
│   ├── monitoring/__tests__/
│   ├── events/__tests__/
│   ├── games/__tests__/
│   └── async-tasks/__tests__/
├── shared/
│   ├── ui/__tests__/
│   ├── ui/components/__tests__/
│   ├── ui/components/Form/__tests__/
│   ├── ui/components/Table/__tests__/
│   ├── ui/components/Modal/__tests__/
│   ├── hooks/__tests__/
│   └── popup/__tests__/
├── event-builder/__tests__/
├── monitoring/__tests__/
└── analytics/__tests__/
```

#### 3.3 测试覆盖问题

| 问题类型 | 描述 | 影响 |
|---------|------|------|
| **测试分散** | 测试文件分布在 20 个不同目录 | 难以管理和维护 |
| **测试重复** | 部分组件存在重复测试 | 维护成本高 |
| **测试缺失** | 部分组件缺少单元测试 | 覆盖率不足 |
| **测试质量** | 部分测试用例设计不合理 | 测试有效性低 |

---

## 优化目标

### 总体目标

1. **架构清晰化**: 统一组件目录结构，消除双轨组件
2. **代码优质化**: 所有组件符合 React 最佳实践
3. **测试完善化**: 测试覆盖率达到 80% 以上
4. **性能优化**: 所有核心组件完成性能优化
5. **文档完善**: 完整的组件文档和使用指南

### 具体目标

#### 架构目标

- ✅ 清理所有废弃组件（BaseModal、旧 Select、旧 Table）
- ✅ 统一组件目录结构（所有组件迁移到 `components/` 目录）
- ✅ 明确组件职责划分
- ✅ 建立组件命名规范

#### 代码质量目标

- ✅ 所有组件文件行数 < 500 行
- ✅ 所有测试文件行数 < 800 行
- ✅ 所有组件使用 TypeScript 严格模式
- ✅ 所有组件完成性能优化（React.memo、useCallback、useMemo）
- ✅ 所有组件支持可访问性（ARIA 属性）

#### 测试目标

- ✅ 测试覆盖率达到 80% 以上
- ✅ 所有组件至少有 1 个单元测试文件
- ✅ 核心组件有集成测试
- ✅ 测试文件统一管理（集中在 `__tests__` 目录）

#### 文档目标

- ✅ 每个组件有完整的 JSDoc 注释
- ✅ 每个组件有使用示例
- ✅ 建立组件库文档站点
- ✅ 提供迁移指南

---

## 四阶段渐进式优化方案

### 阶段概览

```
阶段 1: 低风险清理 (预计 2-3 天)
    ↓
阶段 2: 架构优化 (预计 3-5 天)
    ↓
阶段 3: 性能优化 (预计 2-3 天)
    ↓
阶段 4: 测试完善 (预计 3-5 天)
```

### 阶段 1: 低风险清理

**目标**: 清理废弃代码，统一导入路径

**任务清单**:

1. **清理废弃组件**
   - [ ] 删除 `BaseModal` 目录及所有引用（5处）
   - [ ] 删除旧 `Select` 目录及所有引用（3处）
   - [ ] 删除旧 `Table` 目录及所有引用（3处）
   - [ ] 更新所有导入路径到新组件

2. **清理废弃测试**
   - [ ] 删除废弃组件的测试文件
   - [ ] 清理无用的测试工具函数
   - [ ] 整理测试配置文件

3. **更新文档**
   - [ ] 更新组件导入路径文档
   - [ ] 创建废弃组件迁移指南
   - [ ] 更新 README 文件

**验收标准**:
- ✅ 所有废弃组件已删除
- ✅ 所有导入路径已更新
- ✅ 所有测试通过
- ✅ 文档已更新

**风险评估**: 🟢 低风险
- 只删除明确废弃的代码
- 不修改任何业务逻辑
- 可以快速回滚

---

### 阶段 2: 架构优化

**目标**: 重构大文件，优化组件结构

**任务清单**:

1. **拆分大文件**
   - [ ] 拆分 `Table.tsx` (854行 → 多个子组件)
     - 提取 `TableHeader` 组件
     - 提取 `TableBody` 组件
     - 提取 `TableFooter` 组件
     - 提取 `TableRow` 组件
     - 提取 `TableCell` 组件
   - [ ] 拆分 `Select.tsx` (590行 → 多个子组件)
     - 提取 `SelectOption` 组件
     - 提取 `SelectDropdown` 组件
     - 提取 `SelectSearch` 组件
   - [ ] 拆分 `DatePicker.tsx` (519行 → 多个子组件)
     - 提取 `Calendar` 组件
     - 提取 `DateInput` 组件

2. **重构测试文件**
   - [ ] 拆分 `Form.test.tsx` (1095行 → 多个测试文件)
     - 拆分为 `Form.render.test.tsx`
     - 拆分为 `Form.validation.test.tsx`
     - 拆分为 `Form.submission.test.tsx`
     - 拆分为 `Form.integration.test.tsx`
   - [ ] 拆分 `Modal.test.tsx` (692行 → 多个测试文件)
     - 拆分为 `Modal.render.test.tsx`
     - 拆分为 `Modal.interaction.test.tsx`
     - 拆分为 `Modal.accessibility.test.tsx`
   - [ ] 拆分 `FormTable.integration.test.tsx` (843行 → 多个测试文件)

3. **优化组件结构**
   - [ ] 统一组件目录结构
     ```
     ComponentName/
     ├── ComponentName.tsx        # 主组件
     ├── ComponentName.types.ts   # 类型定义
     ├── ComponentName.styles.ts  # 样式（如需要）
     ├── ComponentName.utils.ts   # 工具函数（如需要）
     ├── ComponentName.test.tsx   # 测试文件
     ├── ComponentName.stories.tsx # Storybook（如需要）
     └── index.ts                 # 导出
     ```
   - [ ] 统一组件命名规范
     - 组件名使用 PascalCase
     - 文件名使用 PascalCase
     - 测试文件使用 `.test.tsx` 后缀
     - 类型文件使用 `.types.ts` 后缀

4. **更新导入导出**
   - [ ] 统一导出方式（使用 `index.ts`）
   - [ ] 更新所有导入路径
   - [ ] 创建组件库统一入口

**验收标准**:
- ✅ 所有组件文件 < 500 行
- ✅ 所有测试文件 < 800 行
- ✅ 所有组件遵循统一目录结构
- ✅ 所有测试通过

**风险评估**: 🟡 中等风险
- 需要修改组件内部结构
- 需要更新大量导入路径
- 需要仔细测试确保功能不变

---

### 阶段 3: 性能优化

**目标**: 优化组件性能，符合 React 最佳实践

**任务清单**:

1. **React 性能优化**
   - [ ] 为所有组件添加 `React.memo`
   - [ ] 为所有事件处理器添加 `useCallback`
   - [ ] 为所有计算属性添加 `useMemo`
   - [ ] 优化组件渲染逻辑
   - [ ] 添加性能监控

2. **性能优化检查清单**

   **每个组件必须检查**:
   - [ ] 是否使用 `React.memo` 包裹组件
   - [ ] 是否为事件处理器使用 `useCallback`
   - [ ] 是否为计算属性使用 `useMemo`
   - [ ] 是否避免内联对象和数组
   - [ ] 是否使用正确的依赖数组
   - [ ] 是否避免不必要的重新渲染

3. **性能测试**
   - [ ] 编写性能测试用例
   - [ ] 测试组件渲染时间
   - [ ] 测试内存使用情况
   - [ ] 测试大数据量下的性能

4. **性能文档**
   - [ ] 编写性能优化指南
   - [ ] 记录性能基准数据
   - [ ] 提供性能优化建议

**验收标准**:
- ✅ 所有组件使用 `React.memo`
- ✅ 所有事件处理器使用 `useCallback`
- ✅ 所有计算属性使用 `useMemo`
- ✅ 性能测试通过
- ✅ 性能文档完整

**风险评估**: 🟡 中等风险
- 性能优化可能引入 bug
- 需要仔细测试确保功能不变
- 需要性能基准测试

---

### 阶段 4: 测试完善

**目标**: 完善测试覆盖，提高测试质量

**任务清单**:

1. **测试覆盖率提升**
   - [ ] 为所有组件添加单元测试
   - [ ] 为核心组件添加集成测试
   - [ ] 为关键业务流程添加 E2E 测试
   - [ ] 达到 80% 测试覆盖率

2. **测试文件整理**
   - [ ] 统一测试文件位置（集中在 `__tests__` 目录）
   - [ ] 统一测试文件命名规范
   - [ ] 清理重复测试
   - [ ] 优化测试工具函数

3. **测试质量提升**
   - [ ] 编写有意义的测试用例
   - [ ] 测试边界情况
   - [ ] 测试错误处理
   - [ ] 测试可访问性
   - [ ] 测试性能

4. **测试文档**
   - [ ] 编写测试指南
   - [ ] 记录测试最佳实践
   - [ ] 提供测试示例

**验收标准**:
- ✅ 测试覆盖率达到 80%
- ✅ 所有组件至少有 1 个单元测试
- ✅ 核心组件有集成测试
- ✅ 测试文件统一管理
- ✅ 测试文档完整

**风险评估**: 🟢 低风险
- 只添加测试，不修改代码
- 可以逐步添加测试
- 不会影响现有功能

---

## 详细实施计划

### 阶段 1: 低风险清理 - 详细计划

#### 任务 1.1: 清理 BaseModal 组件

**步骤**:

1. **识别所有使用位置**
   ```bash
   # 搜索所有 BaseModal 的导入
   grep -r "import.*BaseModal" frontend/src --include="*.tsx" --include="*.ts"
   ```

2. **更新导入路径**
   - 文件 1: `frontend/src/features/xxx/File1.tsx`
     ```typescript
     // 修改前
     import { BaseModal } from '@shared/ui/BaseModal';
     
     // 修改后
     import { Modal } from '@shared/ui/components/Modal';
     ```
   
   - 文件 2: `frontend/src/features/yyy/File2.tsx`
     ```typescript
     // 修改前
     import BaseModal from '@shared/ui/BaseModal/BaseModal';
     
     // 修改后
     import { Modal } from '@shared/ui/components/Modal';
     ```

3. **更新组件使用**
   - 检查 `BaseModal` 和 `Modal` 的 API 差异
   - 更新组件属性名称（如有差异）
   - 更新事件处理器名称（如有差异）

4. **删除废弃文件**
   ```bash
   # 删除 BaseModal 目录
   rm -rf frontend/src/shared/ui/BaseModal
   ```

5. **运行测试**
   ```bash
   # 运行相关测试
   npm test -- --grep "Modal"
   ```

**预期结果**:
- ✅ 所有 BaseModal 引用已更新为 Modal
- ✅ BaseModal 目录已删除
- ✅ 所有测试通过

---

#### 任务 1.2: 清理旧 Select 组件

**步骤**:

1. **识别所有使用位置**
   ```bash
   grep -r "import.*from.*@shared/ui/Select" frontend/src --include="*.tsx" --include="*.ts" | grep -v "components/"
   ```

2. **更新导入路径**
   ```typescript
   // 修改前
   import { Select } from '@shared/ui/Select';
   
   // 修改后
   import { Select } from '@shared/ui/components/Select';
   ```

3. **删除废弃文件**
   ```bash
   rm -rf frontend/src/shared/ui/Select
   ```

4. **运行测试**
   ```bash
   npm test -- --grep "Select"
   ```

**预期结果**:
- ✅ 所有旧 Select 引用已更新
- ✅ 旧 Select 目录已删除
- ✅ 所有测试通过

---

#### 任务 1.3: 清理旧 Table 组件

**步骤**: 类似于 Select 组件的清理步骤

---

### 阶段 2: 架构优化 - 详细计划

#### 任务 2.1: 拆分 Table.tsx 组件

**当前结构**:
```
Table.tsx (854 行)
├── Table 组件主逻辑
├── TableHeader 逻辑
├── TableBody 逻辑
├── TableRow 逻辑
├── TableCell 逻辑
└── 工具函数
```

**目标结构**:
```
Table/
├── Table.tsx              # 主组件 (~200 行)
├── Table.types.ts         # 类型定义
├── components/
│   ├── TableHeader.tsx    # 表头组件
│   ├── TableBody.tsx      # 表体组件
│   ├── TableRow.tsx       # 行组件
│   └── TableCell.tsx      # 单元格组件
├── hooks/
│   ├── useTableSort.ts    # 排序 Hook
│   ├── useTableFilter.ts  # 过滤 Hook
│   └── useTablePagination.ts # 分页 Hook
├── utils/
│   ├── tableUtils.ts      # 工具函数
│   └── tableConstants.ts  # 常量定义
├── Table.test.tsx         # 主组件测试
├── __tests__/
│   ├── TableHeader.test.tsx
│   ├── TableBody.test.tsx
│   ├── TableRow.test.tsx
│   └── TableCell.test.tsx
└── index.ts               # 导出
```

**拆分步骤**:

1. **提取类型定义**
   ```typescript
   // Table.types.ts
   export interface TableProps {
     // ...
   }
   
   export interface TableColumn {
     // ...
   }
   
   // ... 其他类型定义
   ```

2. **提取子组件**
   ```typescript
   // components/TableHeader.tsx
   export const TableHeader: React.FC<TableHeaderProps> = ({ columns, sortConfig, onSort }) => {
     // ...
   };
   
   // components/TableBody.tsx
   export const TableBody: React.FC<TableBodyProps> = ({ data, columns }) => {
     // ...
   };
   
   // ... 其他子组件
   ```

3. **提取 Hooks**
   ```typescript
   // hooks/useTableSort.ts
   export const useTableSort = (data: any[], defaultSortConfig?: SortConfig) => {
     // ...
   };
   
   // ... 其他 Hooks
   ```

4. **提取工具函数**
   ```typescript
   // utils/tableUtils.ts
   export const sortData = (data: any[], sortConfig: SortConfig) => {
     // ...
   };
   
   // ... 其他工具函数
   ```

5. **重构主组件**
   ```typescript
   // Table.tsx
   import { TableHeader } from './components/TableHeader';
   import { TableBody } from './components/TableBody';
   import { useTableSort } from './hooks/useTableSort';
   import { useTableFilter } from './hooks/useTableFilter';
   
   export const Table: React.FC<TableProps> = ({ data, columns, ...props }) => {
     const { sortedData, sortConfig, handleSort } = useTableSort(data);
     const { filteredData, filterConfig, handleFilter } = useTableFilter(sortedData);
     
     return (
       <div className="table-container">
         <TableHeader columns={columns} sortConfig={sortConfig} onSort={handleSort} />
         <TableBody data={filteredData} columns={columns} />
       </div>
     );
   };
   ```

**验收标准**:
- ✅ 主组件文件 < 200 行
- ✅ 所有子组件文件 < 200 行
- ✅ 功能与拆分前完全一致
- ✅ 所有测试通过

---

#### 任务 2.2: 拆分 Form.test.tsx 测试文件

**当前结构**:
```
Form.test.tsx (1095 行)
├── 渲染测试
├── 验证测试
├── 提交测试
├── 集成测试
└── 辅助函数
```

**目标结构**:
```
Form/
├── __tests__/
│   ├── Form.render.test.tsx       # 渲染测试 (~200 行)
│   ├── Form.validation.test.tsx   # 验证测试 (~300 行)
│   ├── Form.submission.test.tsx   # 提交测试 (~300 行)
│   ├── Form.integration.test.tsx  # 集成测试 (~200 行)
│   └── Form.accessibility.test.tsx # 可访问性测试 (~100 行)
├── test-utils/
│   ├── formTestUtils.ts           # 测试工具函数
│   └── formTestData.ts            # 测试数据
└── Form.test.tsx                  # 主测试文件（导入所有测试）
```

**拆分步骤**:

1. **提取测试工具函数**
   ```typescript
   // test-utils/formTestUtils.ts
   export const renderForm = (props: FormProps) => {
     // ...
   };
   
   export const fillForm = (values: Record<string, any>) => {
     // ...
   };
   
   // ... 其他工具函数
   ```

2. **拆分测试文件**
   ```typescript
   // __tests__/Form.render.test.tsx
   describe('Form Rendering', () => {
     it('should render form with default props', () => {
       // ...
     });
     
     // ... 其他渲染测试
   });
   
   // __tests__/Form.validation.test.tsx
   describe('Form Validation', () => {
     it('should validate required fields', () => {
       // ...
     });
     
     // ... 其他验证测试
   });
   
   // ... 其他测试文件
   ```

3. **创建主测试文件**
   ```typescript
   // Form.test.tsx
   import './__tests__/Form.render.test';
   import './__tests__/Form.validation.test';
   import './__tests__/Form.submission.test';
   import './__tests__/Form.integration.test';
   import './__tests__/Form.accessibility.test';
   ```

**验收标准**:
- ✅ 所有测试文件 < 300 行
- ✅ 测试覆盖与拆分前一致
- ✅ 所有测试通过

---

### 阶段 3: 性能优化 - 详细计划

#### 任务 3.1: 为所有组件添加性能优化

**优化检查清单**:

**每个组件必须完成以下优化**:

1. **使用 React.memo**
   ```typescript
   export const MyComponent = React.memo(function MyComponent(props: MyComponentProps) {
     // 组件实现
   });
   ```

2. **使用 useCallback**
   ```typescript
   const handleClick = useCallback((event: React.MouseEvent) => {
     // 事件处理
   }, [dependencies]);
   
   const handleChange = useCallback((value: string) => {
     // 值变化处理
   }, [dependencies]);
   ```

3. **使用 useMemo**
   ```typescript
   const computedValue = useMemo(() => {
     return expensiveComputation(props.data);
   }, [props.data]);
   
   const sortedList = useMemo(() => {
     return props.list.sort((a, b) => a - b);
   }, [props.list]);
   ```

4. **避免内联对象和数组**
   ```typescript
   // ❌ 错误：每次渲染都创建新对象
   <ChildComponent style={{ margin: 10 }} />
   
   // ✅ 正确：使用 useMemo 缓存对象
   const style = useMemo(() => ({ margin: 10 }), []);
   <ChildComponent style={style} />
   ```

5. **正确的依赖数组**
   ```typescript
   // ❌ 错误：缺少依赖
   useEffect(() => {
     fetchData(props.id);
   }, []); // 缺少 props.id 依赖
   
   // ✅ 正确：包含所有依赖
   useEffect(() => {
     fetchData(props.id);
   }, [props.id]);
   ```

**优化步骤**:

1. **识别需要优化的组件**
   ```bash
   # 查找未使用 React.memo 的组件
   grep -r "export const.*=.*function" frontend/src/shared/ui --include="*.tsx" | grep -v "React.memo"
   
   # 查找未使用 useCallback 的事件处理器
   # ... (需要手动检查)
   
   # 查找未使用 useMemo 的计算属性
   # ... (需要手动检查)
   ```

2. **逐个优化组件**
   - 为组件添加 `React.memo`
   - 为事件处理器添加 `useCallback`
   - 为计算属性添加 `useMemo`
   - 修复依赖数组问题

3. **性能测试**
   ```typescript
   // 编写性能测试
   describe('Component Performance', () => {
     it('should not re-render when props are the same', () => {
       const { rerender } = render(<MyComponent value="test" />);
       const renderCount = jest.spyOn(console, 'log');
       
       rerender(<MyComponent value="test" />);
       
       expect(renderCount).not.toHaveBeenCalled();
     });
     
     it('should render within acceptable time', () => {
       const startTime = performance.now();
       render(<MyComponent largeData={largeDataset} />);
       const endTime = performance.now();
       
       expect(endTime - startTime).toBeLessThan(100); // 100ms
     });
   });
   ```

**验收标准**:
- ✅ 所有组件使用 `React.memo`
- ✅ 所有事件处理器使用 `useCallback`
- ✅ 所有计算属性使用 `useMemo`
- ✅ 所有依赖数组正确
- ✅ 性能测试通过

---

### 阶段 4: 测试完善 - 详细计划

#### 任务 4.1: 提升测试覆盖率

**目标**: 达到 80% 测试覆盖率

**策略**:

1. **识别未覆盖的代码**
   ```bash
   # 运行测试覆盖率报告
   npm test -- --coverage --coverageReporters=html
   
   # 查看覆盖率报告
   open coverage/index.html
   ```

2. **为未覆盖的组件添加测试**
   - 优先级 P0: 核心业务组件（Form、Select、Modal、Table）
   - 优先级 P1: 常用 UI 组件（Button、Input、Checkbox）
   - 优先级 P2: 辅助组件（Spinner、Skeleton、EmptyState）

3. **测试用例设计原则**
   - **渲染测试**: 测试组件是否正确渲染
   - **交互测试**: 测试用户交互是否正确处理
   - **状态测试**: 测试组件状态变化是否正确
   - **边界测试**: 测试边界情况和错误处理
   - **可访问性测试**: 测试 ARIA 属性和键盘导航
   - **性能测试**: 测试组件渲染性能

4. **测试示例**
   ```typescript
   // Form.test.tsx
   describe('Form Component', () => {
     // 渲染测试
     describe('Rendering', () => {
       it('should render form with default props', () => {
         const { container } = render(<Form />);
         expect(container.querySelector('form')).toBeInTheDocument();
       });
       
       it('should render form with children', () => {
         const { getByText } = render(
           <Form>
             <FormInput name="username" />
             <FormInput name="password" type="password" />
           </Form>
         );
         
         expect(getByText('username')).toBeInTheDocument();
         expect(getByText('password')).toBeInTheDocument();
       });
     });
     
     // 交互测试
     describe('Interaction', () => {
       it('should submit form with correct values', async () => {
         const onSubmit = jest.fn();
         const { getByLabelText, getByText } = render(
           <Form onSubmit={onSubmit}>
             <FormInput name="username" label="Username" />
             <button type="submit">Submit</button>
           </Form>
         );
         
         await userEvent.type(getByLabelText('Username'), 'testuser');
         await userEvent.click(getByText('Submit'));
         
         expect(onSubmit).toHaveBeenCalledWith({ username: 'testuser' });
       });
     });
     
     // 验证测试
     describe('Validation', () => {
       it('should show validation errors', async () => {
         const { getByText, getByLabelText } = render(
           <Form>
             <FormInput name="email" label="Email" required />
             <button type="submit">Submit</button>
           </Form>
         );
         
         await userEvent.click(getByText('Submit'));
         
         expect(getByText('Email is required')).toBeInTheDocument();
       });
     });
     
     // 可访问性测试
     describe('Accessibility', () => {
       it('should have correct ARIA attributes', () => {
         const { container } = render(<Form />);
         const form = container.querySelector('form');
         
         expect(form).toHaveAttribute('role', 'form');
       });
       
       it('should support keyboard navigation', async () => {
         const { getByLabelText } = render(
           <Form>
             <FormInput name="username" label="Username" />
             <FormInput name="password" label="Password" />
           </Form>
         );
         
         const usernameInput = getByLabelText('Username');
         const passwordInput = getByLabelText('Password');
         
         await userEvent.tab();
         expect(usernameInput).toHaveFocus();
         
         await userEvent.tab();
         expect(passwordInput).toHaveFocus();
       });
     });
   });
   ```

**验收标准**:
- ✅ 测试覆盖率达到 80%
- ✅ 所有核心组件有完整测试
- ✅ 所有测试文件 < 300 行
- ✅ 测试质量高，覆盖各种场景

---

## 风险评估与缓解策略

### 风险矩阵

| 风险类型 | 风险描述 | 概率 | 影响 | 风险等级 | 缓解策略 |
|---------|---------|------|------|---------|---------|
| **功能回归** | 重构导致功能异常 | 中 | 高 | 🔴 高 | 完整测试覆盖，逐步验证 |
| **性能下降** | 优化后性能反而下降 | 低 | 中 | 🟡 中 | 性能基准测试，对比验证 |
| **导入错误** | 导入路径更新遗漏 | 中 | 中 | 🟡 中 | 使用工具批量更新，全局搜索验证 |
| **测试失败** | 测试用例需要更新 | 高 | 低 | 🟢 低 | 逐步更新测试，确保测试通过 |
| **兼容性问题** | 新旧组件 API 不兼容 | 低 | 高 | 🟡 中 | 详细 API 对比，提供迁移指南 |

### 缓解策略详细说明

#### 1. 功能回归风险缓解

**策略**:
- 每个阶段完成后进行完整的功能测试
- 使用 E2E 测试验证关键业务流程
- 建立功能回归测试套件
- 使用 Git 分支进行隔离开发，随时可以回滚

**具体措施**:
```bash
# 每个阶段完成后运行完整测试
npm test

# 运行 E2E 测试
npm run test:e2e

# 运行性能测试
npm run test:performance
```

#### 2. 性能下降风险缓解

**策略**:
- 建立性能基准数据
- 每次优化后进行性能对比
- 使用 React DevTools 进行性能分析
- 使用 Lighthouse 进行性能评分

**具体措施**:
```bash
# 建立性能基准
npm run benchmark

# 性能对比
npm run benchmark:compare

# React DevTools 性能分析
# 使用 Chrome DevTools 的 Profiler 面板

# Lighthouse 性能评分
lighthouse http://localhost:3000 --view
```

#### 3. 导入错误风险缓解

**策略**:
- 使用工具批量更新导入路径
- 全局搜索验证所有导入
- 使用 TypeScript 编译器检查导入错误
- 使用 ESLint 检查未使用的导入

**具体措施**:
```bash
# 使用工具批量更新导入
# 例如：使用 VSCode 的 "Find and Replace" 功能

# 全局搜索验证
grep -r "from.*BaseModal" frontend/src --include="*.tsx" --include="*.ts"

# TypeScript 编译检查
npm run type-check

# ESLint 检查
npm run lint
```

---

## 验收标准

### 总体验收标准

- ✅ **架构清晰**: 所有组件遵循统一目录结构，无双轨组件
- ✅ **代码优质**: 所有组件文件 < 500 行，符合 React 最佳实践
- ✅ **测试完善**: 测试覆盖率 ≥ 80%，所有核心组件有完整测试
- ✅ **性能优化**: 所有组件完成性能优化，性能测试通过
- ✅ **文档完善**: 所有组件有完整文档和使用示例

### 阶段验收标准

#### 阶段 1 验收标准

- ✅ 所有废弃组件已删除
- ✅ 所有导入路径已更新
- ✅ 所有测试通过
- ✅ 文档已更新
- ✅ 无功能回归

#### 阶段 2 验收标准

- ✅ 所有组件文件 < 500 行
- ✅ 所有测试文件 < 800 行
- ✅ 所有组件遵循统一目录结构
- ✅ 所有测试通过
- ✅ 无功能回归

#### 阶段 3 验收标准

- ✅ 所有组件使用 `React.memo`
- ✅ 所有事件处理器使用 `useCallback`
- ✅ 所有计算属性使用 `useMemo`
- ✅ 性能测试通过
- ✅ 性能无下降

#### 阶段 4 验收标准

- ✅ 测试覆盖率 ≥ 80%
- ✅ 所有组件至少有 1 个单元测试
- ✅ 核心组件有集成测试
- ✅ 测试文件统一管理
- ✅ 所有测试通过

---

## 附录

### A. 组件迁移清单

#### A.1 BaseModal 迁移清单

| 文件路径 | 当前导入 | 目标导入 | 状态 |
|---------|---------|---------|------|
| `features/xxx/File1.tsx` | `@shared/ui/BaseModal` | `@shared/ui/components/Modal` | ⏳ 待迁移 |
| `features/yyy/File2.tsx` | `@shared/ui/BaseModal/BaseModal` | `@shared/ui/components/Modal` | ⏳ 待迁移 |
| ... | ... | ... | ... |

#### A.2 Select 迁移清单

| 文件路径 | 当前导入 | 目标导入 | 状态 |
|---------|---------|---------|------|
| `features/xxx/File3.tsx` | `@shared/ui/Select` | `@shared/ui/components/Select` | ⏳ 待迁移 |
| ... | ... | ... | ... |

#### A.3 Table 迁移清单

| 文件路径 | 当前导入 | 目标导入 | 状态 |
|---------|---------|---------|------|
| `features/xxx/File4.tsx` | `@shared/ui/Table` | `@shared/ui/components/Table` | ⏳ 待迁移 |
| ... | ... | ... | ... |

### B. 性能优化检查清单

#### B.1 React 性能优化检查清单

- [ ] 组件使用 `React.memo` 包裹
- [ ] 事件处理器使用 `useCallback`
- [ ] 计算属性使用 `useMemo`
- [ ] 避免内联对象和数组
- [ ] 使用正确的依赖数组
- [ ] 避免不必要的重新渲染
- [ ] 使用 `React.lazy` 进行代码分割（如适用）
- [ ] 使用 `Suspense` 进行懒加载（如适用）

#### B.2 渲染性能检查清单

- [ ] 组件渲染时间 < 16ms (60fps)
- [ ] 大列表使用虚拟化（如 react-window）
- [ ] 图片使用懒加载
- [ ] 使用 Web Workers 处理计算密集型任务
- [ ] 避免布局抖动（Layout Thrashing）

### C. 测试用例模板

#### C.1 组件测试模板

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  // 渲染测试
  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<ComponentName />);
      expect(screen.getByRole('...')).toBeInTheDocument();
    });
    
    it('should render with custom props', () => {
      render(<ComponentName prop1="value1" prop2="value2" />);
      expect(screen.getByText('value1')).toBeInTheDocument();
    });
  });
  
  // 交互测试
  describe('Interaction', () => {
    it('should handle click event', async () => {
      const onClick = jest.fn();
      render(<ComponentName onClick={onClick} />);
      
      await userEvent.click(screen.getByRole('button'));
      
      expect(onClick).toHaveBeenCalled();
    });
  });
  
  // 状态测试
  describe('State', () => {
    it('should update state correctly', () => {
      const { rerender } = render(<ComponentName value="initial" />);
      expect(screen.getByText('initial')).toBeInTheDocument();
      
      rerender(<ComponentName value="updated" />);
      expect(screen.getByText('updated')).toBeInTheDocument();
    });
  });
  
  // 边界测试
  describe('Edge Cases', () => {
    it('should handle empty data', () => {
      render(<ComponentName data={[]} />);
      expect(screen.getByText('No data')).toBeInTheDocument();
    });
    
    it('should handle error gracefully', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      
      render(<ComponentName invalidProp={undefined} />);
      
      expect(consoleError).toHaveBeenCalled();
      consoleError.mockRestore();
    });
  });
  
  // 可访问性测试
  describe('Accessibility', () => {
    it('should have correct ARIA attributes', () => {
      render(<ComponentName />);
      const element = screen.getByRole('...');
      
      expect(element).toHaveAttribute('aria-label', '...');
    });
    
    it('should support keyboard navigation', async () => {
      render(<ComponentName />);
      
      await userEvent.tab();
      expect(screen.getByRole('...')).toHaveFocus();
    });
  });
  
  // 性能测试
  describe('Performance', () => {
    it('should not re-render when props are the same', () => {
      const { rerender } = render(<ComponentName value="test" />);
      const renderCount = jest.spyOn(console, 'log');
      
      rerender(<ComponentName value="test" />);
      
      expect(renderCount).not.toHaveBeenCalled();
    });
  });
});
```

### D. 文档模板

#### D.1 组件文档模板

```typescript
/**
 * ComponentName Component
 * 
 * @description 组件的详细描述，包括用途、功能特性等
 * 
 * @features
 * - 功能特性 1
 * - 功能特性 2
 * - 功能特性 3
 * 
 * @example
 * ```tsx
 * import { ComponentName } from '@shared/ui/components/ComponentName';
 * 
 * function MyComponent() {
 *   const [value, setValue] = useState('');
 *   
 *   return (
 *     <ComponentName
 *       value={value}
 *       onChange={setValue}
 *       placeholder="Enter value"
 *     />
 *   );
 * }
 * ```
 * 
 * @see 相关组件或文档的链接
 */
export const ComponentName: React.FC<ComponentNameProps> = (props) => {
  // 组件实现
};
```

### E. 工具和资源

#### E.1 推荐工具

- **代码分析**: ESLint, TypeScript Compiler
- **性能分析**: React DevTools, Chrome DevTools, Lighthouse
- **测试工具**: Jest, React Testing Library, Cypress
- **代码格式化**: Prettier
- **依赖管理**: npm, yarn

#### E.2 推荐资源

- [React 官方文档](https://react.dev/)
- [React Testing Library 文档](https://testing-library.com/docs/react-testing-library/intro/)
- [React 性能优化指南](https://react.dev/learn/render-and-commit)
- [Web 可访问性指南](https://www.w3.org/WAI/WCAG21/quickref/)

---

**文档结束**

**变更历史**:
- v1.0 (2026-03-21): 初始版本，完整的设计文档