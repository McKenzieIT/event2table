# 快速开始

> **版本**: 1.0 | **最后更新**: 2026-02-10
>
> 本文档将帮助你快速搭建 Event2Table 开发环境并开始开发。

---

## 目录

- [系统要求](#系统要求)
- [环境搭建](#环境搭建)
- [项目结构](#项目结构)
- [快速开发](#快速开发)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

- **CPU**: 双核及以上
- **内存**: 4GB及以上（推荐8GB）
- **磁盘**: 2GB可用空间

### 软件要求

**后端开发**：
- **Python**: 3.9 或更高版本
- **pip**: 21.0 或更高版本
- **SQLite**: 3.35 或更高版本

**前端开发**：
- **Node.js**: 18.0 或更高版本
- **npm**: 9.0 或更高版本

**开发工具**（推荐）：
- **IDE**: VSCode / PyCharm
- **Git**: 2.30 或更高版本
- **浏览器**: Chrome / Firefox（开发调试）

---

## 环境搭建

### 1. 克隆项目

```bash
# 克隆仓库
git clone <repository-url>
cd event2table
```

### 2. 后端环境搭建

```bash
# 创建虚拟环境（推荐在backend目录下创建，方便开发）
cd backend
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 验证安装
python --version  # Python 3.9+
pip list
```

**注意**：backend/venv/已添加到.gitignore，不会被git跟踪。

**初始化数据库**：

```bash
# 运行初始化脚本
python scripts/setup/init_db.py

# 验证数据库
ls -lh dwd_generator.db
```

### 3. 前端环境搭建

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 验证安装
node --version  # v18+
npm --version  # 9+
npm list --depth=0
```

### 4. 启动应用

**启动后端**：

```bash
# 在项目根目录
python web_app.py

# 看到以下输出表示启动成功
# * Running on http://127.0.0.1:5001
# * Press CTRL+C to quit
```

**启动前端（开发模式）**：

```bash
# 在 frontend 目录
npm run dev

# 看到以下输出表示启动成功
# VITE ready in xxx ms
# ➜ Local: http://localhost:5173/
```

### 5. 访问应用

打开浏览器访问：
- **前端应用**: http://localhost:5173
- **后端API**: http://127.0.0.1:5001

---

## 项目结构

### 后端结构

```
backend/
├── api/                    # API路由层
│   └── routes/
│       └── dwd_generator/  # API端点
│           ├── games.py    # 游戏API
│           ├── events.py   # 事件API
│           └── parameters.py # 参数API
├── core/                   # 核心工具
│   ├── config/            # 配置管理
│   ├── database/          # 数据库操作
│   ├── cache/             # 缓存系统
│   ├── security/          # 安全工具
│   ├── utils/             # 工具函数
│   └── validators/        # 验证器
├── models/                # 数据模型层
│   ├── schemas.py         # Pydantic Schema
│   └── repositories/      # Repository
│       ├── games.py
│       ├── events.py
│       └── parameters.py
└── services/              # 业务服务层
    ├── games/             # 游戏服务
    ├── events/            # 事件服务
    ├── parameters/        # 参数服务
    ├── canvas/            # Canvas服务
    └── hql/               # HQL生成器
        ├── core/          # 核心生成器
        ├── builders/      # Builder模式
        ├── models/        # 数据模型
        └── validators/    # 验证器
```

### 前端结构

```
frontend/
├── src/
│   ├── features/          # 功能模块
│   │   ├── games/         # 游戏管理
│   │   ├── events/        # 事件管理
│   │   ├── parameters/    # 参数管理
│   │   ├── canvas/        # Canvas系统
│   │   └── event-builder/ # 事件构建器
│   ├── shared/            # 共享组件
│   │   ├── ui/            # UI组件
│   │   ├── hooks/         # 共享Hooks
│   │   ├── utils/         # 工具函数
│   │   └── types/         # 类型定义
│   ├── styles/            # 全局样式
│   ├── App.jsx            # 应用入口
│   └── main.jsx           # 主文件
├── tests/                 # 测试文件
│   ├── e2e/               # E2E测试
│   └── unit/              # 单元测试
├── package.json           # 依赖配置
└── vite.config.js         # Vite配置
```

---

## 快速开发

### 1. 创建游戏（后端）

**步骤1: 编写测试**

```python
# test/unit/backend/services/test_game_service.py
import pytest
from backend.services.games.game_service import GameService
from backend.models.schemas import GameCreate

def test_create_game():
    """测试创建游戏"""
    # Arrange
    service = GameService()
    game_data = GameCreate(
        gid="10000147",
        name="Test Game",
        ods_db="ieu_ods"
    )

    # Act
    game = service.create_game(game_data)

    # Assert
    assert game is not None
    assert game['gid'] == "10000147"
    assert game['name'] == "Test Game"
```

**步骤2: 运行测试（失败）**

```bash
pytest test/unit/backend/services/test_game_service.py::test_create_game -v
# FAILED - 这是期望的！
```

**步骤3: 实现代码**

```python
# backend/services/games/game_service.py
from backend.models.repositories.games import GameRepository
from backend.models.schemas import GameCreate
from typing import Dict, Any

class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()

    def create_game(self, game_data: GameCreate) -> Dict[str, Any]:
        """创建游戏"""
        # 检查gid唯一性
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game gid {game_data.gid} already exists")

        # 创建游戏
        game_id = self.game_repo.create(game_data.dict())
        return self.game_repo.find_by_id(game_id)
```

**步骤4: 运行测试（通过）**

```bash
pytest test/unit/backend/services/test_game_service.py::test_create_game -v
# PASSED
```

### 2. 创建API端点

```python
# backend/api/routes/dwd_generator/games.py
from flask import Blueprint, request
from backend.services.games.game_service import GameService
from backend.models.schemas import GameCreate, GameResponse
from backend.core.utils import json_success_response, json_error_response
import logging

logger = logging.getLogger(__name__)
games_bp = Blueprint('games', __name__)

@games_bp.route('/api/games', methods=['POST'])
def create_game():
    """创建游戏API"""
    try:
        # 1. 解析和验证请求
        data = request.get_json()
        game_data = GameCreate(**data)

        # 2. 调用Service
        service = GameService()
        game = service.create_game(game_data)

        # 3. 返回响应
        return json_success_response(
            data=GameResponse(**game).dict(),
            message="Game created successfully"
        )

    except ValueError as e:
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        logger.error(f"Error: {e}")
        return json_error_response("Failed to create game", status_code=500)
```

### 3. 创建前端组件

```typescript
// frontend/src/features/games/components/GameForm.jsx
import { useState } from 'react';
import { Button } from '../../../shared/ui/Button';

export function GameForm() {
  const [gameData, setGameData] = useState({
    gid: '',
    name: '',
    ods_db: 'ieu_ods'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/games', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gameData)
      });

      const result = await response.json();

      if (result.success) {
        alert('Game created successfully!');
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Game GID"
        value={gameData.gid}
        onChange={(e) => setGameData({...gameData, gid: e.target.value})}
      />
      <input
        type="text"
        placeholder="Game Name"
        value={gameData.name}
        onChange={(e) => setGameData({...gameData, name: e.target.value})}
      />
      <select
        value={gameData.ods_db}
        onChange={(e) => setGameData({...gameData, ods_db: e.target.value})}
      >
        <option value="ieu_ods">IEU ODS</option>
        <option value="overseas_ods">Overseas ODS</option>
      </select>
      <Button type="submit">Create Game</Button>
    </form>
  );
}
```

---

## 开发工作流

### 1. TDD开发流程

```
编写测试 → 运行测试（失败） → 编写代码 → 运行测试（通过） → 重构
```

### 2. 代码提交流程

```bash
# 1. 查看修改
git status
git diff

# 2. 添加文件
git add .

# 3. 提交代码
git commit -m "feat(game): add game creation feature"

# 4. 推送代码
git push origin feature/your-feature
```

### 3. 测试流程

**后端测试**：

```bash
# 单元测试
pytest test/unit/backend/ -v

# 集成测试
pytest test/integration/ -v

# 测试覆盖率
pytest --cov=backend --cov-report=html
```

**前端测试**：

```bash
# 单元测试
npm run test

# E2E测试
npm run test:e2e

# 测试覆盖率
npm run test:coverage
```

---

## 常见问题

### Q1: 虚拟环境激活失败？

**A**: 确保使用正确的激活命令：

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Q2: pip install 失败？

**A**: 尝试升级pip和使用国内镜像：

```bash
# 升级pip
pip install --upgrade pip

# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: npm install 失败？

**A**: 清除缓存并重试：

```bash
# 清除缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### Q4: 数据库初始化失败？

**A**: 检查SQLite是否安装：

```bash
# 检查SQLite版本
sqlite3 --version

# 手动创建数据库
sqlite3 dwd_generator.db
```

### Q5: 端口被占用？

**A**: 修改端口号或杀死占用进程：

```bash
# 查找占用端口的进程
lsof -i :5001  # 后端
lsof -i :5173  # 前端

# 杀死进程
kill -9 <PID>

# 或修改配置
export FLASK_PORT=5002
```

### Q6: 前端无法连接后端？

**A**: 检查后端是否启动和CORS配置：

```bash
# 检查后端
curl http://127.0.0.1:5001/api/games

# 检查CORS
# backend/api/routes/__init__.py
from flask_cors import CORS
CORS(app)
```

### Q7: 测试失败？

**A**: 检查测试数据库配置：

```bash
# 设置测试环境
export FLASK_ENV=testing

# 运行测试
pytest test/unit/backend/ -v

# 检查测试数据库
ls -lh test/test_database.db
```

---

## 下一步

**学习资源**：

1. 阅读 [架构设计](architecture.md) - 了解系统架构
2. 阅读 [贡献指南](contributing.md) - 学习开发规范
3. 阅读 [API文档](../api/README.md) - 了解API接口
4. 查看 [示例代码](../../examples/) - 学习最佳实践

**开发任务**：

- 查看 [GitHub Issues](https://github.com/your-org/event2table/issues)
- 选择一个good first issue
- 按照 [贡献指南](contributing.md) 提交PR

---

**文档版本**: 1.0
**最后更新**: 2026-02-10
**维护者**: Event2Table Development Team
