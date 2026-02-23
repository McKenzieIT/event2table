# 测试指南

> **来源**: 整合了3个文档的测试相关经验
> **最后更新**: 2026-02-24
> **维护**: 每次测试相关问题修复后立即更新

---

## E2E测试方法论 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 2次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md), [phase2-lessons-learned.md](../archive/2026-02/testing-reports/phase2-lessons-learned.md), [FINAL-REPORT](../archive/2026-02/e2e-test-reports/FINAL-REPORT.md)

### 核心测试哲学

**从浅层到深度的转变**:
- ❌ **旧方法**：页面加载测试（20%深度）
- ✅ **新方法**：用户工作流测试（60%深度）

**测试深度比例**:
- 页面加载测试：20%
- 用户交互测试：60%
- 工作流完成测试：20%

### Ralph Loop迭代测试法

**测试流程**:
```
发现问题 → Subagent深度分析 → 设计修复方案 → 实施修复 → Chrome MCP验证 → 记录结果
```

**具体步骤**:
1. **发现问题** - 执行E2E测试，记录错误
2. **Subagent深度分析** - 使用并行Subagent分析根因
3. **设计修复方案** - 使用Brainstorming skill系统化设计
4. **实施修复** - 编写代码修复问题
5. **Chrome MCP验证** - 使用Chrome DevTools MCP验证修复
6. **记录结果** - 更新经验文档

### Chrome DevTools MCP测试流程

**标准测试步骤**:
```javascript
// 1. 列出所有页面
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

// 5. 截图记录
mcp__chrome-devtools__take_screenshot({
  filePath: "docs/reports/2026-02-23/verification-screenshot.png",
  fullPage: true
})

// 6. 点击交互元素
mcp__chrome-devtools__click({ uid: "clickable-element-uid" })
```

**错误检测模式**:

**React Hooks错误**:
```
[error] React has detected a change in the order of Hooks called
[error] Uncaught Error: Rendered more hooks than during the previous render
```

**加载超时错误**:
```
页面状态：卡在"LOADING EVENT2TABLE..."超过30秒
控制台：无错误信息（但也不显示任何内容）
```

**API错误**:
```
[error] Failed to load resource: 400 (BAD REQUEST)
```

### 测试工具选择

**Playwright vs Chrome DevTools MCP**:
- **Playwright**: 适合自动化测试、回归测试、CI/CD集成
- **Chrome DevTools MCP**: 适合探索性测试、根因分析、交互式调试

**选择原则**:
- 自动化测试 → Playwright
- 探索性测试 → Chrome DevTools MCP
- 回归测试 → Playwright
- Bug调试 → Chrome DevTools MCP

### 代码审查清单

**E2E测试检查**:
- [ ] 用户工作流是否完整测试？
- [ ] 是否测试了错误场景？
- [ ] 是否验证了控制台无错误？
- [ ] 是否截图记录测试结果？
- [ ] 是否测试了边界情况？

---

## TDD实践 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md)

### TDD铁律

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

**TDD流程（Red-Green-Refactor）**:
1. **Red** - 先写测试，看测试失败
2. **Green** - 编写最小代码使测试通过
3. **Refactor** - 重构优化，保持测试通过

### 为什么需要TDD？

**好处**:
- ✅ 测试先行确保代码满足需求（而非"实现后验证"）
- ✅ 失败的测试证明测试有效（通过的测试可能什么都没测）
- ✅ 快速反馈循环减少调试时间
- ✅ 测试即文档，展示代码的正确使用方式

**违反TDD的代价**:
- ❌ 看似"更快"实际更慢（调试时间 > TDD时间）
- ❌ 测试通过立即 = 测试无效 = 假安全感
- ❌ 技术债务累积 = 未来重构困难

### 强制检查清单

**开发前检查**:
- [ ] 调用 `/superpowers:test-driven-development` skill
- [ ] 阅读TDD铁律
- [ ] 确认已设置测试环境（pytest/npm test等）
- [ ] 准备好先写测试，再看测试失败

**禁止行为**:
- ❌ 代码存在先于测试
- ❌ 测试通过立即（未看到失败）
- ❌ 跳过测试直接实现功能

### 相关经验

