# 完整实现原则设计文档

**版本**: 1.0
**日期**: 2026-03-08
**作者**: Claude Sonnet 4.6
**状态**: 已批准

---

## 概述

本文档定义了Event2Table项目的**完整实现原则**，明确禁止因token或时间限制而进行简化或留空实现，确保代码质量和项目长期可维护性。

### 核心理念

> **"宁可少做，不可做半"**
> 宁可只实现1个完整功能，不做3个半成品功能

### 为什么需要这个原则

过往项目中有多次因token限制或时间压力而简化实现，导致：
- ⚠️ **技术债务累积**：占位符代码被遗忘，后续需要2-3倍时间返工
- ⚠️ **生产事故风险**：省略的错误处理导致运行时崩溃
- ⚠️ **安全漏洞**：简化的验证逻辑被利用
- ⚠️ **代码审查失效**：Reviewer无法区分"有意简化"和"疏忽遗漏"

---

## 原则声明

- ❌ **禁止任何理由的简化实现**（token不足、时间紧迫、"暂时先这样"）
- ❌ **禁止留空或占位符实现**（pass、TODO、返回默认值）
- ✅ **质量优先于完整性**（部分完整 > 全部残缺）
- ✅ **透明沟通进度**（主动告知用户资源状态，请求决策）

---

## 全面禁止的简化行为

### A. 代码实现层面的简化（零容忍）

#### 禁止的占位符模式

```python
# ❌ 禁止：使用pass作为实现
def validate_input(data):
    pass  # TODO: 后续实现

# ❌ 禁止：NotImplementedError（除非是抽象接口）
def process_payment(amount):
    raise NotImplementedError("支付功能待实现")

# ❌ 禁止：省略号作为占位符
def calculate_tax(order):
    ...

# ❌ 禁止：返回空值/默认值代替实现
def get_user_permissions(user_id):
    return []  # 暂时返回空列表
```

#### 禁止的省略验证

```python
# ❌ 禁止：只实现快乐路径
def delete_game(game_id):
    execute_delete("DELETE FROM games WHERE id = ?", (game_id,))
    # 缺少：游戏是否存在的检查、关联事件的处理、事务回滚

# ❌ 禁止：省略异常处理
def fetch_api_data(url):
    response = requests.get(url)
    return response.json()  # 没有检查response.status_code
```

#### 禁止的硬编码敏感信息

```python
# ❌ 禁止：硬编码密码/密钥
DB_PASSWORD = "password123"
API_KEY = "sk_live_abc123"

# ✅ 正确：使用环境变量
DB_PASSWORD = os.environ.get("DB_PASSWORD")
API_KEY = os.environ.get("API_KEY")
```

### D. 安全性层面的简化（零容忍）

**禁止省略的安全检查**：
- ❌ SQL查询未使用参数化（SQL注入风险）
- ❌ 用户输入未进行XSS防护
- ❌ 缺少权限检查（任何用户可访问任何资源）
- ❌ 敏感数据未加密存储
- ❌ 未验证文件类型/大小就允许上传

---

## 必须达到的最低标准

### B. 测试层面的最低标准

#### 单元测试要求

- ✅ **覆盖率**: ≥ 80%（新代码必须达到）
- ✅ **关键路径**: 100%覆盖（所有业务逻辑分支）
- ✅ **公共API**: 100%有对应测试
- ✅ **异常处理**: 必须测试错误分支

#### E2E测试要求

- ✅ **主流程**: 必须有E2E测试覆盖（smoke test）
- ✅ **关键功能**: 登录、CRUD操作、权限控制
- ✅ **真实环境**: 使用测试数据库和测试配置

#### 测试质量要求

- ✅ **避免Mock过度**: Mock只用于外部依赖
- ✅ **测试独立性**: 每个测试可独立运行
- ✅ **清晰命名**: `test_函数名_场景_预期结果`

```python
# ✅ 正确的测试示例
def test_create_game_with_duplicate_gid_returns_409():
    """测试：创建重复GID的游戏应返回409冲突"""
    # Arrange
    existing_game = create_test_game(gid="10000147")

    # Act
    response = client.post('/api/games', json={"gid": "10000147", "name": "Duplicate"})

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.json()["error"]
```

### C. 文档层面的最低标准

#### docstring要求

- ✅ **复杂函数**: 函数体>10行或包含逻辑分支，必须有docstring
- ✅ **公共API**: 所有对外暴露的函数/类必须有docstring
- ✅ **格式**: 使用Google风格或NumPy风格

