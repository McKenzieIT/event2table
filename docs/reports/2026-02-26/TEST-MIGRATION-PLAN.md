# 测试文件迁移计划 - Entity架构

**日期**: 2026-02-26
**状态**: In Progress
**影响范围**: backend/tests/ 目录下所有测试文件

---

## 问题分析

### 当前状态

运行旧测试时出现导入错误：
```
ModuleNotFoundError: No module named 'backend.domain.models'
```

**根本原因**：
- 旧DDD架构已废弃（`backend.domain.models.parameter` 等）
- 新架构使用统一Entity模型（`backend.models.entities`）
- 测试文件仍在使用已删除的模块

### 影响的测试文件

| 文件 | 状态 | 需要更新 |
|------|------|---------|
| `backend/tests/unit/domain/test_parameter_model.py` | ❌ 失败 | ✅ 是 |
| `backend/tests/unit/domain/test_common_parameter_model.py` | ❌ 失败 | ✅ 是 |
| `backend/tests/unit/application/test_parameter_app_service.py` | ❌ 失败 | ✅ 是 |
| `backend/tests/unit/infrastructure/repositories/test_parameter_repository_impl.py` | ❌ 失败 | ✅ 是 |
| `backend/tests/unit/infrastructure/repositories/test_common_parameter_repository_impl.py` | ❌ 失败 | ✅ 是 |
| 其他 GraphQL 测试 | ⚠️ 需检查 | ⚠️ 可能 |

---

## 迁移策略

### 策略 1: 删除已废弃的DDD测试

**适用场景**：
- 测试的DDD模式已完全废弃（如Value Objects、Aggregates）
- 新架构不再需要这些测试

**需要删除的测试**：
```python
# ❌ 删除 - DDD领域模型测试
backend/tests/unit/domain/test_parameter_model.py
backend/tests/unit/domain/test_common_parameter_model.py
backend/tests/unit/domain/test_parameter_management_service.py

# ❌ 删除 - DDD应用服务测试
backend/tests/unit/application/test_parameter_app_service.py
backend/tests/unit/application/test_parameter_dto.py
backend/tests/unit/application/test_event_builder_app_service.py

# ❌ 删除 - DDD仓储实现测试
backend/tests/unit/infrastructure/repositories/test_parameter_repository_impl.py
backend/tests/unit/infrastructure/repositories/test_common_parameter_repository_impl.py
backend/tests/unit/infrastructure/persistence/test_unit_of_work_enhanced.py
```

### 策略 2: 保留并迁移功能测试

**适用场景**：
- 测试的业务逻辑仍然有效
- 只需要更新导入和断言

**迁移模式**：

#### 旧模式（DDD）
```python
from backend.domain.models.parameter import Parameter
from backend.application.services.parameter_app_service import ParameterAppService

def test_create_parameter():
    param = Parameter(
        param_name='guild_id',
        param_type='string',
        is_common=False
    )
    assert param.param_name == 'guild_id'
```

#### 新模式（Entity）
```python
from backend.models.entities import ParameterEntity
from backend.services.parameters.parameter_service import ParameterService

def test_create_parameter():
    param = ParameterEntity(
        name='guild_id',
        param_type='base',
        json_path='$.guildId'
    )
    assert param.name == 'guild_id'
```

### 策略 3: 创建新的Entity验证测试

**新增测试**：
```python
# backend/tests/unit/models/test_parameter_entity.py
"""
Unit Tests for ParameterEntity

Tests for Pydantic Entity model including:
- Field validation
- Type conversion
- XSS protection
- JSON schema generation
"""

import pytest
from backend.models.entities import ParameterEntity

class TestParameterEntityValidation:
    """Test Pydantic validation"""

    def test_valid_parameter_creation(self):
        """Test valid parameter creation"""
        param = ParameterEntity(
            id=1,
            event_id=1,
            game_gid=90000001,
            name='guild_id',
            param_type='base',
            json_path='$.guildId'
        )
        assert param.name == 'guild_id'
        assert param.param_type == 'base'

    def test_xss_protection(self):
        """Test XSS protection in name field"""
        param = ParameterEntity(
            event_id=1,
            game_gid=90000001,
            name='<script>alert("xss")</script>',
            param_type='base'
        )
        assert '<script>' not in param.name
        assert '&lt;script&gt;' in param.name

    def test_json_path_validation(self):
        """Test JSON path validation"""
        with pytest.raises(ValueError, match="JSON路径必须以"):
            ParameterEntity(
                event_id=1,
                game_gid=90000001,
                name='test',
                param_type='param',
                json_path='invalid_path'
            )

    def test_gid_type_conversion(self):
        """Test GID accepts string and converts to int"""
        param1 = ParameterEntity(
            event_id=1,
            game_gid=90000001,
            name='test',
            param_type='base'
        )
        param2 = ParameterEntity(
            event_id=1,
            game_gid="90000001",  # String
            name='test',
            param_type='base'
        )
        assert param1.game_gid == param2.game_gid
        assert isinstance(param2.game_gid, int)

class TestParameterEntitySerialization:
    """Test Entity serialization"""

    def test_model_dump(self):
        """Test model_dump() returns dict"""
        param = ParameterEntity(
            id=1,
            event_id=1,
            game_gid=90000001,
            name='guild_id',
            param_type='base'
        )
        data = param.model_dump()
        assert isinstance(data, dict)
        assert data['name'] == 'guild_id'

    def test_model_dump_json(self):
        """Test model_dump_json() returns JSON string"""
        param = ParameterEntity(
            id=1,
            event_id=1,
            game_gid=90000001,
            name='guild_id',
            param_type='base'
        )
        json_str = param.model_dump_json()
        assert isinstance(json_str, str)
        assert 'guild_id' in json_str

    def test_json_schema(self):
        """Test JSON Schema generation"""
        schema = ParameterEntity.model_json_schema()
        assert 'properties' in schema
        assert 'name' in schema['properties']
        assert 'param_type' in schema['properties']
```

