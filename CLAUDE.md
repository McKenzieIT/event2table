# Event2Table - 开发规范

> **版本**: 7.3 | **最新优化**: 文档组织规范化 | **最后更新**: 2026-02-12
>
> **🆕 最新变更**: 新增文档组织规范章节 (2026-02-12)
> **🆕 最新变更**: 重组文档结构，修复路径引用 (2026-02-12)

---

⚠️ **强制遵守：自行主动测试**
---
所有代码和脚本的开发、修复、修改，都需要在完成后自己先测试，再交给用户
1. ✅ 先执行API契约一致性
2. ✅ 执行单元测试
3. ✅ 执行E2E测试

❌ 禁止完成编写后，未进行交付直接测试
---

⚠️ **强制执行：TDD开发模式**
---
所有代码开发必须遵循测试驱动开发（TDD）：
1. ✅ 先写测试，看测试失败
2. ✅ 编写最小代码使测试通过
3. ✅ 重构优化，保持测试通过

**如何执行**：在实现任何功能前，调用：
```
/superpowers:test-driven-development
```

❌ 违反TDD = 不合格的代码

---

## Critical Rules → 关键规则（必读）

### 沟通语言规范

- **开发过程**: 使用英文以节省tokens
- **方案汇报**: 始终使用中文与用户沟通
- **代码注释**: 使用英语
- **提交信息**: 使用英语
- **本文档**: 使用中文以提高上下文效率

### API契约测试规范 ⚠️ **极其重要 - 强制执行**

> **🚨 前端调用的每个API必须后端实现**
> **🆕 更新 (2026-02-10)**: 建立API契约测试体系，确保前后端API一致性

#### 核心原则

**API契约一致性**：
```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 自动修复API契约问题
python scripts/test/api_contract_test.py --fix

# 验证修复后的代码
python scripts/test/api_contract_test.py --verify
```

**必填检查项**：
- ✅ 前端调用的API端点必须后端存在
- ✅ HTTP方法必须匹配（GET/POST/PUT/DELETE等）
- ✅ 参数格式必须一致（game_gid vs game_id）
- ✅ 错误状态码必须定义（404/409/500）

#### 开发工作流

**新增API时**：
```python
# 1. 先在前端实现API调用
fetch('/api/games/${gameGid}', { method: 'DELETE' })

# 2. 运行契约测试
python scripts/test/api_contract_test.py

# 3. 测试会报告缺失的路由
❌ DELETE /api/games/<int:id>
   前端: GamesList.jsx:44
   后端: 路由未定义

# 4. 运行自动修复
python scripts/test/api_contract_test.py --fix

# 5. 验证修复
python scripts/test/api_contract_test.py
```

**Pre-commit Hook**：
```bash
# 每次提交前自动运行API契约测试
git commit  # 会自动运行契约测试

# 如果测试失败，提交被阻止
❌ API契约测试失败，提交被阻止

# 修复后重新提交
python scripts/test/api_contract_test.py --fix
git commit
```

### E2E测试规范 ⚠️ **极其重要 - 强制执行**

> **🚨 每次代码修改后必须执行完整的E2E测试**
> **🆕 更新 (2026-02-11)**: 建立强制E2E测试流程，确保每次修改后进行端到端验证

#### 核心原则

**修改即测试**：
```bash
# 1. 修改代码后立即启动开发服务器
cd frontend
npm run dev

# 2. 执行完整的E2E测试
# 详细测试清单：docs/testing/e2e-testing-guide.md

# 3. 发现错误立即修复
# 4. 修复后重新测试

# 5. 所有测试通过才能提交代码
```

**必须测试的场景**：
- ✅ 修改任何组件代码
- ✅ 修改任何导入/导出
- ✅ 修改任何API路由
- ✅ 修改任何样式文件
- ✅ 修改任何配置文件

**E2E测试指南**：
- 完整测试清单：`docs/testing/e2e-testing-guide.md`
- 测试报告模板：`docs/testing/e2e-testing-guide.md#测试报告模板`

**禁止行为**：
- ❌ 修改代码后不进行E2E测试
- ❌ 仅进行静态分析，不启动服务器测试
- ❌ 跳过任何测试步骤
- ❌ 发现错误不立即修复

**违反后果**：
- ❌ 生产环境出现用户可见的错误
- ❌ 技术债务累积
- ❌ 团队效率下降

### 测试隔离规范 ⚠️ **极其重要 - 强制执行**

> **🚨 严禁测试污染生产数据库**
> **✅ 已完成**: 三环境完全隔离（2026-02-10）

#### 实现状态

✅ **已完成**: 三环境完全隔离
- 环境检测: 4/4 tests passed
- 数据库隔离: 4/4 tests passed
- 配置文件: 3/3 tests passed
- **总计**: 11/11 tests passed (100%)

#### 核心原则

**测试数据库隔离**：
```python
# ✅ 测试使用独立数据库
# FLASK_ENV=testing → data/test_database.db
# FLASK_ENV=production → data/dwd_generator.db

# 配置文件: backend/core/config/config.py
def get_db_path():
    if os.environ.get("FLASK_ENV") == "testing":
        return TEST_DB_PATH  # data/test_database.db
    return DB_PATH  # data/dwd_generator.db
```

