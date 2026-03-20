# Event2Table 下一步发展 - 实施计划

> **文档版本**: 1.0  
> **日期**: 2026-03-20  
> **基于设计文档**: docs/superpowers/specs/2026-03-20-event2table-next-steps-design.md  
> **执行模式**: 端到端自动化，中间不停止

---

## 1. 执行概览

### 1.1 执行策略

- **执行模式**: subagent-driven-development
- **并行策略**: 每批次最多3个subagent并行
- **审查流程**: 每个任务完成后进行规范审查 + 代码质量审查
- **隔离策略**: 技术债务使用git worktree隔离

### 1.2 时间规划

- 第1周：短期目标（P0功能补齐）
- 第2周：中期目标（生成能力增强）
- 第3-4周：技术债务清理

---

## 2. 任务清单

### 批次1: 异步任务UI + E2E测试 + 文档同步（并行）

#### 任务1.1: 异步任务前端UI

**任务类型**: 前端feature开发

**依赖**: AsyncTaskService（✅已完成）

**文件范围**: `frontend/src/features/async-tasks/`

**详细步骤**:

1. **创建API客户端** (`frontend/src/features/async-tasks/api/taskApi.ts`)
   ```typescript
   // API方法:
   // - getTasks(filters?) - 获取任务列表
   // - getTask(taskId) - 获取单个任务
   // - cancelTask(taskId) - 取消任务
   // - getTaskStatistics() - 获取任务统计
   ```

2. **创建React Query hooks** (`frontend/src/features/async-tasks/hooks/useTasks.ts`)
   ```typescript
   // Hooks:
   // - useTasks(filters) - 任务列表查询
   // - useTask(taskId) - 单个任务查询
   // - useCancelTask() - 取消任务mutation
   // - useTaskPolling(taskId, interval) - 任务轮询
   ```

3. **创建组件** (`frontend/src/features/async-tasks/components/`)
   - `TaskList.tsx` - 任务列表组件（展示任务卡片）
   - `TaskProgress.tsx` - 进度展示组件（进度条 + 状态）
   - `TaskDetail.tsx` - 任务详情组件（完整信息展示）
   - `TaskFilters.tsx` - 任务过滤组件（状态、类型筛选）

4. **创建页面** (`frontend/src/features/async-tasks/pages/TaskManagementPage.tsx`)
   - 集成所有组件
   - 添加路由配置

5. **编写单元测试** (`frontend/src/features/async-tasks/__tests__/`)
   - API客户端测试
   - Hooks测试
   - 组件测试

**验证标准**:
- [ ] 可查看任务列表（分页、过滤）
- [ ] 可查看任务进度（实时更新，轮询间隔3秒）
- [ ] 可取消运行中的任务
- [ ] 单元测试覆盖率 >80%

**提交信息**: `feat(async-tasks): implement async task management UI`

---

#### 任务1.2: E2E测试验证

**任务类型**: 测试任务

**依赖**: 无

**测试范围**:
- 游戏管理流程
- 事件管理流程
- HQL生成流程
- Canvas可视化流程

**详细步骤**:

1. **创建测试文件** (`frontend/tests/e2e/`)
   - `game-management.spec.ts` - 游戏管理测试
   - `event-management.spec.ts` - 事件管理测试
   - `hql-generation.spec.ts` - HQL生成测试
   - `canvas-workflow.spec.ts` - Canvas流程测试

2. **编写测试用例**
   ```typescript
   // game-management.spec.ts
   test('创建游戏', async () => { ... });
   test('编辑游戏', async () => { ... });
   test('删除游戏', async () => { ... });
   test('批量操作', async () => { ... });
   
   // event-management.spec.ts
   test('创建事件', async () => { ... });
   test('Excel导入', async () => { ... });
   test('批量编辑', async () => { ... });
   
   // hql-generation.spec.ts
   test('Single模式生成', async () => { ... });
   test('Join模式生成', async () => { ... });
   test('Union模式生成', async () => { ... });
   
   // canvas-workflow.spec.ts
   test('拖拽节点', async () => { ... });
   test('连接节点', async () => { ... });
   test('执行生成', async () => { ... });
   ```

3. **运行测试并生成报告**
   ```bash
   npm run test:e2e
   ```

**验证标准**:
- [ ] 所有E2E测试通过
- [ ] 覆盖阶段4所有新功能
- [ ] 测试报告无阻塞问题

