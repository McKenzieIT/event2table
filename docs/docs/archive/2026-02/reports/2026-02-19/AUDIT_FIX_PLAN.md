# 代码审计问题修复详细计划

**日期**: 2026-02-19
**审计结果**: 316个问题 (312严重 + 4高优先级)
**实施策略**: 分阶段修复，使用subagent并行实现

---

## 📋 总览

| 阶段 | 任务 | 问题数 | 预计时间 | 优先级 |
|------|------|--------|----------|--------|
| **阶段1** | SQL注入修复 | 19 | 2-3小时 | P0 |
| **阶段2** | API端点实现 | 4 | 4-6小时 | P1 |
| **阶段3** | Game GID迁移 | 293 | 8-12小时 | P1 |
| **阶段4** | 代码重构 | 5个文件 | 2-3周 | P2 |

---

## 🔴 阶段1: SQL注入漏洞修复 (P0)

### 问题分析 (19个)

#### 类型A: PRAGMA语句 (4个) - **低风险**
这些PRAGMA语句使用的是整数版本号，风险较低，但应使用参数化查询。

**文件**: `backend/core/database/database.py`, `backend/core/database/_helpers.py`

```python
# ❌ 当前代码
cursor.execute(f"PRAGMA user_version = {version}")
cursor.execute(f"PRAGMA {key}={value}")
cursor.execute(f"PRAGMA table_info({table_name})")

# ✅ 修复方案
# 方案1: 使用参数化查询（SQLite不支持PRAGMA参数化）
# 方案2: 验证输入为整数/合法标识符
def _execute_pragma_version(cursor, version):
    """安全执行PRAGMA版本设置"""
    if not isinstance(version, int) or version < 0:
        raise ValueError(f"Invalid PRAGMA version: {version}")
    cursor.execute(f"PRAGMA user_version = {version}")

def _execute_pragma_table_info(cursor, table_name):
    """安全执行PRAGMA table_info"""
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    cursor.execute(f'PRAGMA table_info("{table_name}")')
```

#### 类型B: 动态表名 (8个) - **中等风险**
这些使用`self.table_name`等类属性，来自受控的类定义，但仍应验证。

**文件**: `backend/core/data_access.py`

```python
# ❌ 当前代码
query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"

# ✅ 修复方案
# 在类的__init__中验证表名和字段名
def __init__(self, table_name, primary_key='id'):
    # 验证表名格式
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    self.table_name = table_name

    # 验证主键名格式
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', primary_key):
        raise ValueError(f"Invalid primary key: {primary_key}")
    self.primary_key = primary_key

    # 缓存验证过的字段名
    self._validated_fields = set()
```

#### 类型C: HQL生成器 (7个) - **无风险**
这些是HQL字符串构建，不直接执行SQL，无需修复。

**文件**: `backend/services/hql/core/*.py`, `backend/services/hql/builders/*.py`

**操作**: 标记为误报，在报告中添加说明。

### 修复步骤

#### 步骤1: 创建验证工具函数
```python
# backend/core/security/sql_validator.py
import re
from typing import List

class SQLValidator:
    """SQL标识符验证器"""

    # 合法的SQL标识符正则
    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    @classmethod
    def validate_identifier(cls, identifier: str, name: str = "identifier") -> str:
        """
        验证SQL标识符是否安全

        Args:
            identifier: 要验证的标识符
            name: 标识符名称（用于错误消息）

        Returns:
            验证通过的标识符

        Raises:
            ValueError: 标识符不合法时
        """
        if not isinstance(identifier, str):
            raise ValueError(f"{name} must be a string")

        if not cls.IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(
                f"Invalid {name}: '{identifier}'. "
                f"Must match pattern: {cls.IDENTIFIER_PATTERN.pattern}"
            )

        return identifier

    @classmethod
    def validate_table_name(cls, table_name: str) -> str:
        """验证表名"""
        return cls.validate_identifier(table_name, "table_name")

    @classmethod
    def validate_column_name(cls, column_name: str) -> str:
        """验证列名"""
        return cls.validate_identifier(column_name, "column_name")

    @classmethod
    def validate_pragma_key(cls, key: str) -> str:
        """验证PRAGMA键名"""
        allowed_pragmas = {
            'user_version', 'journal_mode', 'synchronous',
            'cache_size', 'foreign_keys', 'table_info'
        }
        key = cls.validate_identifier(key, "pragma_key")
        if key not in allowed_pragmas:
            raise ValueError(f"PRAGMA key '{key}' not in allowed list")
        return key

    @classmethod
    def validate_integer(cls, value: int, name: str = "value") -> int:
        """验证整数值"""
        if not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
        return value
```

