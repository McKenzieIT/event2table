# E2E回归测试 - 快速参考指南

## 📋 任务完成状态

✅ **任务3/5**: 添加E2E回归测试
✅ **状态**: 已完成
✅ **日期**: 2026-03-13

---

## 🎯 交付物

### 1. 测试文件
**路径**: `/Users/mckenzie/Documents/event2table/frontend/test/e2e/chrome-mcp-compatibility.spec.ts`
**大小**: 28.6 KB
**行数**: ~850行
**测试数量**: 11个测试

### 2. 文档
- **总结报告**: `E2E-REGRESSION-TEST-SUMMARY.md`
- **验证报告**: `E2E-TEST-VERIFICATION.md`
- **快速参考**: 本文件

---

## 🚀 快速开始

### 运行所有测试
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npx playwright test chrome-mcp-compatibility.spec.ts
```

### 运行特定测试
```bash
# 测试1: 事件选择和参数加载
npx playwright test chrome-mcp-compatibility.spec.ts -g "1. Event Selection"

# 测试2: 批量添加字段
npx playwright test chrome-mcp-compatibility.spec.ts -g "2. Batch Add"

# 测试3: 节点配置模态框
npx playwright test chrome-mcp-compatibility.spec.ts -g "3. Node Configuration"

# 测试4: HQL预览生成
npx playwright test chrome-mcp-compatibility.spec.ts -g "4. HQL Preview"

# 测试5: 标识符清理
npx playwright test chrome-mcp-compatibility.spec.ts -g "5. Identifier Cleanup"

# 测试6: 性能指标
npx playwright test chrome-mcp-compatibility.spec.ts -g "6. Performance"

# 测试7: 错误处理
npx playwright test chrome-mcp-compatibility.spec.ts -g "7. Error Handling"

# 测试8: 可访问性
npx playwright test chrome-mcp-compatibility.spec.ts -g "8. Accessibility"

# 回归预防测试
npx playwright test chrome-mcp-compatibility.spec.ts -g "PREVENT"
```

### UI模式运行
```bash
npx playwright test chrome-mcp-compatibility.spec.ts --ui
```

### 调试模式运行
```bash
npx playwright test chrome-mcp-compatibility.spec.ts --debug
```

---

## 📊 测试场景详解

### 场景1: 事件选择和参数加载
**目的**: 验证选择事件后正确加载参数
**步骤**:
1. 导航到Event Node Builder
2. 选择一个事件
3. 验证参数列表加载
4. 检查无控制台错误

**预期结果**:
- ✅ 参数列表显示
- ✅ 无控制台错误
- ✅ 截图保存

### 场景2: 批量添加字段
**目的**: 测试批量添加字段到画布
**步骤**:
1. 导航并选择事件
2. 选择多个基础字段
3. 点击"添加选中"按钮
4. 验证字段在画布中显示

**预期结果**:
- ✅ 字段添加到画布
- ✅ 字段顺序保持
- ✅ 无控制台错误

### 场景3: 节点配置模态框 (Chrome MCP API)
**目的**: 测试Chrome MCP API模拟
**步骤**:
1. 点击配置中的字段
2. 打开配置模态框
3. 填写表单字段
4. 提交表单
5. 验证更新

**预期结果**:
- ✅ 模态框打开
- ✅ 表单可填写
- ✅ 提交成功
- ✅ 字段更新

### 场景4: HQL预览生成
**目的**: 验证HQL生成功能
**步骤**:
1. 添加字段到画布
2. 点击预览按钮
3. 等待HQL生成
4. 验证HQL语法

**预期结果**:
- ✅ HQL非空
- ✅ 包含SELECT
- ✅ 包含FROM
- ✅ SQL语法正确

### 场景5: 标识符清理
**目的**: 测试标识符自动清理
**步骤**:
1. 检查字段名称
2. 测试无效字符输入
3. 验证自动清理
4. 检查SQL标准符合性

**预期结果**:
- ✅ 特殊字符移除
- ✅ 空格替换为下划线
- ✅ 符合SQL命名标准

### 场景6: 性能指标
**目的**: 监控性能指标
**步骤**:
1. 测量页面加载时间
2. 测量事件选择时间
3. 测量HQL生成时间

**预期结果**:
- ✅ 页面加载 < 10秒
- ✅ 事件选择 < 5秒
- ✅ HQL生成 < 5秒

### 场景7: 错误处理
**目的**: 测试错误处理和用户反馈
**步骤**:
1. 使用无效游戏GID导航
2. 验证错误消息显示
3. 检查友好错误提示
4. 验证无崩溃

**预期结果**:
- ✅ 错误消息友好
- ✅ 无TypeError
- ✅ 页面恢复

### 场景8: 可访问性
**目的**: 测试键盘导航和ARIA
**步骤**:
1. 测试Tab导航
2. 验证焦点顺序
3. 检查ARIA标签
4. 验证可访问性

**预期结果**:
- ✅ 键盘可导航
- ✅ ARIA标签存在
- ✅ 焦点管理正确

---

## 🛡️ 回归预防测试

### PREVENT-001: React Hooks违规
**目的**: 防止React Hooks顺序违规
**检测**: Hook顺序变化错误
**预期**: 无Hook违规

### PREVENT-002: 内存泄漏
**目的**: 防止事件监听器内存泄漏
**检测**: 多次导航无挂起
**预期**: 无内存泄漏

### PREVENT-003: API错误处理
**目的**: 验证API错误优雅降级
**检测**: 模拟API失败
**预期**: 优雅降级

---

## 📈 测试输出

### 截图位置
```
frontend/test-output/e2e/screenshots/
├── event-selection-loaded.png
├── batch-fields-added.png
├── config-modal-open.png
├── config-modal-submitted.png
├── hql-preview-generated.png
├── identifier-cleanup.png
└── error-handling.png
```

### 测试结果
```
frontend/test-results/
└── chrome-mcp-compatibility-*/
    └── test-results.json
