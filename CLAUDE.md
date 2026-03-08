# Event2Table - 开发规范

> **版本**: 7.9.0 | **最新优化**: 项目管理最佳实践 | **最后更新**: 2026-03-02
>
> **🆕 最新变更**: 后端架构全面优化完成 - Phase 1-4 (2026-03-01)
> **🆕 最新变更**: Entity架构迁移 + DDD清理完成 (2026-02-26)
> **🆕 最新变更**: 缓存系统文档完善 - 7份新文档 + CLAUDE.md开发规范 (2026-02-25)
> **🆕 最新变更**: 批量删除事件修复 + Dashboard统计准确性修复 + 环境设置规范强化 (2026-02-23)
> **🆕 最新变更**: 后端优化完成 - 安全加固、性能优化、架构重构 (2026-02-20)
> **🆕 最新变更**: Input组件架构重构与游戏编辑UX优化 (2026-02-22)
> **🆕 最新变更**: 事件节点构建器6大问题修复 (2026-02-18)

---

⚠️ **环境设置：必须先激活虚拟环境**
---
**在执行任何Python命令前，必须先激活虚拟环境**：

```bash
source backend/venv/bin/activate
```

**激活后**：
- ✅ 使用 `python3` 执行Python脚本
- ✅ 使用 `pip3` 安装依赖
- ❌ 不要使用 `python`（会使用系统Python，可能导致依赖问题）

**检查虚拟环境是否激活**：
```bash
which python3  # 应该显示: /Users/mckenzie/Documents/event2table/backend/venv/bin/python3
```

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

## 问题修复记录

完整的问题修复记录已迁移至 [CHANGELOG.md](/CHANGELOG.md)