#### 步骤2: 修复database.py中的PRAGMA语句
```python
# backend/core/database/database.py

# 在文件顶部导入
from backend.core.security.sql_validator import SQLValidator

# 修复第1440行
def _set_pragma_version(cursor, version):
    """设置数据库版本（安全）"""
    version = SQLValidator.validate_integer(version, "PRAGMA version")
    cursor.execute(f"PRAGMA user_version = {version}")

# 修复第2738行（同上）

# 修复_helpers.py中的PRAGMA语句
def get_table_info(cursor, table_name):
    """获取表信息（安全）"""
    table_name = SQLValidator.validate_table_name(table_name)
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    return cursor.fetchall()
```

#### 步骤3: 修复data_access.py中的动态表名
```python
# backend/core/data_access.py

from backend.core.security.sql_validator import SQLValidator

class BaseDataAccess:
    def __init__(self, table_name, primary_key='id'):
        # 在构造时验证表名和主键
        self.table_name = SQLValidator.validate_table_name(table_name)
        self.primary_key = SQLValidator.validate_column_name(primary_key)
        self._validated_fields = set()

    def _validate_field(self, field_name: str) -> str:
        """验证并缓存字段名"""
        if field_name not in self._validated_fields:
            SQLValidator.validate_column_name(field_name)
            self._validated_fields.add(field_name)
        return field_name

    def find_by_field(self, field, value):
        """按字段查找（安全）"""
        field = self._validate_field(field)
        query = f"SELECT * FROM {self.table_name} WHERE {field} = ?"
        # ... 执行查询
```

#### 步骤4: 更新API路由中的动态SQL
```python
# backend/api/routes/templates.py

from backend.core.security.sql_validator import SQLValidator

@templates_bp.route('/api/templates', methods=['GET'])
def get_templates():
    # 验证WHERE子句中的字段名
    # 只允许预定义的字段
    ALLOWED_WHERE_FIELDS = {'name', 'game_gid', 'created_at', 'updated_at'}

    where_parts = []
    params = []

    if 'name' in request.args:
        where_parts.append("name LIKE ?")
        params.append(f"%{request.args['name']}%")

    if where_parts:
        where_sql = " AND ".join(where_parts)
        # where_sql现在只包含预定义的字段，安全
        count_sql = f"SELECT COUNT(*) FROM flow_templates WHERE {where_sql}"
        # ... 执行查询
```

### 测试计划

1. **单元测试** - 测试SQLValidator
2. **集成测试** - 测试修复后的函数
3. **安全测试** - 尝试注入攻击

---

## 🟠 阶段2: 实现缺失的API端点 (P1)

### 问题分析 (4个)

前端调用的API端点在后端不存在：

1. **`/api/events/import`** - 事件导入功能
2. **`/api/flows`** - 流程/画布管理
3. **`/api/generate`** - HQL生成
4. **`/api/preview-ex`** - 预览（可能被截断）

### 实施计划

#### API 1: 事件导入 `/api/events/import`

**需求分析**:
- 前端需要批量导入事件
- 可能从CSV/Excel文件导入
- 或从其他数据源同步

**实现方案**:
```python
# backend/api/routes/events.py

@events_bp.route('/api/events/import', methods=['POST'])
def import_events():
    """
    批量导入事件

    Request Body:
        {
            "game_gid": int,
            "events": [
                {
                    "event_name": str,
                    "event_code": str,
                    "description": str,
                    ...
                }
            ]
        }

    Returns:
        {
            "success": true,
            "imported": int,
            "failed": int,
            "errors": []
        }
    """
    from backend.models.schemas import EventImportSchema
    from backend.services.events.event_importer import EventImporter

    try:
        data = EventImportSchema(**request.json)
        game_gid = data.game_gid
        events_data = data.events

        importer = EventImporter()
        result = importer.import_events(game_gid, events_data)

        return json_success_response(
            data={
                "imported": result['imported'],
                "failed": result['failed'],
                "errors": result['errors']
            }
        )

    except Exception as e:
        logger.error(f"Event import failed: {e}")
        return json_error_response(
            f"Event import failed: {str(e)}",
            status_code=500
        )
```