**pytest fixture配置**：
```python
# backend/tests/conftest.py
@pytest.fixture(scope="session")
def db():
    """
    使用独立的测试数据库进行测试
    测试前清理，测试后保留以便调试
    """
    # 删除旧测试数据库（如果存在）
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 初始化测试数据库
    init_db(TEST_DB_PATH)

    # 提供测试数据库连接
    conn = get_db_connection(TEST_DB_PATH)
    yield conn
    conn.close()
```

**测试数据命名规范**：
```python
# ✅ 使用TEST_前缀确保不与生产数据冲突
unique_gid = f"TEST_{uuid.uuid4().hex[:8]}"

# ❌ 不要使用以下命名（可能污染生产数据）:
unique_gid = f"777777{random.randint(1000, 9999)}"  # 危险
unique_gid = 10000147  # 危险：可能与生产数据冲突
```

#### 运行测试

**运行pytest测试**：
```bash
# 自动使用测试数据库
pytest test/unit/backend/ -v

# 验证生产数据库未受污染
sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM log_events"

# 检查测试数据库存在
ls -lh data/test_database.db
```

### 游戏标识符规范 ⚠️ **极其重要 - 强制执行**

> **🚨 严禁使用 game_id 进行数据关联**
> **✅ 已完成**: game_gid迁移完成，所有数据关联必须使用game_gid

#### 核心原则

**game_id vs game_gid**：
```python
# ⚠️ 严格区分两种ID：
# game_id: 数据库自增主键 (1, 2, 3) → ❌ 仅用于games表主键，禁止用于关联
# game_gid: 游戏业务GID (10000147) → ✅ 唯一合法的数据关联标识符

# 🚨 严禁以下用法：
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_id = ?', (game_id,))
# JOIN games g ON le.game_id = g.id  ❌ 错误

# ✅ 正确用法：
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
# JOIN games g ON le.game_gid = g.gid  ✅ 正确
```

#### Python后端规范

**所有SQL查询必须使用game_gid**：
```python
# ✅ 正确：游戏查询
game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))

# ✅ 正确：事件查询
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ✅ 正确：参数查询
params = fetch_all_as_dict('''
    SELECT ep.* FROM event_params ep
    INNER JOIN log_events le ON ep.event_id = le.id
    WHERE le.game_gid = ?
''', (game_gid,))

# ✅ 正确：统计查询
stats = fetch_all_as_dict('''
    SELECT
        g.gid,
        g.name,
        (SELECT COUNT(*) FROM log_events le WHERE le.game_gid = g.gid) as event_count
    FROM games g
''')
```

**表名生成规范**：
```python
# ✅ 使用 game_gid 生成表名
source_table = f'{game["ods_db"]}.ods_{game["gid"]}_all_view'  # ieu_ods.ods_10000147_all_view
target_table = f'{dwd_prefix}.v_dwd_{game["gid"]}_{event}_di'  # dwd.v_dwd_10000147_login_di

# ❌ 不要使用 game_id
source_table = f'{ods_db}.ods_{game_id}_all_view'  # 错误！
```

#### 前端JavaScript规范

```javascript
// ✅ 正确：使用 gameData.gid
const gameGid = gameData.gid;  // 10000147
const odsDb = gameData.ods_db;  // ieu_ods
const tableName = `${odsDb}.ods_${gameGid}_all_view`;

// ✅ 正确：API调用
fetch(`/api/events?game_gid=${gameGid}`)
fetch(`/api/parameters/all?game_gid=${gameGid}`)

// ❌ 错误：不要使用 gameId
const tableName = `ods_${gameId}_all_view`;  // 错误！
fetch(`/api/events?game_id=${gameId}`)  // 错误！
```

#### 代码审查强制检查项

**每次代码审查必须检查**：
- [ ] 所有SQL查询是否使用 `game_gid` 而非 `game_id`
- [ ] 所有JOIN条件是否使用 `game_gid = g.gid`
- [ ] 所有表名生成是否使用 `game["gid"]` 而非 `game["id"]`
- [ ] 所有API调用是否使用 `game_gid` 参数
- [ ] 数据库Schema是否使用 `game_gid` 作为外键

**违规后果**：
- ⚠️ 数据关联错误（Dashboard显示0）
- ⚠️ 查询性能下降
- ⚠️ 业务逻辑混乱
- ❌ Code Review必须拒绝

### 游戏上下文强制验证

```python
# 所有路由必须验证游戏上下文
game_gid = request.args.get('game_gid', type=int) or session.get('current_game_gid')
if not game_gid:
    return jsonify(error_response('Game context required', status_code=400)[0]), 400

# 所有查询必须包含游戏过滤（使用 game_gid）
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

### API安全规范

> **🚨 所有API必须遵循安全开发规范**

#### 核心安全原则

**1. 输入验证与XSS防护**：
```python
import html
from backend.core.utils import sanitize_and_validate_string

# ✅ 正确：使用Pydantic Schema进行验证
from backend.models.schemas import GameCreate

# Pydantic自动进行XSS防护和验证
game_data = GameCreate(**request.json)
```

**2. SQL注入防护**：
```python
# ✅ 正确：参数化查询
games = fetch_all_as_dict("SELECT * FROM games WHERE name = ?", (name,))

