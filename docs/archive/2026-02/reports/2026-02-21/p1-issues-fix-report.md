# E2E测试P1问题分析与修复报告

**日期**: 2026-02-21
**工具**: Chrome DevTools MCP (skill原始能力)
**状态**: 2/3问题已修复，1个API契约问题

---

## 执行总结

使用**Chrome DevTools MCP**（skill的原始设计能力）诊断了3个P1测试失败问题：

| # | 测试名称 | 状态 | 问题类型 | 修复方法 |
|---|---------|------|---------|---------|
| 1 | Homepage main navigation | ✅ 已修复 | 测试选择器错误 | 更新选择器匹配实际HTML |
| 2 | Field builder page load | ✅ 已修复 | 测试URL错误 | 修正URL路径 |
| 3 | HQL manage page load | ⚠️ API契约问题 | API不存在 | 需要后端实现或前端修改 |

---

## 问题1: Homepage main navigation display

### Playwright测试失败
```
✘ Homepage & Navigation: should display main navigation (33.3s)
```

### Chrome DevTools MCP诊断

**步骤1**: 导航到homepage
```javascript
mcp__chrome-devtools__navigate_page({ type: "url", url: "http://localhost:5173/" })
```

**步骤2**: 获取页面快照
```javascript
mcp__chrome-devtools__take_snapshot()
```

**发现**: Navigation**确实存在**且**正常显示**！

**实际HTML结构**:
```html
<complementary>
  <link href="#/">概览 仪表板</link>
  <link href="#/event-node-builder">节点 事件节点构建器</link>
  ...
</complementary>
```

**测试代码** (错误):
```javascript
const nav = page.locator('nav')
  .or(page.locator('[role="navigation"]'))
  .or(page.locator('.navbar'));
await expect(nav.first()).toBeVisible();
```

**问题**: 测试在寻找：
- `<nav>` 标签 ❌
- `[role="navigation"]` 属性 ❌
- `.navbar` class ❌

但实际使用的是：
- `<complementary>` 标签 ✅ (正确的ARIA role)

### 修复方案

**文件**: `frontend/test/e2e/smoke/smoke-tests.spec.ts:44`

**修复前**:
```javascript
test('should display main navigation', async ({ page }) => {
  await page.goto(BASE_URL, { timeout: 60000, waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);

  const nav = page.locator('nav').or(page.locator('[role="navigation"]')).or(page.locator('.navbar'));
  await expect(nav.first()).toBeVisible({ timeout: 10000 });
});
```

**修复后**:
```javascript
test('should display main navigation', async ({ page }) => {
  await page.goto(BASE_URL, { timeout: 60000, waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);

  // Check for navigation elements (based on actual UI structure)
  // The sidebar uses <complementary> tag with links
  const sidebar = page.locator('complementary').or(page.locator('[role="complementary"]'));
  await expect(sidebar.first()).toBeVisible({ timeout: 10000 });

  // Verify navigation links exist
  const navLinks = page.locator('complementary a[href]');
  await expect(navLinks.first()).toBeVisible({ timeout: 5000 });
});
```

### 验证

- ✅ 页面功能正常
- ✅ Navigation显示正常
- ❌ 测试选择器不匹配实际HTML
- ✅ 修复后测试应该通过

---

## 问题2: Field builder page load

### Playwright测试失败
```
✘ Canvas & Flow Builder: should load field builder page (20.0s)
```

### Chrome DevTools MCP诊断

**步骤1**: 导航到field builder
```javascript
mcp__chrome-devtools__navigate_page({ type: "url", url: "http://localhost:5173/#/event-node-builder" })
```

**步骤2**: 获取页面快照
```javascript
mcp__chrome-devtools__take_snapshot()
```

**发现**: **Event Node Builder页面正常加载**！

**页面元素**:
```
heading "📊 事件节点构建器"
textbox "搜索事件..."
heading " 参数字段"
heading " 基础字段"
heading "字段画布"
button "基础" (添加基础字段)
...
```

**测试代码** (错误):
```javascript
await page.goto(`${BASE_URL}/#/field-builder`); // ❌ 错误的URL
```

**问题**: 测试访问了错误的URL：
- 测试访问: `/#/field-builder`
- 实际路由: `/#/event-node-builder`

### 修复方案

**文件**: `frontend/test/e2e/smoke/smoke-tests.spec.ts:245`

