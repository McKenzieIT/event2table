# P0-16 resolve_parameter_changes 快速参考

## 功能概述

GraphQL resolver用于查询参数变更历史

## API签名

```python
def resolve_parameter_changes(
    info,
    game_gid: int,
    parameter_id: Optional[int] = None,
    limit: int = 50
) -> List[Dict[str, Any]]
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏GID |
| parameter_id | int | ❌ | 参数ID（可选过滤） |
| limit | int | ❌ | 结果限制（1-1000，默认50） |

## 返回数据

```python
[
    {
        'id': 1,
        'parameter_id': 100,
        'param_name': 'zoneId',
        'param_type': 'int',
        'event_code': 'login',
        'old_value': '1',
        'new_value': '2',
        'change_type': 'update',  # create/update/delete
        'changed_at': '2026-03-09 10:00:00',
        'changed_by': 1,
        'changed_by_username': 'admin'
    }
]
```

## 使用示例

### GraphQL查询

```graphql
query GetParameterChanges {
  parameterChanges(gameGid: 10000147, limit: 20) {
    id
    parameterId
    paramName
    paramType
    eventCode
    oldValue
    newValue
    changeType
    changedAt
    changedByUsername
  }
}
```

### Python调用

```python
from backend.gql_api.resolvers.parameter_resolvers import resolve_parameter_changes

# 查询所有变更
changes = resolve_parameter_changes(
    info=info,
    game_gid=10000147,
    limit=50
)

# 查询特定参数的变更
changes = resolve_parameter_changes(
    info=info,
    game_gid=10000147,
    parameter_id=100,
    limit=20
)
```

## 错误处理

| 错误 | 原因 | HTTP状态码 |
|------|------|-----------|
| Invalid game_gid | game_gid < 1 | 400 |
| Invalid parameter_id | parameter_id < 1 | 400 |
| Invalid limit | limit < 1 or > 1000 | 400 |

## 数据库表

```sql
CREATE TABLE IF NOT EXISTS parameter_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parameter_id INTEGER NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_type TEXT NOT NULL
        CHECK(change_type IN ('create', 'update', 'delete')),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by INTEGER,
    FOREIGN KEY (parameter_id) REFERENCES parameters(id)
        ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
        ON DELETE SET NULL
);
```

## 测试

```bash
# 运行单元测试
pytest backend/test/unit/gql_api/resolvers/test_parameter_resolvers.py \
  ::TestResolveParameterChanges -v

# 运行集成测试
python3 << 'EOF'
from backend.gql_api.resolvers.parameter_resolvers import resolve_parameter_changes

class MockInfo:
    pass

info = MockInfo()
result = resolve_parameter_changes(info, game_gid=10000147)
print(f"Found {len(result)} changes")
EOF
```

## 相关文件

- **实现**: `backend/gql_api/resolvers/parameter_resolvers.py`
- **测试**: `backend/test/unit/gql_api/resolvers/test_parameter_resolvers.py`
- **报告**: `backend/test/unit/gql_api/resolvers/P0-16-FIX-REPORT.md`

## 版本历史

- **2026-03-09**: v1.0 - 初始实现（GREEN阶段）
- **2026-03-09**: v0.1 - 空实现（RED阶段）

## 作者

Event2Table Development Team

## 许可证

MIT License
