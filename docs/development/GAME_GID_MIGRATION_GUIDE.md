# game_gid 迁移指南

> **版本**: 1.0 | **迁移日期**: 2026-02-20 | **状态**: 完成

本文档说明如何从 `game_id` 迁移到 `game_gid`，包括迁移原因、代码变更、测试和验证。

---

## 📋 目录

- [迁移背景](#迁移背景)
- [game_id vs game_gid](#game_id-vs-game_gid)
- [后端迁移](#后端迁移)
- [前端迁移](#前端迁移)
- [数据库迁移](#数据库迁移)
- [测试验证](#测试验证)
- [常见问题](#常见问题)

---

## 🎯 迁移背景

### 为什么迁移？

**问题1: game_id不稳定性**
```python
# game_id是数据库自增ID，可能因重建数据库而变化
game_id = 1  # 今天
game_id = 5  # 重建数据库后
```

**问题2: 业务关联错误**
```python
# ❌ 错误：使用game_id进行关联
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_id = ?',
    (game_id,)  # game_id可能变化
)

# ✅ 正确：使用game_gid进行关联
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_gid = ?',
    (game_gid,)  # game_gid稳定不变
)
```

**问题3: 跨表JOIN混乱**
```sql
-- ❌ 错误：使用game_id关联（主键不一致）
SELECT * FROM log_events le
JOIN games g ON le.game_id = g.id  # id可能重建

-- ✅ 正确：使用game_gid关联
SELECT * FROM log_events le
JOIN games g ON le.game_gid = g.gid  -- gid稳定不变
```

### 迁移目标

- ✅ **完全切换到game_gid**: 所有API、数据库查询、JOIN条件
- ✅ **保留game_id**: 仅作为games表主键，不用于业务关联
- ✅ **提升数据一致性**: 消除因game_id变化导致的数据关联错误
- ✅ **优化查询性能**: game_gid有索引，查询更高效

---

## 🆚 game_id vs game_gid

| 特性 | game_id | game_gid |
|------|---------|----------|
| **类型** | 数据库自增主键 | 业务GID（游戏标识符） |
| **稳定性** | 可能因重建而变化 | 永久不变 |
| **用途** | 仅用于games表主键 | 用于所有业务关联 |
| **示例** | 1, 2, 3, ... | 10000147, 90000001, ... |
| **API使用** | ❌ 已废弃 | ✅ 强制使用 |
| **JOIN条件** | ❌ 不推荐 | ✅ 推荐使用 |

### 使用规则

```python
# ✅ 正确：game_id仅用于games表主键
game = fetch_one_as_dict(
    'SELECT * FROM games WHERE id = ?',
    (game_id,)  # 仅在games表内部使用
)

# ✅ 正确：game_gid用于所有业务关联
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_gid = ?',
    (game_gid,)  # 跨表关联
)

# ✅ 正确：JOIN使用game_gid
query = '''
    SELECT g.name, COUNT(le.id) as event_count
    FROM games g
    LEFT JOIN log_events le ON g.gid = le.game_gid  -- 使用game_gid
    GROUP BY g.gid
'''
```

---

## 🔧 后端迁移

### 1. API路由变更

#### 修改前（game_id）
```python
@games_bp.route('/api/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = fetch_one_as_dict(
        'SELECT * FROM games WHERE id = ?',
        (game_id,)
    )
    return json_success_response(data=game)
```

#### 修改后（game_gid）
```python
@games_bp.route('/api/games/<int:game_gid>', methods=['GET'])
def get_game(game_gid):
    game = fetch_one_as_dict(
        'SELECT * FROM games WHERE gid = ?',
        (game_gid,)
    )
    return json_success_response(data=game)
```

### 2. Service层变更

#### GameService
```python
class GameService:
    def get_game(self, game_gid: int) -> Dict[str, Any]:
        """根据game_gid获取游戏"""
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game {game_gid} not found")
        return game

    def get_game_events(self, game_gid: int) -> List[Dict]:
        """获取游戏的所有事件"""
        events = self.event_repo.find_by_game_gid(game_gid)
        return events
```

#### EventService
```python
class EventService:
    def create_event(self, game_gid: int, event_data: Dict) -> Dict:
        """创建事件"""
        # 使用game_gid而非game_id
        event_data['game_gid'] = game_gid
        event = self.event_repo.create(event_data)
        return event
```

### 3. Repository层变更

```python
class EventRepository(GenericRepository):
    def find_by_game_gid(self, game_gid: int) -> List[Dict]:
        """根据game_gid查询事件"""
        query = 'SELECT * FROM log_events WHERE game_gid = ?'
        return fetch_all_as_dict(query, (game_gid,))

    def count_by_game_gid(self, game_gid: int) -> int:
        """统计游戏事件数量"""
        query = 'SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?'
        result = fetch_one_as_dict(query, (game_gid,))
        return result['count']
```

### 4. 数据库查询变更

#### 修改前
```python
# ❌ 错误：使用game_id
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_id = ?',
    (game_id,)
)

# ❌ 错误：JOIN使用game_id
query = '''
    SELECT le.*, g.name
    FROM log_events le
    JOIN games g ON le.game_id = g.id
    WHERE le.game_id = ?
'''
```

#### 修改后
```python
# ✅ 正确：使用game_gid
events = fetch_all_as_dict(
    'SELECT * FROM log_events WHERE game_gid = ?',
    (game_gid,)
)

# ✅ 正确：JOIN使用game_gid
query = '''
    SELECT le.*, g.name
    FROM log_events le
    JOIN games g ON le.game_gid = g.gid
    WHERE le.game_gid = ?
'''
```

### 5. 缓存键变更

```python
# ✅ 使用game_gid作为缓存键
cache_key = f'game:{game_gid}'
cache.set(cache_key, game_data, timeout=300)

# 清理缓存
cache.delete_many(f'game:{game_gid}*')
```

---

## 🎨 前端迁移

### 1. API调用变更

#### 修改前（game_id）
```javascript
// ❌ 旧代码（不再使用）
const gameId = gameData.id;  // 数据库自增ID
const events = await fetch(`/api/events?game_id=${gameId}`);
```

#### 修改后（game_gid）
```javascript
// ✅ 新代码（正确方式）
const gameGid = gameData.gid;  // 业务GID
const events = await fetch(`/api/events?game_gid=${gameGid}`);
```

### 2. 组件状态变更

```javascript
// ✅ 使用gameGid而非gameId
const [gameGid, setGameGid] = useState(null);

// 从游戏数据中提取gid
useEffect(() => {
  if (gameData) {
    setGameGid(gameData.gid);  // 使用gid而非id
  }
}, [gameData]);

// API调用使用gameGid
const loadEvents = async () => {
  const response = await fetch(`/api/events?game_gid=${gameGid}`);
  const data = await response.json();
  setEvents(data.data);
};
```

### 3. 表单提交变更

```javascript
// ✅ 表单提交包含game_gid
const handleSubmit = async (e) => {
  e.preventDefault();
  await fetch('/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_gid: gameGid,  // 使用game_gid
      event_name: eventName,
      event_code: eventCode
    })
  });
};
```

### 4. 表名生成变更

```javascript
// ✅ 使用gameGid生成表名
const gameGid = gameData.gid;
const odsDb = gameData.ods_db;
const sourceTable = `${odsDb}.ods_${gameGid}_all_view`;
const targetTable = `dwd.v_dwd_${gameGid}_event_di`;

// ❌ 不要使用gameId
// const sourceTable = `ods_${gameId}_all_view`;  // 错误！
```

---

## 🗄️ 数据库迁移

### 迁移脚本位置

`backend/services/games/games.py` - 包含game_gid迁移逻辑

### 迁移步骤

1. **备份数据库**
```bash
cp data/dwd_generator.db data/dwd_generator.db.backup-$(date +%Y%m%d)
```

2. **验证game_gid字段存在**
```sql
-- 检查games表
.schema games
-- 应该包含：gid INTEGER UNIQUE NOT NULL
```

3. **验证log_events表game_gid字段**
```sql
-- 检查log_events表
.schema log_events
-- 应该包含：game_gid INTEGER NOT NULL
```

4. **验证数据完整性**
```sql
-- 检查game_gid是否都有值
SELECT COUNT(*) FROM log_events WHERE game_gid IS NULL;
-- 应该返回：0

-- 检查game_gid是否都对应有效游戏
SELECT COUNT(DISTINCT le.game_gid)
FROM log_events le
LEFT JOIN games g ON le.game_gid = g.gid
WHERE g.gid IS NULL;
-- 应该返回：0
```

5. **验证外键约束**
```sql
-- 检查外键约束（如果有）
PRAGMA foreign_keys;
PRAGMA foreign_key_list(log_events);
```

### 迁移后验证

```bash
# 运行验证脚本
python scripts/verify/verify_game_gid_migration.py

# 检查输出
# ✅ All games have valid game_gid
# ✅ All events reference valid game_gid
# ✅ No orphaned events found
```

---

## ✅ 测试验证

### 单元测试

```python
# backend/test/unit/test_game_gid_migration.py

def test_find_game_by_gid():
    """测试使用game_gid查询游戏"""
    game = game_repo.find_by_gid(10000147)
    assert game is not None
    assert game['gid'] == 10000147

def test_find_events_by_game_gid():
    """测试使用game_gid查询事件"""
    events = event_repo.find_by_game_gid(10000147)
    assert len(events) > 0
    assert all(e['game_gid'] == 10000147 for e in events)

def test_join_with_game_gid():
    """测试使用game_gid进行JOIN"""
    query = '''
        SELECT g.name, COUNT(le.id) as event_count
        FROM games g
        LEFT JOIN log_events le ON g.gid = le.game_gid
        WHERE g.gid = ?
        GROUP BY g.gid
    '''
    result = fetch_one_as_dict(query, (10000147,))
    assert result is not None
```

### 集成测试

```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 验证所有API使用game_gid
pytest backend/test/integration/test_game_gid_api.py -v
```

### E2E测试

```bash
# 启动服务器
python web_app.py  # 终端1
cd frontend && npm run dev  # 终端2

# 运行E2E测试
cd frontend
npm run test:e2e

# 验证游戏管理流程
# 1. 创建游戏（使用game_gid）
# 2. 创建事件（使用game_gid）
# 3. 查询事件（使用game_gid）
# 4. 删除事件（使用game_gid）
```

---

## ❓ 常见问题

### Q1: 为什么不直接用game_id？

**A**: game_id是数据库自增主键，重建数据库后会变化。game_gid是业务GID，永久稳定。使用game_gid可以避免因数据库重建导致的数据关联错误。

### Q2: 现有代码如何快速迁移？

**A**: 按以下步骤迁移：
1. 全局搜索 `game_id`
2. 分析每个使用场景
3. 替换为 `game_gid`（跨表关联）或保留 `game_id`（仅games表主键）
4. 运行测试验证

### Q3: 迁移后性能会下降吗？

**A**: 不会。game_gid字段已建立索引，查询性能与game_id相当。在某些场景下，game_gid查询甚至更快（避免多表JOIN）。

### Q4: 如何处理旧数据？

**A**: 迁移脚本已处理：
- 所有现有数据都有game_gid值
- 外键关系已更新
- 无需手动处理

### Q5: 前端需要改哪些地方？

**A**: 主要修改：
1. API调用参数：`game_id` → `game_gid`
2. 组件状态：`gameId` → `gameGid`
3. 表单字段：`game_id` → `game_gid`
4. 表名生成：使用 `gameData.gid`

### Q6: 如何验证迁移成功？

**A**: 运行验证脚本：
```bash
# 1. API契约测试
python scripts/test/api_contract_test.py

# 2. 单元测试
pytest backend/test/unit/ -v

# 3. E2E测试
cd frontend && npm run test:e2e

# 4. 手动验证
# 访问 http://localhost:5173
# 测试游戏管理、事件管理、参数管理功能
```

---

## 📚 相关文档

- [开发规范 - 游戏标识符规范](../../CLAUDE.md#游戏标识符规范-⚠️-极其重要---强制执行)
- [后端优化报告](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md)
- [API文档](../api/README.md)
- [快速开始指南](./QUICKSTART.md)

---

## 📝 变更清单

### 已完成 ✅

- [x] 所有API路由切换到game_gid
- [x] Service层使用game_gid
- [x] Repository层使用game_gid
- [x] 数据库JOIN条件使用game_gid
- [x] 缓存键使用game_gid
- [x] 前端API调用使用game_gid
- [x] 单元测试更新
- [x] E2E测试验证
- [x] 文档更新

### 无需变更 ⚠️

- [ ] games表主键仍使用id（game_id仅用于内部）
- [ ] 外键约束保持不变

---

**文档版本**: 1.0
**最后更新**: 2026-02-22
**维护者**: Event2Table Development Team