**提交信息**: `test(e2e): add comprehensive e2e tests for phase 4 features`

---

#### 任务1.3: 文档同步

**任务类型**: 文档更新

**依赖**: 无

**文档范围**:
- API文档
- 用户手册
- 开发指南

**详细步骤**:

1. **更新API文档** (`docs/api/README.md`)
   - 添加异步任务API端点文档
   - 更新请求/响应示例

2. **创建用户手册** (`docs/user-guide/async-tasks.md`)
   - 异步任务功能说明
   - 使用截图
   - 常见问题

3. **更新架构文档** (`docs/development/architecture.md`)
   - 添加异步任务模块说明
   - 更新前端架构图

4. **更新CHANGELOG** (`CHANGELOG.md`)
   - 添加版本更新记录

**验证标准**:
- [ ] API文档覆盖所有新增端点
- [ ] 用户手册包含截图和示例
- [ ] 文档无断开链接

**提交信息**: `docs: update documentation for async tasks feature`

---

### 批次2: 批量操作完善 + 性能监控面板 + 错误处理优化（并行）

#### 任务2.1: 批量操作完善

**任务类型**: 前端feature增强

**依赖**: 无

**文件范围**: `frontend/src/features/events/components/`

**详细步骤**:

1. **创建批量编辑组件** (`BatchEditModal.tsx`)
   ```typescript
   // 功能:
   // - 选择多个事件
   // - 批量编辑属性（事件名称、分类等）
   // - 预览变更
   // - 确认提交
   ```

2. **创建批量验证组件** (`BatchValidateModal.tsx`)
   ```typescript
   // 功能:
   // - 验证事件配置完整性
   // - 展示验证结果
   // - 提供修复建议
   ```

3. **创建批量操作hook** (`useBatchOperations.ts`)
   ```typescript
   // Hooks:
   // - useBatchEdit() - 批量编辑
   // - useBatchValidate() - 批量验证
   // - useBatchDelete() - 批量删除
   ```

**验证标准**:
- [ ] 支持批量编辑事件属性
- [ ] 支持批量验证事件配置
- [ ] 操作结果清晰展示

**提交信息**: `feat(events): add batch edit and validate features`

---

#### 任务2.2: 性能监控面板

**任务类型**: 新feature开发

**依赖**: 后端缓存监控接口（✅已完成）

**文件范围**: `frontend/src/features/monitoring/`

**详细步骤**:

1. **创建API客户端** (`frontend/src/features/monitoring/api/monitoringApi.ts`)
   ```typescript
   // API方法:
   // - getCacheStats() - 获取缓存统计
   // - getApiLatency() - 获取API延迟
   // - getPerformanceMetrics() - 获取性能指标
   ```

2. **创建组件** (`frontend/src/features/monitoring/components/`)
   - `PerformanceDashboard.tsx` - 监控面板主组件
   - `CacheStats.tsx` - 缓存统计组件
   - `ApiLatencyChart.tsx` - API延迟图表
   - `MetricCard.tsx` - 指标卡片组件

3. **创建页面** (`frontend/src/features/monitoring/pages/PerformancePage.tsx`)
   - 集成所有组件
   - 添加刷新功能

**验证标准**:
- [ ] 实时展示缓存命中率
- [ ] 展示API响应时间趋势
- [ ] 支持刷新和历史查询

**提交信息**: `feat(monitoring): add performance monitoring dashboard`

---

#### 任务2.3: 错误处理优化

**任务类型**: 架构优化

**依赖**: 无

**文件范围**: `frontend/src/shared/`

**详细步骤**:

1. **创建统一错误处理** (`frontend/src/shared/utils/errorHandler.ts`)
   ```typescript
   // 功能:
   // - 统一错误分类
   // - 错误消息格式化
   // - 错误上报
   ```

2. **创建错误边界组件** (`frontend/src/shared/components/ErrorBoundary.tsx`)
   ```typescript
   // 功能:
   // - 捕获React渲染错误
   // - 展示友好的错误页面
   // - 提供重试功能
   ```

3. **创建重试hook** (`frontend/src/shared/hooks/useRetry.ts`)
   ```typescript
   // 功能:
   // - 自动重试机制
   // - 指数退避策略
   // - 最大重试次数配置
   ```

4. **创建错误提示组件** (`frontend/src/shared/ui/ErrorToast/ErrorToast.tsx`)
   ```typescript
   // 功能:
   // - 统一错误提示样式
   // - 支持不同错误级别
   // - 自动消失
   ```

