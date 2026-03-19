## Event2Table 项目完善方案（深度分析版）

**日期**: 2025-07  
**版本**: v2.0（基于代码库深度调研的修订版）  
**状态**: 已完成首轮重构，以下为经过多轮反思迭代后的完整优化路线图

---

## 〇、四个优化方向的依赖关系分析

### 依赖金字塔

四个优化方向并非独立存在，它们形成了一个**自底向上的依赖金字塔**：

```
                    ┌─────────────────────────┐
            层4     │   功能完整性补强          │  ← 最终目标：在稳定架构上开发新功能
                    └────────────┬────────────┘
                                 │ 依赖：需要清晰的架构才能高效开发
                    ┌────────────▼────────────┐
            层3     │   架构优化方案            │  ← 为新功能提供清晰的代码组织
                    └────────────┬────────────┘
                                 │ 依赖：需要代码质量达标才能安全重构
                    ┌────────────▼────────────┐
            层2     │   代码质量改进策略        │  ← 确保重构过程中的类型安全和规范一致
                    └────────────┬────────────┘
                                 │ 依赖：需要先消除冲突才能改进质量
                    ┌────────────▼────────────┐
            层1     │   技术债务清理路径        │  ← 一切的基础：消除冲突、重复和歧义
                    └─────────────────────────┘
```

### 关键依赖链

| 依赖关系 | 具体说明 | 影响评估 |
|----------|----------|----------|
| **技术债务 → 代码质量** | `utils.py`/`utils/` 冲突不解决，无法安全地为 utils 模块添加类型注解 | 🔴 阻塞 |
| **技术债务 → 架构优化** | Entity 重复不消除，Blueprint 迁移时会引入更多混乱 | 🔴 阻塞 |
| **代码质量 → 架构优化** | GraphQL 操作不统一，前端目录重组时无法确定规范路径 | 🟡 部分阻塞 |
| **架构优化 → 功能补强** | Blueprint 路由分散在 services/ 中，新功能不知道路由该放哪里 | 🟡 部分阻塞 |
| **代码质量 → 功能补强** | 181 个 @ts-nocheck 文件，新功能开发缺乏类型安全保障 | 🟡 影响效率 |

### 并行执行可行性矩阵

```
                    后端技术债务  前端技术债务  后端架构优化  前端架构优化  功能补强
后端技术债务          -           ✅ 可并行     🔴 串行      ✅ 可并行     🔴 串行
前端技术债务         ✅ 可并行      -           ✅ 可并行     🟡 部分串行   🔴 串行
后端架构优化         🔴 串行       ✅ 可并行      -           ✅ 可并行     🔴 串行
前端架构优化         ✅ 可并行     🟡 部分串行   ✅ 可并行      -           🔴 串行
功能补强             🔴 串行       🔴 串行      🔴 串行       🔴 串行       -
```

**核心结论**：后端和前端的改进工作在大部分场景下可以**并行执行**，但功能补强必须等待前三层完成。

---

## 一、已完成的重构（首轮）

| 编号 | 改进项 | 变更说明 |
|------|--------|----------|
| 1 | 清理废弃文件 | 删除 15 个 `.bak/.backup` 文件 + 3 个废弃 API 文件（`legacy_api.py`、`join_configs_old_backup.py`、前端 `.archive/.example` 文件） |
| 2 | 统一错误处理 | 合并 `backend/core/errors.py` 和 `exceptions.py` 为单一模块，新增 `NotFoundError`、`DuplicateError`、`FileProcessingError`、`ConfigurationError` |
| 3 | 重构 `web_app.py` | 移除 5 个冗余测试路由；删除重复缓存预热；清理注释代码；统一导入；提取 `API_ROUTE_PREFIXES` 常量；简化 `add_cache_headers` |
| 4 | 修复前端 GraphQL 语法错误 | 修复 `queries.ts` 中孤立的模板字符串闭合和重复的 flow 查询片段 |
| 5 | 统一 useDebounce Hook | `hooks/useDebounce.ts` 改为重导出 `@shared/hooks/useDebounce`，消除重复实现 |

---

## 二、技术债务清理路径（层1 — 一切的基础）

### 2.1 总览

