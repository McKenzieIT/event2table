# DDD Infrastructure 清理计划

> **日期**: 2026-02-26
> **状态**: 待执行
> **目的**: 清理DDD架构遗留代码，完成架构迁移

---

## 一、清理范围

### 1.1 Infrastructure 目录结构

```
backend/infrastructure/
├── __init__.py (0行)
├── events/
│   ├── __init__.py (0行)
│   ├── domain_event_publisher.py (150行)
│   ├── event_handlers.py (288行)
│   └── parameter_event_handlers.py (320行)
├── persistence/
│   ├── __init__.py (15行)
│   ├── event_repository_impl.py (264行)
│   ├── game_repository_impl.py (135行)
│   ├── hql_repository_impl.py (231行)
│   ├── parameter_repository_impl.py (271行)
│   ├── unit_of_work.py (397行)
│   ├── unit_of_work_enhanced.py (549行)
│   └── repositories/
│       ├── __init__.py (49行)
│       ├── common_parameter_repository_impl.py (417行)
│       └── parameter_repository_impl.py (630行)
```

**总代码行数**: 3716 行

### 1.2 已确认的引用关系

#### 生产代码引用（仅2个文件）

1. **backend/api/routes/events_v2.py** (已标记DEPRECATED)
   - 引用: `from backend.infrastructure.persistence.event_repository_impl import EventRepositoryImpl`
   - 状态: 文件头部已标注 "DEPRECATED - Legacy DDD Implementation"
   - 迁移日期: 2026-02-25
   - 计划移除: 版本 2.0
   - **建议**: 直接删除此文件

2. **backend/core/startup/app_initializer.py** (已注释)
   - 引用: `# from backend.infrastructure.events.event_handlers import register_event_handlers`
   - 状态: 已注释掉，标注 "DDD event system removed (2026-02-25)"
   - **建议**: 无需操作，代码已废弃

#### 测试代码引用（4个文件）

- `backend/tests/unit/infrastructure/repositories/test_parameter_repository_impl.py`
- `backend/tests/unit/infrastructure/repositories/test_common_parameter_repository_impl.py`
- `backend/tests/unit/infrastructure/persistence/test_unit_of_work_enhanced.py`
- `backend/tests/integration/infrastructure/test_unit_of_work_integration.py`

**建议**: 随infrastructure目录一起删除

---

## 二、清理计划

### 2.1 可以安全删除的目录

```bash
# 1. 删除infrastructure主目录
rm -rf backend/infrastructure/

# 2. 删除events_v2.py（已标记DEPRECATED）
rm backend/api/routes/events_v2.py

# 3. 删除相关测试目录
rm -rf backend/tests/unit/infrastructure/
rm -rf backend/tests/integration/infrastructure/
```

**预期删除文件数**: ~20个Python文件
**预期删除代码行数**: ~4000行（包含测试）

### 2.2 需要更新的文件

#### backend/core/startup/app_initializer.py

**当前状态**: 已注释掉infrastructure引用
**所需操作**: 无（代码已废弃）

**相关代码**:
```python
# NOTE: DDD event system removed in architecture migration (2026-02-25)
# Event handlers are now managed directly in Service layer with CacheInvalidator
# from backend.infrastructure.events.event_handlers import register_event_handlers, unregister_event_handlers
```

### 2.3 无需迁移的代码

**分析结果**: 所有infrastructure目录中的代码都是DDD架构的实现，已被新的Repository/Service层替代，无需保留任何代码。

---

## 三、依赖关系分析

### 3.1 功能替代关系

| DDD Infrastructure | 新架构替代 | 状态 |
|-------------------|-----------|------|
| EventRepositoryImpl | backend.models.repositories.events.EventRepository | ✅ 已完成 |
| GameRepositoryImpl | backend.models.repositories.games.GameRepository | ✅ 已完成 |
| ParameterRepositoryImpl | backend.models.repositories.parameters.ParameterRepository | ✅ 已完成 |
| EventAppService | backend.services.events.EventService | ✅ 已完成 |
| DomainEventPublisher | CacheInvalidator (Service层直接使用) | ✅ 已完成 |
| UnitOfWork | 直接使用db.session (Flask-SQLAlchemy) | ✅ 已完成 |

### 3.2 API端点替代