# ❌ 错误：字符串拼接
query = f"SELECT * FROM games WHERE name = '{name}'"  # SQL注入风险！
```

**3. 错误处理不暴露敏感信息**：
```python
# ✅ 正确：通用错误消息
try:
    # 业务逻辑
except Exception as e:
    logger.error(f"Error creating game: {e}")  # 详细日志
    return json_error_response("Failed to create game", status_code=500)  # 通用消息

# ❌ 错误：暴露内部错误
except Exception as e:
    return jsonify({"error": str(e)}), 500  # 可能暴露路径、SQL等
```

#### 安全检查清单

每个API必须检查：
- [ ] 输入验证（必填字段、数据类型、长度限制）
- [ ] XSS防护（HTML转义用户输入）
- [ ] SQL注入防护（参数化查询）
- [ ] 输出编码（JSON响应，不暴露内部信息）
- [ ] 错误处理（适当的HTTP状态码：400/404/409/500）

---

## 文档组织规范 ⚠️ **极其重要**

> **🚨 所有文档必须按照本规范放置在正确的位置**
> **🆕 更新 (2026-02-12)**: 建立文档组织规则，避免根目录混乱

### 根目录文件规范

**仅允许以下文件在根目录**：
- ✅ `README.md` - 项目说明
- ✅ `CHANGELOG.md` - 更新日志
- ✅ `CLAUDE.md` - 开发规范（本文档）
- ✅ `LICENSE` - 许可证

**禁止在根目录创建文档**：
- ❌ 测试报告 → 应放在 `docs/testing/reports/`
- ❌ 修复报告 → 应放在 `docs/reports/`
- ❌ 测试指南 → 应放在 `docs/testing/` 或 `docs/development/`
- ❌ 性能报告 → 应放在 `docs/performance/`
- ❌ 临时输出文件 → 应放在 `output/` 或直接删除

### 文档目录结构

```
docs/
├── development/      # 开发指南
│   ├── architecture.md          # 架构设计
│   ├── contributing.md          # 贡献指南
│   ├── skills/                # Claude Code Skills
│   └── getting-started.md     # 快速开始
├── testing/          # 测试文档
│   ├── e2e-testing-guide.md    # E2E测试指南
│   ├── quick-test-guide.md      # 快速测试指南
│   └── reports/               # 测试报告
│       ├── test-report-2026-02-11.md
│       ├── final-verification-report.md
│       └── verification-summary.md
├── reports/          # 开发报告
│   ├── dashboard-card-click-fix-summary.md
│   ├── game-id-violations-detail.md
│   └── ...
├── performance/      # 性能报告
│   ├── vercel-optimization-summary.md
│   └── complexity-refactoring.md
├── requirements/     # 需求文档
│   └── prd.md                   # 产品需求文档（TODO）
├── api/             # API文档
│   └── README.md              # API文档索引（TODO）
├── canvas/          # Canvas模块文档
├── hql/             # HQL生成器文档
└── adr/             # 架构决策记录
```

### 文档命名规范

**文件命名格式**：
- ✅ 使用小写字母和连字符：`dashboard-fix-summary.md`
- ✅ 日期格式：`test-report-2026-02-11.md`
- ❌ 避免下划线：不用 `test_report_2026_02_11.md`
- ❌ 避免全大写：不用 `E2E_TESTING_GUIDE.md`

**示例**：
```
❌ E2E_TESTING_GUIDE.md          → ✅ e2e-testing-guide.md
❌ TEST_REPORT_2026-02-11.md      → ✅ test-report-2026-02-11.md
❌ game_id_violations_detail.md    → ✅ game-id-violations-detail.md
❌ DASHBOARD_CARD_CLICK_FIX_SUMMARY.md → ✅ dashboard-card-click-fix-summary.md
```

### 文档创建流程

**新增文档前，请确认**：
1. 文档类型（指南/报告/需求）
2. 目标目录（development/testing/reports等）
3. 文件命名（小写+连字符）
4. 是否需要更新 CLAUDE.md 中的引用

**禁止行为**：
- ❌ 在根目录创建 `.md` 文件（除 README.md, CHANGELOG.md, CLAUDE.md）
- ❌ 在根目录创建临时报告文件
- ❌ 使用不一致的命名格式

---

## 测试文件组织规范 ⚠️ **极其重要**

> **🚨 测试文件必须按照以下规范放置，禁止混乱存放**

### 核心原则

**分治策略**：尊重测试工具的工作机制，而非强行统一

### 前端测试（frontend/tests/）

**保留位置的原因**：
- Vitest需要访问`package.json`和相对路径`src/`
- Playwright需要`webServer: 'npm run dev'`
- npm scripts依赖当前工作目录

**允许的测试类型**：
- ✅ 单元测试：`frontend/tests/unit/`（Vitest）
- ✅ 集成测试：`frontend/tests/integration/`
- ✅ 组件测试：`frontend/tests/unit/components/`

**禁止的测试类型**：
- ❌ E2E测试 → 应放在`test/e2e/`
- ❌ 性能测试 → 应放在`test/performance/`

### 后端测试（test/）

**统一位置的原因**：
- Pytest需要根目录的`conftest.py`
- 后端测试不需要启动前端服务器
- 可独立运行`pytest test/unit/`

**目录结构**：
```
test/
├── unit/                    # Python单元测试
├── integration/              # Python集成测试
├── contract/                # API契约测试
├── e2e/                     # 端到端测试（Playwright）
├── performance/              # 性能测试
├── fixtures/                # 测试fixtures
├── helpers/                  # 测试工具
├── output/                   # ⭐ 测试输出统一目录
└── archive/                  # 归档的测试
```

### E2E测试（test/e2e/）

E2E测试需要启动前后端服务器，统一放在`test/e2e/`：
- `test/e2e/critical/` - 关键流程测试
- `test/e2e/smoke/` - 冒烟测试
- `test/e2e/playwright.config.ts` - Playwright配置

### 测试输出统一管理 ⚠️ **极其重要**

> **🚨 所有测试工具的输出必须重定向到test/output/**

#### 目的

- 统一的测试报告入口
- 简化.gitignore配置
- 简化CI/CD流程

#### 配置方式

**Playwright**：
```typescript
reporter: [
  ['html', { outputFolder: '../../test/output/playwright-report' }],
  ['json', { outputFile: '../../test/output/playwright-results.json' }],
]
```

**Vitest**：
```json
"scripts": {
  "test:coverage": "vitest run --coverage --reporter=../../test/output/coverage"
}
```

**Pytest**：
```ini
[pytest]
addopts =
    --html=test/output/html-report/index.html
    --cov-report=html:test/output/coverage