技术债务清理是所有后续工作的前提。当前项目存在三类核心技术债务：

| 类别 | 具体问题 | 影响范围 | 优先级 |
|------|----------|----------|--------|
| **文件/目录冲突** | `utils.py` 与 `utils/` 共存；`security.py` 与 `security/` 共存 | 后端所有模块的导入 | 🔴 P0 |
| **实体定义重复** | `entities.py` 与 `entities_game/event/category.py` 中 3 个 Entity 完全重复 | 数据模型层 | 🔴 P0 |
| **废弃 Blueprint 残留** | `flows_bp`、`games_bp`、`events_bp` 已废弃但文件仍存在 | 后端路由层 | 🟡 P1 |

### 2.2 任务 TD-1：解决 utils.py/utils/ 文件冲突

**现状分析**：
- `backend/core/utils.py`（旧版单文件）：包含数据库操作（`fetch_all_as_dict`、`execute_write`）、响应格式化（`success_response`、`error_response`）、请求验证（`validate_json_request`）、安全函数（`sanitize_html`）、自定义异常（`HQLGenerationError` 等）
- `backend/core/utils/`（新版模块化）：子模块包括 `validators/`、`formatters/`、`converters/`、`sanitizers/`、`error_messages/`
- `utils/__init__.py` 通过 `importlib` 动态导入 `utils.py` 中的遗留函数保持兼容

**实施步骤**：
1. 扫描所有 `from backend.core.utils import ...` 的导入语句，建立完整的引用图
2. 将 `utils.py` 中的函数按职责分类迁移到 `utils/` 对应子模块：
   - 数据库操作 → `utils/database.py`（新建）
   - 响应格式化 → `utils/formatters/response.py`
   - 请求验证 → `utils/validators/request.py`
   - 安全函数 → 迁移到 `backend/core/security/sanitizers.py`
   - 自定义异常 → 迁移到 `backend/core/errors.py`
3. 更新 `utils/__init__.py` 从子模块重导出所有公共 API（保持向后兼容）
4. 删除 `utils.py` 单文件
5. 全局搜索并更新所有导入语句

**验证标准**：
- `python -c "from backend.core.utils import fetch_all_as_dict, success_response"` 正常执行
- `pytest` 全部通过
- `utils.py` 文件不再存在

**预估工时**：1 个 sub agent session

---

### 2.3 任务 TD-2：解决 security.py/security/ 文件冲突

**现状分析**：
- `backend/core/security.py`（旧版）：CSRF 保护（`generate_csrf_token`、`csrf_protect`）、速率限制（`rate_limit`）、安全头（`add_security_headers`）、文件名清理（`sanitize_filename`）
- `backend/core/security/`（新版）：`sql_validator.py`（SQL 注入防护）、`authentication.py`（认证）、`cache_key_validator.py`、`path_validator.py`、`sensitive_data_filter.py`

**实施步骤**：
1. 扫描所有 `from backend.core.security import ...` 的导入语句
2. 将 `security.py` 中的函数迁移到 `security/` 对应子模块：
   - CSRF → `security/csrf.py`（新建）
   - 速率限制 → `security/rate_limiter.py`（新建）
   - 安全头 → `security/headers.py`（新建）
   - 文件名清理 → `security/sanitizers.py`（新建）
3. 更新 `security/__init__.py` 重导出所有公共 API
4. 删除 `security.py` 单文件
5. 更新所有导入语句

**验证标准**：
- `python -c "from backend.core.security import generate_csrf_token, rate_limit"` 正常执行
- `pytest` 全部通过

**预估工时**：1 个 sub agent session

**⚡ 并行说明**：TD-1 和 TD-2 操作不同目录，**可完全并行执行**。

---

### 2.4 任务 TD-3：合并重复的 Entity 定义

**现状分析**：
- `entities.py` 中定义了 `GameEntity`、`EventEntity`、`EventCategoryEntity`（完整版，含测试环境兼容的验证器）
- `entities_game.py`、`entities_event.py`、`entities_category.py` 中有完全重复的定义（但 `entities_game.py` 的 `ods_db` 验证器更严格，仅允许 `ieu_ods` 或 `overseas_ods`）

**策略选择**（经反思迭代后的决策）：