```

### HTML报告
```
frontend/playwright-report/
└── index.html
```

### 查看HTML报告
```bash
npx playwright show-report
```

---

## 🔍 故障排除

### 测试超时
**问题**: 测试超时失败
**解决**:
```typescript
// 增加测试超时
test.setTimeout(60000); // 60秒

// 或在命令行
npx playwright test chrome-mcp-compatibility.spec.ts --timeout=60000
```

### 找不到元素
**问题**: 元素定位器失败
**解决**:
```typescript
// 使用更灵活的选择器
await page.locator('button:has-text("提交")').click();

// 或等待元素
await expect(page.locator('.modal')).toBeVisible();
```

### 后端未运行
**问题**: 后端服务未启动
**解决**:
```bash
# 启动后端
cd /Users/mckenzie/Documents/event2table
source backend/venv/bin/activate
python web_app.py
```

### 数据库未初始化
**问题**: 测试数据不存在
**解决**:
```bash
# 初始化数据库
python scripts/setup/init_db.py
```

---

## 📝 测试最佳实践

### 1. 测试隔离
每个测试都是独立的，不依赖其他测试

### 2. 清晰的断言
使用明确的期望和断言消息

### 3. 自动清理
使用`beforeEach`和`afterEach`钩子

### 4. 错误跟踪
自动捕获和报告错误

### 5. 性能监控
自动测量性能指标

---

## 🎯 CI/CD集成

### GitHub Actions示例
```yaml
name: E2E Tests - Chrome MCP Compatibility

on:
  push:
    paths:
      - 'frontend/src/**'
      - 'frontend/test/e2e/chrome-mcp-compatibility.spec.ts'
  pull_request:
    paths:
      - 'frontend/src/**'
      - 'frontend/test/e2e/chrome-mcp-compatibility.spec.ts'

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci
        working-directory: ./frontend

      - name: Install Playwright
        run: npx playwright install --with-deps
        working-directory: ./frontend

      - name: Run Chrome MCP Compatibility Tests
        run: npx playwright test chrome-mcp-compatibility.spec.ts
        working-directory: ./frontend

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: chrome-mcp-test-results
          path: frontend/test-results/

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: chrome-mcp-screenshots
          path: frontend/test-output/e2e/screenshots/
```

---

## 📞 相关文档

### 项目文档
- **开发规范**: `/Users/mckenzie/Documents/event2table/CLAUDE.md`
- **测试指南**: `docs/lessons-learned/testing-guide.md`
- **E2E测试指南**: `docs/testing/e2e-testing-guide.md`

### Playwright文档
- **官方文档**: https://playwright.dev/
- **API参考**: https://playwright.dev/docs/api/class-playwright
- **最佳实践**: https://playwright.dev/docs/best-practices

---

## ✅ 验证清单

### 文件验证
- [x] 测试文件创建成功
- [x] 语法验证通过
- [x] 所有测试可被Playwright识别
- [x] 文档完整

### 功能验证
- [x] 8个主要测试场景
- [x] 3个回归预防测试
- [x] 性能监控
- [x] 错误检测
- [x] 可访问性测试

### 运行验证
- [x] 可独立运行
- [x] 可作为CI/CD一部分
- [x] 支持UI模式
- [x] 支持调试模式

---

## 🎓 学习资源

### Playwright测试
- [Playwright入门](https://playwright.dev/docs/intro)
- [选择器指南](https://playwright.dev/docs/selectors)
- [断言指南](https://playwright.dev/docs/test-assertions)
- [最佳实践](https://playwright.dev/docs/best-practices)

### Chrome MCP
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [MCP规范](https://modelcontextprotocol.io/)

---

**创建日期**: 2026-03-13
**版本**: 1.0.0
**状态**: ✅ 完成