**创建服务层**:
```python
# backend/services/events/event_importer.py

class EventImporter:
    """事件导入服务"""

    def import_events(self, game_gid: int, events_data: List[Dict]) -> Dict:
        """
        批量导入事件

        Args:
            game_gid: 游戏GID
            events_data: 事件数据列表

        Returns:
            导入结果统计
        """
        imported = 0
        failed = 0
        errors = []

        for idx, event_data in enumerate(events_data):
            try:
                # 验证事件数据
                event = EventCreate(**event_data)

                # 检查事件是否已存在
                existing = fetch_one_as_dict(
                    'SELECT * FROM log_events WHERE game_gid = ? AND event_code = ?',
                    (game_gid, event.event_code)
                )

                if existing:
                    errors.append(f"Row {idx+1}: Event {event.event_code} already exists")
                    failed += 1
                    continue

                # 创建事件
                event_id = create_event(game_gid, event)

                imported += 1

            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")
                failed += 1

        return {
            'imported': imported,
            'failed': failed,
            'errors': errors
        }
```

#### API 2: 流程管理 `/api/flows`

**需求分析**:
- Canvas/画布系统需要保存和加载流程配置
- 流程包含多个节点和连接

**实现方案**:
```python
# backend/api/routes/flows.py (新建)

from flask import Blueprint, request
from backend.core.utils import json_success_response, json_error_response
from backend.models.repositories.flow_repository import FlowRepository

flows_bp = Blueprint('flows', __name__)

@flows_bp.route('/api/flows', methods=['GET'])
def list_flows():
    """
    获取流程列表

    Query Params:
        game_gid: int (required)
    """
    game_gid = request.args.get('game_gid', type=int)

    if not game_gid:
        return json_error_response('game_gid is required', status_code=400)

    try:
        repo = FlowRepository()
        flows = repo.find_by_game_gid(game_gid)

        return json_success_response(data=flows)

    except Exception as e:
        logger.error(f"Failed to list flows: {e}")
        return json_error_response(str(e), status_code=500)

@flows_bp.route('/api/flows', methods=['POST'])
def create_flow():
    """
    创建新流程

    Request Body:
        {
            "game_gid": int,
            "name": str,
            "description": str,
            "config": dict  # Canvas配置
        }
    """
    try:
        data = request.json

        repo = FlowRepository()
        flow_id = repo.create(data)

        flow = repo.find_by_id(flow_id)

        return json_success_response(
            data=flow,
            message="Flow created successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create flow: {e}")
        return json_error_response(str(e), status_code=500)

@flows_bp.route('/api/flows/<int:flow_id>', methods=['GET'])
def get_flow(flow_id):
    """获取单个流程详情"""
    try:
        repo = FlowRepository()
        flow = repo.find_by_id(flow_id)

        if not flow:
            return json_error_response('Flow not found', status_code=404)

        return json_success_response(data=flow)

    except Exception as e:
        logger.error(f"Failed to get flow: {e}")
        return json_error_response(str(e), status_code=500)

@flows_bp.route('/api/flows/<int:flow_id>', methods=['PUT'])
def update_flow(flow_id):
    """更新流程"""
    try:
        data = request.json

        repo = FlowRepository()
        repo.update(flow_id, data)

        flow = repo.find_by_id(flow_id)

        return json_success_response(
            data=flow,
            message="Flow updated successfully"
        )

    except Exception as e:
        logger.error(f"Failed to update flow: {e}")
        return json_error_response(str(e), status_code=500)

@flows_bp.route('/api/flows/<int:flow_id>', methods=['DELETE'])
def delete_flow(flow_id):
    """删除流程"""
    try:
        repo = FlowRepository()
        repo.delete(flow_id)

        return json_success_response(
            message="Flow deleted successfully"
        )

    except Exception as e:
        logger.error(f"Failed to delete flow: {e}")
        return json_error_response(str(e), status_code=500)
```

**创建Repository**:
```python
# backend/models/repositories/flow_repository.py

class FlowRepository(GenericRepository):
    """流程仓储类"""

    def __init__(self):
        super().__init__('flow_templates')

    def find_by_game_gid(self, game_gid: int) -> List[Dict]:
        """按游戏GID查找流程"""
        query = 'SELECT * FROM flow_templates WHERE game_gid = ? ORDER BY updated_at DESC'
        return fetch_all_as_dict(query, (game_gid,))

    def create(self, data: Dict) -> int:
        """创建流程"""
        insert_sql = '''
            INSERT INTO flow_templates (
                game_gid, name, description, config,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        '''
        cursor = get_db().execute(insert_sql, (
            data['game_gid'],
            data['name'],
            data.get('description', ''),
            json.dumps(data.get('config', {}))
        ))
        return cursor.lastrowid

    def update(self, flow_id: int, data: Dict):
        """更新流程"""
        update_sql = '''
            UPDATE flow_templates SET
                name = ?,
                description = ?,
                config = ?,
                updated_at = datetime('now')
            WHERE id = ?
        '''
        get_db().execute(update_sql, (
            data['name'],
            data.get('description', ''),
            json.dumps(data.get('config', {})),
            flow_id
        ))

    def delete(self, flow_id: int):
        """删除流程"""
        delete_sql = 'DELETE FROM flow_templates WHERE id = ?'
        get_db().execute(delete_sql, (flow_id,))
```