```python
# ✅ 正确的docstring示例
def create_game(game_data: GameCreate) -> Dict[str, Any]:
    """
    创建新游戏

    验证游戏GID的唯一性，创建游戏记录，并返回创建的游戏数据。

    Args:
        game_data: 游戏创建数据，包含gid、name、ods_db等字段

    Returns:
        包含创建游戏数据的字典，包含数据库生成的id

    Raises:
        ValueError: 当gid已存在时
        ValidationError: 当输入数据验证失败时

    Example:
        >>> game = create_game(GameCreate(gid="10000147", name="STAR001"))
        >>> print(game['name'])
        'STAR001'
    """
```

#### 代码注释要求

- ✅ **复杂逻辑**: 必须注释说明WHY（为什么），而非WHAT（做什么）
- ✅ **临时方案**: 必须标注原因和预计解决时间
- ✅ **外部引用**: 包含GitHub Issue、文档链接

```python
# ✅ 好的注释示例
# 双层数据库连接以避免锁等待（参见：GitHub issue #123）
# 每层最多等待5秒，超时后回滚
conn1 = get_db_connection(timeout=5)
conn2 = get_db_connection(timeout=5)
```

---

## Token/时间限制的处理流程

### 核心原则

**主动沟通 + 质量优先**

### 步骤1: 监控资源状态

#### Token监控
- 当token使用率达到 **70%** 时，评估剩余工作量
- 当token使用率达到 **85%** 时，必须主动与用户沟通
- 计算剩余token是否足够完成当前任务

#### 时间评估
- 评估任务剩余时间 vs 对话剩余时间
- 如果任务预计需要超过剩余时间的 **50%**，主动告知

### 步骤2: 主动告知用户

**沟通模板**：
```
⚠️ **资源状态提醒**

当前进度：
- ✅ 已完成：功能A（完整实现+测试）
- ✅ 已完成：功能B（完整实现+测试）
- 🚧 进行中：功能C（实现50%，预计还需X分钟）

剩余资源：
- Token: 已用85%，剩余约{token数}
- 预计完成所有功能还需: {时间}

建议选项：
1️⃣ **继续完整实现** - 完成功能C、D、E（可能需要续对话或延长时间）
2️⃣ **分阶段交付** - 先交付功能A+B，C和D在下次迭代完成
3️⃣ **调整范围** - 只完成功能C（最核心功能），D和E延后

请选择: 1/2/3 或提出其他方案
```

### 步骤3: 根据用户选择执行

#### 选项1: 继续完整实现
- 评估是否需要增加资源
- 如果token不足，建议用户："需要新对话继续，是否生成任务清单？"
- 保持质量标准，不简化实现

#### 选项2: 分阶段交付
- 明确标记本次交付范围
- 创建技术债务清单（GitHub Issues或TODO.md）

**未完成功能记录模板**：
```markdown
## 未完成功能记录 (2026-03-08)

### 功能C: 用户权限验证
- **状态**: 实现中（50%）
- **剩余工作**: 完成RBAC权限检查、添加单元测试、更新API文档
- **预计工作量**: 2小时
- **优先级**: P0（下次迭代优先完成）
- **相关文件**: backend/services/auth/permission_checker.py

### 功能D: 审计日志
- **状态**: 未开始
- **计划**: 实现审计日志中间件（参考：docs/design/audit-log.md）
- **预计工作量**: 4小时
- **优先级**: P1
```

#### 选项3: 调整范围
- 只完成最核心功能
- 确保核心功能100%完整（测试、文档、错误处理）
- 明确告知用户："功能C已完整实现并测试，功能D和E需要后续迭代"

### 步骤4: 质量验证

无论选择哪个选项，交付前必须验证：
- ✅ 所有已实现功能都有对应测试（覆盖率≥80%）
- ✅ 所有公共API都有文档
- ✅ 没有使用pass、TODO、NotImplementedError占位符
- ✅ E2E测试通过主流程
- ✅ 代码审查清单通过

**禁止行为**：
- ❌ 自行决定"简化实现"以适应限制
- ❌ 不告知用户就减少功能范围
- ❌ 为了"完成更多功能"而降低质量标准

---

## 执行机制

### Code Review强制检查

**每次代码审查必须检查**：
- [ ] 是否存在`pass`、`...`、`NotImplementedError`占位符？
- [ ] 是否存在TODO/FIXME注释（除非对应GitHub Issue）？
- [ ] 是否存在返回空值/默认值代替实现？
- [ ] 单元测试覆盖率是否≥80%？
- [ ] 关键功能是否有E2E测试？
- [ ] 公共API是否有docstring？
- [ ] 复杂逻辑是否有注释说明？
- [ ] 是否省略了安全检查（SQL注入、XSS、权限）？
- [ ] 是否硬编码了敏感信息？

### Pre-commit Hook检查