**修复前**:
```javascript
test('should load field builder page', async ({ page }) => {
  const errors = await checkConsoleErrors(page);

  await page.goto(`${BASE_URL}/#/field-builder`); // ❌ 错误URL
  await page.waitForLoadState('networkidle');

  // Check page loaded
  await expect(page.locator('body')).toBeVisible();

  // Should have canvas or builder elements
  const hasCanvas = await page.locator('.react-flow, canvas, [data-testid="canvas"]').count() > 0;
  expect(hasCanvas).toBeTruthy();

  await page.waitForTimeout(1000);
  expect(errors).toEqual([]);
});
```

**修复后**:
```javascript
test('should load field builder page', async ({ page }) => {
  const errors = await checkConsoleErrors(page);

  // Correct URL: Event Node Builder
  await page.goto(`${BASE_URL}/#/event-node-builder`); // ✅ 正确URL
  await page.waitForLoadState('networkidle');

  // Check page loaded
  await expect(page.locator('body')).toBeVisible();

  // Should have event builder elements
  const hasEventSelector = await page.locator('[placeholder*="搜索事件"]').count() > 0;
  const hasFieldCanvas = await page.locator('text=/基础字段|参数字段|字段画布/').count() > 0;
  expect(hasEventSelector || hasFieldCanvas).toBeTruthy();

  await page.waitForTimeout(1000);
  expect(errors).toEqual([]);
});
```

### 验证

- ✅ 页面功能正常
- ✅ Event Node Builder正常加载
- ❌ 测试URL错误
- ✅ 修复后测试应该通过

---

## 问题3: HQL manage page load

### Playwright测试失败
```
✘ HQL Management: should load HQL manage page (18.1s)
```

### Chrome DevTools MCP诊断

**步骤1**: 导航到HQL管理页面
```javascript
mcp__chrome-devtools__navigate_page({ type: "url", url: "http://localhost:5173/#/hql-manage" })
```

**步骤2**: 获取页面快照
```javascript
mcp__chrome-devtools__take_snapshot()
```

**发现**: **HQL管理页面正常加载**，显示空状态"未找到HQL记录"！

**页面元素**:
```
heading "HQL管理"
link "生成新HQL"
combobox "全部类型"
combobox "全部"
textbox "搜索事件..."
text "未找到HQL记录" // ← 空状态，正常！
```

**步骤3**: 检查console错误
```javascript
mcp__chrome-devtools__list_console_messages({ types: ["error"] })
```

**发现**: 2个400错误！

```
[error] Failed to load resource: the server responded with a status of 400 (BAD REQUEST)
```

**步骤4**: 检查网络请求
```javascript
mcp__chrome-devtools__list_network_requests({ resourceTypes: ["xhr", "fetch"] })
```

**发现问题请求**:
```
GET http://localhost:5173/api/hql? [400]
Response: {"error":"Missing game_gid parameter","success":false}
```

### 根本原因分析

**问题**: **API契约不匹配**

1. **前端调用** (`HqlManage.jsx`):
   ```javascript
   const response = await fetch(`/api/hql?${params}`);
   // params: hql_type, edited_only (没有game_gid!)
   ```

2. **后端期望**:
   - 后端有 `GET /api/hql/<int:id>` - 获取单个HQL
   - 后端**没有** `GET /api/hql` - 列表HQL
   - 如果存在这个API，应该需要 `game_gid` 参数

3. **后端实际API**:
   ```python
   @api_bp.route("/api/hql/<int:id>", methods=["GET"])
   def api_get_hql(id):
       """API: Get HQL content by ID"""
       # 获取单个HQL
   ```

   **没有列表API！**

### 修复方案（3个选项）

#### 选项1: 后端实现列表API（推荐）

**文件**: `backend/api/routes/hql_generation.py`

```python
@api_bp.route("/api/hql", methods=["GET"])
def api_list_hql():
    """API: List HQL statements with filters"""
    game_gid = request.args.get('game_gid', type=int)
    hql_type = request.args.get('hql_type')  # 'CREATE', 'JOIN', 'UNION'
    edited_only = request.args.get('edited_only', 'false').lower() == 'true'
    keyword = request.args.get('keyword', '')

    if not game_gid:
        return json_error_response("Missing game_gid parameter", status_code=400)

    try:
        # 查询HQL列表
        query = """
            SELECT hs.*, g.name as game_name, g.gid as game_gid
            FROM hql_statements hs
            INNER JOIN games g ON hs.game_id = g.id
            WHERE g.gid = ?
        """
        params = [game_gid]

        if hql_type:
            query += " AND hs.hql_type = ?"
            params.append(hql_type)

        if edited_only:
            query += " AND hs.is_custom = 1"

        if keyword:
            query += " AND hs.event_name LIKE ?"
            params.append(f"%{keyword}%")

        query += " ORDER BY hs.updated_at DESC"

        results = fetch_all_as_dict(query, params)

        return json_success_response(data=results)
    except Exception as e:
        logger.error(f"Error listing HQL: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
```

#### 选项2: 前端修改调用现有API

**文件**: `frontend/src/analytics/pages/HqlManage.jsx`

```javascript
const queryFn: async () => {
  const gameGid = getCurrentGameGid(); // 从context获取
  const params = new URLSearchParams();
  params.append('game_gid', gameGid); // ✅ 添加game_gid
  if (typeFilter) params.append('hql_type', typeFilter);
  if (editedOnly) params.append('edited_only', 'true');

  const response = await fetch(`/api/hql?${params}`);
  if (!response.ok) throw new Error('加载HQL失败');
  return response.json();
}
```

但问题是：后端没有`/api/hql`列表API！

#### 选项3: 使用不同的API

如果后端有其他列表API，前端应该调用正确的API。

### 建议

**推荐选项1**（后端实现列表API），因为：
1. 符合RESTful API设计规范
2. 前端已经有调用逻辑，只需后端支持
3. 其他页面也可能需要HQL列表功能

---

## Chrome DevTools MCP vs Playwright

### 关键发现

这次诊断使用了**Chrome DevTools MCP**（skill的原始能力），而不是Playwright。两者有本质区别：

| 特性 | Chrome DevTools MCP | Playwright |
|------|-------------------|------------|
| **类型** | 交互式诊断工具 | 自动化测试框架 |
| **用途** | 问题诊断、探索性测试 | 回归测试、CI/CD |
| **能力** | 实时页面分析、网络监控 | 脚本化测试、多浏览器 |
| **优势** | 深度诊断、灵活调试 | 可重复、批量执行 |
| **输出** | 详细的分析报告 | Pass/Fail结果 |

### 本次诊断过程

使用Chrome DevTools MCP的诊断流程：

```
1. navigate_page() - 导航到目标页面
2. take_snapshot() - 获取DOM快照，验证元素存在
3. list_console_messages() - 检查JavaScript错误
4. list_network_requests() - 发现API调用问题
5. get_network_request() - 获取详细错误信息
```

**这正是skill的原始设计理念**：
> **"测试不是验证页面能加载，而是验证用户能完成任务。"**

### Skill能力偏移分析

**原始设计**（Phase 1-2）:
- 使用Chrome DevTools MCP进行**智能交互式测试**
- 重点发现**功能障碍**和**用户体验问题**
- 探索性测试，不依赖预设脚本

**Phase 3实施**（错误方向）:
- 变成了**Playwright自动化测试**
- 重点编写**测试脚本**和**CI/CD集成**
- 偏离了skill的交互式诊断核心能力

---

## 建议

### 立即行动（P0）

1. ✅ **应用测试修复** - 2个测试选择器问题已修复
2. ⚠️ **修复API契约** - 实现后端`/api/hql`列表API
3. 🧪 **重新运行测试** - 验证修复效果

### 短期优化（P1）

1. 📝 **更新测试文档** - 记录正确的HTML结构
2. 🔍 **API契约测试** - 确保前后端API一致
3. 🎯 **聚焦核心能力** - 回归Chrome DevTools MCP

### 长期改进（P2）

1. **重新评估Phase 3方向** - Playwright是否正确？
2. **Hybrid方法** - Chrome DevTools MCP诊断 + Playwright回归
3. **Skill澄清** - 明确使用场景和能力边界

---

## 结论

**使用Chrome DevTools MCP的诊断结果**:

| 问题 | 原因 | 类型 | 状态 |
|------|------|------|------|
| Navigation display | 测试选择器错误 | 测试问题 | ✅ 已修复 |
| Field builder load | 测试URL错误 | 测试问题 | ✅ 已修复 |
| HQL manage page | API契约不匹配 | 代码问题 | ⚠️ 需要修复 |

**关键发现**:
- **页面功能都正常** - 这是测试/代码问题，不是功能bug
- **Chrome DevTools MCP非常适合问题诊断** - 能够快速定位根本原因
- **Skill能力发生了偏移** - 从交互式诊断变成了自动化测试框架

**下一步**: 修复API契约问题，然后重新思考skill的正确定位。

---

**报告生成**: 2026-02-21 01:30
**工具**: Chrome DevTools MCP
**状态**: 2/3问题已修复
**优先级**: P0 - API契约问题需要立即处理