#### API 3: HQL生成 `/api/generate`

**需求分析**:
- 前端需要生成HQL语句
- 可能是HQL预览或批量生成

**实现方案**:
```python
# backend/api/routes/hql.py (新建)

from flask import Blueprint, request
from backend.core.utils import json_success_response, json_error_response
from backend.services.hql.core.generator import HQLGenerator
from backend.models.schemas import HQLGenerateSchema

hql_bp = Blueprint('hql', __name__)

@hql_bp.route('/api/generate', methods=['POST'])
def generate_hql():
    """
    生成HQL语句

    Request Body:
        {
            "events": [
                {
                    "event_name": str,
                    "table_name": str
                }
            ],
            "fields": [
                {
                    "name": str,
                    "type": str,  # "base", "param", "custom"
                    "json_path": str  # optional
                }
            ],
            "mode": str,  # "single", "join", "union"
            "conditions": []  # optional
        }

    Returns:
        {
            "success": true,
            "hql": str,
            "warnings": []
        }
    """
    try:
        # 验证输入
        data = HQLGenerateSchema(**request.json)

        # 创建生成器
        generator = HQLGenerator()

        # 生成HQL
        hql_result = generator.generate(
            events=data.events,
            fields=data.fields,
            conditions=data.conditions,
            mode=data.mode
        )

        return json_success_response(
            data={
                'hql': hql_result['hql'],
                'warnings': hql_result.get('warnings', [])
            }
        )

    except Exception as e:
        logger.error(f"HQL generation failed: {e}")
        return json_error_response(
            f"HQL generation failed: {str(e)}",
            status_code=500
        )
```

#### API 4: 预览端点 `/api/preview-ex`

**需求分析**:
- 名称被截断，可能是扩展预览功能
- 需要查看前端调用代码确认

**临时方案**:
- 先实现为 `/api/preview` 的别名
- 与前端确认后调整

```python
# backend/api/routes/preview.py (新建)

from flask import Blueprint, request
from backend.services.hql.core.generator import HQLGenerator

preview_bp = Blueprint('preview', __name__)

@preview_bp.route('/api/preview', methods=['POST'])
@preview_bp.route('/api/preview-ex', methods=['POST'])  # 别名
def preview_hql():
    """
    HQL预览（执行并返回结果）

    Request Body: 与/api/generate相同
    Returns: 包含HQL和执行结果
    """
    try:
        # 先生成HQL
        data = HQLGenerateSchema(**request.json)

        generator = HQLGenerator()
        hql_result = generator.generate(
            events=data.events,
            fields=data.fields,
            conditions=data.conditions,
            mode=data.mode
        )

        # TODO: 执行HQL并返回结果（如果需要）
        # 目前只返回HQL

        return json_success_response(
            data={
                'hql': hql_result['hql'],
                'preview': True
            }
        )

    except Exception as e:
        logger.error(f"Preview failed: {e}")
        return json_error_response(str(e), status_code=500)
```

### 注册Blueprint

```python
# backend/api/routes/__init__.py (或 web_app.py)

from backend.api.routes.flows import flows_bp
from backend.api.routes.hql import hql_bp
from backend.api.routes.preview import preview_bp

# 注册新的blueprints
app.register_blueprint(flows_bp)
app.register_blueprint(hql_bp)
app.register_blueprint(preview_bp)
```

### 测试计划

1. **API契约测试** - 验证所有端点可访问
2. **功能测试** - 测试每个API的业务逻辑
3. **集成测试** - 测试前端调用

---

## 🟡 阶段3: Game GID合规性修复 (P1)

### 问题分析 (293个)

**核心问题**:
- 数据库表使用`game_id`而非`game_gid`作为外键
- 违反Event2Table架构规则
- 影响所有数据关联

**受影响的表**:
1. `log_events` - 事件表
2. `event_params` - 事件参数表
3. `common_params` - 公共参数表
4. `join_configs` - 连接配置表
5. `flow_templates` - 流程模板表
6. `event_nodes` - 事件节点表
7. `parameter_aliases` - 参数别名表
8. `field_name_mappings` - 字段名映射表

### 修复策略

#### 方案选择

**方案A: 创建新表 + 迁移数据** ✅ 推荐
- 优点：安全，可以回滚
- 缺点：需要较长时间
- 步骤：创建新表 → 迁移数据 → 验证 → 删除旧表

**方案B: 修改现有表** ❌ 高风险
- 优点：快速
- 缺点：数据丢失风险高，不可回滚

