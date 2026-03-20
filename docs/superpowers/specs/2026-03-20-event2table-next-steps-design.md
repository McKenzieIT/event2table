# Event2Table 下一步发展 - 设计文档

> **文档版本**: 1.0  
> **日期**: 2026-03-20  
> **状态**: 已批准  
> **执行模式**: 端到端自动化，中间不停止

---

## 1. 项目定位说明

### 1.1 核心定位

**Event2Table 是一个 HQL 生成辅助工具**，用于辅助基建数据分析师基于事件埋点快速生成 Hive 视图创建语句。

### 1.2 目标用户

- **基建数据分析师**：需要频繁编写 HQL 创建 DWD 层数据视图

### 1.3 核心价值

- **快速生成**：通过可视化配置，自动生成标准 HQL 语句
- **降低门槛**：无需手写复杂 SQL，通过拖拽和配置完成
- **提高效率**：批量处理、模板复用、历史管理

### 1.4 边界说明

**本工具不涉及**：
- ❌ HQL 语句执行（生成后由用户在各自平台执行）
- ❌ 任务调度系统（由外部调度平台负责）
- ❌ 用户权限管理（非多租户系统）
- ❌ 多数据源支持（专注 Hive/MaxCompute）

---

## 2. 当前状态总结

### 2.1 已完成功能概览

| 阶段 | 主要成果 | 完成度 |
|------|---------|--------|
| 阶段1-3 | 核心功能（游戏管理、事件管理、HQL生成、Canvas可视化） | 100% |
| 阶段4 | 功能补强（V2统一、模板引擎、性能优化、异步任务） | 100% |

### 2.2 功能模块实现度

| 模块 | 后端 | 前端 | 说明 |
|------|------|------|------|
| 游戏管理 | 100% | 100% | 完整CRUD + 批量操作 |
| 事件管理 | 100% | 100% | 完整CRUD + Excel导入 |
| 事件分类 | 100% | 100% | 多对多关系管理 |
| HQL生成器 | 100% | 95% | Single/Join/Union模式 |
| Canvas可视化 | 100% | 90% | ReactFlow拖拽式构建 |
| 模板系统 | 70% | 90% | 模板引擎+编辑器完成 |
| 批量操作 | 90% | 80% | 后端完整，前端UI已实现 |
| **异步任务** | **90%** | **0%** | **后端完整，前端待实现** |
| SQL优化器 | 60% | 80% | 建议展示UI已完成 |
| 缓存系统 | 100% | 60% | 三层缓存+监控 |

---

## 3. 功能模块依赖关系分析

### 3.1 依赖关系图

```
短期目标（P0）- 可并行执行
├── 异步任务前端UI ──依赖──> AsyncTaskService（✅已完成）
├── E2E测试验证 ──独立──> 无依赖
└── 文档同步 ──独立──> 无依赖

中期目标 - 部分可并行
├── 智能字段推荐 ──依赖──> 事件历史数据 + 统计服务
├── HQL版本对比 ──依赖──> HQL版本管理（需增强）
└── 模板库完善 ──依赖──> 模板系统（70%完成）

技术债务 - 需谨慎处理
├── 状态管理统一 ──影响──> 所有前端组件
├── 组件库标准化 ──影响──> 所有UI组件
├── 错误边界 ──影响──> 全局路由
└── API响应缓存 ──影响──> 所有API调用
```

### 3.2 关键发现

1. **并行机会多**：短期目标中3个任务均可独立并行执行
2. **技术债务风险**：状态管理统一和组件库标准化影响范围广，需隔离执行
3. **中期目标依赖**：智能字段推荐和HQL版本对比有后端依赖，需先增强后端能力

---

## 4. 技术架构

### 4.1 后端架构（四层架构）

```
API层（backend/api/routes/）
    ↓
Service层（backend/services/）
    ↓
Repository层（backend/models/repositories/）
    ↓
Entity层（backend/models/entities/）
```

### 4.2 前端架构（Feature-based）