---

## 测试迁移清单

### Phase 1: 清理废弃测试（立即执行）

- [ ] 删除 `backend/tests/unit/domain/` 目录
- [ ] 删除 `backend/tests/unit/application/` 目录
- [ ] 删除 `backend/tests/unit/infrastructure/` 目录
- [ ] 删除 `backend/tests/integration/infrastructure/` 目录

### Phase 2: 创建新Entity测试（高优先级）

- [ ] 创建 `backend/tests/unit/models/test_game_entity.py`
- [ ] 创建 `backend/tests/unit/models/test_event_entity.py`
- [ ] 创建 `backend/tests/unit/models/test_parameter_entity.py`
- [ ] 创建 `backend/tests/unit/models/test_common_parameter_entity.py`

### Phase 3: 迁移Service层测试（中优先级）

- [ ] 创建 `backend/tests/unit/services/test_game_service.py`
- [ ] 创建 `backend/tests/unit/services/test_event_service.py`
- [ ] 创建 `backend/tests/unit/services/test_parameter_service.py`

### Phase 4: 迁移API层测试（低优先级）

- [ ] 更新 `backend/tests/integration/api/test_games_api.py`
- [ ] 更新 `backend/tests/integration/api/test_events_api.py`
- [ ] 更新 `backend/tests/integration/api/test_parameters_api.py`

### Phase 5: GraphQL测试（待评估）

- [ ] 评估GraphQL测试是否需要保留
- [ ] 如果保留，更新导入路径

---

## 字段映射表

### Parameter Model

| 旧字段（DDD） | 新字段（Entity） | 说明 |
|--------------|-----------------|------|
| `param_name` | `name` | 参数名称 |
| `param_type` | `param_type` | 类型（枚举值变化） |
| `is_common` | `is_common` | 保留 |
| `is_active` | 删除 | 新架构不使用软删除 |
| `version` | 删除 | 新架构不使用乐观锁 |
| `json_path` | `json_path` | 保留 |

### param_type 枚举值变化

| 旧值（DDD） | 新值（Entity） |
|------------|---------------|
| `string` | `base` |
| `int` | `base` |
| `param` | `param` |
| `common` | `common` |
| `calculate` | `calculate` |

---

## 实施步骤

### 步骤 1: 备份现有测试
```bash
cp -r backend/tests backend/tests.backup.$(date +%Y%m%d)
```

### 步骤 2: 删除废弃测试
```bash
rm -rf backend/tests/unit/domain
rm -rf backend/tests/unit/application
rm -rf backend/tests/unit/infrastructure
rm -rf backend/tests/integration/infrastructure
```

### 步骤 3: 创建新测试目录
```bash
mkdir -p backend/tests/unit/models
mkdir -p backend/tests/unit/services
mkdir -p backend/tests/integration/api
```

### 步骤 4: 创建Entity测试
```bash
# 创建基础Entity测试文件
touch backend/tests/unit/models/__init__.py
touch backend/tests/unit/models/test_game_entity.py
touch backend/tests/unit/models/test_event_entity.py
touch backend/tests/unit/models/test_parameter_entity.py
```

### 步骤 5: 运行测试验证
```bash
pytest backend/tests/unit/models/ -v
pytest backend/tests/unit/services/ -v
```

---

## 预期结果

### 测试覆盖率

- **Entity验证**: 100%（所有字段验证规则）
- **Service业务逻辑**: 80%+（核心业务逻辑）
- **API集成**: 60%+（关键API端点）

### 测试运行时间

- **单元测试**: < 30秒
- **集成测试**: < 2分钟
- **总测试时间**: < 5分钟

---

## 风险评估

### 高风险

- ❌ **删除测试后可能遗漏业务逻辑验证**
  - **缓解**: 仔细审查每个测试的业务逻辑，确保在新测试中覆盖

### 中风险

- ⚠️ **GraphQL API可能仍在使用旧模型**
  - **缓解**: 先评估GraphQL使用情况，再决定是否保留测试

### 低风险

- ✅ **Entity验证通过Pydantic自动处理**
  - **优势**: Pydantic本身已包含大量验证逻辑

---

## 后续优化

1. **添加property-based测试**: 使用Hypothesis库生成随机测试数据
2. **添加性能测试**: 测试Entity创建和序列化性能
3. **添加快照测试**: 验证Entity的JSON schema稳定性
4. **集成覆盖率报告**: 使用pytest-cov监控测试覆盖率

---

## 参考资料

- [Pydantic Testing Guide](https://docs.pydantic.dev/latest/concepts/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Entity Architecture](/Users/mckenzie/Documents/event2table/docs/development/architecture.md)