**选择方案A**：安全第一

### 详细实施步骤

#### 步骤1: 准备工作

1. **备份数据库**
```bash
# 创建备份
cp data/dwd_generator.db data/dwd_generator.db.backup_$(date +%Y%m%d)
```

2. **分析当前数据**
```python
# scripts/analyze_game_id_migration.py

def analyze_migration():
    """分析迁移影响"""
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()

    # 统计每个表的记录数
    tables = [
        'log_events', 'event_params', 'common_params',
        'join_configs', 'flow_templates', 'event_nodes',
        'parameter_aliases', 'field_name_mappings'
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    # 检查game_id的唯一值
    cursor.execute("SELECT DISTINCT game_id FROM games ORDER BY game_id")
    game_ids = cursor.fetchall()
    print(f"\nGame IDs: {[g[0] for g in game_ids]}")

    # 检查game_gid的值
    cursor.execute("SELECT gid, name FROM games ORDER BY gid")
    games = cursor.fetchall()
    print(f"\nGame GIDs: {[(g[0], g[1]) for g in games]}")
```

#### 步骤2: 创建迁移脚本

```python
# scripts/migrate_game_gid.py

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/dwd_generator.db"
BACKUP_PATH = f"data/dwd_generator.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Game ID到GID的映射（从games表获取）
GAME_ID_TO_GID = {}
GAME_GID_TO_ID = {}

def load_game_mappings(conn):
    """加载game_id到game_gid的映射"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, gid FROM games")
    mappings = cursor.fetchall()

    for game_id, game_gid in mappings:
        GAME_ID_TO_GID[game_id] = game_gid
        GAME_GID_TO_ID[game_gid] = game_id

    logger.info(f"Loaded {len(mappings)} game mappings")

def backup_database():
    """备份数据库"""
    logger.info(f"Creating backup: {BACKUP_PATH}")
    import shutil
    shutil.copy2(DB_PATH, BACKUP_PATH)
    logger.info("Backup created successfully")

def migrate_table(conn, table_name, old_column='game_id', new_column='game_gid'):
    """
    迁移单个表

    步骤：
    1. 添加game_gid列
    2. 从game_id更新game_gid的值
    3. 删除旧的game_id列
    4. 重建索引和约束
    """
    cursor = conn.cursor()

    logger.info(f"Migrating table: {table_name}")

    try:
        # 1. 检查列是否存在
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        if new_column in columns:
            logger.info(f"  Column {new_column} already exists, skipping...")
            return

        if old_column not in columns:
            logger.warning(f"  Column {old_column} not found, skipping...")
            return

        # 2. 开始事务
        conn.execute("BEGIN TRANSACTION")

        # 3. 添加game_gid列
        logger.info(f"  Adding {new_column} column...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column} INTEGER")

        # 4. 更新数据：从game_id映射到game_gid
        logger.info(f"  Updating data from {old_column} to {new_column}...")
        cursor.execute(f"SELECT DISTINCT {old_column} FROM {table_name}")
        game_ids = [row[0] for row in cursor.fetchall() if row[0] is not None]

        for game_id in game_ids:
            game_gid = GAME_ID_TO_GID.get(game_id)
            if game_gid:
                cursor.execute(
                    f"UPDATE {table_name} SET {new_column} = ? WHERE {old_column} = ?",
                    (game_gid, game_id)
                )
                logger.info(f"    Migrated {old_column}={game_id} -> {new_column}={game_gid}")
            else:
                logger.warning(f"    No mapping found for {old_column}={game_id}")

        # 5. 验证数据
        logger.info("  Verifying migration...")
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {new_column} IS NULL AND {old_column} IS NOT NULL"
        )
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            raise Exception(f"  Migration incomplete: {null_count} records have NULL {new_column}")

        # 6. 删除旧的game_id列（SQLite不支持DROP COLUMN，需要重建表）
        logger.info(f"  Dropping {old_column} column...")
        migrate_table_without_column(conn, table_name, old_column)

        # 提交事务
        conn.commit()
        logger.info(f"  ✅ Table {table_name} migrated successfully")

    except Exception as e:
        conn.rollback()
        logger.error(f"  ❌ Migration failed for {table_name}: {e}")
        raise

def migrate_table_without_column(conn, table_name, column_to_drop):
    """
    SQLite不支持DROP COLUMN，需要重建表

    步骤：
    1. 创建新表（不包含要删除的列）
    2. 复制数据
    3. 删除旧表
    4. 重命名新表
    """
    cursor = conn.cursor()

    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # 构建新表的列定义（排除要删除的列）
    new_columns = [col for col in columns if col[1] != column_to_drop]

    # 获取CREATE TABLE语句
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    create_sql = cursor.fetchone()[0]

    # 修改CREATE TABLE语句
    temp_table = f"{table_name}_new"

    # 构建新表的CREATE语句
    new_create_sql = create_sql.replace(f"CREATE TABLE {table_name}", f"CREATE TABLE {temp_table}")

    # 创建新表
    cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
    cursor.execute(new_create_sql)

    # 复制数据
    columns_list = ', '.join([col[1] for col in new_columns])
    cursor.execute(f"INSERT INTO {temp_table} ({columns_list}) SELECT {columns_list} FROM {table_name}")

    # 删除旧表
    cursor.execute(f"DROP TABLE {table_name}")

    # 重命名新表
    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")

    # 重建索引
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{temp_table}'")
    indexes = cursor.fetchall()
    for index in indexes:
        cursor.execute(f"DROP INDEX IF EXISTS {index[0]}")

def rebuild_foreign_keys(conn):
    """重建外键约束"""

    foreign_keys = [
        ("log_events", "game_gid", "games", "gid"),
        ("event_params", "game_gid", "games", "gid"),
        ("common_params", "game_gid", "games", "gid"),
        ("join_configs", "game_gid", "games", "gid"),
        ("flow_templates", "game_gid", "games", "gid"),
        ("event_nodes", "game_gid", "games", "gid"),
        ("parameter_aliases", "game_gid", "games", "gid"),
        ("field_name_mappings", "game_gid", "games", "gid"),
    ]

    cursor = conn.cursor()

    for table, fk_column, ref_table, ref_column in foreign_keys:
        logger.info(f"Rebuilding foreign key: {table}.{fk_column} -> {ref_table}.{ref_column}")

        # SQLite需要重建表来添加外键
        # 这里简化处理，只确保数据一致性
        cursor.execute(f"PRAGMA foreign_keys=ON")

        # 验证外键
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table}
            WHERE {fk_column} IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM {ref_table} WHERE {ref_column} = {table}.{fk_column})
        """)

        invalid_count = cursor.fetchone()[0]
        if invalid_count > 0:
            logger.warning(f"  Found {invalid_count} invalid foreign key references")

def rebuild_indexes(conn):
    """重建索引"""

    indexes = [
        ("idx_log_events_game_gid", "log_events", "game_gid"),
        ("idx_event_params_game_gid", "event_params", "game_gid"),
        ("idx_common_params_game_gid", "common_params", "game_gid"),
        ("idx_join_configs_game_gid", "join_configs", "game_gid"),
        ("idx_flow_templates_game_gid", "flow_templates", "game_gid"),
        ("idx_event_nodes_game_gid", "event_nodes", "game_gid"),
        ("idx_parameter_aliases_game_gid", "parameter_aliases", "game_gid"),
        ("idx_field_name_mappings_game_gid", "field_name_mappings", "game_gid"),
    ]

    cursor = conn.cursor()

    for index_name, table, column in indexes:
        logger.info(f"Creating index: {index_name}")
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        cursor.execute(f"CREATE INDEX {index_name} ON {table}({column})")

def main():
    """主函数"""
    logger.info("="*60)
    logger.info("Game GID Migration Script")
    logger.info("="*60)

    # 1. 备份数据库
    backup_database()

    # 2. 连接数据库
    conn = sqlite3.connect(DB_PATH)

    try:
        # 3. 加载游戏映射
        load_game_mappings(conn)

        # 4. 迁移每个表
        tables = [
            'log_events',
            'event_params',
            'common_params',
            'join_configs',
            'flow_templates',
            'event_nodes',
            'parameter_aliases',
            'field_name_mappings'
        ]

        for table in tables:
            migrate_table(conn, table)

        # 5. 重建外键
        rebuild_foreign_keys(conn)

        # 6. 重建索引
        rebuild_indexes(conn)

        logger.info("="*60)
        logger.info("✅ Migration completed successfully!")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.info("Rolling back changes...")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
```