```
frontend/src/
├── features/           # 功能模块
│   ├── async-tasks/    # 异步任务（待实现）
│   ├── games/          # 游戏管理
│   ├── events/         # 事件管理
│   ├── canvas/         # Canvas可视化
│   ├── parameters/     # 参数管理
│   ├── monitoring/     # 性能监控（待实现）
│   ├── field-recommendation/  # 字段推荐（待实现）
│   └── hql-comparison/ # HQL对比（待实现）
├── shared/             # 共享模块
│   ├── ui/             # UI组件库
│   ├── api/            # API客户端
│   ├── hooks/          # 自定义Hooks
│   └── utils/          # 工具函数
└── stores/             # Zustand状态管理
```

### 4.3 状态管理策略

- **客户端状态**：Zustand（游戏选择、UI状态、用户偏好）
- **服务端状态**：React Query（API数据、缓存、轮询）

---

## 5. 详细批次规划

### 5.1 第1周 - 短期目标（P0功能补齐）

#### 批次1：核心功能补齐（周一-周二，并行3个subagent）

**Subagent 1: 异步任务前端UI**

- **任务类型**: 前端feature开发
- **依赖**: AsyncTaskService（✅已完成）
- **文件范围**: `frontend/src/features/async-tasks/`
- **关键产出**:
  - `TaskList.tsx` - 任务列表组件
  - `TaskProgress.tsx` - 进度展示组件
  - `TaskDetail.tsx` - 任务详情组件
  - `useTaskPolling.ts` - 轮询hook
  - `taskApi.ts` - API客户端
- **验证标准**:
  - 可查看任务列表
  - 可查看任务进度（实时更新）
  - 可取消运行中的任务
  - 单元测试覆盖率 >80%

**Subagent 2: E2E测试验证**

- **任务类型**: 测试任务
- **依赖**: 无（独立任务）
- **测试范围**:
  - 游戏管理流程（创建、编辑、删除、批量操作）
  - 事件管理流程（创建、编辑、删除、Excel导入）
  - HQL生成流程（Single/Join/Union模式）
  - Canvas可视化流程（拖拽、连接、执行）
- **关键产出**:
  - `tests/e2e/game-management.spec.ts`
  - `tests/e2e/event-management.spec.ts`
  - `tests/e2e/hql-generation.spec.ts`
  - `tests/e2e/canvas-workflow.spec.ts`
- **验证标准**:
  - 所有E2E测试通过
  - 覆盖阶段4所有新功能
  - 测试报告无阻塞问题

**Subagent 3: 文档同步**

- **任务类型**: 文档更新
- **依赖**: 无（独立任务）
- **文档范围**:
  - API文档（新增/变更的API端点）
  - 用户手册（新功能使用说明）
  - 开发指南（架构变更、依赖更新）
- **关键产出**:
  - `docs/api/README.md`（更新）
  - `docs/user-guide/async-tasks.md`（新增）
  - `docs/development/architecture.md`（更新）
  - `CHANGELOG.md`（更新）
- **验证标准**:
  - API文档覆盖所有新增端点
  - 用户手册包含截图和示例
  - 文档无断开链接

#### 批次2：体验优化（周三-周四，并行3个subagent）

**Subagent 1: 批量操作完善**

- **任务类型**: 前端feature增强
- **依赖**: 无
- **文件范围**: `frontend/src/features/events/components/`
- **关键产出**:
  - `BatchEditModal.tsx` - 批量编辑组件
  - `BatchValidateModal.tsx` - 批量验证组件
  - `useBatchOperations.ts` - 批量操作hook
- **验证标准**:
  - 支持批量编辑事件属性
  - 支持批量验证事件配置
  - 操作结果清晰展示

**Subagent 2: 性能监控面板**

- **任务类型**: 新feature开发
- **依赖**: 后端缓存监控接口（✅已完成）
- **文件范围**: `frontend/src/features/monitoring/`
- **关键产出**:
  - `PerformanceDashboard.tsx` - 监控面板
  - `CacheStats.tsx` - 缓存统计组件
  - `ApiLatencyChart.tsx` - API延迟图表
  - `usePerformanceMetrics.ts` - 数据获取hook
- **验证标准**:
  - 实时展示缓存命中率
  - 展示API响应时间趋势
  - 支持刷新和历史查询

**Subagent 3: 错误处理优化**