```

#### .gitignore配置

```gitignore
# Test outputs
test/output/
frontend/playwright-report/
frontend/test-results/
```

---

## Project Overview → 项目概述

### 项目简介

Event2Table 是一个数据仓库（DWD）层HQL生成工具，用于自动化创建Hive视图。

**核心功能**：
1. **基础模块**: ETL数据抽取（CREATE TABLE + INSERT OVERWRITE）
2. **高级模块**: Canvas系统 + 事件节点定制
3. **HQL生成**: 支持 single/join/union 三种模式

### 技术栈

- **后端**: Flask + Python 3.9+
- **前端**: React + Vite + Tailwind CSS
- **数据库**: SQLite
- **测试**: pytest + Playwright
- **数据验证**: Pydantic

### 项目结构概览

```
event2table/
├── backend/          # 后端模块（Flask + Python）
│   ├── api/         # API路由（模块化架构）
│   │   ├── routes/  # API端点
│   │   │   ├── dwd_generator/  # DWD生成API
│   │   │   │   ├── events.py
│   │   │   │   ├── games.py
│   │   │   │   └── parameters.py
│   │   └── middleware/  # 中间件
│   ├── core/       # 核心工具
│   │   ├── config/  # 配置管理
│   │   ├── database/  # 数据库操作
│   │   ├── cache/  # 缓存系统
│   │   ├── security/  # 安全工具
│   │   ├── utils/  # 工具函数
│   │   └── validators/  # 验证器
│   ├── models/     # 数据模型层 🆕
│   │   ├── schemas.py  # Pydantic Schema（数据验证）
│   │   └── repositories/  # Repository（数据访问）
│   │       ├── games.py
│   │       ├── events.py
│   │       └── parameters.py
│   └── services/   # 业务服务层 🆕
│       ├── games/  # 游戏服务
│       ├── events/  # 事件服务
│       ├── parameters/  # 参数服务
│       ├── canvas/  # Canvas服务
│       └── hql/  # HQL生成器（V2架构）🆕
│           ├── core/  # 核心生成器
│           ├── builders/  # Builder模式
│           ├── models/  # 数据模型
│           ├── validators/  # 验证器
│           └── templates/  # 模板管理
├── frontend/         # 前端应用（React + Vite）
│   ├── src/
│   │   ├── features/  # 功能模块
│   │   │   ├── games/
│   │   │   ├── events/
│   │   │   ├── parameters/
│   │   │   ├── canvas/
│   │   │   └── event-builder/
│   │   ├── shared/  # 共享组件
│   │   ├── styles/  # 样式文件
│   │   └── types/  # TypeScript类型
│   └── tests/  # 测试文件
├── data/             # 数据文件目录 ✨ 新增
│   ├── dwd_generator.db      # 生产数据库
│   ├── dwd_generator_dev.db  # 开发数据库
│   └── test_database.db      # 测试数据库
├── test/             # 测试文件
│   ├── unit/  # 单元测试
│   └── e2e/  # E2E测试
├── docs/             # 文档目录
│   ├── development/  # 开发指南
│   ├── api/  # API文档
│   ├── adr/  # 架构决策记录
│   └── reports/  # 开发报告 ✨ 整理
├── scripts/          # 工具脚本 ✨ 整理
│   ├── setup/  # 安装和初始化脚本
│   ├── migrate/  # 数据迁移脚本
│   ├── performance/  # 性能测试脚本
│   ├── verify/  # 验证脚本
│   ├── tools/  # 工具脚本
│   ├── tests/  # 测试运行脚本
│   ├── manual/  # 手动测试脚本
│   └── temp/  # 临时脚本
├── config/           # 配置文件
├── logs/             # 日志文件
├── output/           # 输出文件
├── uploads/          # 上传文件
├── migration/        # 迁移脚本
├── web_app.py        # 应用入口
├── requirements.txt  # Python依赖
├── pyproject.toml    # 项目配置
├── README.md         # 项目说明
├── CHANGELOG.md      # 更新日志
├── CLAUDE.md         # 开发规范
└── LICENSE           # 许可证
```

---

## Development Workflow → 开发工作流

### 快速开始

```bash
# 进入项目目录
cd /Users/mckenzie/Documents/event2table

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/setup/init_db.py