#### 步骤3: 更新代码

**更新Schema**:
```python
# backend/models/schemas.py

class EventBase(BaseModel):
    """事件基础Schema"""
    game_gid: int  # 改为game_gid
    event_code: str
    event_name: str
    # ...
```

**更新Repository**:
```python
# backend/models/repositories/events.py

class EventRepository(GenericRepository):
    """事件仓储类"""

    def find_by_game_gid(self, game_gid: int):
        """按游戏GID查找事件"""
        query = 'SELECT * FROM log_events WHERE game_gid = ?'
        return fetch_all_as_dict(query, (game_gid,))
```

**更新API路由**:
```python
# backend/api/routes/events.py

@events_bp.route('/api/events', methods=['GET'])
def get_events():
    """获取事件列表"""
    game_gid = request.args.get('game_gid', type=int)  # 改为game_gid

    if not game_gid:
        return json_error_response('game_gid is required', status_code=400)

    # ...
```

**更新Service层**:
```python
# backend/services/events/event_service.py

class EventService:
    def get_events_by_game(self, game_gid: int):
        """获取游戏的所有事件"""
        return self.event_repo.find_by_game_gid(game_gid)
```

#### 步骤4: 验证和测试

```python
# scripts/verify_migration.py

def verify_migration():
    """验证迁移结果"""
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()

    print("验证迁移结果...")

    # 1. 检查所有表都有game_gid列
    tables = [
        'log_events', 'event_params', 'common_params',
        'join_configs', 'flow_templates', 'event_nodes',
        'parameter_aliases', 'field_name_mappings'
    ]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        if 'game_gid' not in columns:
            print(f"❌ {table}: Missing game_gid column")
        elif 'game_id' in columns:
            print(f"⚠️  {table}: Still has game_id column")
        else:
            print(f"✅ {table}: Migration successful")

    # 2. 验证外键
    for table in tables:
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table}
            WHERE game_gid IS NOT NULL
            AND NOT EXISTS (SELECT 1 FROM games WHERE gid = {table}.game_gid)
        """)
        invalid_count = cursor.fetchone()[0]

        if invalid_count > 0:
            print(f"❌ {table}: {invalid_count} invalid foreign key references")
        else:
            print(f"✅ {table}: All foreign keys valid")

    # 3. 验证数据完整性
    cursor.execute("SELECT COUNT(*) FROM log_events")
    event_count = cursor.fetchone()[0]
    print(f"\n总事件数: {event_count}")

    cursor.execute("SELECT COUNT(*) FROM log_events WHERE game_gid IS NULL")
    null_count = cursor.fetchone()[0]
    print(f"NULL game_gid: {null_count}")

    if null_count == 0:
        print("✅ 数据迁移完整")
    else:
        print(f"❌ 有{null_count}条记录的game_gid为NULL")

if __name__ == "__main__":
    verify_migration()
```