保留 `entities.py` 作为**单一真相来源（Single Source of Truth）**，原因：
1. `entities.py` 的验证器支持测试环境，更灵活
2. 拆分文件的验证器过于严格，会导致测试失败
3. 保留单文件更简单，避免跨文件同步问题

**实施步骤**：
1. 确认 `entities.py` 中的 3 个 Entity 定义是最完整的版本
2. 扫描所有 `from backend.models.entities_game import ...` 等导入
3. 将 `entities_game.py`、`entities_event.py`、`entities_category.py` 改为从 `entities.py` 重导出
4. 逐步更新外部导入指向 `entities.py`
5. 最终删除拆分文件（在所有导入更新完成后）

**验证标准**：
- 所有 Entity 导入指向 `entities.py`
- `pytest` 全部通过

**预估工时**：1 个 sub agent session

**⚡ 并行说明**：TD-3 操作 `models/` 目录，与 TD-1（`core/utils`）和 TD-2（`core/security`）**可完全并行**。

---

### 2.5 任务 TD-4：清理废弃 Blueprint 残留

**现状分析**：
- `backend/services/flows/routes.py` 中的 `flows_bp` 已标记废弃，`backend/api/routes/flows.py` 已替代
- `backend/services/games/games.py` 中的 `games_bp` 已标记废弃，`backend/api/routes/games.py` 已替代
- `backend/services/events/events.py` 中的 `events_bp` 已标记废弃，`backend/api/routes/events.py` 已替代

**实施步骤**：
1. 确认废弃 Blueprint 未在 `web_app.py` 中注册
2. 确认 `api/routes/` 中的替代路由功能完整
3. 删除废弃的路由文件（保留 Service 层逻辑）
4. 更新相关 `__init__.py` 的导出

**验证标准**：
- 废弃的 Blueprint 文件已删除
- `web_app.py` 中无废弃 Blueprint 的引用
- `pytest` 全部通过

**预估工时**：0.5 个 sub agent session

**⚡ 并行说明**：TD-4 与 TD-1/TD-2/TD-3 **可完全并行**。

---

## 三、代码质量改进策略（层2 — 架构重构的前提）

### 3.1 总览

代码质量改进分为后端和前端两条独立的工作流，**可完全并行执行**。

| 类别 | 具体问题 | 影响范围 | 优先级 |
|------|----------|----------|--------|
| **GraphQL 操作重复** | `queries.ts` 和 `operations.ts` 有 16 个完全重复的查询定义 | 前端所有 GraphQL 消费者 | 🔴 P0 |
| **GraphQL 命名不一致** | `queries.ts` 用 camelCase，`operations.ts` 用 snake_case | 前端数据层 | 🔴 P0 |
| **TypeScript 类型安全** | **181 个文件**使用 `@ts-nocheck`（远超之前估计的 19+） | 前端全局 | 🟡 P1 |
| **代码规范不统一** | 后端异常导入源不一致、前端 Hook 路径不统一 | 全局 | 🟡 P1 |

### 3.2 任务 CQ-1：统一 GraphQL 操作定义

**现状分析**（基于深度调研的修正数据）：

**完全重复的 16 个查询**（同时存在于 `queries.ts` 和 `operations.ts`）：
- 游戏：`GET_GAMES`、`GET_GAME`、`SEARCH_GAMES`
- 事件：`GET_EVENTS`、`GET_EVENT`、`SEARCH_EVENTS`
- 分类：`GET_CATEGORIES`、`GET_CATEGORY`、`SEARCH_CATEGORIES`
- 参数：`GET_PARAMETERS`、`GET_PARAMETER`
- 统计：`GET_DASHBOARD_STATS`、`GET_GAME_STATS`、`GET_ALL_GAME_STATS`
- 流程：`GET_FLOWS`、`GET_FLOW`

**仅在 `queries.ts` 中的查询**（9 个）：
- `SEARCH_PARAMETERS`、`GET_EVENT_FIELDS`、`GET_COMMON_PARAMETERS`、`GET_PARAMETERS_MANAGEMENT`、`GET_PARAMETER_CHANGES`、`GET_ALL_PARAMETERS_BY_GAME`、`GET_TEMPLATES`、`GET_TEMPLATE`、`GET_NODES`

