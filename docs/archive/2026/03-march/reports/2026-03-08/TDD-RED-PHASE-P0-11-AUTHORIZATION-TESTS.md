# TDD RED阶段报告 - P0-11权限检查缺失

**日期**: 2026-03-08
**阶段**: TDD RED（测试先行，确认失败）
**问题**: P0-11 - 所有GraphQL mutations缺少身份验证和授权检查
**测试文件**: `backend/test/unit/security/test_authorization.py`

---

## 执行摘要

✅ **TDD RED阶段成功完成**
- 创建了16个测试用例，验证权限检查缺失问题
- 11个测试失败（符合预期）
- 5个测试跳过（待实现功能）
- **测试成功证明了当前代码缺少所有安全检查**

---

## 测试结果

```
========================= 11 failed, 5 skipped, 1 warning ====================
```

### 测试失败详情

#### 1. 事件Mutations (4个失败)

| 测试用例 | 期望行为 | 实际行为 | 严重程度 |
|---------|---------|---------|---------|
| `test_create_event_requires_authentication` | 未登录应抛出认证错误 | ❌ 未抛出错误 | **P0** |
| `test_update_event_requires_permission` | 无权限应抛出授权错误 | ❌ 未抛出错误 | **P0** |
| `test_delete_event_requires_permission` | 无删除权限应抛出错误 | ❌ 未抛出错误 | **P0** |
| `test_batch_delete_events_has_limit` | 批量删除应有大小限制 | ❌ 未抛出错误 | **P1** |

#### 2. 游戏Mutations (4个失败)

| 测试用例 | 期望行为 | 实际行为 | 严重程度 |
|---------|---------|---------|---------|
| `test_create_game_requires_authentication` | 未登录应抛出认证错误 | ❌ 未抛出错误 | **P0** |
| `test_create_game_requires_permission` | 无权限应抛出授权错误 | ❌ 未抛出错误 | **P0** |
| `test_update_game_requires_permission` | 无权限应抛出授权错误 | ❌ 未抛出错误 | **P0** |
| `test_delete_game_requires_permission` | 无删除权限应抛出错误 | ❌ 未抛出错误 | **P0** |

#### 3. 参数Mutations (1个失败)

| 测试用例 | 期望行为 | 实际行为 | 严重程度 |
|---------|---------|---------|---------|
| `test_create_parameter_requires_authentication` | 未登录应抛出认证错误 | ❌ 未抛出错误 | **P0** |

#### 4. 批量Mutations (1个失败)

| 测试用例 | 期望行为 | 实际行为 | 严重程度 |
|---------|---------|---------|---------|
| `test_batch_create_games_has_limit` | 批量创建应有大小限制 | ❌ 未抛出错误 | **P1** |

#### 5. 代码结构测试 (1个失败)

| 测试用例 | 期望行为 | 实际行为 | 严重程度 |
|---------|---------|---------|---------|
| `test_all_mutations_have_auth_check` | 所有mutations应有认证检查 | ❌ 发现9个缺失 | **P0** |

---

## 缺少认证检查的Mutation列表

以下是AST分析发现的9个缺少认证检查的Mutation类：

```
❌ backend/gql_api/mutations/batch_mutations.py:37 - BatchCreateGames
❌ backend/gql_api/mutations/batch_mutations.py:101 - BatchUpdateGames
❌ backend/gql_api/mutations/batch_mutations.py:163 - BatchDeleteGames
❌ backend/gql_api/mutations/join_config_mutations.py:15 - CreateJoinConfig
❌ backend/gql_api/mutations/join_config_mutations.py:83 - UpdateJoinConfig
❌ backend/gql_api/mutations/join_config_mutations.py:159 - DeleteJoinConfig
❌ backend/gql_api/mutations/field_builder_mutations.py:17 - SaveFieldBuilderConfig
❌ backend/gql_api/mutations/field_builder_mutations.py:142 - DeleteFieldBuilderConfig
❌ backend/gql_api/mutations/field_builder_mutations.py:196 - PreviewFieldBuilderHQL
```