# 启动后端应用
python web_app.py  # http://127.0.0.1:5001

# 前端开发（另开终端）
cd frontend
npm install
npm run dev         # http://localhost:5173 (热更新)
npm run build       # 生产构建
npm run test        # 运行测试
```

### 开发前的强制检查清单 ⚠️ **极其重要**

> **🚨 在开始任何代码开发前，必须完成以下检查**
>
> 违反TDD开发模式将导致代码质量问题和返工

**强制检查项**：

- [ ] 调用 `/superpowers:test-driven-development` skill
- [ ] 阅读TDD铁律：**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**
- [ ] 确认已设置测试环境（pytest/npm test等）
- [ ] 准备好先写测试，再看测试失败

**只有完成以上检查，才能开始编写代码。**

> **💡 为什么需要TDD？**
> - ✅ 测试先行确保代码满足需求（而非"实现后验证"）
> - ✅ 失败的测试证明测试有效（通过的测试可能什么都没测）
> - ✅ 快速反馈循环减少调试时间
> - ✅ 测试即文档，展示代码的正确使用方式
>
> **❌ 违反TDD的代价**：
> - 看似"更快"实际更慢（调试时间 > TDD时间）
> - 测试通过立即 = 测试无效 = 假安全感
> - 技术债务累积 = 未来重构困难

### 需求管理规范

**重要**: 所有功能需求变更必须更新到 [docs/requirements/PRD.md](docs/requirements/PRD.md)

1. **需求新增**: 完成功能开发后，更新PRD对应章节
2. **需求修改**: 修改现有功能时，更新PRD和变更记录
3. **需求删除**: 删除功能时，标注为已废弃并记录
4. **优先级调整**: 更新需求的优先级和状态

### 常用工具函数

```python
from backend.core.utils import json_success_response, json_error_response
from backend.core.database.converters import fetch_one_as_dict, fetch_all_as_dict

# 查询
game = fetch_one_as_dict('SELECT * FROM games WHERE id = ?', (game_id,))
games = fetch_all_as_dict('SELECT * FROM games ORDER BY name')

# 响应
return json_success_response(data=games)
return json_error_response('Not found', status_code=404)
```

### 环境问题排查 ⚠️ **极其重要**

> **🚨 PATH 环境变量问题会导致测试和构建命令失败**
> **🆕 更新 (2026-02-12)**: 记录常见 PATH 问题及解决方案

#### 常见 PATH 错误

在执行测试或构建命令时，可能遇到以下错误：

```bash
# 错误 1: npx 命令未找到
npx: command not found

# 错误 2: Node.js 未找到
env: node: No such file or directory

# 错误 3: npm 脚本执行失败
head: command not found
```

#### 根本原因

这些错误通常是由于：
1. **Node.js 安装路径未添加到 PATH**
2. **npx 二进制文件不在可执行路径中**
3. **系统工具（如 head）路径配置问题**

#### 解决方案

**方案 1: 永久配置 PATH（推荐）**

编辑 shell 配置文件（`~/.zshrc` 或 `~/.bash_profile`）：

```bash
# 添加 Node.js 到 PATH（根据实际安装路径调整）
export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# 重新加载配置
source ~/.zshrc  # 或 source ~/.bash_profile
```

**方案 2: 使用绝对路径（临时方案）**

```bash
# 使用绝对路径运行 npx
/usr/local/Cellar/node/25.6.0/bin/npx playwright test

# 或直接使用 node 执行
/usr/local/Cellar/node/25.6.0/bin/node /usr/local/Cellar/node/25.6.0/lib/node_modules/playwright/cli.js test
```

**方案 3: 使用 npm run 脚本（推荐用于测试）**

在 `frontend/package.json` 中配置脚本：

```json
{
  "scripts": {
    "test": "playwright test",
    "test:ui": "playwright test --ui",
    "test:debug": "playwright test --debug",
    "test:e2e": "playwright test tests/e2e"
  }
}
```

然后运行：
```bash
cd frontend
npm run test        # 使用 npm 的 PATH 环境
npm run test:e2e    # 运行 E2E 测试
```

#### 验证 PATH 配置

```bash
# 1. 验证 Node.js 和 npm
which node    # 应输出: /usr/local/Cellar/node/25.6.0/bin/node
which npm     # 应输出: /usr/local/Cellar/node/25.6.0/bin/npm
which npx     # 应输出: /usr/local/Cellar/node/25.6.0/bin/npx

# 2. 验证系统工具
which head    # 应输出: /usr/bin/head
which bash    # 应输出: /bin/bash