- [E2E测试方法论](#e2e测试) - E2E测试具体方法
- [测试自动化](#测试自动化) - 减少重复工作的自动化策略

---

## 测试自动化 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md)

### Pre-commit Hook强制测试

**安装pre-commit hook**:
```bash
# 复制pre-commit hook到.git/hooks/
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Hook功能**:
- 每次提交前自动运行测试
- 测试失败则阻止提交
- 显示所有失败的测试

**npm scripts配置**:
```json
{
  "scripts": {
    "test": "playwright test",
    "test:unit": "vitest",
    "test:e2e": "playwright test tests/e2e",
    "test:watch": "vitest --watch"
  }
}
```

### 测试分类

**单元测试**:
- 测试单个函数、类、组件
- 快速执行（毫秒级）
- 使用Vitest（前端）、pytest（后端）

**集成测试**:
- 测试多个模块的交互
- 中等执行时间（秒级）
- 使用pytest（后端）、Vitest（前端）

**E2E测试**:
- 测试完整用户工作流
- 较慢执行（分钟级）
- 使用Playwright

### 测试覆盖率目标

**目标**:
- 单元测试覆盖率：>80%
- 集成测试覆盖率：>60%
- E2E测试覆盖率：关键路径100%

**验证命令**:
```bash
# 前端覆盖率
npm run test:coverage

# 后端覆盖率
pytest backend/test/ --cov=backend --cov-report=html
```

---

## 错误消息质量对用户体验的影响 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing-reports/phase2-lessons-learned.md)

### 核心原则

**错误消息质量直接影响用户体验和支持成本**

### 错误消息改进示例

| 场景 | 修复前 | 修复后 | 改进效果 |
|------|--------|--------|----------|
| GID重复 | "Game GID already exists" | "游戏GID 10000147 已存在，请使用其他GID（建议使用90000000+范围）" | ⭐⭐⭐⭐⭐ |
| GID格式错误 | "Game GID must be a positive integer" | "游戏GID必须是有效的正整数（提示：GID必须是正整数，如90000001）" | ⭐⭐⭐⭐ |
| 权限不足 | "Permission denied" | "您没有权限删除系统类别（ID: 1），请联系管理员" | ⭐⭐⭐⭐⭐ |

### 最佳实践代码

```javascript
// ❌ 错误做法
throw new Error('创建失败');

// ✅ 正确做法：根据HTTP状态码提供具体指导
let errorMessage = result.message || '创建失败';
if (response.status === 409) {
  errorMessage = `游戏GID ${data.gid} 已存在，请使用其他GID（建议使用90000000+范围）`;
} else if (response.status === 400) {
  if (errorMessage.includes('GID')) {
    errorMessage += '（提示：GID必须是正整数，如90000001）';
  }
}
throw new Error(errorMessage);
```

### 预防措施

**代码审查清单**:
- [ ] 错误消息是否具体可操作？
- [ ] 是否包含解决方案或建议？
- [ ] 是否避免技术术语？
- [ ] 是否考虑不同技术水平的用户？

---

## 避免重复工作 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 2次 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing-reports/phase2-lessons-learned.md)

### 问题调查流程

```
1. 阅读相关代码（后端 + 前端）
2. 检查是否有现有实现
3. 检查注释和commit历史
4. 如果已实现 → 验证并文档化
5. 如果未实现 → 设计并实现修复
```

### 案例：事件创建分类问题

**Phase 1建议**: "修复事件创建分类问题"
**Phase 2发现**: 后端第29-39行已有自动创建逻辑
**结论**: 问题已解决，只需要验证

**教训**: 调查优先于实施，避免重复工作

### 预防措施

**开发前检查**:
- [ ] 是否已搜索代码库查找类似实现？
- [ ] 是否检查过相关文档和注释？
- [ ] 是否询问过团队成员？

---

## 测试方法论演进 ⭐ **P1重要**

**优先级**: P1 | **来源**: [phase2-lessons-learned.md](../archive/2026-02/testing-reports/phase2-lessons-learned.md)

### Phase 1方法论（浅层测试）❌

```
1. 导航到页面
2. 检查页面是否加载
3. 检查控制台是否有错误
4. 截图
5. 报告：PASS ✅

问题：
- ❌ 没有测试用户交互
- ❌ 没有验证功能是否工作
- ❌ 错过了关键bug
```

### Phase 2方法论（深度测试）✅

```
1. 导航到页面
2. 识别关键用户交互点
3. 对每个交互点：
   a. 执行交互（点击/输入/拖拽）
   b. 等待响应（2-3秒）
   c. 检查结果（UI变化/网络请求/控制台）
   d. 验证期望结果
4. 记录问题（如有）
5. 截图
6. 报告：详细的PASS/FAIL信息

改进：
- ✅ 测试实际用户工作流
- ✅ 发现真实的用户阻碍问题
- ✅ 提供可操作的修复建议
```

### 测试深度比例

**分配**:
- 页面加载测试：20%
- 用户交互测试：60%
- 工作流完成测试：20%

**为什么60%用于用户交互**:
- 用户主要通过交互与应用程序交互
- 加载成功不等于功能可用
- 交互测试最能发现真实问题

---

## 相关经验文档

- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React组件测试常见问题
- [调试技能](./debugging-skills.md) - 测试失败后的调试方法
- [API设计模式 - 错误处理](./api-design-patterns.md#错误处理) - API测试方法