**注意**: 这只是部分列表。其他mutation文件（event_mutations.py, game_mutations.py等）也被测试验证缺少认证检查。

---

## 安全风险评估

### 当前状态：🚨 **严重安全漏洞**

#### 高危风险（P0）
1. **任何人都可以创建/修改/删除数据**
   - 无身份验证
   - 无授权检查
   - 无审计日志

2. **数据完整性风险**
   - 恶意用户可以删除所有游戏
   - 未授权修改事件配置
   - 破坏参数管理系统

3. **合规性风险**
   - 违反数据保护法规（GDPR/等保2.0）
   - 无法追踪操作人员
   - 无法防止内部威胁

#### 中等风险（P1）
1. **DoS攻击风险**
   - 批量操作无大小限制
   - 可以创建海量数据耗尽资源
   - 无速率限制

2. **业务逻辑风险**
   - 敏感操作无特殊权限要求
   - 无操作审批流程
   - 无双人验证机制

---

## 测试覆盖范围

### 已实现测试（16个）

#### 身份验证测试（4个）
- ✅ CreateEvent需要认证
- ✅ CreateGame需要认证
- ✅ CreateParameter需要认证
- ✅ 所有mutations应该有认证检查

#### 授权测试（6个）
- ✅ UpdateEvent需要权限
- ✅ DeleteEvent需要权限
- ✅ CreateGame需要权限
- ✅ UpdateGame需要权限
- ✅ DeleteGame需要权限
- ✅ 敏感操作需要特殊权限

#### 批量操作测试（2个）
- ✅ BatchDeleteEvents有大小限制
- ✅ BatchCreateGames有大小限制

#### 代码结构测试（1个）
- ✅ 所有mutations有认证检查（AST分析）

### 待实现测试（5个）

#### 安全配置测试（2个）
- ⏳ GraphQL context验证
- ⏳ 敏感操作权限检查

#### 速率限制测试（2个）
- ⏳ 批量操作大小限制
- ⏳ API速率限制

#### 输入验证测试（1个）
- ⏳ 输入验证安全（SQL注入/XSS）

---

## 下一步：TDD GREEN阶段

### 任务清单

#### Phase 1: 创建认证基础设施（P0）
- [ ] 创建用户认证装饰器
  - `@authenticated` - 检查用户是否登录
  - `@require_permission` - 检查用户权限
- [ ] 实现GraphQL context user
  - 从session/JWT获取当前用户
  - 加载用户权限列表
- [ ] 创建权限管理系统
  - 定义权限常量（event:write, game:delete等）
  - 实现权限检查逻辑

#### Phase 2: 添加认证到所有Mutations（P0）
- [ ] EventMutations (4个mutations)
  - CreateEvent, UpdateEvent, DeleteEvent, BatchDeleteEvents
- [ ] GameMutations (3个mutations)
  - CreateGame, UpdateGame, DeleteGame
- [ ] ParameterMutations (3个mutations)
  - CreateParameter, UpdateParameter, DeleteParameter
- [ ] BatchMutations (3个mutations)
  - BatchCreateGames, BatchUpdateGames, BatchDeleteGames
- [ ] 其他Mutations (15个mutations)
  - Category, JoinConfig, Node, Flow, HQL, Template等

#### Phase 3: 添加批量操作限制（P1）
- [ ] 实现批量操作大小限制
  - 默认限制：100项/批
  - 可配置限制
- [ ] 添加速率限制
  - 基于用户ID的速率限制
  - 基于IP的速率限制

#### Phase 4: 添加审计日志（P1）
- [ ] 记录所有写操作
  - 操作时间
  - 操作用户
  - 操作类型
  - 操作结果

