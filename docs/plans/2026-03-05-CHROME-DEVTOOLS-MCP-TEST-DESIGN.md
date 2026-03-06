# Event2Table Chrome DevTools MCP E2E测试方案设计

**设计日期**: 2026-03-05
**设计范围**: 12个未测试页面的完整E2E测试方案
**测试工具**: Chrome DevTools MCP (强制要求)
**设计目标**: 将测试覆盖率从10.9%提升到30%+

---

## 设计概述

### 背景

Event2Table项目当前有**46个页面**，但仅测试了**11个核心页面**（覆盖率10.9%）。经过深度分析，发现：

- **需要Chrome DevTools MCP测试**: 12个页面（26%）- 复杂交互、核心业务
- **简单测试即可**: 18个页面（39%）- 基础交互、API测试
- **不需要测试**: 16个页面（35%）- 静态文档、未完成功能

本设计专注于**真正需要Chrome DevTools MCP测试的12个页面**，提供完整的测试方案。

---

### 设计原则

1. **铁则**: Chrome DevTools MCP优先（禁止切换到Playwright）
2. **深度测试**: 专注用户交互验证，非仅页面加载
3. **问题发现**: 发现功能障碍和用户体验问题
4. **可操作性**: 提供具体的修复建议
5. **渐进式**: 分阶段实施，优先解决高风险问题

---

## 第一部分：测试架构

### 测试引擎层

**核心工具**: Chrome DevTools MCP

**主要API**:
```javascript
// 页面导航
mcp__chrome_devtools__navigate_page({ type: "url", url: page_url })

// DOM分析
mcp__chrome_devtools__take_snapshot()

// 交互操作
mcp__chrome_devtools__click({ uid: "element-uid" })
mcp__chrome_devtools__fill({ uid: "input-uid", value: "text" })
mcp__chrome_devtools__drag({ from_uid: "draggable", to_uid: "dropzone" })

// 监控
mcp__chrome_devtools__list_console_messages({ types: ["error", "warn"] })
mcp__chrome_devtools__list_network_requests({ resourceTypes: ["xhr", "fetch"] })

// 性能测量
mcp__chrome_devtools__evaluate_script({ function: "()" })
```

### 测试流程设计

**Phase 1: 页面加载验证** (20%)
- 导航到页面 → 等待加载完成
- 获取DOM快照 → 验证关键元素存在
- 检查控制台错误 → 无JavaScript错误
- 测量加载性能 → <3秒

**Phase 2: 用户交互测试** (60%) ⭐ **核心重点**
- 识别交互元素 → 按钮、表单、可拖拽元素
- 验证元素可见性 → 在视口内、可交互
- 执行交互操作 → 点击、填写、拖拽
- 等待响应 → 验证状态变化
- 检查错误 → 控制台、网络

**Phase 3: 工作流完成验证** (20%)
- 执行完整用户工作流（系列交互）
- 验证每个步骤的状态变化
- 检查API调用和响应
- 验证最终结果

### 数据管理层

**测试数据隔离**:
- 测试GID范围: 90000000-99999999
- 生产GID保护: 10000147 (STAR001) - 严禁测试
- 测试数据库: `data/test_database.db` (独立环境)

**测试数据清理**:
```python
# 清理测试数据
def cleanup_test_data():
    delete_games(gid_range=(90000000, 99999999))
    if FLASK_ENV == "testing":
        init_test_db()
```

### 报告生成层

**报告内容**:
1. 执行摘要（测试统计、通过率）
2. 详细测试结果（每项测试结果）
3. 问题清单（P0-P3分级）
4. 修复建议（代码位置、修复步骤）
5. 截图证据（交互前后对比）
6. 性能数据（加载时间、API响应）

**报告格式**: Markdown
**保存位置**: `docs/testing/reports/YYYY-MM-DD/`

---

## 第二部分：P0核心页面测试用例

### 页面1: Field Builder - `/field-builder`

**功能**: 可视化HQL字段配置，拖拽排序、参数配置、实时预览

**测试时间**: 30分钟

**测试用例**:

1. **页面加载** (5分钟)
   - 导航到Field Builder
   - 验证字段列表显示
   - 验证拖拽功能可用