**仅在 `operations.ts` 中的 Mutation**（15 个）：
- CRUD mutations for games、events、parameters、categories、flows

**合并策略**：
1. 保留 `@shared/graphql/operations.ts` 作为**唯一的 GraphQL 操作定义文件**
2. 将 `queries.ts` 中独有的 9 个查询迁移到 `operations.ts`
3. 统一命名为 **camelCase**（GraphQL 社区惯例）
4. 将 `src/graphql/queries.ts` 改为从 `@shared/graphql/operations.ts` 重导出（向后兼容）
5. 逐步更新所有消费者直接从 `@shared/graphql/operations.ts` 导入
6. 运行 `graphql-codegen` 重新生成类型

**实施步骤**：
1. 读取两个文件的完整内容，逐个对比重复查询的字段差异
2. 对于重复查询，保留字段更完整的版本
3. 将 `queries.ts` 独有的查询迁移到 `operations.ts`
4. 统一所有查询的字段命名为 camelCase
5. 更新 `queries.ts` 为重导出文件
6. 搜索所有 `from '@/graphql/queries'` 的导入，逐步更新
7. 运行 `npm run codegen` 重新生成类型

**验证标准**：
- `operations.ts` 包含所有 40+ 个 GraphQL 操作（16 queries + 9 unique queries + 15 mutations）
- `queries.ts` 仅包含重导出语句
- `npm run build` 无错误
- `npm run codegen` 成功生成类型

**预估工时**：1 个 sub agent session

---

### 3.3 任务 CQ-2：渐进式移除 @ts-nocheck（务实策略）

**现状分析**（修正后的数据）：

实际有 **181 个文件**使用 `@ts-nocheck`，分布如下：

| 模块 | 文件数 | 优先级 | 理由 |
|------|--------|--------|------|
| `shared/ui/` | ~30 | 🔴 P0 | 公共 UI 组件库，被所有模块依赖 |
| `shared/hooks/` | ~10 | 🔴 P0 | 公共 Hook，被所有模块依赖 |
| `shared/apollo/` | ~3 | 🔴 P0 | Apollo 客户端配置，影响所有 GraphQL 操作 |
| `shared/utils/` | ~15 | 🟡 P1 | 工具函数，影响面广 |
| `shared/components/` | ~10 | 🟡 P1 | 共享业务组件 |
| `features/canvas/` | ~15 | 🟡 P1 | Canvas 核心功能 |
| `features/events/` | ~3 | 🟡 P1 | 事件管理 |
| `features/games/` | ~8 | 🟡 P1 | 游戏管理 |
| `event-builder/` | ~25 | 🟢 P2 | 事件构建器 |
| `analytics/` | ~35 | 🟢 P2 | 分析模块 |
| `测试文件` | ~20 | ⚪ P3 | 测试文件的类型安全优先级最低 |
| `其他` | ~7 | ⚪ P3 | 配置、入口等 |

**务实策略**（经反思迭代后的决策）：

> **关键认知**：181 个文件全部移除 @ts-nocheck 是一个巨大的工程量，不应作为阻塞项。采用**增量严格化**策略：

1. **新增/修改的文件**：强制不使用 @ts-nocheck（通过 ESLint 规则）
2. **P0 模块**（shared/ui、shared/hooks、shared/apollo）：优先移除，共 48 个文件
3. **P1 模块**：在架构重构完成后逐步处理
4. **P2/P3 模块**：长期计划，不阻塞其他工作

**P0 模块实施步骤**：
1. 为 `shared/ui/` 下的每个组件移除 @ts-nocheck 并修复类型错误
2. 为 `shared/hooks/` 下的每个 Hook 添加完整类型注解
3. 为 `shared/apollo/` 添加类型安全的 Apollo 配置
4. 添加 ESLint 规则禁止新文件使用 @ts-nocheck

**验证标准**：
- P0 模块（48 个文件）无 @ts-nocheck
- `npm run build` 无错误
- `npm run test` 通过

**预估工时**：3-4 个 sub agent session（按组件批量处理）

**⚡ 并行说明**：CQ-2 是前端工作，与后端的 TD-1/TD-2/TD-3/TD-4 **可完全并行**。CQ-2 内部的不同模块也可并行处理。