**验证标准**:
- [ ] 所有API错误统一处理
- [ ] 支持自动重试机制
- [ ] 错误提示用户友好

**提交信息**: `feat(error-handling): add unified error handling and retry mechanism`

---

### 批次3: 集成测试与修复

**任务类型**: 集成测试

**依赖**: 批次1、批次2完成

**详细步骤**:

1. **运行集成测试**
   ```bash
   npm run test
   npm run test:e2e
   npm run build
   ```

2. **修复发现的问题**
   - Bug修复
   - 性能优化

3. **准备发布**
   - 更新版本号
   - 更新CHANGELOG
   - 创建发布标签

**验证标准**:
- [ ] 所有新功能集成测试通过
- [ ] 无P0级Bug
- [ ] 文档更新完成

**提交信息**: `chore: prepare release v2.1.0`

---

### 批次4: 智能字段推荐（后端+前端串行）

#### 任务4.1: 后端统计服务增强

**任务类型**: 后端service开发

**文件范围**: `backend/services/field_statistics_service.py`

**详细步骤**:

1. **创建字段统计服务**
   ```python
   class FieldStatisticsService:
       def get_field_usage_stats(self, game_gid: int) -> Dict
       def get_recommended_fields(self, game_gid: int, event_name: str) -> List[Dict]
       def get_field_combinations(self, game_gid: int) -> List[Dict]
   ```

2. **创建API端点**
   ```python
   @router.get("/api/fields/recommend")
   async def get_recommended_fields(game_gid: int, event_name: str):
       ...
   ```

3. **编写单元测试**
   ```python
   # tests/services/test_field_statistics_service.py
   ```

**验证标准**:
- [ ] API返回推荐字段列表
- [ ] 推荐算法准确性 >70%
- [ ] 单元测试覆盖

**提交信息**: `feat(backend): add field statistics and recommendation service`

---

#### 任务4.2: 前端字段推荐组件

**任务类型**: 前端feature开发

**依赖**: 任务4.1完成

**文件范围**: `frontend/src/features/field-recommendation/`

**详细步骤**:

1. **创建API客户端** (`frontend/src/features/field-recommendation/api/fieldRecommendationApi.ts`)

2. **创建组件** (`frontend/src/features/field-recommendation/components/`)
   - `FieldRecommendation.tsx` - 推荐组件
   - `RecommendedFields.tsx` - 推荐字段列表

3. **创建hook** (`frontend/src/features/field-recommendation/hooks/useFieldRecommendation.ts`)

**验证标准**:
- [ ] 自动展示推荐字段
- [ ] 支持一键添加推荐字段
- [ ] 推荐结果可视化

**提交信息**: `feat(frontend): add field recommendation UI`

---

### 批次5: HQL版本对比（后端+前端串行）

#### 任务5.1: 后端版本管理增强

**任务类型**: 后端service增强

**文件范围**: `backend/services/hql_version_service.py`

**详细步骤**:

1. **创建版本对比服务**
   ```python
   class HQLVersionService:
       def compare_versions(self, version_id_1: int, version_id_2: int) -> Dict
       def get_version_history(self, hql_id: int) -> List[Dict]
       def generate_diff(self, hql_1: str, hql_2: str) -> Dict
   ```

2. **创建API端点**
   ```python
   @router.get("/api/hql/compare")
   async def compare_hql_versions(version_id_1: int, version_id_2: int):
       ...
   ```

**验证标准**:
- [ ] API返回版本差异
- [ ] 差异高亮准确
- [ ] 性能 <500ms

**提交信息**: `feat(backend): add HQL version comparison service`

---

#### 任务5.2: 前端版本对比组件

**任务类型**: 前端feature开发

**依赖**: 任务5.1完成

**文件范围**: `frontend/src/features/hql-comparison/`

**详细步骤**:

1. **创建组件** (`frontend/src/features/hql-comparison/components/`)
   - `HQLComparison.tsx` - 对比组件
   - `DiffViewer.tsx` - 差异查看器
   - `VersionSelector.tsx` - 版本选择器

2. **创建hook** (`frontend/src/features/hql-comparison/hooks/useHQLComparison.ts`)

**验证标准**:
- [ ] 可选择两个版本对比
- [ ] 差异高亮展示
- [ ] 支持导出对比结果

**提交信息**: `feat(frontend): add HQL version comparison UI`

---

### 批次6: 模板库完善