2. **拖拽测试** (10分钟)
   - 拖拽字段重新排序
   - 验证顺序立即更新
   - 测试拖拽边界情况

3. **参数配置** (10分钟)
   - 打开字段配置模态框
   - 测试字段类型选择
   - 测试参数填写和保存
   - 验证参数生效

4. **HQL预览** (5分钟)
   - 验证HQL预览显示
   - 测试实时更新
   - 验证HQL语法

**Chrome DevTools MCP关键测试**:
```javascript
// 拖拽测试
drag({ from_uid: "field-1", to_uid: "field-2" })
take_snapshot() → 验证顺序变化
evaluate_script("document.querySelector('.field-1').style.order")

// 参数配置
click({ uid: "field-config-button" })
wait_for_element(".config-modal")
fill({ uid: "field-type", value: "param" })
click({ uid: "save-config" })
```

---

### 页面2: Flow Builder - `/flow-builder`

**功能**: 可视化HQL流程编辑器，节点拖拽、连接配置

**测试时间**: 45分钟

**测试用例**:

1. **节点添加** (10分钟)
   - 添加Table节点
   - 添加Join节点
   - 添加Filter节点
   - 验证节点显示在画布

2. **节点拖拽** (15分钟)
   - 拖拽节点到不同位置
   - 验证节点自由移动
   - 测试节点边界限制

3. **节点连接** (15分钟)
   - 从输出端口拖拽连接线
   - 连接到输入端口
   - 验证连接线显示
   - 测试删除连接

4. **流程预览** (5分钟)
   - 点击预览按钮
   - 验证生成的HQL流程
   - 测试保存功能

**Chrome DevTools MCP关键测试**:
```javascript
// 节点拖拽
drag({ from_uid: "table-node", to_uid: { x: 300, y: 200 } })
evaluate_script("document.querySelector('.flow-node').getBoundingClientRect()")

// 节点连接
drag({ from_uid: "node-1-output", to_uid: "node-2-input" })
wait_for_element(".connection-line")
evaluate_script("document.querySelectorAll('.connection-line').length")
```

---

### 页面3: Import Events - `/import-events`

**功能**: Excel批量导入事件，上传、预览、字段匹配

**测试时间**: 40分钟

**测试用例**:

1. **文件上传** (10分钟)
   - 选择Excel文件
   - 验证文件上传进度
   - 测试文件格式验证

2. **预览和匹配** (15分钟)
   - 验证预览表格显示
   - 测试字段映射功能
   - 测试必填字段标记

3. **数据验证** (10分钟)
   - 测试验证按钮
   - 验证错误高亮
   - 测试错误修正

4. **批量导入** (5分钟)
   - 测试确认导入按钮
   - 验证进度条
   - 测试成功提示

**Chrome DevTools MCP关键测试**:
```javascript
// 文件上传
fill({ uid: "file-input", value: "/path/to/test.xlsx" })
wait_for_element(".preview-table")
take_screenshot("preview.png")

// 进度监控
click({ uid: "import-button" })
evaluate_script("document.querySelector('.progress-bar').style.width")
wait_for_text("导入成功", timeout=30000)
```

---

### 页面4: Generate HQL - `/hql-generate`

**功能**: 选择事件和参数，配置生成选项，生成HQL

**测试时间**: 35分钟

**测试用例**:

1. **事件选择** (10分钟)
   - 测试游戏选择
   - 验证事件列表
   - 测试多选事件

2. **参数配置** (10分钟)
   - 从左侧添加参数
   - 验证参数显示
   - 测试参数排序
   - 测试删除参数

3. **生成配置** (10分钟)
   - 选择生成模式
   - 配置WHERE条件
   - 配置分区条件

4. **HQL生成** (5分钟)
   - 点击生成按钮
   - 验证HQL预览
   - 测试复制功能
   - 测试下载功能

**Chrome DevTools MCP关键测试**:
```javascript
// 事件多选
click({ uid: "event-checkbox-1" })
click({ uid: "event-checkbox-2" })
evaluate_script("document.querySelectorAll('.event-checkbox:checked').length")

// HQL生成
click({ uid: "generate-button" })
wait_for_element(".hql-preview")
evaluate_script("document.querySelector('.hql-preview code').textContent")
```

