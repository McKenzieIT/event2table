# Event2Table E2E测试计划 - 迭代6

**测试时间**: 2026-02-18 (迭代6)
**测试环境**:
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:5001
- 测试游戏 GID: 10000147 (STAR001)

**测试工具**: Chrome DevTools MCP + Playwright (新增)

---

## 迭代6目标

基于前5次迭代的成果，迭代6专注于：

1. **测试剩余需上下文页面** (7个)
   - 完成所有8个需游戏上下文页面的验证
   - 创建E2E测试覆盖

2. **实施E2E自动化测试（Phase 1）**
   - 创建Playwright测试文件
   - 实施关键流程测试
   - 验证自动化测试可运行

3. **优化Bundle大小**
   - 分析当前bundle组成
   - 实施代码分割策略
   - 验证性能改进

4. **验证已实施的改进**
   - 测试Pre-commit Hook
   - 测试Error Boundary
   - 确认所有改进正常工作

---

## 待测试/任务清单

### 剩余需上下文页面 (7个)

1. **Parameter History** - `#/parameter-history?game_gid=10000147`
2. **Parameter Network** - `#/parameter-network?game_gid=10000147`
3. **Parameter Compare** - `#/parameters/compare?game_gid=10000147`
4. **Parameters Enhanced** - `#/parameters/enhanced?game_gid=10000147`
5. **Logs Create** - `#/logs/create?game_gid=10000147`
6. **Flow Builder** - `#/flow-builder?game_gid=10000147`
7. **HQL Results** - `#/hql-results?game_gid=10000147`

### E2E自动化测试文件

**优先级 P0 - 关键流程**:
1. `canvas-workflow.spec.ts` - Canvas HQL生成流程
2. `game-management.spec.ts` - 游戏管理CRUD
3. `event-management.spec.ts` - 事件管理CRUD

**优先级 P1 - 重要功能**:
4. `parameter-pages.spec.ts` - 参数页面测试
5. `loading-timeouts.spec.ts` - 加载超时回归测试

### Bundle优化任务

1. 分析当前bundle组成
2. 识别可优化的模块
3. 实施manual chunks
4. 验证性能改进

---

## 测试策略

### 策略A: 快速覆盖优先（推荐）

1. **快速扫描剩余7个页面** (30分钟)
   - 使用Chrome DevTools MCP
   - 截图并记录状态
   - 识别有问题的页面

2. **创建1-2个E2E自动化测试** (1小时)
   - 选择最关键流程（Canvas或游戏管理）
   - 创建Playwright测试文件
   - 验证可运行

3. **Bundle分析** (30分钟)
   - 运行构建分析
   - 识别大模块
   - 制定优化方案

### 策略B: 深度优化优先

1. **完整测试剩余7个页面**
2. **创建完整的E2E测试套件**
3. **实施完整的Bundle优化**

### 策略C: 混合策略（平衡进度）

1. 快速测试剩余页面（策略A第1步）
2. 创建1个E2E测试示例（策略A第2步）
3. Bundle分析和初步优化（策略A第3步）

---

## 成功标准

- ✅ 所有7个剩余页面测试完成
- ✅ 至少1个E2E自动化测试可运行
- ✅ Bundle分析完成
- ✅ Pre-commit Hook验证
- ✅ Error Boundary验证

---

## 测试开始时间

- 2026-02-18 迭代6开始

---

*此文档将在测试过程中持续更新*
