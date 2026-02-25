# 测试目录结构标准

## 目录结构

```
tests/                           # 项目根测试目录
├── unit/                        # 单元测试
│   ├── backend/                 # 后端单元测试
│   └── frontend/                # 前端单元测试
├── integration/                 # 集成测试
│   ├── api/                     # API集成测试
│   ├── database/                # 数据库集成测试
│   └── services/                # 服务集成测试
├── e2e/                         # 端到端测试
│   ├── scenarios/               # 测试场景
│   └── fixtures/                # E2E测试数据
├── fixtures/                    # 测试数据夹具
│   ├── events/                  # 事件测试数据
│   ├── games/                   # 游戏测试数据
│   └── parameters/              # 参数测试数据
└── mocks/                       # Mock对象
    ├── services/                # 服务Mock
    └── repositories/            # 仓库Mock

backend/tests/                   # 后端专用测试目录
├── unit/                        # 后端单元测试
│   ├── domain/                  # 领域层测试
│   ├── application/             # 应用层测试
│   └── infrastructure/          # 基础设施层测试
├── integration/                 # 后端集成测试
├── e2e/                         # 后端E2E测试
└── fixtures/                    # 后端测试数据
```

## 测试命名规范

### 文件命名
- 单元测试: `test_{模块名}.py`
- 集成测试: `test_{模块名}_integration.py`
- E2E测试: `test_{场景名}_e2e.py`

### 测试类命名
- 格式: `Test{功能名称}`
- 示例: `TestEventCreation`, `TestGameManagement`

### 测试方法命名
- 格式: `test_{方法名}_{场景}_{预期结果}`
- 示例: `test_create_event_with_valid_data_returns_success`

## 测试覆盖率目标

| 类型 | 目标覆盖率 |
|------|-----------|
| 单元测试 | >80% |
| 集成测试 | >60% |
| E2E测试 | 核心流程100% |

## 测试执行命令

```bash
# 运行所有单元测试
pytest tests/unit -v

# 运行所有集成测试
pytest tests/integration -v

# 运行所有测试并生成覆盖率报告
pytest --cov=backend --cov-report=html

# 运行E2E测试
pytest tests/e2e -v
```

---
创建日期: 2026-02-23
维护人: Event2Table团队