**自动化检查**：
```yaml
# 添加到.pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-placeholders
      name: 检查代码占位符
      entry: |
        ! git diff --cached --name-only | grep '\.py$' | xargs grep -n "\(pass\|TODO\|FIXME\|NotImplementedError\)" &&
        echo "✅ 未发现占位符"
      language: system
      pass_if_false: true

    - id: check-coverage
      name: 检查测试覆盖率
      entry: pytest --cov=backend --cov-fail-under=80
      language: system
```

### 技术债务追踪

**简化实现的追踪机制**：
- 所有"未完成"功能必须记录到`TECHNICAL_DEBT.md`
- 必须包含：优先级、预计工作量、依赖项、截止日期
- 每周Review技术债务清单，确保不遗漏

---

## 违反后果

### 一级违反：直接占位符

**行为**：使用`pass`、`TODO`、`NotImplementedError`占位符

**后果**：
- ❌ 立即返工，不得合并
- ❌ 记录到开发者评估
- ❌ 要求重新完成并增加10%额外测试

### 二级违反：省略验证/错误处理

**行为**：省略输入验证、异常处理、安全检查

**后果**：
- ❌ 代码Review拒绝
- ❌ 必须补充完整的错误处理
- ❌ 添加针对性的安全测试

### 三级违反：测试/文档不足

**行为**：测试覆盖率<80%、缺少E2E测试、缺少docstring

**后果**：
- ❌ 不得合并到主分支
- ❌ 必须补充测试到80%覆盖率
- ❌ 补充缺失的docstring

### 四级违反：重复违反

**行为**：2次以上违反相同原则

**后果**：
- ❌ 要求重新阅读CLAUDE.md开发规范
- ❌ 后续3次代码需要额外的Review环节
- ❌ 影响绩效考核

---

## 允许的例外情况

### 唯一允许的TODO

**条件**：
- 已在GitHub Issue中跟踪的待办事项
- 必须在注释中引用Issue编号

**示例**：
```python
# TODO: 实现批量删除功能（已记录到GitHub issue #123）
# 预计完成时间: 2026-03-15
# 优先级: P1
```

### 抽象接口的NotImplementedError

**条件**：
- 仅允许在抽象基类或接口定义中使用
- 必须配合`abc`模块使用

**示例**：
```python
from abc import ABC, abstractmethod

class DataRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int):
        """根据ID获取数据"""
        raise NotImplementedError
```

---

## 快速参考卡片

```
┌─────────────────────────────────────────┐
│  完整实现原则 - 快速检查                 │
├─────────────────────────────────────────┤
│  ❌ 禁止: pass, TODO, NotImplementedError  │
│  ❌ 禁止: 返回空值代替实现                │
│  ❌ 禁止: 省略验证/异常处理               │
│  ❌ 禁止: 硬编码敏感信息                  │
│  ✅ 要求: 单元测试≥80%                   │
│  ✅ 要求: E2E测试覆盖主流程              │
│  ✅ 要求: 公共API有docstring             │
│  ✅ 要求: 复杂逻辑有注释                 │
│  ⚠️ Token不足: 主动告知用户，请求决策   │
│  ⚠️ 时间不足: 质量优先，减少范围        │
└─────────────────────────────────────────┘
```

---

## 实施计划

### Phase 1: 文档更新（已完成）
- ✅ 创建设计文档
- ⏳ 更新CLAUDE.md添加新规则

### Phase 2: 工具配置（待执行）
- ⏳ 配置pre-commit hooks
- ⏳ 创建TECHNICAL_DEBT.md模板
- ⏳ 添加代码审查清单模板

### Phase 3: 团队培训（待执行）
- ⏳ 团队会议讲解新原则
- ⏳ 代码审查培训
- ⏳ 技术债务追踪流程培训

### Phase 4: 监督执行（持续）
- ⏳ Code Review严格执行
- ⏳ 定期Review技术债务清单
- ⏳ 收集反馈，持续改进

---

## 附录

### A. 相关文档

- [CLAUDE.md开发规范](/CLAUDE.md) - 项目总体开发规范
- [测试指南](docs/lessons-learned/testing-guide.md) - 测试最佳实践
- [代码审查清单](docs/lessons-learned/refactoring-checklist.md) - Review检查项

### B. 模板文件

- [TECHNICAL_DEBT.md模板](templates/TECHNICAL_DEBT_TEMPLATE.md)
- [代码审查清单模板](templates/CODE_REVIEW_CHECKLIST.md)

### C. 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2026-03-08 | 初始版本 | Claude Sonnet 4.6 |

---

**文档状态**: ✅ 已批准，待实施
**下一步**: 更新CLAUDE.md，添加完整实现原则到Critical Rules部分