**任务类型**: 内容完善 + 前端优化

**依赖**: 模板系统（✅70%完成）

**详细步骤**:

1. **新增预置模板**
   - 电商埋点模板
   - 游戏埋点模板
   - 支付埋点模板
   - 用户行为模板

2. **完善模板管理**
   - 模板分类功能
   - 模板搜索功能
   - 模板使用统计

**验证标准**:
- [ ] 模板覆盖常见业务场景
- [ ] 模板可搜索、可分类
- [ ] 模板使用流程顺畅

**提交信息**: `feat(templates): expand template library with business scenarios`

---

### 批次7: 状态管理统一（git worktree隔离）

**任务类型**: 架构重构

**风险**: 高（影响所有前端组件）

**隔离策略**: git worktree `feature/state-migration`

**详细步骤**:

1. **创建git worktree**
   ```bash
   git worktree add ../event2table-state-migration -b feature/state-migration
   ```

2. **迁移useState到Zustand**
   - 识别所有useState使用
   - 创建对应的Zustand store
   - 迁移组件状态

3. **测试验证**
   ```bash
   npm run test
   npm run test:e2e
   ```

4. **合并回主分支**
   ```bash
   git checkout main
   git merge feature/state-migration
   ```

**验证标准**:
- [ ] 所有组件状态可追踪
- [ ] 无useState残留
- [ ] 所有测试通过

**提交信息**: `refactor(state): migrate all useState to Zustand`

---

### 批次8: 组件库标准化 + API缓存 + 性能优化（并行）

#### 任务8.1: 组件库标准化

**任务类型**: 架构优化

**文件范围**: `frontend/src/shared/ui/`

**详细步骤**:

1. **创建组件库文档** (`frontend/src/shared/ui/README.md`)
   - 组件使用说明
   - Props定义
   - 示例代码

2. **标准化组件Props**
   - 统一命名规范
   - 添加TypeScript类型

3. **统一组件主题**
   - 颜色变量
   - 间距变量
   - 字体变量

**提交信息**: `refactor(ui): standardize component library`

---

#### 任务8.2: API响应缓存完善

**任务类型**: 性能优化

**文件范围**: `frontend/src/shared/api/`

**详细步骤**:

1. **完善缓存策略**
   - 定义缓存键规则
   - 设置缓存过期时间

2. **实现缓存失效机制**
   - 手动失效
   - 自动失效

3. **集成缓存监控**
   - 缓存命中率统计
   - 缓存大小监控

**提交信息**: `perf(api): improve API response caching`

---

#### 任务8.3: 性能优化

**任务类型**: 性能优化

**文件范围**: `frontend/`

**详细步骤**:

1. **代码分割**
   ```typescript
   // 使用React.lazy进行路由级代码分割
   const AsyncTasksPage = React.lazy(() => import('./features/async-tasks/pages/TaskManagementPage'));
   ```

2. **懒加载优化**
   - 图片懒加载
   - 组件懒加载

3. **包大小优化**
   - Tree shaking
   - 压缩优化

4. **首屏加载优化**
   - 关键CSS内联
   - 预加载关键资源

**验证标准**:
- [ ] 首屏加载时间 <1s
- [ ] 前端包大小 <1MB

**提交信息**: `perf: optimize bundle size and loading performance`

---

## 3. 执行流程

每个任务遵循以下流程：

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

## 4. 验证清单

### 4.1 功能验证

- [ ] 所有P0功能100%完成
- [ ] E2E测试覆盖率 >80%
- [ ] 零P0级Bug

### 4.2 性能验证

- [ ] 首屏加载时间 <1s
- [ ] HQL生成时间 <200ms
- [ ] 缓存命中率 >95%
- [ ] 前端包大小 <1MB

### 4.3 代码质量验证

- [ ] 单元测试覆盖率 >85%
- [ ] Linter警告数 0
- [ ] 代码重复率 <5%

---

## 5. 风险缓解

| 风险 | 缓解措施 |
|------|---------|
| 并行任务合并冲突 | 使用feature分支，及时rebase主分支 |
| 状态管理重构影响功能 | git worktree隔离，充分测试后再合并 |
| 后端依赖延迟 | 前端mock数据先行，后端就绪后集成 |
| 性能优化引入Bug | 性能基准测试，灰度发布 |

---

**文档版本**: 1.0  
**最后更新**: 2026-03-20  
**维护者**: Event2Table Development Team
