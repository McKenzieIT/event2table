# Event2Table 测试经验总结

> **版本**: 1.0 | **最后更新**: 2026-02-22
>
> 本文档总结了Event2Table项目所有测试工作的核心经验和最佳实践。

---

## 📋 目录

- [测试概览](#测试概览)
- [E2E测试实践](#e2e测试实践)
- [单元测试实践](#单元测试实践)
- [集成测试实践](#集成测试实践)
- [测试自动化](#测试自动化)
- [常见问题和解决方案](#常见问题和解决方案)
- [测试最佳实践](#测试最佳实践)

---

## 🎯 测试概览

### 测试类型

| 测试类型 | 工具 | 覆盖范围 | 执行频率 |
|---------|------|----------|----------|
| **单元测试** | pytest | Service层、Repository层 | 每次提交 |
| **集成测试** | pytest | API端点、数据库交互 | 每次提交 |
| **E2E测试** | Playwright | 完整用户流程 | 每日/发布前 |
| **API契约测试** | 自定义脚本 | API一致性 | 每次提交 |

### 测试覆盖率

**目标**:
- 单元测试覆盖率：>80%
- API测试覆盖率：100%
- E2E关键路径：100%

**当前状态** (2026-02-22):
- 后端单元测试：85%覆盖
- API契约测试：100%覆盖
- E2E测试：39个页面/场景

---

## 🎭 E2E测试实践

### Chrome DevTools MCP测试法

**核心优势**:
- 真实浏览器环境
- 可视化测试过程
- 精确的DOM交互
- 详细的错误信息

**标准测试流程**:

```javascript
// 1. 列出页面
mcp__chrome-devtools__list_pages()

// 2. 导航到测试页面
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard?game_gid=10000147"
})

// 3. 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages({
  types: ["error", "warn"]
})

// 5. 点击交互
mcp__chrome-devtools__click({ uid: "element-uid" })

// 6. 验证结果
mcp__chrome-devtools__take_snapshot()
```

### Ralph Loop迭代测试法

**方法论**: 发现问题 → Subagent分析 → 设计修复 → 实施修复 → Chrome MCP验证 → 记录结果

**9次迭代总结**:

| 迭代 | 主题 | 问题数 | 修复率 | 关键学习 |
|------|------|--------|--------|----------|
| 1 | 初始E2E | 0 | - | 建立13/13页面基线 |
| 2 | React Hooks | 4 | 100% | Hook顺序规则 |
| 3 | 懒加载 | 3 | 100% | 避免双重Suspense |
| 4 | 性能优化 | 2 | 100% | React.memo优化 |
| 5 | Input组件 | 2 | 100% | Grid布局规范 |
| 6 | Flow Builder | 1 | 100% | 异步状态管理 |
| 7 | CSS冲突 | 1 | 100% | 样式隔离 |
| 8 | 事件节点 | 1 | 100% | 完整验证流程 |
| 9 | 最终验证 | 0 | - | 全部通过 |

### 关键经验教训

#### 1. React Hooks规则 (极其重要)

**错误模式** (导致崩溃):
```javascript
// ❌ 错误：Hook在条件返回之后
function Component() {
  const data = useData();

  if (isLoading) return <Loading />;  // ❌ 条件返回在中间

  const processed = useMemo(() => {}, [data]);  // ❌ Hook在条件返回后
  return <View />;
}
```

**正确模式**:
```javascript
// ✅ 正确：所有Hook在条件返回之前
function Component() {
  const data = useData();

  // ✅ 所有Hook在条件返回之前
  const processed = useMemo(() => {
    if (!data) return null;
    return data.filter(...);
  }, [data]);

  // ✅ 条件返回在所有Hook之后
  if (isLoading) return <Loading />;

  return <View />;
}
```

**强制检测**:
```bash
npm install eslint-plugin-react-hooks --save-dev
```

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',  // 强制规则
    'react-hooks/exhaustive-deps': 'warn',  // 检测依赖项
  },
};
```

#### 2. Lazy Loading最佳实践

**何时使用lazy loading**:
- ✅ 大型组件（>10KB）
- ✅ 不常用的路由页面
- ✅ 复杂的数据可视化组件

**何时不使用**:
- ❌ 小型文档页面（<50行）
- ❌ 已经很快加载的小型组件
- ❌ 可能导致双重Suspense嵌套的组件

**修复案例**:
```javascript
// ❌ 错误：小型组件使用lazy loading
const ApiDocs = lazy(() => import("@analytics/pages/ApiDocs"));  // <50行
const ValidationRules = lazy(() => import("@analytics/pages/ValidationRules"));  // <50行

// ✅ 正确：直接导入
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";
```

#### 3. Input组件CSS布局规范

**核心规则**: 始终使用label prop，不要在Input外部写label

```jsx
// ✅ 正确：使用label prop
<Input
  label="游戏名称"
  type="text"
  value={gameName}
  onChange={(e) => setGameName(e.target.value)}
/>

// ❌ 错误：label在Input外部
<div className="form-group">
  <label>游戏名称</label>
  <Input ... />
</div>
```

**原因**: Input组件使用CSS Grid布局，Label在外部会导致Grid预留的label列空置

---

## 🧪 单元测试实践

### pytest最佳实践

**测试结构**:
```python
# backend/test/unit/test_game_service.py

import pytest
from backend.services.games.game_service import GameService

class TestGameService:
    @pytest.fixture
    def service(self):
        """创建Service实例"""
        return GameService()

    @pytest.fixture
    def sample_game(self):
        """创建测试数据"""
        return {
            "gid": "90000001",
            "name": "Test Game",
            "ods_db": "ieu_ods"
        }

    def test_create_game_success(self, service, sample_game):
        """测试成功创建游戏"""
        # Given
        game_data = GameCreate(**sample_game)

        # When
        result = service.create_game(game_data)

        # Then
        assert result["gid"] == "90000001"
        assert result["name"] == "Test Game"

    def test_create_game_duplicate_gid(self, service, sample_game):
        """测试重复GID抛出异常"""
        # Given
        service.create_game(GameCreate(**sample_game))

        # When & Then
        with pytest.raises(ValueError, match="already exists"):
            service.create_game(GameCreate(**sample_game))
```

### Mock使用

```python
from unittest.mock import Mock, patch

def test_external_api_call():
    """测试外部API调用"""
    # Mock外部API
    with patch('backend.services.games.external_api') as mock_api:
        mock_api.return_value = {"status": "success"}

        # 调用Service
        result = game_service.call_external_api()

        # 验证
        assert result["status"] == "success"
        mock_api.assert_called_once()
```

---

## 🔗 集成测试实践

### API测试

```python
# backend/test/integration/test_games_api.py

import pytest
from web_app import create_app

@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

def test_create_game(client):
    """测试创建游戏API"""
    response = client.post('/api/games', json={
        "gid": "90000001",
        "name": "Test Game",
        "ods_db": "ieu_ods"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["gid"] == "90000001"

def test_create_game_duplicate_gid(client):
    """测试重复GID返回409"""
    # 第一次创建
    client.post('/api/games', json={
        "gid": "90000001",
        "name": "Test Game",
        "ods_db": "ieu_ods"
    })

    # 第二次创建（应该失败）
    response = client.post('/api/games', json={
        "gid": "90000001",
        "name": "Another Game",
        "ods_db": "ieu_ods"
    })

    assert response.status_code == 409
```

### 数据库测试

```python
@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 使用测试数据库
    init_db(TEST_DB_PATH)

    # 提供会话
    conn = get_db_connection(TEST_DB_PATH)
    yield conn

    # 清理
    conn.close()
    TEST_DB_PATH.unlink()

def test_game_crud(db_session):
    """测试游戏CRUD"""
    repo = GameRepository()

    # Create
    game_id = repo.create({"gid": "90000001", "name": "Test"})
    assert game_id > 0

    # Read
    game = repo.find_by_id(game_id)
    assert game["name"] == "Test"

    # Update
    repo.update(game_id, {"name": "Updated"})
    game = repo.find_by_id(game_id)
    assert game["name"] == "Updated"

    # Delete
    repo.delete(game_id)
    assert repo.find_by_id(game_id) is None
```

---

## 🤖 测试自动化

### CI/CD集成

**GitHub Actions示例**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run unit tests
        run: pytest backend/test/unit/ -v

      - name: Run API contract tests
        run: python scripts/test/api_contract_test.py

      - name: Run E2E tests
        run: |
          cd frontend
          npm install
          npm run build
          npm run test:e2e
```

### Pre-commit Hooks

```bash
# .git/hooks/pre-commit

#!/bin/bash

# 运行API契约测试
python scripts/test/api_contract_test.py

if [ $? -ne 0 ]; then
    echo "❌ API契约测试失败，提交被阻止"
    exit 1
fi

# 运行单元测试
pytest backend/test/unit/ -q

if [ $? -ne 0 ]; then
    echo "❌ 单元测试失败，提交被阻止"
    exit 1
fi

echo "✅ 所有测试通过"
```

---

## 🐛 常见问题和解决方案

### 问题1: 测试数据库污染

**症状**: 测试之间相互影响，测试结果不一致

**解决方案**:
```python
@pytest.fixture(scope="function")
def db_session():
    """每次测试前清理数据库"""
    # 删除旧测试数据库
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 初始化新测试数据库
    init_db(TEST_DB_PATH)

    conn = get_db_connection(TEST_DB_PATH)
    yield conn
    conn.close()

    # 测试后删除
    TEST_DB_PATH.unlink()
```

### 问题2: E2E测试超时

**症状**: 页面卡在"LOADING"状态，测试超时

**解决方案**:
```javascript
// 增加超时时间
mcp__chrome-devtools__navigate_page({
  type: "url",
  url: "http://localhost:5173/parameter-dashboard",
  timeout: 60000  // 60秒
})

// 或使用等待特定元素
mcp__chrome-devtools__wait_for({
  text: "参数列表",
  timeout: 30000
})
```

### 问题3: 测试环境变量

**症状**: 测试使用了生产数据库

**解决方案**:
```python
import os

# 设置测试环境
os.environ["FLASK_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///data/test_database.db"

def test_something():
    # 现在使用测试数据库
    assert os.environ.get("FLASK_ENV") == "testing"
```

### 问题4: React Hooks错误

**症状**: "Rendered more hooks than during the previous render"

**解决方案**: 参见上文"React Hooks规则"章节

---

## ✅ 测试最佳实践

### TDD开发流程

```bash
# 1. 调用TDD skill
/superpowers:test-driven-development

# 2. 编写测试（先看测试失败）
def test_create_game():
    service = GameService()
    result = service.create_game(game_data)
    assert result["gid"] == "90000001"

# 运行测试（失败）
pytest backend/test/unit/test_game_service.py::test_create_game -v

# 3. 编写最小代码使测试通过
class GameService:
    def create_game(self, game_data):
        return {"gid": "90000001", **game_data}

# 运行测试（通过）
pytest backend/test/unit/test_game_service.py::test_create_game -v

# 4. 重构优化
```

### 测试命名规范

```python
# ✅ 好的测试名称
def test_create_game_with_valid_data_returns_success()
def test_create_game_with_duplicate_gid_raises_error()
def test_create_game_with_missing_name_raises_validation_error()

# ❌ 不好的测试名称
def test_game()
def test_create()
def test1()
```

### 测试组织结构

```
backend/test/
├── unit/                 # 单元测试
│   ├── services/
│   │   ├── test_game_service.py
│   │   └── test_event_service.py
│   ├── repositories/
│   │   ├── test_game_repository.py
│   │   └── test_event_repository.py
│   └── utils/
│       └── test_json_helpers.py
├── integration/          # 集成测试
│   ├── api/
│   │   ├── test_games_api.py
│   │   └── test_events_api.py
│   └── database/
│       └── test_schema.py
└── conftest.py           # 共享fixtures
```

### 测试数据管理

```python
# conftest.py

@pytest.fixture
def sample_game():
    """标准测试游戏"""
    return {
        "gid": "90000001",
        "name": "Test Game",
        "ods_db": "ieu_ods",
        "description": "Test game for unit tests"
    }

@pytest.fixture
def sample_event():
    """标准测试事件"""
    return {
        "game_gid": 90000001,
        "event_name": "test.event",
        "event_code": "0001",
        "description": "Test event"
    }

# 使用
def test_with_sample(sample_game, sample_event):
    assert sample_game["gid"] == "90000001"
    assert sample_event["game_gid"] == 90000001
```

---

## 📚 相关文档

**测试指南**:
- [e2e-testing-guide.md](e2e-testing-guide.md) - E2E测试完整指南
- [quick-test-guide.md](quick-test-guide.md) - 快速测试参考
- [playwright-automation-guide.md](playwright-automation-guide.md) - Playwright使用

**测试报告**:
- [测试报告索引](reports/README.md) - 所有测试报告
- [Ralph Loop最终报告](../archive/ralph-testing/ralph/FINAL-REPORT.md) - 9次迭代总结

**开发规范**:
- [CLAUDE.md](../../CLAUDE.md) - 开发规范（测试章节）

---

## 🎓 学习资源

**React测试**:
- [React Testing Library](https://testing-library.com/react)
- [Playwright文档](https://playwright.dev/)
- [React Hooks规则](https://react.dev/reference/rules)

**Python测试**:
- [pytest文档](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**文档版本**: 1.0
**最后更新**: 2026-02-22
**维护者**: Event2Table Development Team
