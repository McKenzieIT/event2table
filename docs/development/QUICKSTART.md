# Event2Table 快速开始指南

> **版本**: 7.5 | **最后更新**: 2026-02-22

本文档提供Event2Table开发快速参考，涵盖最常用的开发模式和最佳实践。

---

## 📋 目录

- [环境设置](#环境设置)
- [快速开始](#快速开始)
- [开发模式](#开发模式)
- [常见任务](#常见任务)
- [故障排除](#故障排除)
- [相关文档](#相关文档)

---

## 🔧 环境设置

### 前置要求

- Python 3.9+
- Node.js 25.6.0+
- SQLite 3
- Redis（可选，用于缓存）

### 初始化项目

```bash
# 1. 克隆仓库
cd /Users/mckenzie/Documents/event2table

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 初始化数据库
python scripts/setup/init_db.py

# 5. 安装前端依赖
cd frontend
npm install

# 6. 返回项目根目录
cd ..
```

---

## 🚀 快速开始

### 启动开发服务器

**后端服务器** (终端1):
```bash
python web_app.py
# 访问: http://127.0.0.1:5001
```

**前端开发服务器** (终端2):
```bash
cd frontend
npm run dev
# 访问: http://localhost:5173
```

### 验证安装

```bash
# 1. 检查后端API
curl http://127.0.0.1:5001/api/games

# 2. 检查前端
# 打开浏览器访问 http://localhost:5173

# 3. 运行测试
pytest backend/test/ -v
npm run test  # 前端测试
```

---

## 💻 开发模式

### TDD开发流程 ⚠️ **强制**

```bash
# 1. 在实现功能前，调用TDD skill
/superpowers:test-driven-development

# 2. 编写测试（先看测试失败）
# 3. 编写最小代码使测试通过
# 4. 重构优化，保持测试通过
```

**TDD铁律**: NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

### API契约测试

```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 自动修复API契约问题
python scripts/test/api_contract_test.py --fix

# 验证修复
python scripts/test/api_contract_test.py --verify
```

### E2E测试

```bash
# 1. 确保开发服务器运行
python web_app.py  # 终端1
cd frontend && npm run dev  # 终端2

# 2. 运行E2E测试
cd frontend
npm run test:e2e

# 3. 使用UI模式
npm run test:e2e:ui
```

---

## 🎯 常见任务

### 1. 创建新的API端点

**后端（推荐模式 - 使用Service层）**:
```python
# backend/api/routes/your_feature.py
from flask import Blueprint, request, jsonify
from backend.services.your_feature.your_service import YourService
from backend.core.utils import json_success_response, json_error_response

your_bp = Blueprint('your_feature', __name__)

@your_bp.route('/api/your-endpoint', methods=['POST'])
def create_something():
    """创建资源"""
    try:
        # 1. 解析请求参数
        data = request.get_json()

        # 2. 调用Service层
        service = YourService()
        result = service.create_something(data)

        # 3. 返回响应
        return json_success_response(data=result, message="Success")
    except Exception as e:
        return json_error_response(str(e), status_code=500)
```

**前端调用API**:
```javascript
import { apiCall } from '@/shared/api/client';

// 使用game_gid（而非game_id）
const gameGid = 10000147;
const data = await apiCall(`/api/your-endpoint?game_gid=${gameGid}`, {
  method: 'POST',
  body: JSON.stringify({ name: 'Test' })
});
```

### 2. 使用Service层进行业务逻辑

```python
# backend/services/your_feature/your_service.py
from typing import Dict, Any
from backend.models.repositories.your_repository import YourRepository

class YourService:
    """业务服务层"""

    def __init__(self):
        self.repo = YourRepository()

    def create_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建资源

        业务逻辑：
        1. 验证输入
        2. 检查约束
        3. 创建资源
        4. 返回结果
        """
        # 业务逻辑
        if self.repo.exists(data['name']):
            raise ValueError("Resource already exists")

        # 创建资源
        resource_id = self.repo.create(data)
        return self.repo.find_by_id(resource_id)
```

### 3. 使用SQLValidator防止SQL注入 ⚠️ **极其重要**

```python
from backend.core.security.sql_validator import SQLValidator

# ✅ 正确：验证动态表名
table_name = request.args.get("table")
validated_table = SQLValidator.validate_table_name(table_name)
query = f"SELECT * FROM {validated_table}"

# ✅ 正确：验证动态列名
column = request.args.get("column")
validated_column = SQLValidator.validate_column_name(column)

# ✅ 正确：使用白名单验证
ALLOWED_FIELDS = {"name", "created_at", "id"}
SQLValidator.validate_field_whitelist(sort_by, ALLOWED_FIELDS)

# ❌ 错误：未验证的动态标识符
query = f"SELECT * FROM {table_name} WHERE {column} = ?"  # SQL注入风险！
```

**详细指南**: [sql-validator-guidelines.md](../development/sql-validator-guidelines.md)

### 4. 使用game_gid而非game_id ⚠️ **强制**

```python
# ✅ 正确：使用game_gid
game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_gid = ?', (game_gid,))

# ❌ 错误：使用game_id
game = fetch_one_as_dict('SELECT * FROM games WHERE id = ?', (game_id,))
events = fetch_all_as_dict('SELECT * FROM log_events WHERE game_id = ?', (game_id,))
```

**详细规范**: [CLAUDE.md - 游戏标识符规范](../../CLAUDE.md#游戏标识符规范-⚠️-极其重要---强制执行)

### 5. 前端组件开发

```jsx
// ✅ 正确：使用TypeScript和Props类型
import React from 'react';
import { GameData } from '@/shared/types';

interface GameCardProps {
  game: GameData;
  onEdit: (gameGid: number) => void;
}

export const GameCard: React.FC<GameCardProps> = ({ game, onEdit }) => {
  // 组件逻辑
  return (
    <div className="game-card">
      <h3>{game.name}</h3>
      <p>GID: {game.gid}</p>
      <button onClick={() => onEdit(game.gid)}>编辑</button>
    </div>
  );
};
```

### 6. 使用Input组件 ⚠️ **正确用法**

```jsx
// ✅ 正确：使用label prop
<Input
  label="游戏名称"
  type="text"
  value={gameName}
  onChange={(e) => setGameName(e.target.value)}
  required
/>

// ❌ 错误：label在Input外部
<div className="form-group">
  <label>游戏名称</label>
  <Input ... />
</div>
```

**详细规范**: [CLAUDE.md - Input组件使用规范](../../CLAUDE.md#input组件使用规范-⚠️-极其重要---2026-02-22新增)

### 7. 缓存失效管理

```python
from backend.core.cache import cache

# 修改游戏数据后清理缓存
@game_bp.route('/api/games/<int:game_gid>', methods=['PUT'])
def update_game(game_gid):
    """更新游戏"""
    # 更新数据库
    game = game_service.update_game(game_gid, request.json)

    # 清理缓存
    cache.delete_many(f'game:{game_gid}*')
    cache.delete('games:all')

    return json_success_response(data=game)
```

---

## 🔍 故障排除

### 常见问题

**Q: npm run test 失败，提示 "npx: command not found"**

A: PATH配置问题，解决方法：
```bash
# 使用npm run脚本（推荐）
npm run test
npm run test:e2e

# 或配置PATH
export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH"
source ~/.zshrc
```

**Q: API返回400错误，提示参数无效**

A: 检查是否使用game_gid而非game_id：
```python
# ✅ 正确
fetch('/api/games?game_gid=10000147')

# ❌ 错误
fetch('/api/games?game_id=1')
```

**Q: 测试失败，提示数据库连接错误**

A: 确保使用独立的测试数据库：
```bash
# 设置环境变量
export FLASK_ENV=testing

# 运行测试（会自动使用data/test_database.db）
pytest backend/test/
```

**Q: 前端页面卡在"LOADING"状态**

A: 检查lazy loading配置：
```javascript
// 小型组件应该直接导入
import ApiDocs from '@analytics/pages/ApiDocs';

// 不要使用lazy loading（除非组件>10KB）
// const ApiDocs = lazy(() => import('@analytics/pages/ApiDocs'));
```

**Q: Redis缓存导致数据不一致**

A: 清理Redis缓存：
```bash
redis-cli FLUSHALL

# 或在代码中清理
from backend.core.cache import cache
cache.clear()
```

---

## 📚 相关文档

### 核心文档
- [开发规范](../../CLAUDE.md) - 完整开发规范和最佳实践
- [架构设计](./architecture.md) - 系统架构设计文档
- [贡献指南](./contributing.md) - 如何贡献代码

### 专题文档
- [API设计模式](../lessons-learned/api-design-patterns.md) - API开发规范
- [React最佳实践](../lessons-learned/react-best-practices.md) - 前端开发规范
- [E2E测试指南](../archive/2026-02/testing/e2e-testing-guide.md) - E2E测试规范
- [SQL Validator指南](./sql-validator-guidelines.md) - SQL注入防护

### 优化文档
- [后端优化报告](../archive/2026-02/optimization/FINAL_OPTIMIZATION_REPORT.md) - 6阶段优化总结
- [核心优化指南](../archive/2026-02/optimization/CORE_OPTIMIZATION_GUIDE.md) - 优化实施指南
- [缓存优化](../archive/2026-02/optimization/CACHE_OPTIMIZATION_SUMMARY.md) - 缓存系统优化

### 测试文档
- [快速测试指南](../archive/2026-02/testing/quick-test-guide.md) - PATH问题排查
- [测试指南](../lessons-learned/testing-guide.md) - TDD和E2E测试实践

---

## 🎓 学习路径

### 新手入门
1. 阅读[环境设置](#环境设置)
2. 完成[快速开始](#快速开始)
3. 学习[TDD开发流程](#tdd开发流程-⚠️-强制)
4. 实践[创建新的API端点](#1-创建新的api端点)

### 进阶开发
1. 学习[Service层模式](#2-使用service层进行业务逻辑)
2. 掌握[SQLValidator使用](#3-使用sqlvalidator防止sql注入-⚠️-极其重要)
3. 理解[game_gid规范](#4-使用game_gid而非game_id-⚠️-强制)
4. 阅读[架构设计文档](./architecture.md)

### 最佳实践
1. 遵循[CLAUDE.md规范](../../CLAUDE.md)
2. 定期运行[API契约测试](#api契约测试)
3. 执行完整的[E2E测试](#e2e测试)
4. 参考[优化文档](../archive/2026-02/optimization/)

---

**文档版本**: 1.0
**最后更新**: 2026-02-22
**维护者**: Event2Table Development Team
