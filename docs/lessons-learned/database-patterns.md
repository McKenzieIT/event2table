# 数据库模式

> **来源**: 整合了2个文档的数据库相关经验
> **最后更新**: 2026-02-24
> **维护**: 每次数据库相关问题修复后立即更新

---

## game_gid迁移经验 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [FINAL_OPTIMIZATION_REPORT.md](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md), [GAME_GID_MIGRATION_GUIDE.md](../development/GAME_GID_MIGRATION_GUIDE.md)

### game_id vs game_gid

**关键区别**:
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

**为什么使用game_gid**:
- `game_gid`是业务GID，稳定不变
- `game_id`是数据库自增ID，可能因重建而变化
- 使用game_gid确保数据关联的稳定性

### Python后端规范

**所有SQL查询必须使用game_gid**:
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

### 表名生成规范

```python
# ✅ 使用 game_gid 生成表名
source_table = f'{game["ods_db"]}.ods_{game["gid"]}_all_view'  # ieu_ods.ods_10000147_all_view
target_table = f'{dwd_prefix}.v_dwd_{game["gid"]}_{event}_di'  # dwd.v_dwd_10000147_login_di

# ❌ 不要使用 game_id
source_table = f'{ods_db}.ods_{game_id}_all_view'  # 错误！
```

### 前端JavaScript规范

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

### 代码审查清单

**每次代码审查必须检查**:
- [ ] 所有SQL查询是否使用 `game_gid` 而非 `game_id`
- [ ] 所有JOIN条件是否使用 `game_gid = g.gid`
- [ ] 所有表名生成是否使用 `game["gid"]` 而非 `game["id"]`
- [ ] 所有API调用是否使用 `game_gid` 参数
- [ ] 数据库Schema是否使用 `game_gid` 作为外键

**违规后果**:
- ⚠️ 数据关联错误（Dashboard显示0）
- ⚠️ 查询性能下降
- ⚠️ 业务逻辑混乱
- ❌ Code Review必须拒绝

### 相关经验

- [性能模式 - N+1查询优化](./performance-patterns.md#n1查询优化) - JOIN优化
- [安全要点 - SQL注入防护](./security-essentials.md#sql注入防护) - SQL安全

### 案例文档

- [后端优化Phase 5 - game_gid迁移](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md#phase-5-game_gid迁移)
- [GAME_GID迁移指南](../development/GAME_GID_MIGRATION_GUIDE.md)

---

## 数据库事务 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [架构设计文档](../development/architecture.md)

### 事务使用原则

**何时使用事务**:
- ✅ 多个INSERT/UPDATE/DELETE操作需要原子性
- ✅ 关联数据需要同时创建或删除
- ✅ 业务逻辑需要保证数据一致性

**事务示例**:
```python
from backend.core.database.connection import get_db_connection

def create_event_with_params(event_data, params_data):
    """创建事件及其参数（使用事务保证一致性）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 开始事务
        cursor.execute("BEGIN TRANSACTION")

        # 创建事件
        cursor.execute('''
            INSERT INTO log_events (game_gid, name, ...)
            VALUES (?, ?, ...)
        ''', (event_data['game_gid'], event_data['name'], ...))
        event_id = cursor.lastrowid

        # 创建参数
        for param in params_data:
            cursor.execute('''
                INSERT INTO event_params (event_id, name, ...)
                VALUES (?, ?, ...)
            ''', (event_id, param['name'], ...))

        # 提交事务
        conn.commit()
        return event_id

    except Exception as e:
        # 回滚事务
        conn.rollback()
        raise e
    finally:
        conn.close()
```

### 预防措施

**代码审查清单**:
- [ ] 关联数据操作是否使用事务？
- [ ] 事务是否正确提交或回滚？
- [ ] 是否处理了事务异常？

---

## 数据隔离规范 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [CLAUDE.md](../../CLAUDE.md#测试隔离规范), [STAR001-GAME-PROTECTION.md](../development/STAR001-GAME-PROTECTION.md)

### 三环境完全隔离

**环境配置**:
```python
# backend/core/config/config.py
def get_db_path():
    if os.environ.get("FLASK_ENV") == "testing":
        return TEST_DB_PATH  # data/test_database.db
    if os.environ.get("FLASK_ENV") == "development":
        return DEV_DB_PATH   # data/dwd_generator_dev.db
    return DB_PATH          # data/dwd_generator.db
```

**测试数据库隔离**:
```python
# backend/tests/conftest.py
@pytest.fixture(scope="session")
def db():
    """使用独立的测试数据库进行测试"""
    # 删除旧测试数据库
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 初始化测试数据库
    init_db(TEST_DB_PATH)

    # 提供测试数据库连接
    conn = get_db_connection(TEST_DB_PATH)
    yield conn
    conn.close()
```

### STAR001游戏保护

**核心规则**:
- ❌ **绝对禁止** 删除 GID 10000147 (STAR001) 的任何数据
- ✅ **所有测试** 必须使用 90000000+ 范围的测试GID
- ✅ 测试前必须确认不包含生产数据

**测试GID规范**:
```python
# ✅ 正确：使用测试GID
TEST_GID_START = 90000000
test_gid = 90000001

# ❌ 错误：使用STAR001
game_gid = 10000147  # 禁止！
```

**违反后果**:
- 数据丢失（已有先例）
- 测试失败
- 必须手动恢复数据

### 预防措施

**代码审查清单**:
- [ ] 测试是否使用独立的测试数据库？
- [ ] 测试GID是否在90000000+范围？
- [ ] 测试是否验证不包含生产数据？
- [ ] 测试完成后是否清理测试数据？

### 相关经验

- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - 测试驱动开发
- [安全要点 - 输入验证](./security-essentials.md#输入验证) - 数据验证

### 案例文档

- [STAR001游戏保护规则](../development/STAR001-GAME-PROTECTION.md)
- [测试隔离规范](../../CLAUDE.md#测试隔离规范)

---

## 数据库文件位置规范 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CLAUDE.md](../../CLAUDE.md#数据库文件位置规范)

### 核心原则

**所有数据库文件必须放在 data/ 目录，禁止在根目录或其他位置创建数据库文件**

#### 配置文件指向 data/ 目录

**配置文件**: `backend/core/config/config.py`
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

#### 为什么需要此规范？

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

#### 禁止行为

- ❌ 在根目录创建 `*.db` 文件
- ❌ 在backend/、scripts/目录创建数据库文件
- ❌ 在代码中使用相对路径创建数据库

**正确做法**:
```python
# ✅ 正确：使用配置文件中的路径
from backend.core.config.config import DB_PATH, TEST_DB_PATH

# 连接数据库
conn = get_db_connection(DB_PATH)  # data/dwd_generator.db

# ❌ 错误：直接使用相对路径
conn = sqlite3.connect("dwd_generator.db")  # 会在当前目录创建！
```

#### 代码审查检查项

- [ ] 是否在非 data/ 目录创建数据库文件？
- [ ] 是否使用相对路径连接数据库？
- [ ] 是否使用配置文件中的 DB_PATH 常量？
- [ ] 所有数据库连接是否使用 `get_db_connection(DB_PATH)`？

#### 违规后果

- ⚠️ 数据库文件散落在各目录
- ⚠️ 生产数据与测试数据混淆
- ⚠️ 数据库版本控制混乱
- ⚠️ .gitignore 失效导致数据库被提交
- ❌ Code Review必须拒绝

---

## 相关经验文档

- [性能模式 - 缓存策略](./performance-patterns.md#缓存策略) - 缓存清理
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - Repository层数据访问
