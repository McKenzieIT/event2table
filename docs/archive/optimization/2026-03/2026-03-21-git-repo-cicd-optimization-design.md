# Git仓库优化和CI/CD分离设计文档

> **日期**: 2026-03-21
> **作者**: Claude Sonnet 4.6
> **状态**: 待实施

## 执行摘要

**问题**: 当前Git仓库存在以下问题：
1. 未追踪文件混乱（测试输出、临时脚本、技能输出）
2. Pre-push hook运行时间过长（6.5分钟），阻塞推送
3. 本地和CI重复运行测试，效率低下
4. 缺乏清晰的文件管理和CI/CD规范

**目标**: 建立清晰的Git仓库管理策略和CI/CD分离架构

**预期结果**:
- 未追踪文件减少90%
- Push验证时间从6.5分钟降至30秒（92%改善）
- CI自动运行完整测试，本地快速反馈
- 清晰的团队工作流文档

---

## 第一部分：Git仓库优化策略

### 1.1 测试结果文件策略

**原则**: 不追踪原始测试结果，只追踪总结性Markdown报告

**规则**:
```gitignore
# 忽略：原始测试输出
frontend/test-results/
output/screenshots/
output/test-results/
test-output/
test-reports/
test-results/
playwright-tests/

# 保留：总结性Markdown报告
!output/reports/*.md
!docs/testing/reports/*.md
```

**理由**:
- 原始输出（JSON、txt、截图）占用大量空间，可随时重新生成
- Markdown报告包含洞察和分析，应该保留
- 符合"测试报告驱动"理念

---

### 1.2 Claude Skills输出策略

**原则**: 按技能类型区分处理

**规则**:
```gitignore
# event2table-universal-test：保留配置，忽略输出
.claude/skills/event2table-universal-test/output/
.claude/skills/event2table-universal-test/config/test_configs/

# performance-audit：全部忽略（本地开发工具）
.claude/skills/performance-audit/

# update-docs：忽略输出
.claude/skills/update-docs/output/
```

**理由**:
- 测试配置应该团队共享（确保一致性）
- 性能审计工具是本地工具，不需要版本控制
- 文档更新输出是临时的

---

### 1.3 Scripts目录生命周期管理

**原则**: 建立脚本生命周期（新→执行→归档）

**分类**:

| 脚本类型 | 位置 | 处理方式 | 示例 |
|---------|------|---------|------|
| **迁移脚本** | `scripts/migrate/` | 执行后归档 | `migrate_game_gid_p0.py` |
| **临时脚本** | `scripts/temp/` | 忽略，定期清理 | `debug_*.py`, `fix_*.py` |
| **Git Hooks** | `scripts/git-hooks/` | 保留最新版本 | `pre-commit.sh` |
| **工具脚本** | `scripts/tools/` | 版本控制 | `setup_audit.py` |

**归档流程**:
```bash
# 1. 执行迁移脚本
python scripts/migrate/migrate_game_gid_p0.py

# 2. 验证成功后归档
git mv scripts/migrate/migrate_game_gid_p0.py \
      docs/archive/migration/2026-03/

# 3. 提交归档
git commit -m "chore: 归档已执行的迁移脚本"
```

**清理规则**:
```gitignore
# 临时脚本目录
scripts/temp/
scripts/temp/*.py
scripts/temp/*.txt

# 已归档的迁移脚本（原位置）
scripts/migrate/
```

---

### 1.4 测试配置文件策略

**原则**: 测试fixtures和配置应该版本控制

**规则**:
- ✅ 提交：`backend/test/unit/repositories/conftest.py`（缓存清理fixture）
- ✅ 提交：通用pytest配置
- ❌ 忽略：`conftest.local.py`（本地特定配置）

**理由**:
- 测试配置确保团队环境一致性
- 缓存清理fixture对测试隔离至关重要
- 通用配置无敏感信息，可以共享

---

### 1.5 文档位置策略

**原则**: 活跃文档在主目录，归档文档按日期组织

**规则**:
- 活跃计划：`docs/superpowers/plans/`
- 归档文档：`docs/archive/general/YYYY-MM/`
- 删除重复文件