- **任务类型**: 架构优化
- **依赖**: 无
- **文件范围**: `frontend/src/shared/`
- **关键产出**:
  - `errorHandler.ts` - 统一错误处理
  - `ErrorBoundary.tsx` - 错误边界组件
  - `useRetry.ts` - 重试hook
  - `ErrorToast.tsx` - 错误提示组件
- **验证标准**:
  - 所有API错误统一处理
  - 支持自动重试机制
  - 错误提示用户友好

#### 批次3：收尾与集成（周五，串行执行）

**集成测试与修复**

- **任务类型**: 集成测试
- **依赖**: 批次1、批次2完成
- **关键产出**:
  - 集成测试报告
  - Bug修复
  - 发布准备（版本号、CHANGELOG）
- **验证标准**:
  - 所有新功能集成测试通过
  - 无P0级Bug
  - 文档更新完成

---

### 5.2 第2周 - 中期目标（生成能力增强）

#### 批次4：智能字段推荐（周一-周二，串行执行）

**步骤1: 后端统计服务增强（周一上午）**

- **任务类型**: 后端service开发
- **文件范围**: `backend/services/field_statistics_service.py`
- **关键产出**:
  - `FieldStatisticsService` - 字段统计服务
  - 字段使用频率统计
  - 字段组合推荐算法
  - API端点: `/api/fields/recommend`
- **验证标准**:
  - API返回推荐字段列表
  - 推荐算法准确性 >70%
  - 单元测试覆盖

**步骤2: 前端字段推荐组件（周一下午-周二）**

- **任务类型**: 前端feature开发
- **依赖**: 步骤1完成
- **文件范围**: `frontend/src/features/field-recommendation/`
- **关键产出**:
  - `FieldRecommendation.tsx` - 推荐组件
  - `RecommendedFields.tsx` - 推荐字段列表
  - `useFieldRecommendation.ts` - 数据获取hook
- **验证标准**:
  - 自动展示推荐字段
  - 支持一键添加推荐字段
  - 推荐结果可视化

#### 批次5：HQL版本对比（周三-周四，串行执行）

**步骤1: 后端版本管理增强（周三上午）**

- **任务类型**: 后端service增强
- **文件范围**: `backend/services/hql_version_service.py`
- **关键产出**:
  - `HQLVersionService` - 版本管理服务
  - 版本对比算法
  - 差异高亮生成
  - API端点: `/api/hql/compare`
- **验证标准**:
  - API返回版本差异
  - 差异高亮准确
  - 性能 <500ms

**步骤2: 前端版本对比组件（周三下午-周四）**

- **任务类型**: 前端feature开发
- **依赖**: 步骤1完成
- **文件范围**: `frontend/src/features/hql-comparison/`
- **关键产出**:
  - `HQLComparison.tsx` - 对比组件
  - `DiffViewer.tsx` - 差异查看器
  - `VersionSelector.tsx` - 版本选择器
  - `useHQLComparison.ts` - 数据获取hook
- **验证标准**:
  - 可选择两个版本对比
  - 差异高亮展示
  - 支持导出对比结果

#### 批次6：模板库完善（周五，独立执行）

**模板库完善**

- **任务类型**: 内容完善 + 前端优化
- **依赖**: 模板系统（✅70%完成）
- **关键产出**:
  - 新增预置模板（10+业务场景）
  - 模板分类管理
  - 模板搜索功能
  - 模板使用统计
- **验证标准**:
  - 模板覆盖常见业务场景
  - 模板可搜索、可分类
  - 模板使用流程顺畅

---

### 5.3 第3-4周 - 技术债务清理

#### 批次7：状态管理统一（第3周，git worktree隔离）

**状态管理统一**

- **任务类型**: 架构重构
- **风险**: 高（影响所有前端组件）
- **隔离策略**: git worktree `feature/state-migration`
- **关键产出**:
  - 迁移所有useState到Zustand
  - 统一状态管理模式
  - 状态持久化策略
  - 状态调试工具
- **验证标准**:
  - 所有组件状态可追踪
  - 无useState残留
  - 所有测试通过

#### 批次8：组件库标准化 + API缓存 + 性能优化（第4周，并行3个subagent）

**Subagent 1: 组件库标准化**

- **任务类型**: 架构优化
- **文件范围**: `frontend/src/shared/ui/`
- **关键产出**:
  - 组件库文档
  - 组件Props标准化
  - 组件主题统一
  - 组件单元测试