**快速链接**:
- [性能优化分析 (2026-03-05)](CHANGELOG.md#800-2026-03-05) - 828个性能问题自动分类
- [文档整合 (2026-03-05)](CHANGELOG.md#801) - 722个文档整合与经验提取
- [后端架构优化 (2026-03-01)](CHANGELOG.md#781-2026-03-01) - Phase 1-4全面优化
- [Entity架构迁移 (2026-02-26)](CHANGELOG.md#652-2026-02-26) - DDD清理完成
- [缓存系统文档 (2026-02-25)](CHANGELOG.md#770-2026-02-25) - 7份新文档
- [批量删除和Dashboard修复 (2026-02-23)](CHANGELOG.md#771-2026-02-23) - 3个关键修复
- [后端优化 (2026-02-20)](CHANGELOG.md) - 6阶段全面优化
- [Input组件重构 (2026-02-22)](CHANGELOG.md#760-2026-02-22) - 架构与UX优化
- [Redis缓存清理 (2026-02-22)](CHANGELOG.md#751-2026-02-22) - 数据一致性
- [事件节点构建器 (2026-02-18)](CHANGELOG.md#741-2026-02-18) - 6大问题修复

---

## 版本历史摘要

**最近重要版本**:
- **v8.0.0** (2026-03-05): 文档整合 + 性能优化分析
- **v7.9.0** (2026-03-02): 项目管理最佳实践
- **v7.8.0** (2026-03-01): 后端架构全面优化 (Phase 1-4)
- **v7.7.0** (2026-02-26): Entity架构迁移 + DDD清理

完整版本历史请参阅 [CHANGELOG.md](/CHANGELOG.md)

---

## Critical Rules → 关键规则（必读）

### 🚨 STAR001 游戏保护规则 ⚠️ **极其重要 - 强制执行**

> **🚨 2026-02-17 新增**: 禁止删除或修改STAR001 (GID: 10000147) 的任何数据

**核心规则**：
- ❌ **绝对禁止** 删除 GID 10000147 (STAR001) 的游戏、事件、参数
- ✅ **所有测试** 必须使用 90000000+ 范围的测试GID
- ✅ 测试前必须确认不包含生产数据
- 📖 完整规则: [docs/development/STAR001-GAME-PROTECTION.md](docs/development/STAR001-GAME-PROTECTION.md)

**测试GID规范**：
```python
# ✅ 正确：使用测试GID
TEST_GID_START = 90000000
test_gid = 90000001

# ❌ 错误：使用STAR001
game_gid = 10000147  # 禁止！
```

**违反后果**：
- 数据丢失（已有先例）
- 测试失败
- 必须手动恢复数据

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

**3. SQLValidator强制使用**：
> **🚨 所有动态SQL标识符必须使用SQLValidator验证**

```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 正确：验证动态表名
table_name = request.args.get("table")
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table}"

# ✅ 正确：验证动态列名
column = request.args.get("column")
validated_column = SQLValidator.validate_column_name(column)

# ✅ 正确：使用白名单验证
ALLOWED_FIELDS = {"name", "created_at", "id"}
SQLValidator.validate_field_whitelist(sort_by, ALLOWED_FIELDS)

# ❌ 错误：未验证的动态标识符
query = f"SELECT * FROM {table_name} WHERE {column} = ?"  # SQL注入风险！
```

**详细指南**: [sql-validator-guidelines.md](docs/development/sql-validator-guidelines.md)

**4. HQL生成器安全**：
> **🚨 HQL（HiveQL）生成器用于构建Hive查询字符串，必须遵循特殊安全规范**

```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 正确：验证HQL标识符
table_name = SQLValidator.validate_table_name("ieu_ods.ods_10000147_all_view")
field_name = SQLValidator.validate_column_name("role_id")

# ✅ 正确：使用操作符白名单
VALID_OPERATORS = ["=", "!=", "<", ">", "<=", ">=", "LIKE"]
if operator not in VALID_OPERATORS:
    raise ValueError(f"Invalid operator: {operator}")

# ✅ 正确：验证自定义表达式
DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "--", ";"]
expr_upper = expression.upper()
for keyword in DANGEROUS_KEYWORDS:
    if keyword in expr_upper:
        raise ValueError(f"Dangerous keyword '{keyword}' found")

# ❌ 错误：直接拼接用户输入到HQL
hql = f"SELECT * FROM {user_table} WHERE {user_field} {user_operator} '{user_value}'"
```

**核心原则**：
- HQL用于生成查询字符串（非直接执行），防止语法破坏
- 所有标识符必须使用`SQLValidator`验证
- 操作符必须使用白名单（不用黑名单）
- 自定义表达式必须检测危险关键字
- 占位符值必须验证格式（如：日期格式`YYYYMMDD`）

**详细指南**：
- [HQL安全开发指南](docs/hql/hql-security-guide.md) - HQL安全规范 ⭐
- [HQL注入防护示例](docs/hql/hql-injection-prevention.md) - 实际漏洞案例 ⭐

**5. 错误处理不暴露敏感信息**：
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
- [ ] SQLValidator验证（动态标识符）
- [ ] 输出编码（JSON响应，不暴露内部信息）
- [ ] 错误处理（适当的HTTP状态码：400/404/409/500）

---

### GraphQL类型同步规范 ⚠️ **极其重要 - 2026-03-08新增**

> **🚨 前端TypeScript类型必须与后端GraphQL schema保持一致**
> **🆕 更新 (2026-03-08)**: 建立GraphQL类型同步规范，防止前后端类型不一致导致的运行时错误

#### 核心原则

**类型一致性**：前端TypeScript枚举和类型必须完全匹配后端GraphQL schema定义

**为什么重要**：
- 类型不匹配会导致GraphQL 400错误（Bad Request）
- 枚举值大小写或格式不一致会直接导致API调用失败
- 开发时难以发现，只在运行时暴露问题

#### GraphQL枚举命名规范

**后端GraphQL Schema**：
```graphql
# ✅ 正确：UPPER_SNAKE_CASE（GraphQL标准）
enum HqlJoinType {
  LEFT_JOIN
  RIGHT_JOIN
  INNER_JOIN
  FULL_JOIN
}

enum NodeType {
  EVENT
  JOIN
  UNION
  FILTER
}
```

**前端TypeScript**：
```typescript
// ✅ 正确：完全匹配GraphQL schema（大小写、格式）
export enum HqlJoinType {
  LEFT_JOIN = "LEFT_JOIN",
  RIGHT_JOIN = "RIGHT_JOIN",
  INNER_JOIN = "INNER_JOIN",
  FULL_JOIN = "FULL_JOIN"
}

// ❌ 错误：使用连字符导致400错误
export enum HqlJoinType {
  LEFT_JOIN = "LEFT-JOIN",      // GraphQL无法解析
  RIGHT_JOIN = "RIGHT-JOIN"     // GraphQL无法解析
}
```

**错误示例**：
```typescript
// ❌ 错误：枚举值不匹配
const mutation = CREATE_EVENT_NODE({
  variables: {
    input: {
      joinType: "LEFT-JOIN"  // GraphQL期望: LEFT_JOIN
    }
  }
});

// 错误信息：Enum 'HqlJoinType' cannot represent value: 'LEFT-JOIN'
// HTTP状态码：400 Bad Request
```

#### Pydantic模型完整性

**后端Pydantic Schema** (`backend/models/schemas.py`)：
```python
from pydantic import BaseModel, Field
from typing import Optional

class EventNodeInput(BaseModel):
    """Event node creation/update input"""

    # ✅ 所有字段必须在Pydantic模型中定义
    id: Optional[int] = Field(None, description="Node ID")
    node_type: str = Field(..., description="Node type")
    event_type: Optional[str] = Field(None, description="Event type")  # ← 必须定义
    table_name: Optional[str] = Field(None, description="Table name")
    join_type: Optional[str] = Field(None, description="Join type")
```

**Service层访问**：
```python
def create_event_node(self, node_data: EventNodeInput):
    # ✅ 安全：所有字段已在Pydantic模型中定义
    event_type = node_data.event_type  # 字段存在，无AttributeError

    # ❌ 危险：如果event_type未定义，会抛出AttributeError
    # AttributeError: 'EventNodeInput' object has no attribute 'event_type'
```

#### 自动化类型生成

**使用graphql-codegen生成类型**：

```bash
# 安装graphql-codegen
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations

# 配置文件：codegen.yml
schema:
  - http://127.0.0.1:5001/api/graphql

documents:
  - "frontend/src/graphql/**/*.tsx"

generates:
  frontend/src/graphql/generated-types.ts:
    plugins:
      - typescript
      - typescript-operations
```

**生成类型**：
```bash
# 从GraphQL schema自动生成TypeScript类型
npx graphql-codegen

# 添加到package.json scripts
"scripts": {
  "generate:types": "graphql-codegen",
  "predev": "npm run generate:types"  # 开发前自动生成
}
```

**使用生成的类型**：
```typescript
// frontend/src/canvas/components/EventNodeBuilder.tsx
import { CreateEventNodeMutation, HqlJoinType } from '@/graphql/generated-types';

function EventNodeBuilder() {
  const [createNode] = useMutation(CREATE_EVENT_NODE);

  const handleCreate = async () => {
    // ✅ 类型安全：所有类型从GraphQL schema生成
    const result = await createNode({
      variables: {
        input: {
          nodeType: NodeType.Join,
          joinType: HqlJoinType.LeftJoin  // 枚举类型安全
        }
      }
    });
  };
}
```

#### 代码审查检查清单

**后端检查**：
- [ ] Pydantic模型是否包含所有Service层访问的字段？
- [ ] 所有字段是否有正确的类型注解（Optional[str]、str、int）？
- [ ] GraphQL枚举是否使用UPPER_SNAKE_CASE？
- [ ] GraphQL枚举值是否与Pydantic模型一致？

**前端检查**：
- [ ] TypeScript枚举是否完全匹配GraphQL schema（大小写敏感）？
- [ ] 是否使用graphql-codegen生成类型？
- [ ] 是否避免硬编码枚举字符串？
- [ ] 是否使用生成的枚举类型而非字符串字面量？

**集成检查**：
- [ ] 运行API契约测试：`python backend/scripts/test/api_contract_test.py`
- [ ] 生成最新类型：`npm run generate:types`
- [ ] 测试GraphQL mutation（有效枚举值）
- [ ] 测试GraphQL mutation（无效枚举值，应失败）

#### 常见错误

**错误1: 枚举值格式不匹配**
```typescript
// ❌ 错误：连字符 vs 下划线
joinType: "LEFT-JOIN"     // 错误
joinType: "LEFT_JOIN"     // 正确
```

**错误2: Pydantic字段缺失**
```python
# ❌ 错误：Service层访问未定义的字段
class EventNodeInput(BaseModel):
    node_type: str
    # 缺少event_type字段

# Service层抛出AttributeError
event_type = node_data.event_type  # AttributeError
```

**错误3: 硬编码枚举字符串**
```typescript
// ❌ 错误：硬编码字符串，容易拼写错误
joinType: "LEFT_JION"  // 拼写错误

// ✅ 正确：使用生成的枚举
joinType: HqlJoinType.LeftJoin  // 类型安全
```

#### 相关文档

- [Event Node Builder错误修复](docs/lessons-learned/event-node-builder-errors.md) - GraphQL类型不匹配案例 ⭐
- [GraphQL开发指南](docs/development/graphql-development-guide.md) - 完整GraphQL开发规范 ⭐
- [API契约测试规范](#api契约测试规范-⚠️-极其重要---强制执行) - API契约一致性测试
- [React最佳实践](docs/lessons-learned/react-best-practices.md) - React组件类型安全

---

### 数据库文件位置规范 ⚠️ **极其重要 - 强制执行**

> **🚨 所有数据库文件必须放在 data/ 目录，禁止在根目录或其他位置创建数据库文件**
> **🆕 更新 (2026-02-14)**: 建立数据库文件位置规范，防止数据库文件散落导致管理混乱

#### 核心原则

**数据库文件必须统一管理**：
```bash
# ✅ 正确：数据库文件位置
data/
├── dwd_generator.db          # 生产数据库（9.3M）
├── dwd_generator.db-wal      # 生产数据库WAL文件（664K）
├── dwd_generator.db-shm      # 生产数据库SHM文件（32K）
├── dwd_generator_dev.db      # 开发数据库
├── test_database.db          # 测试数据库

# ❌ 错误：在以下位置创建数据库文件
/dwd_generator.db                    # 根目录
/backend/core/config/dwd_generator.db # backend目录
/scripts/setup/dwd_generator.db     # scripts目录
```

#### 应用配置指向 data/ 目录

**配置文件**：`backend/core/config/config.py`
```python
# ✅ 正确的数据库路径配置
DB_PATH = BASE_DIR / "data" / "dwd_generator.db"
TEST_DB_PATH = BASE_DIR / "data" / "test_database.db"
DEV_DB_PATH = BASE_DIR / "data" / "dwd_generator_dev.db"

def get_db_path():
    """根据环境返回正确的数据库路径"""
    if os.environ.get("FLASK_ENV") == "testing":
        return TEST_DB_PATH  # data/test_database.db
    if os.environ.get("FLASK_ENV") == "development":
        return DEV_DB_PATH   # data/dwd_generator_dev.db
    return DB_PATH          # data/dwd_generator.db
```

#### 为什么要强制此规范？

**1. 数据隔离和管理**
- 生产数据库、开发数据库、测试数据库完全隔离
- 避免误操作导致数据污染
- 便于数据库备份、迁移和清理

**2. .gitignore 配置统一**
```gitignore
# .gitignore
*.db
*.db-shm
*.db-wal
data/*.db  # 确保data/目录下的数据库也被忽略
```

**3. 历史问题教训**
- 根目录的 `dwd_generator.db` (4.0K) vs `data/dwd_generator.db` (9.3M)
- 过时文件导致应用读取错误数据
- WAL文件为空（0B）说明数据库已废弃

**4. 防止文件散落**
- 根目录：仅保留 README.md, CHANGELOG.md, CLAUDE.md, LICENSE
- backend/、scripts/ 目录：不应包含数据库文件
- 数据库文件仅存在于 data/ 目录

#### 开发规范

**禁止行为**：
- ❌ 在根目录创建 `*.db` 文件
- ❌ 在 backend/ 目录创建 `*.db` 文件
- ❌ 在 scripts/ 目录创建 `*.db` 文件
- ❌ 在任何非 data/ 目录创建 `*.db` 文件
- ❌ 在代码中使用相对路径创建数据库

**正确做法**：
```python
# ✅ 正确：使用配置文件中的路径
from backend.core.config.config import DB_PATH, TEST_DB_PATH

# 连接数据库
conn = get_db_connection(DB_PATH)  # data/dwd_generator.db

# ❌ 错误：直接使用相对路径
conn = sqlite3.connect("dwd_generator.db")  # 会在当前目录创建！
```

#### 代码审查强制检查项

**每次代码审查必须检查**：
- [ ] 是否在非 data/ 目录创建数据库文件
- [ ] 是否使用相对路径连接数据库
- [ ] 是否使用配置文件中的 DB_PATH 常量
- [ ] 所有数据库连接是否使用 `get_db_connection(DB_PATH)`

**违规后果**：
- ⚠️ 数据库文件散落在各目录
- ⚠️ 生产数据与测试数据混淆
- ⚠️ 数据库版本控制混乱
- ⚠️ .gitignore 失效导致数据库被提交
- ❌ Code Review必须拒绝

#### Pre-commit Hook 自动检测

**安装 pre-commit hook**：
```bash
# 复制 pre-commit hook 到 .git/hooks/
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 或使用脚本安装
python scripts/git-hooks/install_hooks.py
```

**Hook 功能**：
- 每次提交前自动检测错误放置的数据库文件
- 发现 `*.db` 文件在 data/ 之外，立即阻止提交
- 显示所有违规文件列表

---

### CORS跨域配置规范 ⚠️ **极其重要 - 2026-03-04新增**

> **🚨 所有前后端分离项目必须正确配置CORS**
> **🆕 更新 (2026-03-04)**: 建立CORS配置规范，解决前后端跨域请求问题

#### 核心原则

**CORS (Cross-Origin Resource Sharing)** 是浏览器的安全机制，用于限制跨域HTTP请求。

**问题表现**：
```
Access to fetch at 'http://127.0.0.1:5001/api/graphql' from origin 'http://localhost:5173'
has been blocked by CORS policy: Response to preflight request doesn't pass access control check:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**根本原因**：
- 前端（http://localhost:5173）与后端（http://127.0.0.1:5001）是不同的源（Origin）
- 浏览器默认阻止跨域请求，除非后端明确允许

#### Flask-CORS 配置

**1. 安装依赖**：

```bash
# 添加到 requirements.txt
echo "Flask-CORS==6.0.2" >> requirements.txt

# 安装包
source backend/venv/bin/activate
pip install flask-cors
```

**2. 在 web_app.py 中配置 CORS**：

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration - Allow frontend-originated requests
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/api/graphql": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
logger.info("✅ CORS已启用: 允许来自 localhost:5173 的请求")
```

**3. 重启后端服务器**：

```bash
# 停止旧服务器
kill <旧进程PID>

# 启动新服务器
source backend/venv/bin/activate
nohup python web_app.py > logs/backend.log 2>&1 &
```

#### CORS 配置说明

**resources 参数**：
- `r"/api/*"` - 匹配所有 `/api/` 开头的路径
- `r"/api/graphql"` - 匹配 GraphQL 端点（更具体的规则优先）

**origins 参数**：
- `http://localhost:5173` - Vite 开发服务器
- `http://127.0.0.1:5173` - 本地回环地址
- 生产环境应添加实际域名，如 `https://event2table.com`

**methods 参数**：
- `GET` - 读取数据
- `POST` - 创建数据
- `PUT` - 更新数据
- `DELETE` - 删除数据
- `OPTIONS` - CORS preflight 请求（必需）

**allow_headers 参数**：
- `Content-Type` - 请求内容类型
- `Authorization` - 认证令牌

#### 验证 CORS 配置

**方法 1: 使用 curl 验证 preflight 请求**：

```bash
curl -s -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://127.0.0.1:5001/api/graphql -I | grep -i "access-control"
```

**预期输出**：
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, OPTIONS, POST
Access-Control-Allow-Headers: Content-Type, Authorization
```

**方法 2: 检查后端日志**：

```bash
tail -20 logs/backend.log | grep CORS
```

**预期输出**：
```
2026-03-04 13:19:13 - __main__ - INFO - ✅ CORS已启用: 允许来自 localhost:5173 的请求
```

**方法 3: 浏览器控制台检查**：

1. 打开浏览器开发者工具（F12）
2. 访问 `http://localhost:5173`
3. 查看 Console 标签页
4. 确认无 CORS 错误

#### 生产环境配置

**生产环境应使用实际的域名**：

```python
import os

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://event2table.com')

CORS(app, resources={
    r"/api/*": {
        "origins": [FRONTEND_URL],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**环境变量配置**：

```bash
# .env 或生产环境变量
FRONTEND_URL=https://event2table.com
```

#### 常见问题

**Q1: CORS 配置后仍然报错？**

A: 检查以下几点：
1. ✅ 后端服务器是否重启？
2. ✅ CORS 配置的 origins 是否包含前端地址？
3. ✅ 浏览器缓存是否清理？（Ctrl+Shift+R 强制刷新）
4. ✅ 浏览器控制台的错误信息是什么？

**Q2: 如何允许多个前端域名？**

A: 在 origins 列表中添加多个域名：
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "https://event2table.com",
            "https://staging.event2table.com"
        ],
        # ...
    }
})
```

**Q3: 生产环境是否应该允许所有来源？**

A: ❌ **强烈不推荐**：
```python
# ❌ 危险：允许任何来源
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ✅ 安全：只允许特定域名
CORS(app, resources={r"/api/*": {"origins": ["https://event2table.com"]}})
```

#### 代码审查强制检查项

**每次配置 CORS 时必须检查**：
- [ ] Flask-CORS 是否已安装？（requirements.txt）
- [ ] web_app.py 是否导入 CORS？
- [ ] CORS 配置的 origins 是否包含前端地址？
- [ ] 是否配置了必要的 HTTP methods？
- [ ] 是否配置了必要的 headers？
- [ ] 后端服务器是否重启？
- [ ] 是否使用 curl 验证 preflight 请求？
- [ ] 生产环境是否使用实际域名而非 `*`？

**违规后果**：
- ⚠️ 前端无法访问后端 API
- ⚠️ GraphQL 请求被浏览器阻止
- ⚠️ 用户看到空白页面或加载失败
- ⚠️ CORS 错误会暴露在浏览器控制台
- ❌ Code Review必须拒绝

#### 相关文档

- [Flask-CORS 官方文档](https://flask-cors.readthedocs.io/)
- [MDN - CORS 详解](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [前端加载问题修复报告](docs/reports/2026-03-04/COMPLETE-FIX-SUMMARY.md)

---

## 经验文档快速查找 ⭐ **极其重要 - 2026-03-08更新**

> **🚨 所有项目经验已整合到经验文档系统，避免重复，持续更新**

### 核心经验文档（docs/lessons-learned/）

| 场景 | 查看文档 | 优先级 |
|------|----------|--------|
| **🚨 React应用挂载** | [测试指南 - React挂载诊断](docs/lessons-learned/testing-guide.md#react应用挂载问题诊断) | P0 |
| **🔍 Chrome DevTools调试** | [测试指南 - MCP调试法](docs/lessons-learned/testing-guide.md#chrome-devtools-mcp测试流程) | P0 |
| **📝 mypy类型错误** | [Python开发 - mypy合规](docs/lessons-learned/python-development.md#mypy---strict合规) | P0 |
| **🚨 React Hooks错误** | [React最佳实践 - Hooks规则](docs/lessons-learned/react-best-practices.md#react-hooks-规则) | P0 |
| **⚡ Vite-Apollo兼容性** | [React最佳实践 - Vite兼容性](docs/lessons-learned/react-best-practices.md#vite与apollo-client兼容性) | P1 |
| **🐌 页面加载超时** | [React最佳实践 - Lazy Loading](docs/lessons-learned/react-best-practices.md#lazy-loading最佳实践) | P0 |
| **💾 缓存失效分析** | [性能模式 - 缓存失效](docs/lessons-learned/performance-patterns.md#缓存失效分析) | P0 |
| **🚀 并行优化策略** | [性能模式 - 并行优化](docs/lessons-learned/performance-patterns.md#并行优化策略) | P0 |
| **⚡ DataLoader批量查询** | [性能模式 - DataLoader优化](docs/lessons-learned/performance-patterns.md#dataloader批量查询优化) 🆕 | P0 |
| **🔢 批量操作优化** | [性能模式 - 批量操作](docs/lessons-learned/performance-patterns.md#批量操作优化) 🆕 | P0 |
| **⏱️ TTL分层设置** | [性能模式 - TTL分层](docs/lessons-learned/performance-patterns.md#ttl分层设置策略) 🆕 | P0 |
| **🎯 Entity架构优化** | [性能模式 - Entity优化](docs/lessons-learned/performance-patterns.md#entity架构下的性能优化) 🆕 | P1 |
| **🔍 控制台错误检测** | [测试指南 - 控制台错误](docs/lessons-learned/testing-guide.md#控制台错误检测的完整工作流) 🆕 | P0 |
| **⚡ Dashboard实时优化** | [测试指南 - Dashboard优化](docs/lessons-learned/testing-guide.md#dashboard实时优化) 🆕 | P1 |
| **🔧 缓存失效装饰器** | [测试指南 - 缓存失效](docs/lessons-learned/testing-guide.md#缓存失效装饰器的自动化实现) 🆕 | P1 |
| **🧪 修复验证流程** | [测试指南 - 修复验证](docs/lessons-learned/testing-guide.md#e2e测试中的代码修复验证流程) 🆕 | P0 |
| **📦 DataLoader实施** | [API设计 - DataLoader清单](docs/lessons-learned/api-design-patterns.md#graphql-dataloader实施清单) 🆕 | P0 |
| **🔢 批量查询模式** | [API设计 - 批量查询](docs/lessons-learned/api-design-patterns.md#批量查询优化模式) 🆕 | P0 |
| **🔑 缓存键设计** | [API设计 - 缓存键规范](docs/lessons-learned/api-design-patterns.md#缓存键设计规范) 🆕 | P0 |
| **❌ GraphQL 400错误** | [API设计 - 400诊断](docs/lessons-learned/api-design-patterns.md#graphql-400错误诊断) 🆕 | P0 |
| **🔒 SQL注入风险** | [安全要点 - SQL注入防护](docs/lessons-learned/security-essentials.md#sql注入防护) | P0 |
| **🧪 E2E测试失败** | [测试指南 - E2E测试](docs/lessons-learned/testing-guide.md#e2e测试) | P0 |
| **⚡ 查询性能差** | [性能模式 - N+1查询](docs/lessons-learned/performance-patterns.md#n1查询优化) | P0 |
| **🗄️ 数据库迁移** | [数据库模式 - game_gid](docs/lessons-learned/database-patterns.md#game_gid迁移) | P0 |
| **🔧 API错误处理** | [API设计模式 - 错误处理](docs/lessons-learned/api-design-patterns.md#错误处理) | P0 |
| **🐛 Bug调试方法** | [调试技能](docs/lessons-learned/debugging-skills.md) | P1 |
| **🚀 并行开发任务** | [项目管理 - 并行开发策略](docs/lessons-learned/project-management.md#并行开发策略) | P0 |
| **🏗️ 大规模重构** | [项目管理 - 分阶段重构](docs/lessons-learned/project-management.md#分阶段重构策略) | P0 |
| **🚢 部署与运维** | [部署与运维](docs/lessons-learned/deployment-operations.md) | P1 |

### 完整经验文档索引

- **[经验文档索引](docs/lessons-learned/README.md)** - 所有经验文档的导航中心 ⭐
- **[React最佳实践](docs/lessons-learned/react-best-practices.md)** - Hooks规则、Lazy Loading、Vite兼容性
- **[测试指南](docs/lessons-learned/testing-guide.md)** - E2E测试、控制台错误检测、修复验证流程 🆕
- **[Python开发](docs/lessons-learned/python-development.md)** - mypy类型安全、GenericRepository
- **[安全要点](docs/lessons-learned/security-essentials.md)** - XSS防护、SQL注入、输入验证
- **[性能模式](docs/lessons-learned/performance-patterns.md)** - DataLoader、批量操作、TTL分层、并行优化 🆕
- **[数据库模式](docs/lessons-learned/database-patterns.md)** - game_gid使用、事务、迁移
- **[API设计模式](docs/lessons-learned/api-design-patterns.md)** - DataLoader实施、批量查询、缓存键设计 🆕
- **[调试技能](docs/lessons-learned/debugging-skills.md)** - Chrome DevTools MCP、Subagent分析
- **[重构检查清单](docs/lessons-learned/refactoring-checklist.md)** - TDD、代码审查、技术债务
- **[项目管理](docs/lessons-learned/project-management.md)** - 并行开发、分阶段重构、零破坏性变更
- **[部署与运维](docs/lessons-learned/deployment-operations.md)** - 部署流程、运维监控、故障排查

### 经验文档使用说明

**为什么建立经验文档系统**：
- ✅ 整合了857个文档的精华经验，避免重复 (+22个新经验点，2026-03-08更新)
- ✅ 文档减少59%，经验整合率提升到95%+
- ✅ 集中管理，便于查找和维护
- ✅ 持续更新，每次问题修复后立即更新

**最新更新 (2026-03-08)**：
- 🆕 **性能优化**: DataLoader批量查询、批量操作、TTL分层、Entity优化 (8个新经验)
- 🆕 **E2E测试**: 控制台错误检测、Dashboard实时优化、缓存失效装饰器 (7个新经验)
- 🆕 **GraphQL**: DataLoader实施、批量查询、缓存键设计、400错误诊断 (7个新经验)

**如何使用**：
1. **遇到问题** → 先查阅经验文档，看是否有类似问题
2. **修复问题后** → 提取经验，更新对应经验文档
3. **Code Review** → 检查是否违反经验文档中的规范

**经验贡献**：
- 修复问题后，请更新对应经验文档
- 使用统一的经验模板（见经验文档索引）
- 在CLAUDE.md中添加简短记录和链接

---

## 文档组织规范 ⚠️ **极其重要**

> **🚨 所有文档必须按照本规范放置在正确的位置**
> **🆕 更新 (2026-02-24)**: 建立经验文档系统，整合399个文档

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

> **🚨 测试文件必须按照以下规范放置在正确的位置**
> **🆕 更新 (2026-02-13)**: 建立frontend/test/、backend/test/目录结构

### 核心原则

**测试靠近被测代码**：
- 前端测试：frontend/test/ (包含E2E测试、单元测试）
- 后端测试：backend/test/ (包含单元测试、集成测试)

### 前端测试（frontend/test/）

**目录结构**：
```
frontend/
├── src/
├── tests/              # 现有前端单元测试（Vitest）
│   └── unit/
└── test/              # ⭐ 新增：前端E2E测试
    ├── e2e/            # End-to-End 测试
    │   ├── critical/    # 关键流程测试
    │   ├── smoke/       # 冒烟测试
    │   ├── api-contract/ # API契约测试
    │   ├── helpers/      # 测试辅助工具
    │   ├── playwright.config.ts
    │   └── output/       # 测试输出
    └── package.json    # 测试配置（可选）
```

**运行前端测试**：
```bash
cd frontend

# 单元测试（Vitest）
npm run test:unit

# E2E测试（Playwright）
npm run test:e2e
npm run test:e2e:ui       # UI模式
npm run test:e2e:debug    # 调试模式
npm run test:e2e:critical # 关键流程测试
npm run test:e2e:smoke    # 冒烟测试
```

### 后端测试（backend/test/）

**目录结构**：
```
backend/
├── api/
├── core/
├── models/
├── services/
└── test/              # ⭐ 新增：后端测试
    ├── unit/           # 单元测试
    │   ├── api/
    │   ├── core/
    │   ├── diagnostics/
    │   ├── integration/
    │   ├── repositories/
    │   ├── schemas/
    │   └── services/
    └── integration/    # 集成测试
        ├── api/
        ├── database/
        └── workflows/
    └── pytest.ini      # Pytest配置
```

**运行后端测试**：
```bash
# 所有后端测试
pytest backend/test/

# 单元测试
pytest backend/test/unit/

# 集成测试
pytest backend/test/integration/

# 生成覆盖率报告
pytest backend/test/ --cov=backend --cov-report=html
```

### 测试输出统一管理 ⚠️ **极其重要**

> **🚨 所有测试工具的输出必须重定向到各模块的output/目录**

#### 前端测试输出
- Playwright: `frontend/test/e2e/output/playwright-report/`
- Vitest: `frontend/test/output/` (如果使用)
- Coverage: `frontend/test/output/coverage/`

#### 后端测试输出
- Pytest: `backend/test/output/coverage/`
- 测试报告: `backend/test/output/reports/`

### 迁移说明

2026-02-13: 测试文件重组
- E2E测试从 test/e2e/ 迁移到 frontend/test/e2e/
- 后端单元测试从 test/unit/backend/ 迁移到 backend/test/unit/
- 后端集成测试从 test/integration/ 迁移到 backend/test/integration/

### 禁止行为

- ❌ 在根目录 test/ 放置新的测试（使用 frontend/test/ 或 backend/test/）
- ❌ 在 frontend/tests/ 放置E2E测试（使用 frontend/test/e2e/）
- ❌ 在 test/e2e/ 或 test/unit/ 放置新的测试（已迁移）

### 验证

运行测试前验证目录结构：
```bash
# 验证前端测试目录
ls frontend/test/e2e/critical/
ls frontend/test/e2e/smoke/

# 验证后端测试目录
ls backend/test/unit/api/
ls backend/test/integration/
```

---

## 文档生命周期管理规范 ⭐ **2026-03-02新增**

> **🚨 所有文档必须按照生命周期进行管理，避免文档膨胀和过时**
> **🆕 更新 (2026-03-02)**: 建立文档生命周期管理系统，确保文档质量和可维护性

### 三阶段文档生命周期

**1. 活跃文档** (`docs/`)
- 经常更新
- 反映当前最佳实践
- 包括：开发指南、测试文档、API文档、经验文档

**2. 归档文档** (`docs/archive/`)
- 按主题分类
- 历史参考价值
- 组织结构：`archive/{主题}/{日期}/`

**3. 临时文档**
- 短期使用
- 完成后删除或归档

### 文档更新流程

**每次代码变更后**:
1. 更新API文档（如果修改了API）
2. 更新架构文档（如果修改了架构）
3. 更新经验文档（如果学到了新经验）
4. 提交文档和代码

**完成阶段时**:
1. 整理重复文档
2. 归档过时文档
3. 更新文档索引
4. 更新CLAUDE.md

### 经验贡献

**如何贡献经验**:
1. 修复问题后，提取经验
2. 使用统一的经验模板
3. 在CLAUDE.md中添加简短记录
4. 更新对应经验文档

### 归档策略

**6个月自动归档**:
- 报告文档：6个月后归档
- 测试文档：完成后归档
- 临时文档：完成后删除

**归档目录结构**:
```
docs/archive/
├── 2026/
│   ├── 02-february/     # 2月文档
│   ├── 03-march/        # 3月文档
│   └── ...
├── reports/             # 归档报告
├── testing/             # 归档测试文档
└── development/         # 归档开发文档
```

### 文档质量检查清单

**创建新文档前**:
- [ ] 确认文档类型（指南/报告/需求）
- [ ] 确认目标目录
- [ ] 使用标准命名格式（小写+连字符）
- [ ] 检查是否已有类似文档（避免重复）

**归档文档前**:
- [ ] 确认文档已过时或不再活跃
- [ ] 更新相关引用
- [ ] 添加归档日期说明
- [ ] 移动到正确归档目录

**删除文档前**:
- [ ] 确认无参考价值
- [ ] 检查是否有其他文档引用
- [ ] 确认可以安全删除

### 文档维护职责

**开发者职责**:
- 修改代码时同步更新文档
- 修复问题后贡献经验
- 定期检查文档准确性
- 归档过时文档

**文档审查**:
- Code Review时检查文档更新
- 每月文档质量审查
- 每季度文档整理归档

---

## 项目管理最佳实践 ⭐ **2026-03-02新增**

> **🚨 基于大规模重构和并行开发的经验总结**

### 并行开发策略 ⚠️ **P0极其重要**

**核心原则**: 独立任务并行执行，依赖任务串行执行

**并行开发模式**:
```python
# ✅ 正确：并行执行独立任务
# Phase 1-4 并行执行（4个独立subagents）
# - Phase 1: 紧急修复（games.py, hql_generation.py）
# - Phase 2: Service层重构（参数管理、HQL服务、Canvas服务）
# - Phase 3: 核心模块迁移（Join Configs、Event Categories）
# - Phase 4: 全面清理（V2文件、Repository层）

# 执行时间：4个Phase并行 → 总时间 = max(Phase时间) 而非 sum(Phase时间)
# 性能提升：~70%（串行需要12小时 → 并行需要3.5小时）
```

**识别独立任务**:
- ✅ 修改不同的文件（games.py vs events.py）
- ✅ 修改不同的模块（Service层 vs Repository层）
- ✅ 修改不同的功能域（缓存系统 vs 验证器）

**识别依赖任务**:
- ❌ Service层依赖Repository层 → 必须串行
- ❌ 前端依赖后端API → 必须串行
- ❌ 测试依赖实现 → 必须串行

### 大规模重构管理 ⚠️ **P0极其重要**

**分阶段执行策略**:

**Phase 0: 紧急修复** - 修复阻塞性问题（56+处异常信息泄露）
**Phase 1: 安全加固** - SQL注入、XSS防护
**Phase 2: 性能优化** - N+1查询、缓存优化
**Phase 3: 架构重构** - Service层、Repository层
**Phase 4: 代码质量** - 类型注解、错误处理
**Phase 5: 数据迁移** - game_gid迁移

**每个Phase都包含**:
1. 明确的目标和验收标准
2. 详细的实施清单
3. 测试验证步骤
4. 文档更新要求

### 零破坏性变更保证 ⚠️ **P0极其重要**

**核心原则**: 所有重构必须保持向后兼容

**实现策略**:
```python
# ✅ 正确：保留旧API作为废弃
def get_game_by_id(game_id):  # 旧API（保留但废弃）
    warnings.warn("Use get_game_by_gid instead", DeprecationWarning)
    game = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (game_id,))
    return get_game_by_gid(game['gid'])

def get_game_by_gid(game_gid):  # 新API
    return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))

# ✅ 正确：渐进式迁移
# 1. 添加新API（不删除旧API）
# 2. 更新调用方逐步使用新API
# 3. 标记旧API为废弃
# 4. 确认所有调用方已迁移
# 5. 删除旧API（至少6个月后）
```

**验证步骤**:
1. 运行所有单元测试（pytest）
2. 运行E2E测试（Playwright）
3. 检查API契约一致性
4. 验证前端功能正常
5. 检查日志中的废弃警告

### 文档驱动开发 ⭐ **P1重要**

**核心原则**: 文档与代码同步更新

**开发流程**:
```bash
# 1. 编写实施计划（先写文档）
# 创建计划文件：.claude/plans/feature-name.md

# 2. 按计划执行开发
# 每完成一个步骤，更新计划状态

# 3. 完成后更新文档
# - 更新API文档（如果修改了API）
# - 更新架构文档（如果修改了架构）
# - 提取经验到经验文档系统
# - 更新CLAUDE.md

# 4. 归档临时文档
# 将实施报告、测试报告移至 archive/
```

**经验贡献流程**:
1. 修复问题后，提取经验
2. 使用统一的经验模板更新经验文档
3. 在CLAUDE.md中添加简短记录和链接
4. 更新经验文档索引

### 代码审查清单

**并行开发检查**:
- [ ] 任务是否真正独立（无共享状态）？
- [ ] 是否有明确的依赖关系？
- [ ] 并行任务是否有冲突的文件修改？

**大规模重构检查**:
- [ ] 是否有详细的实施计划？
- [ ] 每个Phase是否有验收标准？
- [ ] 是否有回滚计划？

**零破坏性变更检查**:
- [ ] 是否保留了旧API？
- [ ] 是否标记了废弃警告？
- [ ] 是否运行了所有测试？

**文档更新检查**:
- [ ] 是否更新了相关文档？
- [ ] 是否提取了经验？
- [ ] 是否归档了临时文档？

### 相关经验文档

- **[经验文档 - 项目管理](docs/lessons-learned/project-management.md)** - 详细的项目管理经验
- **[经验文档 - 重构检查清单](docs/lessons-learned/refactoring-checklist.md)** - 重构最佳实践
- **[经验文档 - 调试技能](docs/lessons-learned/debugging-skills.md)** - 并行开发调试技巧

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

# ⚠️ 第一步：激活虚拟环境（必须！）
source backend/venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python3 scripts/setup/init_db.py

# 启动后端应用
python3 web_app.py  # http://127.0.0.1:5001

# 前端开发（另开终端）
cd frontend
npm install
npm run dev         # http://localhost:5173 (热更新)
npm run build       # 生产构建
npm run test        # 运行测试
```

**⚠️ 重要提示**：
- **必须先激活虚拟环境**：`source backend/venv/bin/activate`
- 激活后使用 `python3` 而不是 `python`
- 如果忘记激活虚拟环境，Python命令会找不到或使用错误的Python版本

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

### 分层架构设计（V7.8 - Entity架构）

项目采用**精简四层架构** + **统一Entity模型**，实现关注点分离和类型安全：

```
┌─────────────────────────────────────────────────────┐
│         API Layer (HTTP + GraphQL端点)               │
│  - RESTful API: backend/api/routes/                  │
│  - GraphQL API: backend/gql_api/ (V2)               │
│  - 处理HTTP请求/响应                                  │
│  - 参数解析和验证 (Pydantic Entity)                   │
│  - 调用Service层                                      │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           Service Layer (业务逻辑)                   │
│  backend/services/                                   │
│  - 实现业务逻辑                                       │
│  - 协调多个Repository                                │
│  - 缓存管理 (@cached, @cache_invalidate)             │
│  - Bloom Filter集成                                  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│        Repository Layer (数据访问)                   │
│  backend/models/repositories/                        │
│  - GenericRepository基类                             │
│  - 封装数据访问逻辑                                   │
│  - CRUD操作                                          │
│  - 返回Entity对象 (而非字典) ⭐                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│      Entity Layer (统一数据模型) ⭐                    │
│  - Pydantic Entity: backend/models/entities.py       │
│  - 单一真相来源 (Schema + Domain Model)              │
│  - 自动输入验证                                       │
│  - 序列化/反序列化                                    │
└─────────────────────────────────────────────────────┘
```

**架构迁移状态**: 6/8核心模块已迁移到Entity架构 (75%)
**详细信息**: [Entity迁移状态报告](docs/reports/2026-02-26/ENTITY-MIGRATION-STATUS.md)

#### 各层职责

**1. Entity层（统一数据模型）⭐**
```python
# backend/models/entities.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的模型定义
    所有模块(GameService/GameRepository/API)都使用这个模型
    """
    # 主键
    id: Optional[int] = None  # 数据库自增ID

    # 业务字段
    gid: str = Field(..., min_length=1, max_length=50, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$', description="ODS数据库")
    description: Optional[str] = Field(None, description="游戏描述")
    dwd_prefix: str = Field("dwd", description="DWD表前缀")

    # 元数据
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 关联数据
    event_count: Optional[int] = Field(0, description="事件数量统计")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html
        return html.escape(v.strip())
```

**2. Repository层（数据访问）**
```python
# backend/models/repositories/games.py
class GameRepository(GenericRepository):
    """游戏仓储类"""

    def find_by_gid(self, gid: int) -> Optional[GameEntity]:
        """根据业务GID查询游戏"""
        query = "SELECT * FROM games WHERE gid = ?"
        row = fetch_one_as_dict(query, (gid,))
        return GameEntity(**row) if row else None  # ⭐ 返回Entity

    def get_all_with_event_count(self) -> List[GameEntity]:
        """获取所有游戏及其事件数量"""
        query = """
            SELECT g.*, COUNT(DISTINCT le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.id = le.game_id
            GROUP BY g.id
        """
        rows = fetch_all_as_dict(query)
        return [GameEntity(**row) for row in rows]  # ⭐ 返回Entity列表
```

**3. Service层（业务逻辑）**
```python
# backend/services/games/game_service.py
from backend.core.cache.decorators import cached, cache_invalidate

class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    @cached(ttl=1800)  # ⭐ 缓存装饰器
    def get_games(self) -> List[GameEntity]:
        """获取所有游戏（带缓存）"""
        return self.game_repo.get_all()

    @cache_invalidate  # ⭐ 自动清理缓存
    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏

        业务逻辑：
        1. 验证gid唯一性
        2. 创建游戏
        3. 清理缓存
        """
        # 检查gid是否已存在
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game_data.model_dump())  # ⭐ Entity.model_dump()

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
        game_data = GameEntity(**data)  # ⭐ 使用Entity验证

        # 2. 调用Service层
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应
        return json_success_response(
            data=game.model_dump(),  # ⭐ Entity.model_dump()
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

### Entity架构关键优势

| 方面 | 旧DDD架构 | 新Entity架构 |
|------|-----------|-------------|
| **模型数量** | 3套 (Domain/Schema/Dict) | 1套统一Entity ✅ |
| **Repository返回** | Dict[str, Any] | Entity对象 ✅ |
| **类型安全** | 部分 | 完全 (Pydantic) ✅ |
| **输入验证** | Schema单独验证 | Entity自动验证 ✅ |
| **代码量** | 216行 | 130行 (-40%) ✅ |
| **学习曲线** | 陡峭 (DDD概念) | 平缓 ✅ |

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

## 缓存系统开发规范 ⚠️ **极其重要 - 2026-02-25新增**

> **🚨 所有后端开发者必须遵守缓存使用规范**
> **🆕 更新 (2026-02-25)**: 建立完整缓存系统文档和开发规范

### 核心原则

**1. 读写分离 - 读使用缓存，写清理缓存**
```python
from backend.core.cache.decorators import cached, cache_invalidate

# ✅ 正确：读操作使用缓存
@cached(ttl=3600)
def get_events(game_gid: int):
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ✅ 正确：写操作清理缓存
@cache_invalidate
def create_event(game_gid: int, event_data: dict):
    return execute_insert('INSERT INTO log_events ...')

# ✅ 正确：更新操作清理缓存
@cache_invalidate
def update_event(event_id: int, event_data: dict):
    execute_update('UPDATE log_events SET ... WHERE id = ?', (event_id,))

# ✅ 正确：删除操作清理缓存
@cache_invalidate
def delete_event(event_id: int):
    execute_update('DELETE FROM log_events WHERE id = ?', (event_id,))
```

**2. 合理设置TTL - 根据数据变化频率**
```python
# ✅ 静态数据：长TTL（1-2小时）
@cached(ttl=7200)
def get_system_config():
    pass

# ✅ 中等变化：中TTL（30分钟）
@cached(ttl=1800)
def get_events(game_gid):
    pass

# ✅ 实时数据：短TTL（1分钟）
@cached(ttl=60)
def get_online_users():
    pass

# ❌ 错误：实时数据使用长TTL
@cached(ttl=3600)  # TTL太长，数据不新鲜
def get_realtime_stats():
    pass
```

**3. 避免缓存大对象**
```python
# ❌ 错误：缓存整个大表（可能百万行）
@cached(ttl=3600)
def get_all_logs():
    return fetch_all_as_dict('SELECT * FROM logs')

# ✅ 正确：分页缓存
@cached(ttl=600, key_prefix="logs:page")
def get_logs_page(page: int, size: int = 100):
    return fetch_all_as_dict('SELECT * FROM logs LIMIT ? OFFSET ?', (size, page * size))
```

### 强制检查清单

每个使用缓存的功能必须完成以下检查：

- [ ] **是否使用了 `@cached` 装饰器？**
  - 所有查询函数必须使用缓存装饰器
  - 参数化查询自动生成不同的缓存键

- [ ] **TTL是否合理？**
  - 静态数据：3600-7200秒
  - 中等变化：1800秒
  - 实时数据：60秒

- [ ] **数据更新时是否调用了 `@cache_invalidate`？**
  - CREATE操作必须清理缓存
  - UPDATE操作必须清理缓存
  - DELETE操作必须清理缓存

- [ ] **缓存键是否遵循命名规范？**
  - 格式：`{prefix}:{module}:{function}:{args}`
  - 使用 `key_prefix` 避免键冲突

- [ ] **是否避免了缓存大对象？**
  - 单个缓存对象 < 1MB
  - 使用分页代替全表缓存

- [ ] **是否添加了缓存验证？**
  - 开发环境检查 `X-Cache-Status` 响应头
  - 生产环境监控缓存命中率

### 常见反模式

**❌ 反模式1: 更新数据后不清理缓存**
```python
# 错误：更新数据库后缓存未清理
def update_event(event_id, data):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (data['name'], event_id))
    # ❌ 缓存未清理，导致数据不一致

# 正确：使用@cache_invalidate
@cache_invalidate
def update_event(event_id, data):
    execute_update('UPDATE log_events SET name = ? WHERE id = ?', (data['name'], event_id))
    # ✅ 装饰器自动清理相关缓存
```

**❌ 反模式2: 缓存实时数据且TTL过长**
```python
# 错误：实时统计数据使用长TTL
@cached(ttl=3600)  # ❌ 数据可能过期1小时
def get_realtime_stats():
    return fetch_one_as_dict('SELECT COUNT(*) as online_users FROM user_sessions')

# 正确：使用短TTL
@cached(ttl=60)  # ✅ 1分钟内相对新鲜
def get_realtime_stats():
    return fetch_one_as_dict('SELECT COUNT(*) as online_users FROM user_sessions')
```

**❌ 反模式3: 忘记参数化缓存键**
```python
# 错误：缓存键不包含参数，所有查询共享同一缓存
@cached(ttl=3600)
def get_events(game_gid):  # ❌ game_gid参数未包含在缓存键中
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# 正确：装饰器自动将参数包含在缓存键中
@cached(ttl=3600)
def get_events(game_gid: int):  # ✅ 不同game_gid有不同缓存
    return fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))
```

### 缓存预热策略

**生产环境缓存预热可以避免冷启动性能问题**

```python
@app.before_first_request
def warm_up_cache():
    """服务启动时预热缓存"""
    from backend.services.games.game_service import GameService
    game_service = GameService()
    games = game_service.get_all()
    logger.info(f"Warmed up {len(games)} games")
```

**预热时机**:
- 服务启动时
- 低峰期（定时任务）
- 数据更新后

**预热策略**:
- 静态数据：完整预热
- 热点数据：分批次预热
- 大数据集：分页预热

### 缓存监控指标

**关键指标**:
- 缓存命中率：目标 >85%
- API响应时间：目标 95% <500ms
- 慢查询率：目标 <5%
- 错误率：目标 <1%

### API快速参考

**装饰器**:
```python
from backend.core.cache.decorators import cached, cache_invalidate

@cached(ttl=3600, key_prefix="custom")  # 缓存查询
def query_function(arg1, arg2):
    pass

@cache_invalidate  # 自动清理缓存
def update_function(arg1, arg2):
    pass
```

**缓存API**:
```python
from backend.core.cache.cache_system import cache_result

# 手动操作（不推荐，优先使用装饰器）
cache_result.set(key, value, ttl=3600)
data = cache_result.get(key)
cache_result.delete(key)
cache_result.delete_many(pattern="games:*")
```

**验证缓存生效**:
```bash
# 方法1: 查看HTTP响应头
curl -i http://127.0.0.1:5001/api/events?game_gid=10000147
# 响应头应包含: X-Cache-Status: HIT 或 MISS

# 方法2: 查看缓存统计
curl http://127.0.0.1:5001/api/cache/stats

# 方法3: 直接查看Redis
redis-cli GET "cache:events:10000147"
```

### 违反后果

**不遵守缓存规范的后果**:
- ⚠️ **数据不一致**：用户看到过期数据，导致业务错误
- ⚠️ **性能问题**：缓存命中率低，查询性能下降100-1000倍
- ⚠️ **内存浪费**：缓存大对象导致内存占用过高
- ⚠️ **技术债务**：后期需要重构以添加缓存支持

**Code Review必须拒绝**:
- ❌ 查询函数未使用 `@cached` 装饰器
- ❌ 更新函数未使用 `@cache_invalidate` 装饰器
- ❌ TTL设置不合理（过长或过短）
- ❌ 缓存大对象（>1MB）

### 完整文档

- **[缓存系统文档中心](docs/cache/)** - 完整的缓存系统文档 ⭐
- **[5分钟快速开始](docs/cache/quickstart/5-minute-guide.md)** - 新用户快速上手
- **[常见问题FAQ](docs/cache/quickstart/faq.md)** - 10个最常见问题
- **[开发者指南](docs/cache/development/developer-guide.md)** - 深入了解架构和高级用法
- **[故障排除手册](docs/cache/operations/troubleshooting.md)** - 解决常见问题
- **[部署运维文档](docs/cache/operations/deployment.md)** - 生产环境配置

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

### Input组件使用规范 ⚠️ **极其重要 - 2026-02-22新增**

> **🚨 必须遵循的Input组件使用模式，避免CSS布局冲突**

#### 核心原则

**1. 始终使用label prop，不要在Input外部写label**

```jsx
// ✅ 正确：使用label prop
<Input
  label="游戏名称"
  type="text"
  value={gameName}
  onChange={(e) => setGameName(e.target.value)}
/>

// ❌ 错误：label在Input外部
<div className="form-group">
  <label>游戏名称</label>
  <Input ... />
</div>
```

**为什么？**
- Input组件使用CSS Grid布局（140px label列 + 1fr input列）
- Label在Input外部会导致Grid预留的label列空置
- 结果：Input右侧出现152px空白间隙

**2. 保持Input组件的完整性**

```jsx
// ✅ 正确：Input组件自包含所有结构
<Input label="游戏GID" type="text" value={gid} disabled />

// ❌ 错误：拆分Input组件的结构
<div className="some-wrapper">
  <Input ... />
  <small>提示信息</small>
</div>
```

**3. 避免覆盖Input组件的内部class**

```css
/* ❌ 错误：破坏Grid架构 */
.form-group .cyber-input {
  width: 100%;  /* 覆盖Grid容器 */
  padding: 0.625rem 0.75rem;
}

/* ✅ 正确：通过新的class定制 */
.form-group .cyber-field {
  margin-bottom: 1rem;
}

.form-group .cyber-field__input {
  background: #1e293b;
  border-color: #334155;
}
```

#### 推荐的表单结构

**简单表单**:
```jsx
<form onSubmit={handleSubmit}>
  <Input
    label="游戏名称"
    type="text"
    value={gameData.name}
    onChange={(e) => setGameData({...gameData, name: e.target.value})}
    required
  />

  <Input
    label="游戏GID"
    type="text"
    value={gameData.gid}
    disabled
    helperText="GID为只读字段"
  />

  <Button type="submit">保存</Button>
</form>
```

**带自定义样式的表单**:
```jsx
<div className="custom-form">
  <Input
    label="游戏名称"
    type="text"
    value={gameData.name}
    onChange={(e) => setGameData({...gameData, name: e.target.value})}
    className="custom-input"  // ✅ 安全：只添加到外层容器
  />
</div>

/* CSS */
.custom-input.cyber-field {
  margin-bottom: 2rem;
}

.custom-input .cyber-field__input {
  border-color: #06b6d4;
}
```

#### 常见错误和修复

**错误1: Label在外部导致空白间隙**
```jsx
// ❌ 问题代码
<div className="form-group">
  <label>游戏名称</label>
  <Input ... />
</div>

// ✅ 修复：使用label prop
<Input label="游戏名称" ... />
```

**错误2: 外部CSS破坏Grid布局**
```css
/* ❌ 错误 */
.form-group .cyber-input {
  width: 100%;  /* 破坏Grid */
}

/* ✅ 正确 */
.form-group .cyber-field {
  margin-bottom: 1rem;  /* 只调整margin */
}
```

**错误3: 混淆Grid容器和input元素**
```css
/* ❌ 错误：试图给Grid容器添加input样式 */
.cyber-input {
  padding: 0.625rem;  /* 这会破坏Grid */
}

/* ✅ 正确：给实际input添加样式 */
.cyber-field__input {
  padding: 0.625rem;
}
```

#### 组件架构说明

**Input组件的DOM结构**:
```html
<div class="cyber-field cyber-input">              ← Grid容器（140px label列 + 1fr input列）
  <label class="cyber-field__label cyber-input__label">
    游戏名称 <span class="cyber-field__required">*</span>
  </label>
  <div class="cyber-field__wrapper cyber-input-wrapper">  ← Flex容器（占满第2列）
    <input class="cyber-field__input cyber-input"      ← 实际input元素（占满wrapper）
      type="text"
      value="..."
    />
  </div>
  <p class="cyber-field__helper cyber-input__helper">
    提示信息
  </p>
</div>
```

**关键点**:
- `.cyber-field` = Grid容器（整体布局）
- `.cyber-field__label` = Label（第1列）
- `.cyber-field__wrapper` = Flex容器（第2列）
- `.cyber-field__input` = input元素（Flex子项）

#### 向后兼容性

**2026-02-22重构保留了旧class名作为alias**:
- ✅ `.cyber-input` = `.cyber-field` (Grid容器)
- ✅ `.cyber-input__label` = `.cyber-field__label`
- ✅ `.cyber-input-wrapper` = `.cyber-field__wrapper`
- ✅ `.cyber-input` (在wrapper内) = `.cyber-field__input`

**旧代码无需修改**，但新代码应使用新class名。

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
- [文档中心](docs/README.md) - 所有文档导航索引 ⭐ (2026-02-22新增)

#### 开发指南
- [快速开始](docs/development/QUICKSTART.md) ⭐ - 快速上手指南 (2026-02-22新增)
- [环境搭建](docs/development/getting-started.md) - 环境配置
- [API开发指南](docs/development/api-development.md) - API开发规范
- [前端开发指南](docs/development/frontend-development.md) - 前端开发规范
- [game_gid迁移指南](docs/development/GAME_GID_MIGRATION_GUIDE.md) - game_gid迁移 (2026-02-22新增)

#### 测试文档
- [E2E测试指南](docs/testing/e2e-testing-guide.md) - E2E测试规范
- [快速测试指南](docs/testing/quick-test-guide.md) - PATH问题排查
- [测试经验总结](docs/testing/TESTING_LESSONS_LEARNED.md) ⭐ - 测试最佳实践 (2026-02-22新增)
- [TDD实践](docs/development/tdd-practices.md) (TODO) - TDD最佳实践

#### 优化文档
- [优化经验总结](docs/optimization/OPTIMIZATION_LESSONS_LEARNED.md) ⭐ - 6阶段优化总结 (2026-02-22新增)
- [最终优化报告](docs/optimization/FINAL_OPTIMIZATION_REPORT.md) - 后端优化报告
- [核心优化指南](docs/optimization/CORE_OPTIMIZATION_GUIDE.md) - 优化实施指南
- [缓存优化总结](docs/optimization/CACHE_OPTIMIZATION_SUMMARY.md) - 缓存系统优化

---

## E2E测试关键学习成果 ⚠️ **极其重要**

> **🚨 基于实际E2E测试的经验总结**
> **🆕 更新 (2026-02-18)**: 完成4轮迭代E2E测试，修复8个严重问题

### 测试方法论

**Ralph Loop迭代测试法**：
```
发现问题 → Subagent深度分析 → 设计修复方案 → 实施修复 → Chrome MCP验证 → 记录结果
```

**测试工具**：
1. **Chrome DevTools MCP** - 页面导航、快照、截图、控制台监控
2. **并行Subagent分析** - 根本原因深度分析
3. **Brainstorming Skill** - 系统化修复策略设计

### 关键学习 #1: React Hooks 规则 ⚠️ **极其重要**

> **🚨 违反React Hooks规则会导致组件崩溃**

#### 错误模式（导致崩溃）

```javascript
// ❌ 错误：Hook在条件返回之后调用
function Component() {
  const data = useData();

  if (isLoading) return <Loading />; // ❌ 条件返回在中间

  const processed = useMemo(() => {}, [data]); // ❌ Hook在条件返回后
  return <View />;
}
```

**错误原因**：
- 第1次渲染 (`isLoading=true`): 只调用1个Hook
- 第2次渲染 (`isLoading=false`): 调用2个Hook
- **React检测到Hooks数量不一致** → 崩溃

**控制台错误**：
```
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render
```

#### 正确模式（符合规范）

```javascript
// ✅ 正确：所有Hook在条件返回之前
function Component() {
  const data = useData();

  // ✅ 所有Hook在条件返回之前
  const processed = useMemo(() => {
    if (!data) return null;
    return data.filter(...);
  }, [data]);

  // ✅ 条件返回在所有Hook之后
  if (isLoading) return <Loading />;

  return <View />;
}
```

**关键规则**：
1. ✅ 只在顶层调用Hooks（不在if、for、嵌套函数中）
2. ✅ 没有在Hooks调用之间进行条件返回
3. ✅ 每次渲染时Hooks的调用顺序相同
4. ✅ 所有Hook都在组件最顶层调用

#### ESLint配置（强制检测）

```bash
npm install eslint-plugin-react-hooks --save-dev
```

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error', // 强制规则
    'react-hooks/exhaustive-deps': 'warn', // 检测依赖项
  },
};
```

#### 代码审查清单

**React Hooks检查**：
- [ ] 所有Hooks都在组件最顶层调用？
- [ ] 没有任何Hook在条件语句、循环或嵌套函数中？
- [ ] 没有在Hooks调用之间进行条件返回？
- [ ] 每次渲染时Hooks的调用顺序相同？
- [ ] ESLint React Hooks规则已启用？

### 关键学习 #2: Lazy Loading 最佳实践 ⚠️ **极其重要**

> **🚨 不恰当的lazy loading会导致页面卡在加载状态**

#### 问题模式：双重Suspense嵌套

```javascript
// ❌ 错误架构：双重Suspense嵌套
// App.jsx
<Suspense fallback={<GlobalLoading text="Loading Event2Table..." />}>
  <MainLayout />
</Suspense>

// MainLayout.jsx
<Suspense fallback={<Loading text="加载中..." />}>
  <Outlet />
</Suspense>

// routes.jsx
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));

// 问题：lazy组件永不resolve → 永远显示"Loading Event2Table..."
```

**问题表现**：
- 页面卡在 "LOADING EVENT2TABLE..." 状态
- 控制台无错误信息
- 用户无法看到实际加载内容或错误信息

**根本原因**：
- 外层Suspense优先显示fallback
- lazy组件加载失败但错误被外层Suspense捕获
- 用户永远看不到内层的加载状态或错误

#### 正确模式：选择性使用Lazy Loading

**何时使用lazy loading**：
- ✅ 大型组件（>10KB）
- ✅ 不常用的路由页面
- ✅ 复杂的数据可视化组件
- ❌ 简单的文档页面（<50行）
- ❌ 已经很快加载的小型组件

**正确修复**：

```javascript
// ✅ 正确：小型组件直接导入
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";
import ParameterDashboard from "@analytics/pages/ParameterDashboard";

// ❌ 错误：小型组件使用lazy loading
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));
const ValidationRules = lazy(() => import("@analytics/pages/ValidationRules"));
const ParameterDashboard = lazy(() => import("@analytics/pages/ParameterDashboard"));
```

**修复案例**：
- API Docs（<50行）→ 改为直接导入
- Validation Rules（<50行）→ 改为直接导入
- Parameter Dashboard（~100行）→ 改为直接导入

#### 性能对比

**修复前**：
```
dist/assets/js/ApiDocs-xxx.js          0.99 kB
dist/assets/js/ValidationRules-xxx.js  0.40 kB
dist/assets/js/ParameterDashboard-xxx.js 0.46 kB

总大小：~2KB
加载超时：❌ 页面卡住
```

**修复后**：
```
dist/assets/js/index-BygV0Ywq.js      1,806.19 kB

总大小：~1.8MB（合并到主bundle）
加载成功：✅ 所有页面正常加载
```

**结论**：对于小型组件，lazy loading的性能收益极小，但可能导致严重的加载问题。

#### 代码审查清单

**Lazy Loading检查**：
- [ ] 组件大小是否>10KB？
- [ ] 是否是不常用页面？
- [ ] 是否有双重Suspense嵌套？
- [ ] 小型组件是否使用直接导入？

### 关键学习 #3: Chrome DevTools MCP 测试流程

#### 标准测试步骤

```javascript
// 1. 列出所有页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})

// 3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 5. 截图记录
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/ralph/iteration-2/screenshots/fix-01.png",
  fullPage: true
})

// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

#### 错误检测模式

**React Hooks错误**：
```
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render
```

**加载超时错误**：
```
页面状态：卡在"LOADING EVENT2TABLE..."超过30秒
控制台：无错误信息（但也不显示任何内容）
```

**API错误**：
```
[error] Failed to load resource: 400 (BAD REQUEST)
```

### 关键学习 #4: 根因分析方法

#### Subagent并行分析策略

**步骤1：识别问题模式**
- 问题是孤立事件还是重复模式？
- 多个页面有相同症状？

**步骤2：并行深度分析**
```javascript
// 启动2个并行subagent
Task(subagent_type="general-purpose", prompt="分析React Hooks错误根因")
Task(subagent_type="general-purpose", prompt="分析加载超时模式")
```

**步骤3：综合分析结果**
- 对比两个subagent的发现
- 识别共同点和差异
- 确定根本原因

**步骤4：设计修复方案**
- 基于根因分析，而非症状
- 考虑长期预防措施
- 避免表面修复

#### Brainstorming系统化设计

```bash
/superpowers:brainstorming

# 提示：设计React Hooks修复方案
# 1. 理解问题：Hook在条件返回后调用
# 2. 探索方案：2-3种修复策略
# 3. 选择最佳：重构Hook调用顺序
# 4. 分段验证：先验证Hook顺序，再验证功能
```

### 实际修复案例

#### 案例1：HQL Manage React Hooks修复

**文件**：`frontend/src/analytics/pages/HqlManage.jsx`

**修复前**：
```javascript
function HqlManage() {
  const [state, setState] = useState();
  const { data, isLoading } = useQuery({...});

  if (isLoading) return <Loading />; // ❌ 条件返回

  const filtered = useMemo(() => {}, [data]); // ❌ Hook在条件返回后
  const handleClick = useCallback(() => {}, []); // ❌ Hook在条件返回后

  return <Component />;
}
```

**修复后**：
```javascript
function HqlManage() {
  const [state, setState] = useState();
  const { data, isLoading } = useQuery({...});

  // ✅ 所有Hook在条件返回之前
  const filtered = useMemo(() => {}, [data]);
  const handleClick = useCallback(() => {}, [info]);

  if (isLoading) return <Loading />; // ✅ 条件返回在所有Hook之后

  return <Component />;
}
```

**验证结果**：
- ✅ 页面正常加载
- ✅ 无React Hooks错误
- ✅ 显示"未找到HQL记录"空状态

#### 案例2：Lazy Loading加载超时修复

**文件**：`frontend/src/routes/routes.jsx`

**修复前**（7个页面）：
```javascript
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));
const ValidationRules = lazy(() => import("@analytics/pages/ValidationRules"));
const ParameterDashboard = lazy(() => import("@analytics/pages/ParameterDashboard"));
const ParameterUsage = lazy(() => import("@analytics/pages/ParameterUsage"));
const ParameterHistory = lazy(() => import("@analytics/pages/ParameterHistory"));
const ParameterNetwork = lazy(() => import("@analytics/pages/ParameterNetwork"));
// ... 7个页面全部超时
```

**修复后**：
```javascript
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";
import ParameterDashboard from "@analytics/pages/ParameterDashboard";
import ParameterUsage from "@analytics/pages/ParameterUsage";
import ParameterHistory from "@analytics/pages/ParameterHistory";
import ParameterNetwork from "@analytics/pages/ParameterNetwork";
// ... 所有页面正常加载
```

**验证结果**：
- ✅ 所有页面正常加载
- ✅ 无超时问题
- ✅ 控制台无错误

### 预防措施总结

#### 1. 开发环境配置

**ESLint强制检测**：
```bash
npm install eslint-plugin-react-hooks --save-dev
```

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
  },
};
```

#### 2. 代码审查清单

**React组件审查**：
- [ ] 所有Hooks都在组件最顶层调用？
- [ ] 没有任何Hook在if、for或嵌套函数中？
- [ ] 没有在Hooks调用之间进行条件返回？
- [ ] 每次渲染时Hooks的调用顺序相同？
- [ ] Lazy loading只用于真正的大型组件？

**Lazy Loading审查**：
- [ ] 组件大小是否>10KB？
- [ ] 是否是不常用页面？
- [ ] 是否有双重Suspense嵌套？
- [ ] 是否有Error Boundary捕获错误？

#### 3. E2E测试要求

**每次代码修改后**：
1. ✅ 启动开发服务器（`npm run dev`）
2. ✅ 执行完整的E2E测试
3. ✅ 检查控制台错误信息
4. ✅ 验证页面正常加载
5. ✅ 截图记录测试结果

**禁止行为**：
- ❌ 修改代码后不进行E2E测试
- ❌ 仅进行静态分析，不启动服务器测试
- ❌ 跳过任何测试步骤
- ❌ 发现错误不立即修复

### 测试文档参考

**完整测试报告**：
- [迭代1测试报告](docs/ralph/iteration-1/E2E-TEST-REPORT.md) - 13/13页面通过
- [迭代2测试报告](docs/ralph/iteration-2/E2E-TEST-REPORT.md) - 发现4个严重问题
- [迭代2修复报告](docs/ralph/iteration-2/FIX-REPORT.md) - 详细修复方案
- [问题日志](docs/ralph/issues-log.md) - 所有问题追踪
- [最终测试报告](docs/ralph/FINAL-REPORT.md) - 完整总结
- [迭代4总结](docs/ralph/iteration-4/SUMMARY.md) - 项目状态评估

### 测试统计

**测试覆盖**：
- 总测试页面：39+
- 测试通过率：~90%
- 问题修复率：80% (8/10)
- 严重问题修复率：100% (8/8)

**修复文件**：
1. `frontend/src/analytics/pages/HqlManage.jsx` - React Hooks修复
2. `frontend/src/routes/routes.jsx` - Lazy loading修复（7个页面）

**生成文档**：12份markdown文件
**生成截图**：24+张

### 后续建议

**P0 - 立即执行**：
1. ✅ 添加ESLint React Hooks插件
2. ✅ 建立代码审查清单
3. ✅ 更新开发文档

**P1 - 尽快执行**：
1. 测试剩余的参数管理页面
2. 为关键页面添加E2E自动化测试
3. 添加Error Boundary

**P2 - 可选优化**：
1. 优化bundle大小（目前主bundle 1.8MB）
2. 使用manual chunks改进代码分割
3. 添加性能监控

---

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

**文档版本**: 7.9.0
**最后更新**: 2026-03-02
**维护者**: Event2Table Development Team

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 7.9 | 2026-03-02 | 新增项目管理最佳实践章节：并行开发、大规模重构、零破坏性变更 |
| 7.8 | 2026-03-01 | 后端架构全面优化（Phase 1-4 完成）：100% ERS 架构迁移 |
| 7.8 | 2026-02-26 | Entity架构迁移 + DDD清理完成：6/8核心模块迁移 |
| 7.7.1 | 2026-02-26 | 缓存系统架构统一：双实例合并为单实例 |
| 7.6.1 | 2026-02-25 | 缓存系统文档完善：7份新文档，使用率从7.5%提升到60% |
| 7.4 | 2026-02-18 | 事件节点构建器全面修复：6大问题解决，React性能优化，API适配器迁移 |
| 7.3 | 2026-02-12 | 新增文档组织规范章节，重组文档结构，修复路径引用 |
| 7.2 | 2026-02-12 | 新增环境问题排查章节，记录 PATH 问题及解决方案 |
| 7.1 | 2026-02-11 | 建立强制 E2E 测试流程 |
| 7.0 | 2026-02-10 | 完善分层架构和 TDD 开发规范 |