# 3. 验证 Playwright
npx --version
node --version
npm --version
```

#### 绝对路径参考（2026-02-13 已配置）

**Node.js 25.6.0 安装路径**：
- **node**: `/usr/local/Cellar/node/25.6.0/bin/node`
- **npm**: `/usr/local/Cellar/node/25.6.0/bin/npm`
- **npx**: `/usr/local/Cellar/node/25.6.0/bin/npx`

**配置方式**：
已通过 `~/.zshrc` 永久配置：
```bash
# Node.js 25.6.0 - Event2Table开发环境
export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH"
```

**验证方法**：
```bash
# 重新加载配置
source ~/.zshrc

# 验证路径（应输出 Cellar 路径）
which node    # /usr/local/Cellar/node/25.6.0/bin/node
which npm     # /usr/local/Cellar/node/25.6.0/bin/npm
which npx     # /usr/local/Cellar/node/25.6.0/bin/npx

# 验证版本
node --version    # v25.6.0
npm --version     # 10.x.x
npx --version     # 10.x.x
```

#### 前端测试最佳实践

**推荐工作流程**：

```bash
# 1. 进入前端目录
cd /Users/mckenzie/Documents/event2table/frontend

# 2. 启动开发服务器（如果需要）
npm run dev &

# 3. 运行测试（使用 npm scripts）
npm run test              # 运行所有测试
npm run test:e2e         # 仅运行 E2E 测试
npm run test:ui          # 使用 UI 模式运行测试

# 4. 调试失败的测试
npm run test:debug       # 调试模式
npm run test -- --grep "test name"  # 运行特定测试
```

**避免的命令**：

```bash
# ❌ 不推荐：直接使用 npx（可能遇到 PATH 问题）
npx playwright test

# ❌ 不推荐：使用绝对路径（难以维护）
/usr/local/Cellar/node/25.6.0/bin/npx playwright test

# ✅ 推荐：使用 npm run 脚本
npm run test
```

#### E2E 测试执行清单

运行 E2E 测试前的检查清单：

- [ ] Node.js 和 npm 已安装（`node --version`）
- [ ] 前端依赖已安装（`cd frontend && npm install`）
- [ ] Playwright 浏览器已安装（`npx playwright install`）
- [ ] 开发服务器正在运行（`npm run dev`）
- [ ] 后端服务器正在运行（`python web_app.py`）
- [ ] 数据库已初始化（`python scripts/setup/init_db.py`）
- [ ] PATH 配置正确（`which npx` 返回有效路径）

#### 故障排除步骤

**步骤 1: 检查 PATH**
```bash
echo $PATH | tr ':' '\n' | grep node
```

**步骤 2: 重新安装 Node.js 工具**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm install -D @playwright/test
npx playwright install
```

**步骤 3: 使用 npm run 执行测试**
```bash
npm run test -- --list  # 列出所有测试
npm run test            # 运行测试
```

**步骤 4: 检查 Playwright 配置**
```bash
cd frontend
npx playwright test --config=playwright.config.ts --dry-run  # 验证配置
```

#### 相关文档