**Subagent 2: API响应缓存完善**

- **任务类型**: 性能优化
- **文件范围**: `frontend/src/shared/api/`
- **关键产出**:
  - 完善缓存策略
  - 缓存失效机制
  - 缓存命中率优化
  - 缓存监控集成

**Subagent 3: 性能优化**

- **任务类型**: 性能优化
- **文件范围**: `frontend/`
- **关键产出**:
  - 代码分割
  - 懒加载优化
  - 包大小优化
  - 首屏加载优化

---

## 6. Subagent执行流程

每个subagent任务遵循以下流程（符合subagent-driven-development规范）：

```
1. 派遣实施subagent
   ↓
2. Subagent提问？ → 回答问题 → 重新派遣
   ↓ 否
3. Subagent实施、测试、提交、自审
   ↓
4. 派遣规范审查subagent
   ↓
5. 规范合规？ → 否 → Subagent修复 → 重新审查
   ↓ 是
6. 派遣代码质量审查subagent
   ↓
7. 代码质量通过？ → 否 → Subagent修复 → 重新审查
   ↓ 是
8. 标记任务完成，进入下一任务
```

---

## 7. 里程碑节点与验证标准

| 里程碑 | 时间 | 交付物 | 验证标准 |
|--------|------|--------|---------|
| **M1: 短期目标完成** | 第1周五 | 异步任务UI + E2E测试 + 文档 | 所有P0功能可用，E2E测试通过 |
| **M2: 中期目标完成** | 第2周五 | 智能推荐 + 版本对比 + 模板库 | 核心能力增强，用户体验提升 |
| **M3: 技术债务清理完成** | 第4周五 | 状态统一 + 组件标准化 + 性能优化 | 代码质量提升，性能达标 |

---

## 8. 风险评估与缓解措施

| 风险 | 影响批次 | 缓解措施 |
|------|---------|---------|
| 并行任务合并冲突 | 批次1、2、8 | 使用feature分支，及时rebase主分支 |
| 状态管理重构影响功能 | 批次7 | git worktree隔离，充分测试后再合并 |
| 后端依赖延迟 | 批次4、5 | 前端mock数据先行，后端就绪后集成 |
| 性能优化引入Bug | 批次8 | 性能基准测试，灰度发布 |

---

## 9. 成功指标

### 9.1 功能指标

- ✅ 所有P0功能100%完成
- ✅ E2E测试覆盖率 >80%
- ✅ 零P0级Bug

### 9.2 性能指标

- ✅ 首屏加载时间 <1s（当前~2s）
- ✅ HQL生成时间 <200ms（当前~500ms）
- ✅ 缓存命中率 >95%（当前85%）
- ✅ 前端包大小 <1MB（当前~2MB）

### 9.3 代码质量指标

- ✅ 单元测试覆盖率 >85%（当前75%）
- ✅ Linter警告数 0（当前12）
- ✅ 代码重复率 <5%（当前8%）

---

## 10. 附录

### 10.1 关键文件路径

**后端**:
- `backend/services/async_tasks/async_task_service.py` - 异步任务服务
- `backend/services/field_statistics_service.py` - 字段统计服务（待创建）
- `backend/services/hql_version_service.py` - HQL版本服务（待创建）

**前端**:
- `frontend/src/features/async-tasks/` - 异步任务feature（待创建）
- `frontend/src/features/monitoring/` - 性能监控feature（待创建）
- `frontend/src/features/field-recommendation/` - 字段推荐feature（待创建）
- `frontend/src/features/hql-comparison/` - HQL对比feature（待创建）

### 10.2 技术栈

**后端**:
- Python 3.11+
- FastAPI
- SQLite（开发）/ PostgreSQL（生产）
- Redis（缓存）

**前端**:
- React 18.3.1
- TypeScript 5.9.3
- Vite 7.3.1
- TanStack React Query 5.17.0
- Zustand（状态管理）
- ReactFlow 11.10.4（Canvas）
- CodeMirror 6.x（代码编辑器）

**测试**:
- Vitest（单元测试）
- Playwright（E2E测试）

---

**文档版本**: 1.0  
**最后更新**: 2026-03-20  
**维护者**: Event2Table Development Team