### 回滚计划

如果迁移失败，执行回滚：

```python
# scripts/rollback_migration.py

def rollback_migration():
    """回滚迁移"""
    import shutil
    from pathlib import Path

    backup = Path(BACKUP_PATH)
    current = Path(DB_PATH)

    if not backup.exists():
        print("❌ 备份文件不存在")
        return

    # 删除当前数据库
    current.unlink()

    # 恢复备份
    shutil.copy2(backup, current)

    print(f"✅ 已回滚到备份: {backup}")
```

---

## 🟢 阶段4: 代码重构 (P2)

### 问题分析

最复杂的5个文件需要重构：

1. `backend/core/database/database.py` - **2,827行** 🔴
2. `backend/api/routes/hql_preview_v2.py` - **1,369行** 🟡
3. `backend/core/utils.py` - **1,355行** 🟡
4. `backend/models/events.py` - **1,350行** 🟡
5. `backend/core/cache/cache_system.py` - **921行** 🟡

### 重构计划

#### 文件1: database.py (2827行)

**拆分方案**:
```
backend/core/database/
├── __init__.py
├── database.py           # 核心数据库连接 (200行)
├── migrations/           # 迁移脚本
│   ├── __init__.py
│   ├── migration_v1.py
│   ├── migration_v2.py
│   └── ...
├── schema/               # 数据库架构
│   ├── __init__.py
│   ├── games_schema.py
│   ├── events_schema.py
│   └── params_schema.py
├── operations/           # 数据库操作
│   ├── __init__.py
│   ├── game_operations.py
│   ├── event_operations.py
│   └── param_operations.py
└── _helpers.py           # 辅助函数
```

**重构步骤**:
1. 提取迁移脚本到`migrations/`目录
2. 提取表架构定义到`schema/`目录
3. 提取CRUD操作到`operations/`目录
4. 保留核心连接和事务管理在`database.py`

#### 文件2: hql_preview_v2.py (1369行)

**拆分方案**:
```
backend/api/routes/hql/
├── __init__.py
├── preview.py            # 预览路由 (300行)
├── generation.py         # 生成路由 (300行)
├── validation.py         # 验证路由 (200行)
└── helpers.py            # 辅助函数
```

#### 文件3: utils.py (1355行)

**拆分方案**:
```
backend/core/utils/
├── __init__.py
├── validators.py         # 验证函数
├── formatters.py         # 格式化函数
├── converters.py         # 转换函数
└── helpers.py            # 其他辅助函数
```