| DDD API | 新API | 状态 |
|---------|-------|------|
| /api/v2/events/* | /api/events/* | ✅ 已完成 |
| /api/v2/parameters/* | /api/parameters/* | ✅ 已完成 |

---

## 四、验证计划

### 4.1 删除前检查

- [ ] 确认infrastructure目录无外部引用（除events_v2.py）
- [ ] 确认events_v2.py已标记DEPRECATED
- [ ] 确认所有功能已迁移到新架构

### 4.2 删除后验证

```bash
# 1. 验证应用启动
python web_app.py

# 2. 检查import错误
python -m py_compile backend/api/*.py
python -m py_compile backend/services/**/*.py

# 3. 运行现有测试
pytest backend/tests/unit/ -v
pytest backend/tests/integration/ -v

# 4. 验证API端点
curl http://127.0.0.1:5001/api/events
curl http://127.0.0.1:5001/api/games
```

### 4.3 预期结果

- ✅ 应用正常启动
- ✅ 无import错误
- ✅ 现有测试通过（除infrastructure测试）
- ✅ API端点正常工作

---

## 五、风险评估

### 5.1 低风险 ✅

- **生产代码无直接引用**: 仅2个文件引用，1个已废弃，1个已删除
- **测试代码可安全删除**: 所有infrastructure测试都可以删除
- **功能已完全迁移**: 新架构已完全替代DDD架构

### 5.2 需要注意的点

- ⚠️ 确保events_v2.py确实无前端调用
- ⚠️ 删除前运行一次完整测试作为baseline

---

## 六、执行步骤

### Step 1: 创建备份分支（可选）

```bash
git checkout -b backup/ddd-infrastructure-2026-02-26
git push origin backup/ddd-infrastructure-2026-02-26
git checkout optimization/backend-refactoring-20260220
```

### Step 2: 删除目录和文件

```bash
cd /Users/mckenzie/Documents/event2table

# 删除infrastructure目录
rm -rf backend/infrastructure/

# 删除events_v2.py
rm backend/api/routes/events_v2.py

# 删除infrastructure测试
rm -rf backend/tests/unit/infrastructure/
rm -rf backend/tests/integration/infrastructure/
```

### Step 3: 验证应用

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 启动应用
python web_app.py

# 在另一个终端测试API
curl http://127.0.0.1:5001/api/events
curl http://127.0.0.1:5001/api/games
```

### Step 4: 运行测试

```bash
# 运行单元测试
pytest backend/tests/unit/ -v

# 运行集成测试
pytest backend/tests/integration/ -v
```

### Step 5: 提交更改

```bash
git add -A
git commit -m "refactor: 清理DDD Infrastructure遗留代码

- 删除backend/infrastructure/目录 (3716行)
- 删除backend/api/routes/events_v2.py (已标记DEPRECATED)
- 删除backend/tests/unit/infrastructure/
- 删除backend/tests/integration/infrastructure/

所有功能已迁移到新的Repository/Service架构

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 七、预期成果

### 代码清理

- 删除代码行数: ~4000行（包含测试）
- 删除文件数: ~20个Python文件
- 清理目录数: 4个

### 架构简化

- 移除DDD分层复杂性
- 统一到精简的4层架构（API → Service → Repository → Schema）
- 提高代码可维护性

### 技术债务清理

- 移除遗留的DDD实现
- 移除废弃的Unit of Work模式
- 移除复杂的Domain Event系统

---

## 八、后续工作

### 8.1 更新文档

- [ ] 更新CLAUDE.md，移除DDD相关引用
- [ ] 更新架构文档，反映当前架构
- [ ] 添加架构迁移完成报告

### 8.2 代码审查

- [ ] 检查是否有其他DDD遗留代码
- [ ] 检查是否有未使用的import
- [ ] 检查是否有废弃的TODO注释

---

## 九、参考资料

- [架构迁移指南](/Users/mckenzie/Documents/event2table/docs/development/ARCHITECTURE-MIGRATION-GUIDE.md)
- [架构总结文档](/Users/mckenzie/Documents/event2table/docs/development/architecture.md)
- [清理DDD遗留代码报告](/Users/mckenzie/Documents/event2table/docs/reports/2026-02-25/clean-up-ddd-legacy.md)

---

**文档版本**: 1.0
**创建日期**: 2026-02-26
**维护者**: Event2Table Development Team
