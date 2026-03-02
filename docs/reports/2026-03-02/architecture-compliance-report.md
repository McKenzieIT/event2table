## ✅ 导入违规检查
未发现导入违规

## ❌ Service层直接数据库访问

发现 178 处直接数据库访问

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 28
**内容**: `game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 140
**内容**: `params = fetch_all_as_dict(`
**模式**: fetch_all_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 202
**内容**: `game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 207
**内容**: `event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 212
**内容**: `existing = fetch_one_as_dict(`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 231
**内容**: `node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 261
**内容**: `node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 302
**内容**: `updated_node = fetch_one_as_dict(`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 323
**内容**: `node = fetch_one_as_dict(`
**模式**: fetch_one_as_dict\(

**文件**: backend/services/event_node_builder/__init__.py
**行号**: 362
**内容**: `game = fetch_one_as_dict("SELECT gid FROM games WHERE gid = ?", (game_gid,))`
**模式**: fetch_one_as_dict\(


*... 还有 168 个违规*

## ⚠️  Repository层业务逻辑检查

发现 54 处可能的业务逻辑（需人工审查）

**文件**: backend/models/repositories/event_node_repository.py
**行号**: 28
**内容**: `def __init__(self):`

**文件**: backend/models/repositories/event_node_repository.py
**行号**: 227
**内容**: `def hard_delete(self, node_id: int) -> bool:`

**文件**: backend/models/repositories/event_node_repository.py
**行号**: 244
**内容**: `def count_by_game_gid(self, game_gid: int) -> int:`

**文件**: backend/models/repositories/hql_history_repository.py
**行号**: 28
**内容**: `def __init__(self):`

**文件**: backend/models/repositories/hql_history_repository.py
**行号**: 129
**内容**: `def search_by_keyword(`

**文件**: backend/models/repositories/hql_history_repository.py
**行号**: 185
**内容**: `def count_by_user_id(self, user_id: int) -> int:`

**文件**: backend/models/repositories/hql_history_repository.py
**行号**: 302
**内容**: `def _deserialize_json_fields(self, row: Dict[str, Any]) -> Dict[str, Any]:`

**文件**: backend/models/repositories/flow_repository.py
**行号**: 28
**内容**: `def __init__(self):`

**文件**: backend/models/repositories/flow_repository.py
**行号**: 98
**内容**: `def find_all_active(self) -> List[FlowEntity]:`

**文件**: backend/models/repositories/flow_repository.py
**行号**: 231
**内容**: `def hard_delete(self, flow_id: int) -> bool:`

## 错误处理一致性检查

### ❌ 缺少try-except: 14处

- backend/api/routes/v1_adapter.py:500
- backend/api/routes/events.py:315
- backend/api/routes/hql_preview_v2.py:56
- backend/api/routes/hql_preview_v2.py:654
- backend/api/routes/hql_preview_v2.py:691

### ❌ 原始异常暴露: 84处

- backend/api/routes/v1_adapter.py:359
- backend/api/routes/v1_adapter.py:488
- backend/api/routes/health.py:54
- backend/api/routes/events.py:115
- backend/api/routes/events.py:205

## 数据验证一致性检查

### ❌ 缺少Entity验证: 57处

- backend/api/routes/v1_adapter.py:256
- backend/api/routes/v1_adapter.py:371
- backend/api/routes/events.py:121
- backend/api/routes/events.py:245
- backend/api/routes/events.py:408


================================================================================
📊 合规性统计
================================================================================

- 总检查文件数: 111
- 发现违规数量: 333
- **架构合规率: 70.0%**

================================================================================
🔧 修复建议
================================================================================

### 数据库访问修复
1. 将直接数据库操作移到Repository层
2. Service层只调用Repository方法
3. 使用依赖注入模式

### 错误处理修复
1. 所有路由函数添加try-except
2. 使用json_error_response统一返回错误
3. 避免暴露原始异常信息

### 数据验证修复
1. POST/PUT请求使用Pydantic Entity验证
2. 在API层入口进行参数验证
3. 使用Entity.field_validator进行业务规则验证