---

## 第三部分：P1重要页面测试用例

### 页面5: Alter SQL Builder - `/alter-sql-builder`

**功能**: SQL编辑器，语法高亮、验证、预览

**测试时间**: 25分钟

**测试用例**:

1. **SQL编辑** (10分钟)
   - 测试代码输入
   - 验证语法高亮
   - 测试自动缩进
   - 测试撤销/重做

2. **语法验证** (10分钟)
   - 测试验证按钮
   - 验证错误标记
   - 检查错误提示

3. **执行预览** (5分钟)
   - 测试预览按钮
   - 验证结果展示
   - 测试限制行数

---

### 页面6: Generate Result - `/generate-result`

**功能**: 显示HQL生成结果，支持复制、下载

**测试时间**: 20分钟

**测试用例**:

1. **结果展示** (5分钟)
   - 验证HQL显示
   - 测试语法高亮
   - 测试格式化

2. **操作功能** (10分钟)
   - 测试复制按钮
   - 测试下载按钮
   - 测试编辑功能

3. **历史记录** (5分钟)
   - 测试历史列表
   - 验证点击重载结果

**Chrome DevTools MCP关键测试**:
```javascript
// 复制测试
click({ uid: "copy-button" })
evaluate_script("navigator.clipboard.readText()")

// 下载测试
click({ uid: "download-button" })
list_network_requests() → 验证文件下载
```

---

## 第四部分：实施计划

### Phase 1: P0核心功能 (第1周)

**目标**: 测试4个未测试的P0页面

**执行顺序**:
1. **Generate HQL** (35分钟)
   - 独立功能，风险低
   - 为Field Builder提供基础

2. **Field Builder** (30分钟)
   - 依赖Generate HQL
   - 复杂度高，重点测试

3. **Flow Builder** (45分钟)
   - 可视化编辑器
   - 需要深度测试

4. **Import Events** (40分钟)
   - 独立功能
   - 批量操作关键

**总时间**: 150分钟 (2.5小时)

**验收标准**:
- ✅ 所有P0页面10项测试全部通过
- ✅ 拖拽、连接、上传功能正常
- ✅ 无P0级阻塞性问题

---

### Phase 2: P1重要功能 (第2周)

**目标**: 测试2个未测试的P1页面

**执行顺序**:
1. **Alter SQL Builder** (25分钟)
2. **Generate Result** (20分钟)

**总时间**: 45分钟

**验收标准**:
- ✅ SQL编辑器功能正常
- ✅ 语法验证准确
- ✅ 无P1级功能问题

---

### Phase 3: 回归和优化 (第3周)

**目标**: 确保测试稳定性，建立测试基线

**工作内容**:
1. **回归测试**: 重新测试所有12个页面
2. **性能优化**: 优化测试执行速度
3. **文档完善**: 更新测试用例文档

---

## 第五部分：测试脚本和工具

### Chrome DevTools MCP最佳实践

**页面加载**:
```javascript
// ✅ 正确: 等待网络空闲
navigate_page({ url: page_url })
wait_for_load_state("networkidle")

// ❌ 错误: 不等待加载
navigate_page({ url: page_url })
take_snapshot()  // 可能还在加载
```

**元素交互**:
```javascript
// ✅ 正确: 验证可见性
take_snapshot()
evaluate_script("el => el.offsetParent !== null")
click({ uid: "button" })

// ❌ 错误: 直接点击
click({ uid: "button" })
```

**拖拽操作**:
```javascript
// ✅ 正确: 验证结果
drag({ from_uid: "draggable", to_uid: "dropzone" })
take_snapshot()
evaluate_script("document.querySelector('.dropzone').children.length")

// ❌ 错误: 不验证
drag({ from_uid: "draggable", to_uid: "dropzone" })
```

### 测试模板

