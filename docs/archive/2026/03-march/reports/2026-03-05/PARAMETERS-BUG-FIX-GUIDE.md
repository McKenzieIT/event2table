# Parameters API Bug Fix Guide

**问题发现时间**: 2026-03-05
**严重级别**: P0 - 严重
**影响范围**: Common Parameters 页面完全无法加载

---

## Bug #3: `/api/parameters/common` 返回 500 错误

### 错误详情

**症状**:
```bash
$ curl "http://127.0.0.1:5001/api/parameters/common?game_gid=10000147"
HTTP 500
```

**错误日志**:
```
Error fetching common parameters: 'ParameterRepository' object has no attribute 'get_game_by_gid'
Traceback (most recent call last):
  File ".../backend/api/routes/parameters.py", line 321, in api_get_common_parameters
    common_params = service.get_common_params(game_gid)
  File ".../backend/core/cache/cache_system.py", line 716, in wrapper
    except (AttributeError, RuntimeError):
  File ".../backend/services/parameters/parameter_service.py", line 669, in get_common_params
    if not game_gid or game_gid <= 0:
AttributeError: 'ParameterRepository' object has no attribute 'get_game_by_gid'
```

### 根本原因分析

**问题代码位置**: `backend/services/parameters/parameter_service.py:655-688`

```python
@cached("params.commonByGame", timeout=180)
def get_common_params(self, game_gid: int) -> List[Dict[str, Any]]:
    """
    获取指定游戏的公共参数列表 (带缓存)
    """
    if not game_gid or game_gid <= 0:
        raise ValueError(f"Invalid game_gid: {game_gid}")

    # ❌ 错误：ParameterRepository 没有 get_game_by_gid 方法
    game = self.param_repo.get_game_by_gid(game_gid)
    if not game:
        raise ValueError(f"Game not found: {game_gid}")

    # 获取公共参数
    common_params = self.param_repo.get_common_params_by_game(game_gid)
    # ...
```

**问题分析**:
1. `ParameterRepository` 没有 `get_game_by_gid` 方法
2. `get_game_by_gid` 是 `GameRepository` 的方法，不是 `ParameterRepository` 的方法
3. 调用不存在的方法导致 `AttributeError`

**ParameterRepository 实际方法**:
```python
# ParameterRepository 有这些方法：
- get_common_parameters(game_gid)
- get_common_params_by_game(game_gid)
- find_common_param_by_name(game_gid, param_name)
- search_parameters(...)
- get_parameter_usage_stats(param_name)
# ... 但没有 get_game_by_gid()
```

**GameRepository 有这个方法**:
```python
# GameRepository 有：
- find_by_gid(game_gid)  # ✅ 这个方法存在
```

### 修复方案

#### 方案 1: 使用 GameRepository 验证游戏存在（推荐）

```python
# backend/services/parameters/parameter_service.py
from backend.models.repositories.games import GameRepository

class ParameterService:
    def __init__(self):
        self.param_repo = ParameterRepository()
        self.game_repo = GameRepository()  # ✅ 添加 GameRepository

    @cached("params.commonByGame", timeout=180)
    def get_common_params(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取指定游戏的公共参数列表 (带缓存)
        """
        if not game_gid or game_gid <= 0:
            raise ValueError(f"Invalid game_gid: {game_gid}")

        # ✅ 使用 GameRepository 验证游戏
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: {game_gid}")

        # 获取公共参数
        common_params = self.param_repo.get_common_params_by_game(game_gid)

        # 映射字段
        for param in common_params:
            param["data_type"] = param.get("param_type", "string")
            param["key"] = param.get("param_name", "")
            param["name"] = param.get("param_name_cn", param.get("param_name", ""))
            param["description"] = param.get("param_description", "")

        return common_params
```

#### 方案 2: 移除游戏验证（快速修复）

如果游戏验证已在 API 层完成，可以直接移除：

