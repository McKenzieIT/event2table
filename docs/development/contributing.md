# 贡献指南

> **版本**: 1.0 | **最后更新**: 2026-02-10
>
> 感谢你对 Event2Table 项目的关注！本文档将指导你如何参与项目开发。

---

## 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [测试规范](#测试规范)
- [代码审查清单](#代码审查清单)
- [提交规范](#提交规范)
- [问题报告](#问题报告)
- [功能请求](#功能请求)

---

## 开发环境设置

### 后端环境（Python）

**系统要求**：
- Python 3.9+
- SQLite 3
- pip 21+

**安装步骤**：

```bash
# 1. 克隆项目
git clone <repository-url>
cd event2table

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python scripts/setup/init_db.py

# 5. 运行应用
python web_app.py
```

**验证安装**：

```bash
# 检查Python版本
python --version  # Python 3.9+

# 检查依赖
pip list

# 运行测试
pytest test/unit/backend/ -v

# 访问应用
open http://127.0.0.1:5001
```

### 前端环境（Node.js）

**系统要求**：
- Node.js 18+
- npm 9+

**安装步骤**：

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev  # http://localhost:5173

# 4. 构建生产版本
npm run build

# 5. 运行测试
npm run test
```

**验证安装**：

```bash
# 检查Node版本
node --version  # v18+

# 检查npm版本
npm --version  # 9+

# 检查依赖
npm list --depth=0
```

### IDE配置

**VSCode推荐插件**：

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-playwright.playwright",
    "EditorConfig.EditorConfig"
  ]
}
```

**VSCode设置**：

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

**PyCharm配置**：

1. **代码风格**：设置 → Editor → Code Style → Python
   - 缩进：4空格
   - 命名风格：snake_case

2. **检查工具**：设置 → Tools → External Tools
   - 启用 PEP 8 检查
   - 启用类型检查

---

## 代码规范

### Python命名规范

**文件和模块命名**：

```python
# ✅ 正确：使用小写字母和下划线
# game_service.py
# event_repository.py
# hql_generator.py

# ❌ 错误：不要使用驼峰命名
# GameService.py
# EventRepository.py
```

**类命名**：

```python
# ✅ 正确：使用PascalCase
class GameService:
    pass

class EventRepository:
    pass

class HQLGenerator:
    pass

# ❌ 错误：不要使用下划线
class game_service:
    pass
```

**函数和变量命名**：

```python
# ✅ 正确：使用snake_case
def get_game_by_gid(game_gid: int) -> Dict[str, Any]:
    game_name = "Test Game"
    event_count = 10

    pass

# ❌ 错误：不要使用camelCase
def getGameByGid(gameGid: int):
    gameName = "Test Game"
    eventCount = 10
    pass
```

**常量命名**：

```python
# ✅ 正确：使用大写字母和下划线
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 300
CACHE_KEY_PREFIX = "dwd_gen:v3:"

# ❌ 错误：不要使用小写
max_retry_count = 3
default_timeout = 300
```

### TypeScript命名规范

**文件和模块命名**：

```typescript
// ✅ 正确：使用小写字母和连字符
// game-service.ts
// event-repository.ts
// hql-generator.ts

// ❌ 错误：不要使用下划线
// game_service.ts
// event_repository.ts
```

**接口和类型命名**：

```typescript
// ✅ 正确：使用PascalCase
interface GameData {
  gid: string;
  name: string;
}

type EventStatus = "active" | "inactive";

// ❌ 错误：不要使用小写
interface gameData {
  gid: string;
}
```

**函数和变量命名**：

```typescript
// ✅ 正确：使用camelCase
const fetchGameByGid = (gameGid: number): Game => {
  const gameName = "Test Game";
  const eventCount = 10;

  return game;
};

// ❌ 错误：不要使用下划线
const fetch_game_by_gid = (game_gid: number) => {
  const game_name = "Test Game";
  return game;
};
```

**React组件命名**：

```typescript
// ✅ 正确：使用PascalCase
function GameList() {
  return <div>...</div>;
}

const EventBuilder = () => {
  return <div>...</div>;
};

// ❌ 错误：不要使用小写
function gameList() {
  return <div>...</div>;
}
```

### 文件组织规范

**后端文件组织**：

```
backend/
├── api/
│   └── routes/
│       └── dwd_generator/
│           ├── games.py        # 游戏相关API
│           ├── events.py       # 事件相关API
│           └── parameters.py   # 参数相关API
├── models/
│   ├── schemas.py              # Pydantic Schema
│   └── repositories/
│       ├── games.py            # 游戏Repository
│       ├── events.py           # 事件Repository
│       └── parameters.py       # 参数Repository
└── services/
    ├── games/
    │   └── game_service.py     # 游戏Service
    ├── events/
    │   └── event_service.py    # 事件Service
    └── hql/
        └── core/
            └── generator.py    # HQL生成器
```

**前端文件组织**：

```
frontend/src/
├── features/
│   ├── games/
│   │   ├── components/         # 游戏相关组件
│   │   ├── hooks/             # 游戏相关Hooks
│   │   ├── api/               # 游戏API调用
│   │   └── types/             # 游戏类型定义
│   ├── events/
│   │   └── ...
│   └── parameters/
│       └── ...
├── shared/
│   ├── ui/                    # 共享UI组件
│   ├── hooks/                 # 共享Hooks
│   ├── utils/                 # 工具函数
│   └── types/                 # 共享类型
└── styles/                    # 全局样式
```

### Git提交规范

**提交信息格式**：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新增功能，也不是修复bug）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

**示例**：

```bash
# 新功能
git commit -m "feat(game): add game export feature"

# 修复bug
git commit -m "fix(event): resolve event filtering issue"

# 文档更新
git commit -m "docs(readme): update installation instructions"

# 重构
git commit -m "refactor(hql): simplify HQL generator architecture"
```

**完整的提交信息**：

```
feat(hql): add multi-event JOIN support

- Implement JoinBuilder for complex JOIN operations
- Support INNER, LEFT, RIGHT, FULL JOIN types
- Add JOIN condition validation
- Update API to accept join_config parameter

Closes #123
```

---

## 测试规范

### TDD开发流程

**核心原则**：
> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

**开发步骤**：

1. **编写测试**：
   ```python
   # test/unit/backend/services/test_game_service.py
   def test_create_game_with_duplicate_gid():
       """测试创建重复gid的游戏"""
       # Arrange
       service = GameService()
       existing_game = GameCreate(gid="1001", name="Game 1")
       service.create_game(existing_game)

       duplicate_game = GameCreate(gid="1001", name="Game 2")

       # Act & Assert
       with pytest.raises(ValueError, match="already exists"):
           service.create_game(duplicate_game)
   ```

2. **运行测试（失败）**：
   ```bash
   pytest test/unit/backend/services/test_game_service.py::test_create_game_with_duplicate_gid -v
   # FAILED - 这是期望的！
   ```

3. **编写最小代码使测试通过**：
   ```python
   # backend/services/games/game_service.py
   def create_game(self, game_data: GameCreate) -> Dict[str, Any]:
       # 检查gid是否已存在
       existing = self.game_repo.find_by_gid(game_data.gid)
       if existing:
           raise ValueError(f"Game gid {game_data.gid} already exists")

       # 创建游戏
       return self.game_repo.create(game_data.dict())
   ```

4. **运行测试（通过）**：
   ```bash
   pytest test/unit/backend/services/test_game_service.py::test_create_game_with_duplicate_gid -v
   # PASSED
   ```

5. **重构优化**：
   ```python
   # 提取私有方法，优化代码结构
   def _validate_gid_unique(self, gid: str):
       """验证gid唯一性"""
       existing = self.game_repo.find_by_gid(gid)
       if existing:
           raise ValueError(f"Game gid {gid} already exists")
   ```

6. **再次运行测试**：
   ```bash
   # 确保重构后测试仍然通过
   pytest test/unit/backend/services/test_game_service.py -v
   ```

### 测试隔离规范

**测试数据库隔离**：

```python
# backend/tests/conftest.py
import pytest
from backend.core.config.config import TEST_DB_PATH, get_db_path
from backend.core.database import init_db

@pytest.fixture(scope="session")
def test_db():
    """
    使用独立的测试数据库
    """
    # 删除旧测试数据库
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 初始化测试数据库
    init_db(TEST_DB_PATH)

    yield TEST_DB_PATH

    # 测试后保留数据库以便调试
    # 如果想自动清理，取消下面的注释
    # TEST_DB_PATH.unlink()
```

**测试数据命名**：

```python
import uuid

# ✅ 正确：使用TEST_前缀和UUID
test_game_gid = f"TEST_{uuid.uuid4().hex[:8]}"

# ✅ 正确：使用pytest fixture
@pytest.fixture
def test_game():
    """创建测试游戏"""
    return {
        "gid": f"TEST_{uuid.uuid4().hex[:8]}",
        "name": "Test Game",
        "ods_db": "ieu_ods"
    }

# ❌ 错误：使用硬编码数字
test_game_gid = 10000147  # 可能与生产数据冲突
```

### API契约测试

**运行API契约测试**：

```bash
# 检查前后端API一致性
python scripts/test/api_contract_test.py

# 自动修复API契约问题
python scripts/test/api_contract_test.py --fix

# 验证修复
python scripts/test/api_contract_test.py --verify
```

### E2E测试

**运行E2E测试**：

```bash
# 安装Playwright
cd frontend
npx playwright install

# 运行E2E测试
npm run test:e2e

# 运行特定测试
npx playwright test critical-journey.spec.ts

# 查看测试报告
npx playwright show-report
```

---

## 代码审查清单

### 功能正确性

**基础功能**：
- [ ] 功能按照需求正确实现
- [ ] 边界条件处理正确
- [ ] 错误处理完善
- [ ] 日志记录充分

**数据验证**：
- [ ] 使用Pydantic Schema验证输入
- [ ] SQL参数化查询防止注入
- [ ] XSS防护（HTML转义）
- [ ] 输出编码正确

**业务逻辑**：
- [ ] 使用game_gid而非game_id
- [ ] 游戏上下文验证
- [ ] 事务处理正确
- [ ] 并发处理安全

### 代码质量

**代码结构**：
- [ ] 遵循分层架构（Schema/Repository/Service/API）
- [ ] 单一职责原则
- [ ] DRY（Don't Repeat Yourself）
- [ ] 代码复用性良好

**命名规范**：
- [ ] Python使用snake_case
- [ ] TypeScript使用camelCase
- [ ] 类和接口使用PascalCase
- [ ] 常量使用UPPER_CASE

**文档和注释**：
- [ ] 函数有完整docstring
- [ ] 复杂逻辑有注释
- [ ] API有文档说明
- [ ] README更新

**类型安全**：
- [ ] Python有完整类型注解
- [ ] TypeScript有类型定义
- [ ] 避免使用`Any`类型
- [ ] 接口定义清晰

### 测试覆盖

**单元测试**：
- [ ] 核心逻辑有单元测试
- [ ] 测试覆盖率 > 80%
- [ ] 测试命名清晰
- [ ] 测试数据独立

**集成测试**：
- [ ] API有集成测试
- [ ] 数据库操作有测试
- [ ] 外部服务调用有测试

**E2E测试**：
- [ ] 核心流程有E2E测试
- [ ] 关键用户场景覆盖
- [ ] 测试稳定可靠

### 文档完整性

**代码文档**：
- [ ] README更新
- [ ] API文档更新
- [ ] 架构文档更新
- [ ] 变更日志更新

**使用文档**：
- [ ] 新功能有使用说明
- [ ] 配置项有说明
- [ ] 环境变量有说明
- [ ] 示例代码完整

---

## 提交规范

### 提交前检查

**代码质量**：
```bash
# 1. 运行代码格式化
black backend/
isort backend/

# 2. 运行代码检查
pylint backend/
flake8 backend/

# 3. 运行类型检查
mypy backend/

# 4. 运行测试
pytest test/unit/backend/ -v
pytest test/integration/ -v

# 5. 运行API契约测试
python scripts/test/api_contract_test.py
```

**前端检查**：
```bash
# 1. 运行代码格式化
npm run format

# 2. 运行代码检查
npm run lint

# 3. 运行类型检查
npm run type-check

# 4. 运行测试
npm run test
npm run test:e2e
```

### 提交流程

1. **创建分支**：
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **开发代码**：
   - 遵循TDD流程
   - 编写测试
   - 实现功能
   - 更新文档

3. **提交代码**：
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

4. **推送分支**：
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**：
   - 填写PR模板
   - 关联相关Issue
   - 请求代码审查

### Pull Request模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 重构
- [ ] 文档更新
- [ ] 性能优化
- [ ] 测试

## 变更说明
简要描述本次变更的内容和目的。

## 相关Issue
Closes #123

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] E2E测试通过
- [ ] API契约测试通过

## 文档
- [ ] README已更新
- [ ] API文档已更新
- [ ] 架构文档已更新

## 截图（如适用）
添加截图或演示视频。

## Checklist
- [ ] 代码遵循项目规范
- [ ] 测试覆盖率充足
- [ ] 文档已更新
- [ ] 无合并冲突
```

---

## 问题报告

### Bug报告模板

```markdown
## 问题描述
简要描述遇到的问题。

## 复现步骤
1. 步骤1
2. 步骤2
3. 步骤3

## 期望行为
描述期望的正确行为。

## 实际行为
描述实际发生的错误行为。

## 环境信息
- OS: [e.g. macOS 14.0]
- Python: [e.g. 3.9.0]
- Node.js: [e.g. 18.0.0]
- 浏览器: [e.g. Chrome 120]

## 日志/截图
粘贴相关日志或添加截图。

## 附加信息
其他有助于解决问题的信息。
```

---

## 功能请求

### 功能请求模板

```markdown
## 功能描述
简要描述请求的功能。

## 问题背景
描述这个功能解决的问题或使用场景。

## 期望解决方案
描述期望的功能实现方式。

## 替代方案
描述考虑过的其他解决方案。

## 附加信息
其他有助于理解功能请求的信息。
```

---

## 获取帮助

**社区支持**：
- GitHub Issues: 报告问题和功能请求
- GitHub Discussions: 技术讨论和问题解答

**文档资源**：
- [架构设计](architecture.md)
- [快速开始](getting-started.md)
- [API文档](../api/README.md)

**联系方式**：
- 邮件: support@event2table.com
- Discord: Event2Table Community

---

## 行为准则

**我们的承诺**：
- 尊重不同观点和经验
- 使用欢迎和包容的语言
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

**不可接受的行为**：
- 使用性化语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人私人信息
- 其他在专业场合可能被认为不合适的行为

---

**感谢你的贡献！**

**文档版本**: 1.0
**最后更新**: 2026-02-10
**维护者**: Event2Table Development Team