**模板1: 页面加载验证**
```javascript
async function testPageLoad(baseUrl, pageUrl) {
  await navigate_page({ url: `${baseUrl}${pageUrl}` });
  await wait_for_load_state("networkidle");
  const snapshot = await take_snapshot();
  const errors = await list_console_messages({ types: ["error"] });
  const perf = await evaluate_script("() => performance.timing.loadEventEnd - performance.timing.navigationStart");

  return {
    pageLoaded: true,
    hasRequiredElements: snapshot.elements.length > 0,
    errorCount: errors.length,
    loadTime: perf
  };
}
```

**模板2: 拖拽测试**
```javascript
async function testDragDrop(draggableUid, dropzoneUid) {
  const before = await evaluate_script(`(uid) => {
    const el = document.querySelector(`[data-uid="${uid}"]`);
    const rect = el.getBoundingClientRect();
    return { x: rect.x, y: rect.y };
  }`, { args: [{ uid: draggableUid }] });

  await drag({ from_uid: draggableUid, to_uid: dropzoneUid });
  await new Promise(resolve => setTimeout(resolve, 300));

  const after = await evaluate_script(`(uid) => {
    const el = document.querySelector(`[data-uid="${uid}"]`);
    const rect = el.getBoundingClientRect();
    return { x: rect.x, y: rect.y };
  }`, { args: [{ uid: draggableUid }] });

  return {
    dragSuccess: before.x !== after.x || before.y !== after.y,
    newPosition: after
  };
}
```

---

## 第六部分：文档和知识库

### 主文档结构

**主文档**: `docs/testing/e2e-testing-guide.md`

**章节**:
1. **概述** - Chrome DevTools MCP E2E测试哲学
2. **快速开始** - 环境搭建和首个测试
3. **测试方法论** - 标准测试流程
4. **工具参考** - Chrome DevTools MCP完整API
5. **测试用例库** - 12页面的详细用例
6. **最佳实践** - 常见模式和反模式
7. **故障排查** - 问题诊断指南

### 12页面测试用例文档

**位置**: `docs/testing/test-cases/`

**文件命名**: `[PAGE-NAME]-test-cases.md`

**包含内容**:
- 页面信息（路由、功能、复杂度、测试时间）
- 测试前准备（环境、数据、清理）
- 测试用例清单（10项基础测试 + 复杂交互测试）
- 故障排查（常见问题、解决方案）
- 截图证据要求

### 知识库FAQ

**Q1: Chrome DevTools MCP连接失败？**
- 检查Chrome调试端口 (9222)
- 验证VSCode MCP配置
- 重启VSCode

**Q2: 拖拽功能不工作？**
- 检查元素定位（position、z-index）
- 测量元素尺寸
- 验证目标区域大小

**Q3: 如何验证API调用？**
- 使用list_network_requests()
- 使用curl预验证
- 检查控制台错误

**Q4: 元素找不到？**
- 使用take_snapshot()验证存在
- 检查元素选择器
- 检查是否动态加载

---

## 第七部分：成功指标

### 量化指标

**测试覆盖率**:
- P0页面: 0% → 100%
- P1页面: 0% → 100%
- 整体覆盖率: 10.9% → 30%+

**质量指标**:
- 所有测试可重复执行
- 测试报告详细准确
- 问题定位精准
- 修复建议可操作

### 时间估算

**P0测试** (第1周): 150分钟 (2.5小时)
**P1测试** (第2周): 45分钟
**回归测试** (第3周): 480分钟 (8小时)

**总计**: 约11小时实际测试 + 文档编写

---

## 总结

### 设计亮点

1. **聚焦真正需要的测试** - 只测试26%的页面（12个），而非所有页面
2. **深度优于广度** - 专注用户交互验证，而非页面加载检查
3. **实用主义** - 提供具体的修复建议，而非仅报告问题
4. **渐进式实施** - 分3个阶段，先P0后P1
5. **工具约束明确** - 强制使用Chrome DevTools MCP，不切换到Playwright

### 下一步行动

1. ✅ 审阅本设计文档
2. ⚠️ 确认设计范围和优先级
3. 📝 生成测试用例文档
4. 🧪 执行P0页面测试
5. 📊 生成测试报告
6. 🔧 修复发现的问题

---

**设计版本**: 1.0
**设计日期**: 2026-03-05
**设计师**: Claude Code (E2E Testing System)
**状态**: 待审批