#### Phase 5: 验证测试通过（P0）
- [ ] 运行所有测试
- [ ] 确认11个失败的测试现在通过
- [ ] 实现5个跳过的测试
- [ ] 达到100%测试通过率

---

## 测试文件位置

```
backend/test/unit/security/test_authorization.py
```

### 运行测试

```bash
# 运行所有权限测试
source backend/venv/bin/activate
pytest backend/test/unit/security/test_authorization.py -v

# 运行单个测试类
pytest backend/test/unit/security/test_authorization.py::TestEventMutationsAuth -v

# 运行单个测试
pytest backend/test/unit/security/test_authorization.py::TestEventMutationsAuth::test_create_event_requires_authentication -v
```

---

## 技术细节

### 测试架构

```python
class TestEventMutationsAuth:
    """测试事件mutations的权限检查"""

    def test_create_event_requires_authentication(self):
        """
        测试创建事件需要身份验证

        期望:
        - 检查用户是否已登录
        - 未登录时抛出认证错误
        """
        from backend.gql_api.mutations.event_mutations import CreateEvent

        info = Mock()
        info.context = Mock(user=None)  # 模拟未登录用户

        mutation = CreateEvent()

        # 期望抛出认证错误
        with pytest.raises(Exception) as exc_info:
            mutation.mutate(
                info,
                game_gid=90000001,
                event_name="Test Event",
                event_name_cn="测试事件",
                category_id=None
            )

        # 验证错误消息
        error_msg = str(exc_info.value).lower()
        assert (
            "authentication" in error_msg or
            "unauthorized" in error_msg or
            "login" in error_msg
        ), f"Expected authentication error, got: {exc_info.value}"
```

### AST分析代码

```python
def test_all_mutations_have_auth_check(self):
    """
    测试所有mutation类都有认证检查

    这是一个元测试，使用AST分析检查代码结构。
    """
    mutation_files = [
        'backend/gql_api/mutations/event_mutations.py',
        'backend/gql_api/mutations/game_mutations.py',
        # ... 更多文件
    ]

    mutations_without_auth = []

    for file_path in mutation_files:
        with open(file_path, 'r') as f:
            content = f.read()

        tree = ast.parse(content, file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是Mutation类
                if node.name.endswith('Mutation'):
                    # 查找mutate方法
                    mutate_method = next(
                        method for method in node.body
                        if isinstance(method, ast.FunctionDef) and method.name == 'mutate'
                    )

                    # 检查前10行是否有认证检查
                    has_auth_check = False
                    for stmt in mutate_method.body[:10]:
                        stmt_source = ast.get_source_segment(content, stmt)
                        if stmt_source and any(keyword in stmt_source.lower() for keyword in [
                            'authenticate', 'authorization', 'permission',
                            'info.context.user', 'get_current_user'
                        ]):
                            has_auth_check = True
                            break

                    if not has_auth_check:
                        mutations_without_auth.append({
                            'file': file_path,
                            'class': node.name,
                            'line': node.lineno
                        })

    if mutations_without_auth:
        pytest.fail(f"发现 {len(mutations_without_auth)} 个mutation缺少认证检查")
```

---

## 预期成果

### TDD GREEN阶段完成后

```
========================= 16 passed, 1 warning in 13.75s ====================
```

### 安全保障

- ✅ 所有写操作都需要身份验证
- ✅ 所有写操作都需要权限检查
- ✅ 批量操作有大小限制
- ✅ API有速率限制
- ✅ 所有操作有审计日志

---

## 参考资料

- [OWASP Top 10 - Broken Access Control](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Graphene Documentation - Authentication](https://docs.graphene-python.org/en/latest/execution/django/#authentication)
- [Python Authlib](https://authlib.org/)
- [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/)

---

**报告生成时间**: 2026-03-08
**TDD阶段**: RED ✅ （测试失败，符合预期）
**下一阶段**: GREEN（实现功能，使测试通过）