---

### 3.4 任务 CQ-3：后端代码规范统一

**实施步骤**：
1. 全局搜索 `from backend.core.exceptions import` 并替换为 `from backend.core.errors import`（已部分完成）
2. 确认 `utils.py` 中的自定义异常（`HQLGenerationError` 等）已迁移到 `errors.py`
3. 统一 Service 层的返回值格式（使用 Entity 对象而非 dict）

**验证标准**：
- 无任何文件从 `exceptions.py` 导入
- `pytest` 全部通过

**预估工时**：0.5 个 sub agent session

---

## 四、架构优化方案（层3 — 功能开发的基础）

### 4.1 总览

架构优化的核心目标是**职责分离**：路由归路由、业务归业务、数据访问归数据访问。

### 4.2 任务 AO-1：后端 Blueprint 路由迁移

**现状分析**（基于深度调研的精确数据）：

**需要迁移的 6 个活跃 Blueprint**：

| Blueprint | 当前位置 | 路由前缀 | 迁移目标 |
|-----------|----------|----------|----------|
| `bulk_bp` | `services/bulk_operations/bulk_routes.py` | 无 | `api/routes/bulk_operations.py` |
| `cache_monitor_bp` | `services/cache_monitor/cache_monitor.py` | `/admin/cache` | `api/routes/cache_monitor.py` |
| `canvas_bp` | `services/canvas/canvas.py` | `/canvas` | `api/routes/canvas.py`（需新建） |
| `event_node_builder_bp` | `services/event_node_builder/__init__.py` | `/event_node_builder` | `api/routes/event_node_builder.py` |
| `common_params_bp` | `services/parameters/common_params.py` | `/api/common-params` | `api/routes/common_params.py` |
| `parameter_aliases_bp` | `services/parameters/parameter_aliases.py` | `/api/parameter-aliases` | `api/routes/parameter_aliases.py` |

**迁移模式**（每个 Blueprint 统一采用）：
1. 在 `api/routes/` 中创建新的路由文件
2. 将路由处理函数从 Service 文件中提取到路由文件
3. 路由文件调用 Service 层的方法处理业务逻辑
4. 更新 `api/__init__.py` 注册新 Blueprint
5. 从 `web_app.py` 中移除旧 Blueprint 的注册
6. 保留 Service 文件中的纯业务逻辑

**实施步骤**：
1. 逐个迁移 Blueprint（按优先级：common_params_bp → parameter_aliases_bp → bulk_bp → canvas_bp → cache_monitor_bp → event_node_builder_bp）
2. 每迁移一个，运行 `pytest` 确认无回归
3. 更新 `web_app.py` 中的 Blueprint 注册列表

**验证标准**：
- `backend/services/` 中无 Blueprint 定义
- 所有路由通过 `api/routes/` 注册
- `pytest` 全部通过
- API 端点功能不变（通过 E2E 测试验证）

**预估工时**：2 个 sub agent session

**⚡ 并行说明**：AO-1 依赖 TD-4（废弃 Blueprint 清理）完成后执行。但与前端工作（CQ-1、CQ-2）**可完全并行**。

---

### 4.3 任务 AO-2：提取 web_app.py 的 Blueprint 注册到工厂函数

**现状分析**：
- `web_app.py` 约 300 行，承担 app 创建、Blueprint 注册、错误处理、缓存配置等多重职责
- Blueprint 注册逻辑散布在文件各处

**实施步骤**：
1. 创建 `backend/app_factory.py`，包含 `create_app()` 工厂函数
2. 将 Blueprint 注册逻辑移到 `backend/api/__init__.py` 的 `register_blueprints(app)` 函数
3. 将错误处理器移到 `backend/core/error_handlers.py`
4. 将缓存配置移到 `backend/core/cache.py`
5. `web_app.py` 简化为仅调用 `create_app()` 并启动

**验证标准**：
- `web_app.py` 不超过 50 行
- `create_app()` 可被测试框架直接调用
- `pytest` 全部通过

**预估工时**：1 个 sub agent session

**⚡ 并行说明**：AO-2 依赖 AO-1 完成后执行（需要所有 Blueprint 已迁移到 `api/routes/`）。

---