```python
@cached("params.commonByGame", timeout=180)
def get_common_params(self, game_gid: int) -> List[Dict[str, Any]]:
    """
    获取指定游戏的公共参数列表 (带缓存)
    """
    if not game_gid or game_gid <= 0:
        raise ValueError(f"Invalid game_gid: {game_gid}")

    # ✅ 直接获取公共参数，不验证游戏
    common_params = self.param_repo.get_common_params_by_game(game_gid)

    # 映射字段
    for param in common_params:
        param["data_type"] = param.get("param_type", "string")
        param["key"] = param.get("param_name", "")
        param["name"] = param.get("param_name_cn", param.get("param_name", ""))
        param["description"] = param.get("param_description", "")

    return common_params
```

### 修复步骤

**步骤 1**: 备份当前文件
```bash
cp backend/services/parameters/parameter_service.py backend/services/parameters/parameter_service.py.backup
```

**步骤 2**: 应用修复（推荐方案 1）
```bash
# 编辑文件
vim backend/services/parameters/parameter_service.py

# 在 __init__ 中添加 GameRepository
def __init__(self):
    self.param_repo = ParameterRepository()
    self.game_repo = GameRepository()  # 添加这行

# 修复 get_common_params 方法（约 673 行）
# 将 self.param_repo.get_game_by_gid(game_gid)
# 改为 self.game_repo.find_by_gid(game_gid)
```

**步骤 3**: 重启后端服务器
```bash
# 停止旧服务器
kill <PID>

# 启动新服务器
source backend/venv/bin/activate
nohup python web_app.py > logs/backend.log 2>&1 &
```

**步骤 4**: 验证修复
```bash
# 测试 API
curl "http://127.0.0.1:5001/api/parameters/common?game_gid=10000147"

# 预期结果
HTTP 200
{
  "success": true,
  "data": [...]
}
```

**步骤 5**: 检查前端页面
```bash
# 访问 Common Parameters 页面
open http://localhost:5173/#/common-params?game_gid=10000147

# 验证页面正常加载，显示公共参数列表
```

---

## Bug #4: 搜索功能 SQL 绑定错误

### 错误详情

**症状**:
```bash
$ curl "http://127.0.0.1:5001/api/parameters/all?game_gid=10000147&search=role"
HTTP 200 (但返回 0 结果)
```

**错误日志**:
```
2026-03-05 13:43:27 - backend.core.utils.converters - ERROR -
Error fetching one as dict: Incorrect number of bindings supplied.
The current statement uses 3, and there are 5 supplied.
```

**问题**: SQL 参数绑定错误，搜索功能无法正常工作

### 待修复

需要检查 `search_parameters` 方法的 SQL 查询和参数绑定逻辑。

---

## 测试清单

修复后请完成以下测试：

### P0 测试（必须通过）

- [ ] `/api/parameters/common?game_gid=10000147` 返回 HTTP 200
- [ ] Common Parameters 页面正常加载
- [ ] 公共参数列表正确显示
- [ ] 无后端错误日志

### P1 测试（应该通过）

- [ ] 搜索功能正常工作
- [ ] 分页功能正常工作
- [ ] 统计数据正确
- [ ] 前端 3 个页面全部正常加载

### API 契约测试

```bash
# 运行 API 契约测试
python scripts/test/api_contract_test.py
```

### E2E 测试

```bash
# 启动 Chrome DevTools MCP
# 运行 E2E 测试（需要配置）
```

---

## 相关文件

**需要修改的文件**:
- `backend/services/parameters/parameter_service.py` - ParameterService.get_common_params 方法

**相关文件**:
- `backend/models/repositories/parameters.py` - ParameterRepository
- `backend/models/repositories/games.py` - GameRepository
- `backend/api/routes/parameters.py` - Common Parameters API 端点

---

## 预期修复时间

- **方案 1（推荐）**: 5-10 分钟
- **方案 2（快速）**: 2-3 分钟

---

## 修复后验证

修复完成后，请运行以下命令验证：

```bash
# 1. 测试 Common Parameters API
curl -s "http://127.0.0.1:5001/api/parameters/common?game_gid=10000147" | jq '.success'

# 预期输出: true

# 2. 检查后端日志（应该无错误）
tail -20 logs/backend.log | grep -i error

# 预期输出: 无错误

# 3. 测试前端页面
# 访问 http://localhost:5173/#/common-params?game_gid=10000147
# 验证页面正常显示公共参数列表
```

---

**创建时间**: 2026-03-05 13:50:00
**创建人**: Claude Code
**优先级**: P0 - 紧急修复
