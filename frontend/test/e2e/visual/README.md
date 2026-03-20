# Visual Regression Tests

视觉回归测试套件，用于验证UI优化后的页面是否出现视觉回归。

## 测试页面

| 页面 | 路由 | 涉及CSS文件 |
|------|------|-------------|
| Dashboard | `/` | Dashboard.css |
| Canvas | `/canvas?game_gid=10000147` | CanvasPage.css, Toolbar.css, CustomNode.css, CanvasFlow.css, EventNode.css, JoinNode.css, UnionAllNode.css, OutputNode.css |
| EventNodeBuilder | `/event-node-builder?game_gid=10000147` | HQLPreviewPanelV2.css, WhereConditionBuilderV2.css, DebugViewer.css, MultiEventConfigV2.css, HQLHistoryV2.css, FieldAutocomplete.css |

## 运行测试

### 前置条件

1. 启动后端服务：
```bash
cd /Users/mckenzie/Documents/event2table
./start-dev.sh
```

2. 启动前端开发服务器（Playwright会自动启动，或手动启动）：
```bash
cd frontend
npm run dev
```

### 运行测试

```bash
cd frontend

# 首次运行（生成基线截图）
npm run test:e2e:visual:update

# 后续运行（对比差异）
npm run test:e2e:visual

# 查看差异报告
# 差异截图保存在 test/e2e/output/visual/current/diff/ 目录
```

### 手动运行命令

```bash
# 生成/更新基线
UPDATE_BASELINE=1 npx playwright test test/e2e/visual/visual-regression.spec.ts

# 对比基线
npx playwright test test/e2e/visual/visual-regression.spec.ts

# 调试模式
npx playwright test test/e2e/visual/visual-regression.spec.ts --debug
```

## 截图输出

```
frontend/test/e2e/
└── visual/
    └── output/
        └── visual/
            ├── baseline/           # 基线截图（首次运行生成）
            │   ├── dashboard.png
            │   ├── canvas.png
            │   └── eventnodebuilder.png
            ├── current/           # 当前截图
            │   └── diff/          # 差异截图（检测到差异时生成）
            │       ├── dashboard.png
            │       ├── canvas.png
            │       └── eventnodebuilder.png
```

## 配置

- **阈值**: 0.1 (10% 像素差异容差)
- **浏览器**: Chromium (Chrome)
- **截图模式**: 完整页面截图

## 注意事项

1. 首次运行会生成基线截图，之后的运行会与基线对比
2. 如果UI有预期变更，需要运行 `npm run test:e2e:visual:update` 更新基线
3. 截图仅保存在本地，不提交到代码库
4. 测试会在页面完全加载后等待1秒再截图，确保动态内容已渲染