### 4.4 任务 AO-3：前端目录结构重组

**现状分析**：
- `src/graphql/` 与 `src/shared/graphql/` 重复
- `src/hooks/` 与 `src/shared/hooks/` 重复
- `src/pages/` 仅有 1 个文件（`GamesPageGraphQL.tsx`）
- `src/analytics/` 是独立的大模块（~35 个页面 + 组件），与 `features/` 平级

**目标结构**：
```
frontend/src/
├── shared/                 ← 唯一的共享模块入口
│   ├── graphql/            ← 所有 GraphQL 操作（统一后的 operations.ts）
│   ├── hooks/              ← 所有公共 Hook
│   ├── components/         ← 所有公共组件
│   ├── ui/                 ← UI 组件库
│   ├── apollo/             ← Apollo 客户端配置
│   ├── api/                ← API 工具
│   ├── types/              ← 共享类型
│   ├── utils/              ← 工具函数
│   └── config/             ← 配置
├── features/               ← 按功能模块组织
│   ├── canvas/             ← Canvas 可视化构建器
│   ├── events/             ← 事件管理
│   ├── games/              ← 游戏管理
│   ├── parameters/         ← 参数管理
│   └── analytics/          ← 分析模块（从顶层迁入）
├── event-builder/          ← 事件构建器（保持独立，体量大）
├── pages/                  ← 页面级路由组件
├── types/                  ← 全局类型（api.generated.ts）
└── main.tsx                ← 入口
```

**实施步骤**：
1. 将 `src/graphql/queries.ts` 的内容合并到 `src/shared/graphql/operations.ts`（CQ-1 已完成）
2. 将 `src/graphql/client.ts`、`config.ts`、`subscriptionHooks.ts` 迁移到 `src/shared/graphql/`
3. 将 `src/hooks/` 中的 Hook 迁移到 `src/shared/hooks/`（部分已通过重导出完成）
4. 将 `src/analytics/` 迁移到 `src/features/analytics/`
5. 将 `src/pages/GamesPageGraphQL.tsx` 迁移到 `src/features/games/pages/`
6. 更新 `tsconfig.json` 和 `vite.config.js` 的路径别名
7. 更新所有导入路径
8. 删除空的顶层目录

**验证标准**：
- `src/graphql/`、`src/hooks/` 目录不再存在（或仅包含重导出）
- `npm run build` 无错误
- `npm run test` 通过

**预估工时**：2 个 sub agent session

**⚡ 并行说明**：AO-3 依赖 CQ-1（GraphQL 统一）完成后执行。但与后端的 AO-1、AO-2 **可完全并行**。

---

### 4.5 任务 AO-4：引入 Repository 模式（长期）

**说明**：这是一个较大的架构变更，建议在 AO-1/AO-2 完成后作为独立迭代执行。

**目标**：将 SQL 查询从 Service 层分离到 Repository 层，实现：
- Service 层只包含业务逻辑
- Repository 层封装所有数据库操作
- 便于未来从 SQLite 迁移到其他数据库

**实施步骤**：
1. 创建 `backend/repositories/` 目录
2. 为每个 Entity 创建对应的 Repository（`game_repository.py`、`event_repository.py` 等）
3. 将 Service 中的 SQL 查询逐步迁移到 Repository
4. Service 层通过 Repository 接口访问数据

**预估工时**：3-4 个 sub agent session

**⚡ 并行说明**：AO-4 依赖 AO-1 和 AO-2 完成。可与前端 AO-3 并行。

---

## 五、功能完整性补强计划（层4 — 最终目标）

### 5.1 总览

基于 PRD 文档定义的 15 个核心功能模块，以下为尚需完善的功能，按优先级排序：

### 5.2 P0 核心功能

#### 任务 FE-1：Canvas 可视化查询构建器完善

**现状**：
- 后端：`canvas_bp` 已注册，`canvas_service.py` 提供基础 CRUD
- 前端：`features/canvas/` 有 `CanvasFlow.tsx`（648 行）、`NodeSelector.tsx`、`NodeSidebar.tsx` 等组件
- 使用 ReactFlow 11.x 作为画布引擎

