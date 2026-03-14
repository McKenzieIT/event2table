# Parameters API 快速参考

**最后更新**: 2026-03-05

---

## API 端点状态

| 端点 | 状态 | HTTP | 说明 |
|------|------|------|------|
| `/api/parameters/all` | ✅ | 200 | 完全正常 |
| `/api/parameters/stats` | ✅ | 200 | 完全正常 |
| `/api/parameters/common` | ❌ | 500 | **需要修复** |

---

## 快速测试命令

```bash
# 测试所有端点
curl "http://127.0.0.1:5001/api/parameters/all?game_gid=10000147" | jq '.success'
curl "http://127.0.0.1:5001/api/parameters/stats?game_gid=10000147" | jq '.success'
curl "http://127.0.0.1:5001/api/parameters/common?game_gid=10000147" | jq '.success'

# 预期结果: true, true, false (第3个需要修复)
```

---

## Bug #3 修复步骤

**问题**: `ParameterRepository` 没有方法 `get_game_by_gid`

**位置**: `backend/services/parameters/parameter_service.py:673`

**修复**:

```python
# 在 __init__ 中添加
def __init__(self):
    self.param_repo = ParameterRepository()
    self.game_repo = GameRepository()  # 添加这行

# 在 get_common_params 中修改（第 673 行）
# 修复前
game = self.param_repo.get_game_by_gid(game_gid)  # ❌ 错误

# 修复后
game = self.game_repo.find_by_gid(game_gid)  # ✅ 正确
```

**验证**:
```bash
# 重启后端
kill <PID> && source backend/venv/bin/activate && nohup python web_app.py > logs/backend.log 2>&1 &

# 测试 API
curl "http://127.0.0.1:5001/api/parameters/common?game_gid=10000147" | jq '.success'
# 预期: true
```

---

## 关键数据

**测试游戏**: STAR001 (GID: 10000147)

**统计**:
- 总参数: 2162
- 总事件参数: 36718
- 公共参数: 0 (因为 API 500 错误)

**数据类型**:
- int: 83.3%
- array: 12.5%
- string: 6.0%
- boolean: 4.6%
- map: 0.6%

---

## 文档链接

- **详细验证**: [PARAMETERS-P0-VERIFICATION.md](./PARAMETERS-P0-VERIFICATION.md)
- **修复指南**: [PARAMETERS-BUG-FIX-GUIDE.md](./PARAMETERS-BUG-FIX-GUIDE.md)
- **总结报告**: [PARAMETERS-VERIFICATION-SUMMARY.md](./PARAMETERS-VERIFICATION-SUMMARY.md)

---

**修复优先级**: P0 - 立即执行
**预计时间**: 5-10 分钟
