# 重构检查清单

> **来源**: 整合了多个重构项目的经验
> **最后更新**: 2026-02-24
> **维护**: 每次重构项目后立即更新

---

## TDD重构流程 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CLAUDE.md](../../CLAUDE.md#tdd开发模式), [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md)

### TDD铁律

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

**Red-Green-Refactor循环**:
1. **Red** - 先写测试，看测试失败
2. **Green** - 编写最小代码使测试通过
3. **Refactor** - 重构优化，保持测试通过

### 重构前的准备

**1. 确保有测试覆盖**:
```bash
# 检查测试覆盖率
pytest backend/test/ --cov=backend --cov-report=html
npm run test:coverage
```

**2. 添加失败测试**:
```python
# 先写测试（应该失败）
def test_new_feature():
    result = calculate_something()
    assert result == expected_value  # ❌ 测试失败（功能未实现）

# 然后实现功能（测试通过）
def calculate_something():
    return expected_value  # ✅ 测试通过
```

### 重构步骤

**1. 小步重构**:
- ✅ 每次只重构一小部分
- ✅ 每次重构后运行测试
- ✅ 确保测试始终通过

**2. 提取方法**:
```python
# 重构前
def process_event(event):
    # 复杂逻辑
    if event['type'] == 'login':
        # ... 100行代码 ...
    elif event['type'] == 'logout':
        # ... 100行代码 ...

# 重构后
def process_event(event):
    if event['type'] == 'login':
        return process_login(event)
    elif event['type'] == 'logout':
        return process_logout(event)

def process_login(event):
    # 登录逻辑

def process_logout(event):
    # 登出逻辑
```

**3. 引入参数对象**:
```python
# 重构前
def create_event(name, game_gid, table_name, fields, conditions, mode):
    # 太多参数

# 重构后
@dataclass
class EventConfig:
    name: str
    game_gid: int
    table_name: str
    fields: List[Field]
    conditions: List[Condition]
    mode: str

def create_event(config: EventConfig):
    # 清晰的参数
```

### 重构验证

**验证清单**:
- [ ] 所有测试是否通过？
- [ ] 测试覆盖率是否保持？
- [ ] 功能是否等效？
- [ ] 性能是否改善或保持？

### 相关经验

- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - TDD详细流程
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构重构

---

## 代码审查清单 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [多个审查报告](../archive/2026-02/)

### React组件审查

- [ ] 所有Hooks都在组件最顶层调用？
- [ ] 没有任何Hook在条件语句、循环或嵌套函数中？
- [ ] 没有在Hooks调用之间进行条件返回？
- [ ] 每次渲染时Hooks的调用顺序相同？
- [ ] ESLint React Hooks规则已启用？
- [ ] 组件是否使用TypeScript类型注解？
- [ ] 是否有适当的性能优化（React.memo、useCallback）？

### Python代码审查

- [ ] 所有SQL查询是否使用 `game_gid` 而非 `game_id`？
- [ ] 所有SQL查询是否使用参数化查询？
- [ ] 所有动态SQL标识符是否使用SQLValidator验证？
- [ ] 是否使用Pydantic Schema验证输入？
- [ ] 错误处理是否适当（400/404/409/500）？
- [ ] 是否有完整的类型注解？
- [ ] 是否有完整的docstring？

### 安全审查

- [ ] 输入验证（必填字段、数据类型、长度限制）
- [ ] XSS防护（HTML转义用户输入）
- [ ] SQL注入防护（参数化查询）
- [ ] SQLValidator验证（动态标识符）
- [ ] 输出编码（JSON响应，不暴露内部信息）
- [ ] 错误处理（适当的HTTP状态码：400/404/409/500）

### 性能审查

- [ ] 是否有N+1查询？
- [ ] 是否可以使用JOIN合并多次查询？
- [ ] 是否可以合并统计查询？
- [ ] 缓存TTL是否合理（5-10分钟）？
- [ ] 修改数据的API是否清理缓存？
- [ ] 是否使用EXPLAIN QUERY PLAN分析慢查询？

### 测试审查

- [ ] 是否有单元测试？
- [ ] 是否有集成测试？
- [ ] 是否有E2E测试（关键路径）？
- [ ] 测试覆盖率是否达标（>80%）？
- [ ] 测试是否先于代码编写（TDD）？

### 违规后果

**必须拒绝的Code Review**:
- ❌ 使用game_id而非game_gid
- ❌ SQL注入风险（字符串拼接）
- ❌ XSS风险（未转义用户输入）
- ❌ 暴露堆栈跟踪
- ❌ React Hooks规则违反
- ❌ 缺少测试

### 相关经验

- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - game_gid使用规范
- [安全要点 - SQL注入防护](./security-essentials.md#sql注入防护) - SQL安全
- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React规范

---

## Brainstorming系统化设计 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [E2E测试修复报告](../archive/2026-02/e2e-test-reports/iteration-2/)

### 何时使用Brainstorming

**适用场景**:
- ✅ 需要设计复杂功能的实现方案
- ✅ 需要探索多种解决方案
- ✅ 需要系统化地分析问题
- ❌ 简单显而易见的实现

### Brainstorming流程

**1. 理解问题**:
- 问题的本质是什么？
- 有哪些约束条件？
- 有哪些成功标准？

**2. 探索方案**:
- 列出2-3种可能的解决方案
- 分析每种方案的优缺点
- 评估每种方案的风险

**3. 选择最佳**:
- 基于分析结果选择方案
- 考虑长期维护性
- 考虑团队技能和经验

**4. 分段验证**:
- 先验证核心概念
- 再实现完整功能
- 最后优化性能

**5. 记录经验**:
- 记录为什么选择这个方案
- 记录遇到的问题和解决方法
- 更新相关文档

### 相关经验

- [调试技能 - Subagent并行分析法](./debugging-skills.md#subagent并行分析法) - 并行分析策略
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构设计

---

## 技术债务管理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [技术债务管理文档](../development/technical_debt_management.md)

### 识别技术债务

**常见技术债务**:
- ❌ 缺少测试
- ❌ 违反编码规范
- ❌ 过时的依赖
- ❌ 性能问题
- ❌ 安全漏洞
- ❌ 架构问题

### 优先级评估

**P0 - 立即处理**:
- 安全漏洞（SQL注入、XSS等）
- 数据损坏风险
- 严重的性能问题

**P1 - 尽快处理**:
- 缺少关键测试
- 违反核心规范（game_gid等）
- 架构问题

**P2 - 计划处理**:
- 代码风格不一致
- 过时的注释
- 小的优化机会

### 偿还技术债务

**策略**:
1. **记录债务** - 在代码中添加TODO注释
2. **评估影响** - 分析债务的影响范围
3. **制定计划** - 安排偿还优先级
4. **分步偿还** - 每次迭代偿还一部分
5. **验证清理** - 确保债务已完全偿还

### 相关经验

- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - 避免测试债务
- [代码审查清单](#代码审查清单) - 防止新债务产生