**缺失功能**：
- 拖拽连线的节点配置面板
- 实时 HQL 预览（连线变化时自动更新）
- 节点类型扩展（当前仅支持基础节点）
- 画布状态持久化（保存/加载）

**依赖**：
- 依赖 AO-1（Blueprint 迁移后 canvas 路由在 `api/routes/canvas.py`）
- 依赖 CQ-1（GraphQL 操作统一后使用 `@shared/graphql/operations.ts`）

**预估工时**：3-4 个 sub agent session

---

#### 任务 FE-2：HQL 生成引擎 V2 高级功能

**现状**：
- 后端：`backend/services/hql/` 是最大的服务模块，包含 builders、core、services、validators 等子模块
- API：`hql_preview_v2` 端点已可用
- 前端：`HQLPreviewV2/` 组件已实现基础预览

**缺失功能**：
- 模板变量替换引擎
- 多表 JOIN 自动推导（基于事件关联关系）
- 分区条件自动注入（基于日期范围）
- HQL 语法高亮和错误提示

**依赖**：
- 后端 HQL 模块相对独立，可在 TD 完成后立即开始
- 前端依赖 CQ-1（GraphQL 统一）

**预估工时**：2-3 个 sub agent session

---

#### 任务 FE-3：事件节点构建器完善

**现状**：
- 后端：`event_node_builder_bp` 已注册
- 前端：`event-builder/` 模块体量大（~25 个组件），`EventNodeBuilder.tsx`（647 行）、`FieldBuilder.tsx`（527 行）、`FieldCanvas.tsx`（795 行）
- GraphQL：`GET_EVENT_FIELDS` 查询已定义

**缺失功能**：
- 字段拖拽排序
- 字段类型自动推断
- 批量字段操作

**依赖**：
- 依赖 AO-1（Blueprint 迁移）
- 前端组件已较完整，主要是交互增强

**预估工时**：2 个 sub agent session

---

### 5.3 P1 重要功能

#### 任务 FE-4：批量操作完善

**现状**：`bulk_operations` 蓝图已注册，`batch_import_manager.py` 提供基础批量导入

**缺失**：批量导出、批量参数修改、进度追踪

**预估工时**：1-2 个 sub agent session

---

#### 任务 FE-5：流程管理（Flows）前端实现

**现状**：GraphQL mutations 已定义（`CREATE_FLOW`、`UPDATE_FLOW`、`DELETE_FLOW`），后端 `flow_service.py` 已实现

**缺失**：前端流程编辑器 UI

**预估工时**：2 个 sub agent session

---

#### 任务 FE-6：参数变更历史展示

**现状**：`GET_PARAMETER_CHANGES` 查询已定义

**缺失**：前端变更历史展示组件（时间线视图）

**预估工时**：1 个 sub agent session

---

### 5.4 P2 增强功能

| 任务 | 现状 | 缺失 | 预估工时 |
|------|------|------|----------|
| FE-7：SQL 优化器 | `sql_optimizer_bp` 已注册 | 优化建议引擎 | 2 session |
| FE-8：异步任务系统 | `async_task_bp` 已注册 | 任务队列和进度追踪 | 2 session |
| FE-9：模板管理 | `GET_TEMPLATES` 查询已定义 | 前端模板编辑器 | 1-2 session |

---

## 六、并行执行方案

### 6.1 执行阶段和时间线

```
Week 1-2: 技术债务清理（层1）
├── 🔀 并行流 A（后端）: TD-1 + TD-2 + TD-3 + TD-4
└── 🔀 并行流 B（前端）: CQ-1（GraphQL 统一）

Week 2-3: 代码质量改进（层2）
├── 🔀 并行流 A（后端）: CQ-3（代码规范统一）
└── 🔀 并行流 B（前端）: CQ-2 P0 批次（shared/ui + shared/hooks + shared/apollo）

Week 3-5: 架构优化（层3）
├── 🔀 并行流 A（后端）: AO-1（Blueprint 迁移）→ AO-2（工厂函数）
└── 🔀 并行流 B（前端）: AO-3（目录重组）

Week 5+: 功能补强（层4）
├── 🔀 并行流 A: FE-1（Canvas）+ FE-2（HQL V2）
├── 🔀 并行流 B: FE-3（事件构建器）+ FE-4（批量操作）
└── 🔀 并行流 C: FE-5（流程管理）+ FE-6（参数历史）
```