- [Playwright 官方文档](https://playwright.dev/)
- [E2E 测试规范](docs/testing/e2e-testing-guide.md)
- [快速测试指南](docs/testing/quick-test-guide.md)

---

## Architecture Details → 架构详情

### 分层架构设计（V7.0）

项目采用严格的四层架构，实现关注点分离和高内聚低耦合：

```
┌─────────────────────────────────────────────────────┐
│              API Layer (HTTP端点)                    │
│  backend/api/routes/                                 │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证                                     │
│  - 调用Service层                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  backend/services/                                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 事务管理                                           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  backend/models/repositories/                        │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 复杂查询                                           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Schema Layer (数据验证)                    │
│  backend/models/schemas.py                           │
│  - Pydantic模型定义                                   │
│  - 输入验证                                           │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

#### 各层职责

**1. Schema层（数据验证）**
```python
# backend/models/schemas.py
from pydantic import BaseModel, Field

class GameCreate(BaseModel):
    """游戏创建Schema"""
    gid: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    ods_db: Literal["ieu_ods", "overseas_ods"]

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击"""
        return html.escape(v.strip())
```

**2. Repository层（数据访问）**
```python
# backend/models/repositories/games.py
class GameRepository(GenericRepository):
    """游戏仓储类"""

    def find_by_gid(self, gid: int) -> Optional[Dict[str, Any]]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        return fetch_one_as_dict(query, (gid,))

    def get_all_with_event_count(self) -> List[Dict[str, Any]]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        return fetch_all_as_dict(query)
```

**3. Service层（业务逻辑）**
```python
# backend/services/games/game_service.py
class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    def create_game(self, game_data: GameCreate) -> Dict[str, Any]:
        """
        创建游戏

        业务逻辑：
        1. 验证gid唯一性
        2. 创建游戏
        3. 初始化默认配置
        """
        # 检查gid是否已存在
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game_data.dict())

        return self.game_repo.find_by_id(game_id)
```

**4. API层（HTTP端点）**
```python
# backend/api/routes/dwd_generator/games.py
@games_bp.route('/api/games', methods=['POST'])
def create_game():
    """创建游戏API"""
    try:
        # 1. 解析和验证请求参数
        data = request.get_json()
        game_data = GameCreate(**data)  # Pydantic验证

        # 2. 调用Service层
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应
        return json_success_response(
            data=GameResponse(**game).dict(),
            message="Game created successfully"
        )

    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        return json_error_response("Failed to create game", status_code=500)
```

### HQL V2架构设计

**模块化、解耦的HQL生成器**：

```
backend/services/hql/
├── core/              # 核心生成器
│   ├── generator.py          # 主生成器
│   ├── incremental_generator.py  # 增量生成器
│   └── cache.py              # 缓存管理
├── builders/          # Builder模式
│   ├── field_builder.py      # 字段构建器
│   ├── where_builder.py      # WHERE条件构建器
│   ├── join_builder.py       # JOIN构建器
│   └── union_builder.py      # UNION构建器
├── models/            # 数据模型
│   └── event.py              # 事件模型定义
├── validators/        # 验证器
├── templates/         # 模板管理
└── tests/             # 单元测试
```

**使用示例**：
```python
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field

# 创建生成器
generator = HQLGenerator()

# 定义事件
event = Event(
    name="login",
    table_name="ieu_ods.ods_10000147_all_view"
)

# 定义字段
fields = [
    Field(name="role_id", type="base"),
    Field(name="zone_id", type="param", json_path="$.zoneId")
]

# 生成HQL
hql = generator.generate(
    events=[event],
    fields=fields,
    conditions=[],
    mode="single"
)
```

### Canvas系统设计

**事件节点机制**：
1. **节点类型**: Table、Join、Union、Filter
2. **可视化配置**: 拖拽式流程配置
3. **实时预览**: HQL实时生成预览

**数据流向**：
```
用户操作（前端）
    ↓
Canvas API（backend/services/canvas/）
    ↓
HQL Builder（backend/services/hql/）
    ↓
HQL输出
```

### 数据流向

1. **用户操作**: 前端React组件捕获用户交互
2. **API调用**: 通过RESTful API发送请求到Flask后端
3. **Schema验证**: Pydantic Schema验证请求参数
4. **Service处理**: Service层执行业务逻辑
5. **Repository访问**: Repository层访问数据库
6. **HQL生成**: HQL生成器构建HQL语句
7. **响应返回**: 后端返回JSON响应，前端更新UI

---

## Coding Standards → 编码规范

### Python代码规范

#### 命名规范

```python
# ✅ 使用 snake_case
def get_game_by_gid(game_gid: int) -> Dict[str, Any]:
    pass

class GameService:
    pass

# ❌ 不要使用 camelCase
def getGameByGid(gameGid: int):
    pass
```

#### 类型注解

```python
# ✅ 完整的类型注解
from typing import Dict, List, Optional

def create_game(
    name: str,
    ods_db: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    pass

# ❌ 不要省略类型注解
def create_game(name, ods_db, description=None):
    pass
```

#### Docstrings

```python
# ✅ 完整的docstring
def create_game(game_data: GameCreate) -> Dict[str, Any]:
    """
    创建游戏

    Args:
        game_data: 游戏创建数据

    Returns:
        创建的游戏数据

    Raises:
        ValueError: 当gid已存在时

    Example:
        >>> service = GameService()
        >>> game = service.create_game(GameCreate(gid="1001", name="Test"))
        >>> print(game['name'])
        Test
    """
    pass
```

#### 工具函数使用

```python
from backend.core.utils import json_success_response, json_error_response
from backend.core.database.converters import fetch_one_as_dict, fetch_all_as_dict

# 查询
game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))
games = fetch_all_as_dict('SELECT * FROM games ORDER BY name')

# 响应
return json_success_response(data=games, message="Games retrieved successfully")
return json_error_response('Not found', status_code=404)
```

### TypeScript代码规范

#### 命名规范

```typescript
// ✅ 使用 camelCase
const fetchGameByGid = (gameGid: number): Game => {
  // ...
};

// 接口使用 PascalCase
interface GameData {
  gid: string;
  name: string;
  odsDb: string;
}

// ❌ 不要使用 snake_case
const fetch_game_by_gid = (game_gid: number) => {
  // ...
};
```

#### JSDoc注释

```typescript
// ✅ 完整的JSDoc
/**
 * 获取游戏信息
 * @param gameGid - 游戏GID
 * @returns 游戏信息
 * @example
 * const game = fetchGameByGid(10000147);
 * console.log(game.name);
 */
const fetchGameByGid = (gameGid: number): Game => {
  // ...
};
```

#### 游戏上下文处理

```typescript
// ✅ 正确：使用 gameData.gid
const gameGid = gameData.gid;  // 10000147
const odsDb = gameData.ods_db;  // ieu_ods
const tableName = `${odsDb}.ods_${gameGid}_all_view`;

// ❌ 错误：使用 gameId
const tableName = `ods_${gameId}_all_view`;  // 错误！
```

### SQL/HQL规范

```sql
-- ✅ 使用CREATE OR REPLACE VIEW
CREATE OR REPLACE VIEW dwd_event_login AS
SELECT
    ds, role_id, account_id, utdid,
    get_json_object(params, '$.zoneId') AS zone_id
FROM ods_event_log
WHERE ds = '${bizdate}';

-- ✅ 包含基础字段
-- ds, role_id, account_id, utdid, envinfo, tm, ts

-- ✅ params使用get_json_object()解析
get_json_object(params, '$.field') AS field

-- ✅ 字段命名遵循snake_case
```

### 代码审查清单

#### HQL生成
- [ ] 使用 `CREATE OR REPLACE VIEW` 而非 `DROP + CREATE`
- [ ] 包含基础字段：ds, role_id, account_id, utdid, envinfo, tm, ts
- [ ] params使用 `get_json_object()` 解析
- [ ] 字段命名遵循snake_case

#### 后端逻辑
- [ ] 使用Schema验证（Pydantic）
- [ ] Repository封装数据访问
- [ ] Service实现业务逻辑
- [ ] API返回统一JSON格式
- [ ] 错误处理适当（400/404/409/500）
- [ ] 参数验证完整
- [ ] 使用game_gid而非game_id

#### 前端UI
- [ ] 组件使用TypeScript
- [ ] Props类型定义完整
- [ ] 使用camelCase命名
- [ ] 游戏上下文正确传递
- [ ] 响应式设计

---

## Development Tips → 开发提示

### 常见问题

**Q: 表名生成使用哪个ID？**
A: 使用`game_gid`而非`game_id`：`ods_{game_gid}_all_view`

**Q: 为什么推荐使用 game_gid 而不是 game_id？**
A: `game_gid`是业务GID，稳定不变；`game_id`是数据库自增ID，可能因重建而变化

**Q: Repository和Service的区别？**
A: Repository负责数据访问（CRUD），Service负责业务逻辑（协调、事务、验证）

**Q: 什么时候使用Schema？**
A: 所有API输入参数必须使用Pydantic Schema验证

**Q: 如何处理旧的 game_id 数据？**
A: 参考数据库迁移脚本：`migration/migrate_game_gid.py`

### 快速文档查找

| 场景 | 查找文档 |
|------|----------|
| **架构设计** | [docs/development/architecture.md](docs/development/architecture.md) |
| **贡献指南** | [docs/development/contributing.md](docs/development/contributing.md) |
| **API文档** | [docs/api/README.md](docs/api/README.md) |
| **架构决策** | [docs/adr/README.md](docs/adr/README.md) |

### 相关文档

#### 核心文档
- [产品需求文档(PRD)](docs/requirements/PRD.md) - 功能需求、变更记录 ⭐
- [架构设计文档](docs/development/architecture.md) - 分层架构设计 ⭐
- [贡献指南](docs/development/contributing.md) - 开发规范 ⭐

#### 开发指南
- [快速开始](docs/development/getting-started.md) - 环境搭建
- [API开发指南](docs/development/api-development.md) - API开发规范
- [前端开发指南](docs/development/frontend-development.md) - 前端开发规范

#### 测试文档
- [E2E测试指南](docs/testing/e2e-testing-guide.md) - E2E测试规范
- [快速测试指南](docs/testing/quick-test-guide.md) - PATH问题排查
- [TDD实践](docs/development/tdd-practices.md) (TODO) - TDD最佳实践

### Claude Code Skills

项目提供了专门的 Claude Code Skills 来简化开发工作流。

| 命令 | 用途 | 修改代码 |
|------|------|---------|
| `/start-app` | 启动 Flask 服务器 | 否 |
| `/review-code` | 检查代码规范合规性 | 否 |
| `/analyze-code` | 快速代码质量评分 | 否 |
| `/code-audit` | 深度技术债务分析 | 否 |
| `/optimize-code` | 应用代码优化 | 是 |
| `/update-docs` | 更新项目文档 | 是 |

**日常开发流程**:
```bash
/start-app          # 启动服务器
/analyze-code       # 快速质量检查
/test-runner        # 运行测试
/review-code        # 规范检查
/update-docs        # 更新文档
```

---

## 快速参考

### 项目路径

- **项目根目录**: `/Users/mckenzie/Documents/event2table`
- **后端代码**: `/Users/mckenzie/Documents/event2table/backend`
- **前端代码**: `/Users/mckenzie/Documents/event2table/frontend`
- **测试代码**: `/Users/mckenzie/Documents/event2table/test`
- **文档目录**: `/Users/mckenzie/Documents/event2table/docs`

### 关键配置

- **数据库**: `dwd_generator.db`
- **测试数据库**: `test/test_database.db`
- **配置目录**: `config/`
- **日志目录**: `logs/`
- **上传目录**: `uploads/`
- **输出目录**: `output/`

### 端口信息

- **后端服务**: `http://127.0.0.1:5001`
- **前端开发**: `http://localhost:5173`

### 环境变量

- `FLASK_ENV`: testing/development/production
- `FLASK_SECRET_KEY`: Flask密钥（生产环境必须设置）
- `FLASK_DEBUG`: 调试模式（生产环境必须为False）
- `ENVIRONMENT`: 环境（development/production）

---

**文档版本**: 7.2
**最后更新**: 2026-02-12
**维护者**: Event2Table Development Team

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 7.3 | 2026-02-12 | 新增文档组织规范章节，重组文档结构，修复路径引用 |
| 7.2 | 2026-02-12 | 新增环境问题排查章节，记录 PATH 问题及解决方案 |
| 7.1 | 2026-02-11 | 建立强制 E2E 测试流程 |
| 7.0 | 2026-02-10 | 完善分层架构和 TDD 开发规范 |