**重构优先级**: P2（下季度）
**预计时间**: 2-3周

---

## 🧪 测试计划

### 使用Chrome DevTools MCP进行E2E测试

#### 测试环境准备

1. **启动后端服务器**:
```bash
cd /Users/mckenzie/Documents/event2table
source venv/bin/activate
python web_app.py
# 运行在 http://127.0.0.1:5001
```

2. **启动前端服务器**:
```bash
cd frontend
npm run dev
# 运行在 http://localhost:5173
```

#### 测试场景

**场景1: SQL注入修复验证**
```javascript
// 使用Chrome MCP测试
await mcp__chrome_devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
});

// 检查页面加载成功
await mcp__chrome_devtools__wait_for("参数管理");

// 检查控制台无SQL错误
await mcp__chrome_devtools__list_console_messages({
  types: ["error"]
});
```

**场景2: 新API端点测试**
```javascript
// 测试事件导入API
await mcp__chrome_devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/events/import?game_gid=10000147"
});

// 填写导入表单
await mcp__chrome_devtools__fill({
  uid: "file-input",
  value: "/path/to/test_events.csv"
});

// 提交表单
await mcp__chrome_devtools__click({ uid: "import-button" });

// 验证成功消息
await mcp__chrome_devtools__wait_for("导入成功");

// 检查API响应
await mcp__chrome_devtools__list_network_requests({
  resourceTypes: ["fetch", "xhr"]
});
```

**场景3: Game GID迁移验证**
```javascript
// 测试数据关联正确性
await mcp__chrome_devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/dashboard?game_gid=10000147"
});

// 验证事件统计显示正确
await mcp__chrome_devtools__take_snapshot();

// 检查game_gid参数传递
await mcp__chrome_devtools__list_network_requests({
  resourceTypes: ["fetch", "xhr"]
});

// 验证所有请求使用game_gid而非game_id
```

---

## 📅 实施时间表

| 阶段 | 任务 | 开始时间 | 预计完成 | Subagent数量 |
|------|------|----------|----------|--------------|
| **1** | SQL注入修复 | Day 1 | Day 1 | 2个并行 |
| **2** | API端点实现 | Day 2 | Day 3 | 4个并行 |
| **3** | Game GID迁移 | Day 4 | Day 6 | 1个（需要串行） |
| **4** | Chrome MCP测试 | Day 6 | Day 7 | 1个 |

**总计**: 7个工作日

---

## 🤖 Subagent部署计划

### 阶段1: SQL注入修复 (2个subagent并行)

**Subagent A**: 修复database.py和_helpers.py
- 目标: 修复PRAGMA语句
- 文件: database.py, _helpers.py
- 输出: 验证函数 + 修复的代码

**Subagent B**: 修复data_access.py和templates.py
- 目标: 修复动态表名
- 文件: data_access.py, templates.py
- 输出: 验证函数 + 修复的代码

### 阶段2: API端点实现 (4个subagent并行)

**Subagent A**: 实现事件导入API
- 端点: `/api/events/import`
- 文件: routes/events.py, services/events/event_importer.py

**Subagent B**: 实现流程管理API
- 端点: `/api/flows`
- 文件: routes/flows.py, models/repositories/flow_repository.py

**Subagent C**: 实现HQL生成API
- 端点: `/api/generate`
- 文件: routes/hql.py

**Subagent D**: 实现预览API
- 端点: `/api/preview-ex`
- 文件: routes/preview.py

### 阶段3: Game GID迁移 (1个subagent)

**Subagent A**: 执行迁移
- 创建迁移脚本
- 备份数据库
- 执行迁移
- 验证结果

### 阶段4: Chrome MCP测试 (1个subagent)

**Subagent A**: E2E测试
- 测试SQL修复
- 测试新API
- 测试Game GID功能
- 生成测试报告

---

## ✅ 验收标准

### SQL注入修复
- [ ] 所有PRAGMA语句使用验证
- [ ] 所有动态表名使用验证
- [ ] 通过安全测试
- [ ] 代码审查通过

### API端点实现
- [ ] 4个端点全部实现
- [ ] API契约测试通过
- [ ] 前端调用成功
- [ ] 文档更新完成

### Game GID迁移
- [ ] 所有表使用game_gid
- [ ] 数据迁移完整
- [ ] 外键约束正确
- [ ] 前后端功能正常

### E2E测试
- [ ] 所有测试场景通过
- [ ] 控制台无错误
- [ ] 性能无明显下降
- [ ] 测试报告完整

---

**准备就绪！请确认此计划，我将启动subagents开始实施。**