### 6.2 Sub Agent 并行调度方案

每个阶段的 sub agent 调度策略：

#### 阶段 1：技术债务清理（最多 4 个并行 sub agent）

```
Sub Agent 1: TD-1（utils.py/utils/ 冲突解决）
Sub Agent 2: TD-2（security.py/security/ 冲突解决）
Sub Agent 3: TD-3（Entity 重复合并）
Sub Agent 4: TD-4（废弃 Blueprint 清理）+ CQ-1（GraphQL 统一）
```

**里程碑 M1**：所有文件/目录冲突消除，GraphQL 操作统一
**验证**：`pytest` 全通过 + `npm run build` 成功

#### 阶段 2：代码质量改进（最多 3 个并行 sub agent）

```
Sub Agent 1: CQ-2 批次 1（shared/ui/ 组件移除 @ts-nocheck）
Sub Agent 2: CQ-2 批次 2（shared/hooks/ + shared/apollo/ 移除 @ts-nocheck）
Sub Agent 3: CQ-3（后端代码规范统一）
```

**里程碑 M2**：P0 模块类型安全，后端规范统一
**验证**：P0 模块无 @ts-nocheck + `pytest` 全通过

#### 阶段 3：架构优化（最多 2 个并行 sub agent）

```
Sub Agent 1: AO-1（后端 Blueprint 迁移）→ AO-2（工厂函数）
Sub Agent 2: AO-3（前端目录重组）
```

**里程碑 M3**：架构清晰，职责分离完成
**验证**：`services/` 无 Blueprint + `src/graphql/` 仅含重导出 + E2E 测试通过

#### 阶段 4：功能补强（最多 3 个并行 sub agent）

```
Sub Agent 1: FE-1（Canvas 完善）
Sub Agent 2: FE-2（HQL V2）+ FE-3（事件构建器）
Sub Agent 3: FE-4（批量操作）+ FE-5（流程管理）+ FE-6（参数历史）
```

**里程碑 M4**：P0 + P1 功能完整
**验证**：E2E 测试覆盖所有新功能

### 6.3 每个 Sub Agent 的标准工作流

```
1. 读取目标文件，确认当前状态
2. 执行变更（遵循 refactor 技能的安全重构流程）
3. 运行相关测试（pytest / npm run test）
4. 检查 linter 错误（read_lints）
5. 提交变更并报告结果
```

---

## 七、风险与注意事项

### 7.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| utils.py 迁移导致导入失败 | 中 | 高 | 通过 `__init__.py` 重导出保持向后兼容 |
| @ts-nocheck 移除引入大量类型错误 | 高 | 中 | 按模块批量处理，每批次独立验证 |
| Blueprint 迁移导致 API 端点变化 | 低 | 高 | 保持路由前缀不变，仅移动代码位置 |
| GraphQL 操作合并导致前端查询失败 | 中 | 高 | 通过重导出保持旧路径可用 |

### 7.2 执行原则

- **渐进式重构**：每次只改一个模块，确保测试通过后再继续
- **向后兼容**：重导出模式确保现有导入不会中断
- **数据库无变更**：所有重构不涉及数据库 schema 变更
- **前端构建同步**：目录结构调整需同步更新 `tsconfig.json` 路径别名和 `vite.config.js` resolve 配置
- **每个 sub agent 独立可验证**：每个任务完成后必须通过测试验证

### 7.3 关键度量

| 度量项 | 当前值 | 目标值 | 阶段 |
|--------|--------|--------|------|
| 文件/目录冲突数 | 2 | 0 | 阶段 1 |
| Entity 重复定义数 | 3 | 0 | 阶段 1 |
| GraphQL 重复查询数 | 16 | 0 | 阶段 1 |
| @ts-nocheck 文件数（P0 模块） | 48 | 0 | 阶段 2 |
| @ts-nocheck 文件数（全局） | 181 | <50 | 阶段 2-3 |
| services/ 中的 Blueprint 数 | 6 | 0 | 阶段 3 |
| web_app.py 行数 | ~300 | <50 | 阶段 3 |
| P0 功能完成度 | ~60% | 100% | 阶段 4 |
