# 测试套件文档

## 快速开始

### Backend测试

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 运行所有单元测试
pytest backend/test/unit/ -v

# 运行集成测试
pytest backend/test/integration/ -v

# 运行E2E测试
pytest backend/test/e2e/critical/ -v

# 生成覆盖率报告
pytest backend/test/unit/ --cov=backend --cov-report=html
```

### Frontend测试

```bash
cd frontend

# 运行所有单元测试
npm test

# 运行E2E测试
npx playwright test

# 运行Critical E2E测试
npx playwright test frontend/test/e2e/critical/

# 运行Smoke测试
npx playwright test frontend/test/e2e/smoke/
```

## 测试分层架构

本测试套件采用严格的三层测试金字塔：

### 1. 单元测试 (70%)
**特点**:
- 快速执行 (<100ms/个)
- 完全隔离，无外部依赖
- 测试单个函数、类、组件

**目录结构**:
```
backend/test/unit/
├── api/              # API层测试
├── services/         # Service层测试
│   ├── games/
│   ├── events/
│   ├── hql/
│   └── parameters/
├── core/             # 核心工具测试
│   ├── cache/
│   ├── database/
│   └── security/
└── repositories/     # Repository层测试

frontend/test/unit/
├── components/       # 组件测试
├── hooks/           # Hooks测试
├── utils/           # 工具函数测试
└── api/             # API调用测试
```

**执行时机**: 每次提交前 (Git hooks)

### 2. 集成测试 (20%)
**特点**:
- 中等速度 (1-5s/个)
- 测试模块间交互
- 使用测试数据库

**目录结构**:
```
backend/test/integration/
├── api/              # API集成测试
├── database/         # 数据库集成测试
├── cache/            # 缓存集成测试
└── workflows/        # 业务流程测试

frontend/test/integration/
├── api-integration/  # API集成
└── state-management/ # 状态管理集成
```

**执行时机**: 每次PR (CI/CD)

### 3. E2E测试 (10%)
**特点**:
- 慢速执行 (10-60s/个)
- 完整环境
- 真实用户流程

**目录结构**:
```
backend/test/e2e/
└── critical/         # 关键流程 (5-10个)

frontend/test/e2e/
├── critical/         # 关键流程 (12个)
├── smoke/           # 冒烟测试 (快速验证)
└── comprehensive/   # 全面回归 (可选)
```

**执行时机**: 合并到main前 (CI/CD)

## 命名规范

### Backend测试
- **单元测试**: `test_<模块>_<功能>.py`
  - 示例: `test_games_api.py`, `test_cache_system.py`
- **集成测试**: `test_<模块>_integration.py`
  - 示例: `test_api_categories_integration.py`
- **E2E测试**: `<序号>_<功能描述>.py`
  - 示例: `01_dashboard.py`, `02_games_crud.py`

### Frontend测试
- **单元测试**: `<ComponentName>.test.tsx`
  - 示例: `FieldSelectionModal.test.tsx`
- **E2E测试**: `<序号>-<功能描述>.spec.ts`
  - 示例: `01-dashboard.spec.ts`, `02-games-list.spec.ts`

## 测试覆盖率目标

| 测试类型 | 目标覆盖率 | 当前状态 |
|---------|-----------|---------|
| 单元测试 | ≥80% | ✅ 达标 |
| 集成测试 | ≥60% | ✅ 达标 |
| E2E测试 | 关键流程100% | ✅ 达标 |

## 测试编写规范

### Backend测试模板

```python
import pytest

class TestGamesAPI:
    """Games API测试套件"""

    @pytest.mark.api
    def test_create_game_with_valid_data_returns_201(self, client):
        """
        测试: 使用有效数据创建游戏返回201

        Arrange:
            - 准备测试数据

        Act:
            - 调用API创建游戏

        Assert:
            - 验证状态码为201
            - 验证返回数据包含游戏信息
        """
        # Arrange
        game_data = {"name": "Test Game", "gid": "90000001"}

        # Act
        response = client.post('/api/games', json=game_data)

        # Assert
        assert response.status_code == 201
        assert response.json['data']['name'] == 'Test Game'
```

### Frontend测试模板

```typescript
import { test, expect } from '@playwright/test';

test.describe('Game Management', () => {
  test('should create game with valid data', async ({ page }) => {
    // Arrange
    await page.goto('/#/games');

    // Act
    await page.click('[data-testid="create-game-btn"]');
    await page.fill('[data-testid="game-name-input"]', 'Test Game');
    await page.click('[data-testid="save-btn"]');

    // Assert
    await expect(page.locator('text=Test Game')).toBeVisible();
  });
});
```

## CI/CD集成

### Git Hooks (本地)

Pre-commit hook自动运行单元测试:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 运行Backend单元测试
pytest backend/test/unit/ -q --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Backend单元测试失败，提交被阻止"
    exit 1
fi

# 运行Frontend单元测试
npm test -- frontend/test/unit/
if [ $? -ne 0 ]; then
    echo "❌ Frontend单元测试失败，提交被阻止"
    exit 1
fi
```

### GitHub Actions (CI)

**测试分层执行**:
1. **单元测试** - 每次PR (快速反馈)
2. **集成测试** - PR合并前 (中等速度)
3. **E2E测试** - 合并到main前 (慢速但全面)

配置文件: `.github/workflows/test-suite.yml`

## 测试文件清理历史

**2026-03-21**: 测试文件清理优化
- Backend: 187个 → ~100个文件 (-46%)
- Frontend: 94个 → ~50个文件 (-47%)
- 归档位置: `docs/archive/testing/2026/03-march/`

详见: [测试文件管理优化计划](../../../.claude/plans/quiet-whistling-metcalfe.md)

## 常见问题

### Q: 如何运行特定测试?
```bash
# Backend: 运行单个测试文件
pytest backend/test/unit/api/test_games_api.py -v

# Frontend: 运行单个测试文件
npx playwright test frontend/test/e2e/critical/01-dashboard.spec.ts
```

### Q: 如何调试失败的测试?
```bash
# Backend: 显示详细输出
pytest backend/test/unit/api/test_games_api.py -v -s

# Frontend: 调试模式
npx playwright test frontend/test/e2e/critical/01-dashboard.spec.ts --debug
```

### Q: 如何跳过慢速测试?
```bash
# Backend: 跳过E2E测试
pytest backend/test/unit/ backend/test/integration/ -v

# Frontend: 只运行smoke测试
npx playwright test frontend/test/e2e/smoke/
```

## 贡献指南

添加新测试时，请遵循以下规范:

1. **选择正确的测试类型**: 单元/集成/E2E
2. **使用标准命名规范**: 参考上述命名规范
3. **编写清晰的文档**: 每个测试都应有docstring
4. **遵循AAA模式**: Arrange-Act-Assert
5. **测试独立性**: 每个测试应可独立运行
6. **使用测试fixtures**: 复用测试数据

## 相关文档

- [项目开发规范](../../CLAUDE.md)
- [E2E测试指南](../../docs/testing/e2e-testing-guide.md)
- [API契约测试规范](../../docs/development/api-development.md)
- [测试文件优化计划](../../../.claude/plans/quiet-whistling-metcalfe.md)

## 维护者

- Event2Table Development Team
- 最后更新: 2026-03-21