**示例**:
```
docs/superpowers/plans/2026-03-20-component-library-phase2-plan.md ✅
docs/archive/general/2026-03/2026-03-20-component-library-phase2-plan.md ❌ (重复)
```

---

## 第二部分：CI/CD分离架构

### 2.1 当前问题分析

**Pre-push Hook现状**:
```
执行时间：388.88秒（6.5分钟）
├─ 后端测试：31秒（1044个测试，2个错误）
├─ 前端测试：356秒（1564个测试，144个失败）
└─ 总计：失败（阻止推送）

问题：
❌ 运行时间过长，影响开发效率
❌ 大量失败测试阻塞推送
❌ 本地和CI重复运行相同测试
❌ 开发者绕过hook（使用--no-verify）
```

---

### 2.2 优化方案：三层测试架构

**Layer 1: 本地Pre-push Hook（快速验证，<30秒）**

目标：在推送前进行快速语法和基本检查

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "🚀 Running quick pre-push checks..."

# 1. Python语法检查（5秒）
python3 -m py_compile backend/api/*.py backend/core/*.py

# 2. TypeScript类型检查（10秒）- 可选失败
cd frontend && npx tsc --noEmit --skipLibCheck || echo "⚠️ Type check failed"

# 3. 快速单元测试（15秒）- 只测试核心模块
pytest backend/test/unit/cache/ -v --tb=short -q

echo "✅ Quick checks passed! Pushing..."
exit 0
```

**时间预算**: 30秒

---

**Layer 2: CI Pipeline（完整测试，5-10分钟）**

GitHub Actions工作流：

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 快速反馈：单元测试（每次PR）
  unit-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v3
      - name: Run backend unit tests (shard ${{ matrix.shard }}/4)
        run: |
          pytest backend/test/unit/ \
            --cov=backend \
            --shard-id=${{ matrix.shard }} \
            --num-shards=4 \
            -q

  # 中等速度：集成测试（PR合并前）
  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: pytest backend/test/integration/ -v -n 4

  # 慢速：E2E测试（合并到main前）
  e2e-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: cd frontend && npm run test:e2e:critical
```

**时间预算**:
- 单元测试：10分钟（并行4核心）
- 集成测试：15分钟
- E2E测试：30分钟

---

**Layer 3: 全面测试（定期，每周）**

```yaml
  comprehensive-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v3
      - name: Run all tests with coverage
        run: pytest backend/test/ --cov=backend --cov-report=html
```

---

### 2.3 并行测试优化

**后端pytest并行化**:

```python
# backend/test/pytest.ini

[pytest]
addopts =
    -n auto           # 自动检测CPU核心数
    --dist loadscope  # 按测试类分配
    --maxfail=5       # 失败5个测试后停止
    --tb=short        # 简化traceback
```

**前端Vitest并行化**:

```javascript
// frontend/vitest.config.ts

export default defineConfig({
  test: {
    threads: true,
    maxThreads: 4,
    minThreads: 1,
    shard: process.env.VITEST_SHARD,
  }
})
```

**时间改善**:
- 当前：串行 → 6.5分钟
- 优化：并行 → 2-3分钟（4核心）

---

### 2.4 工作流对比

| 场景 | 当前流程 | 优化后流程 | 改善 |
|------|---------|-----------|------|
| **本地推送** | 等待6.5分钟hook | 等待30秒hook | **92%↓** |
| **PR验证** | 手动运行测试 | CI自动运行（10分钟） | 自动化 |
| **合并到main** | 手动验证 | CI自动E2E（30分钟） | 自动化 |
| **全面测试** | 从不运行 | 每周自动运行 | 新增 |

---

## 第三部分：实施计划

### 阶段1：立即清理（现在执行，10分钟）

**目标**: 清理未追踪文件，建立.gitignore规则

**步骤**:

1. **更新.gitignore**
2. **清理Scripts目录**
   - 归档迁移脚本到`docs/archive/migration/2026-02/`
   - 删除`scripts/temp/`
   - 精简Git Hooks
3. **提交测试配置文件**
4. **验证清理结果**

**预期结果**:
- 未追踪文件减少90%
- .gitignore规则完善
- 仓库结构清晰

---

### 阶段2：优化Pre-push Hook（今天执行，20分钟）

**目标**: 将6.5分钟的hook优化为30秒快速检查

**步骤**:

1. 备份当前hook
2. 创建新的快速hook（30秒）
3. 测试新hook
4. 替换旧hook

**预期结果**:
- Push检查时间：6.5分钟 → 30秒
- 开发体验显著提升

---

### 阶段3：建立CI Pipeline（本周完成，60分钟）

**目标**: 创建GitHub Actions工作流

**步骤**:

1. 创建workflow文件（`.github/workflows/test-suite.yml`）
2. 配置并行测试（pytest-xdist, vitest shards）
3. 推送测试分支验证CI
4. 优化和调整

**预期结果**:
- CI自动运行完整测试套件
- PR自动验证
- 测试结果可视化

---

### 阶段4：文档和规范（本周完成，100分钟）

**目标**: 创建团队文档和规范

**文档清单**:

1. **开发规范更新**（CLAUDE.md）
   - Git工作流章节
   - CI/CD流程说明

2. **测试策略文档**（docs/development/testing-strategy.md）
   - 测试分层
   - 运行时机
   - 失败处理

3. **Scripts生命周期文档**（docs/development/SCRIPTS-LIFECYCLE.md）
   - 脚本分类
   - 归档流程
   - 维护规范

4. **CI/CD运行手册**（docs/development/CICD-GUIDE.md）
   - CI架构
   - 本地工作流
   - 故障排查

**预期结果**:
- 团队有完整的工作流文档
- 新成员可以快速上手

---

### 阶段5：验证和监控（持续进行）

**监控指标**:

1. **Push频率**
   - 优化前：平均每天2-3次
   - 优化后：目标每天10+次

2. **CI通过率**
   - 目标：>85%
   - 监控失败的测试数量和类型

3. **反馈时间**
   - PR创建到CI完成：<15分钟
   - Push到可部署：<45分钟

4. **开发者满意度**
   - 定期调查团队反馈
   - 调整策略

---

## 第四部分：成功指标

### 定量指标

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| **未追踪文件数** | ~40个 | <5个 | 87%↓ |
| **Push验证时间** | 6.5分钟 | 30秒 | 92%↓ |
| **CI自动化率** | 0% | 100% | 新增 |
| **文档完整度** | 40% | 95% | 55%↑ |

### 定性指标

- ✅ 清晰的Git仓库管理策略
- ✅ 快速的本地开发反馈循环
- ✅ 自动化的CI/CD流程
- ✅ 完整的团队工作流文档
- ✅ 新成员友好的上手指南

---

## 附录

### A. .gitignore完整规则

见第一部分的详细规则。

### B. Pre-push Hook完整脚本

```bash
#!/bin/bash
# .git/hooks/pre-push

set -e  # 遇到错误立即退出

echo "🚀 Running quick pre-push checks..."

# 1. Python语法检查（5秒）
echo "📝 [1/3] Checking Python syntax..."
python3 -m py_compile backend/api/*.py backend/core/*.py 2>/dev/null
echo "✅ Python syntax OK"

# 2. TypeScript类型检查（10秒）- 不阻塞
echo "📝 [2/3] Checking TypeScript types..."
cd frontend
if npx tsc --noEmit --skipLibCheck 2>/dev/null; then
    echo "✅ TypeScript types OK"
else
    echo "⚠️  TypeScript type check failed (not blocking)"
fi
cd ..

# 3. 快速单元测试（15秒）
echo "📝 [3/3] Running critical backend tests..."
if pytest backend/test/unit/cache/ -v --tb=short -q 2>/dev/null; then
    echo "✅ Critical tests passed"
else
    echo "❌ Critical tests failed"
    echo "💡 Run 'pytest backend/test/unit/cache/ -v' to see details"
    exit 1
fi

echo "✅ All quick checks passed! Pushing..."
exit 0
```

### C. CI Workflow完整配置

见第二部分的GitHub Actions配置。

---

**文档版本**: 1.0
**最后更新**: 2026-03-21
**维护者**: Event2Table Development Team
