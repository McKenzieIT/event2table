# 前端贡献指南

> **版本**: 1.0 | **最后更新**: 2026-03-22
>
> 感谢你对 Event2Table 前端项目的关注！本文档将指导你如何参与前端开发。

---

## 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [代码审查清单](#代码审查清单)
- [提交规范](#提交规范)
- [常见问题](#常见问题)

---

## 开发环境设置

### 系统要求

- **Node.js**: 18+ (推荐使用 LTS 版本)
- **npm**: 9+ 或 **pnpm**: 8+
- **操作系统**: macOS, Linux, Windows

### 安装步骤

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install
# 或使用 pnpm（推荐）
pnpm install

# 3. 启动开发服务器
npm run dev
# 访问 http://localhost:5173

# 4. 构建生产版本
npm run build

# 5. 运行测试
npm run test
```

### IDE 配置

#### VSCode 推荐插件

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-playwright.playwright",
    "EditorConfig.EditorConfig",
    "usernamehw.errorlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

#### VSCode 设置

在项目根目录创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

#### VSCode 配置文件

创建 `.vscode/extensions.json`：

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "EditorConfig.EditorConfig",
    "ms-playwright.playwright"
  ]
}
```

---

## 项目结构

### 目录组织

```
frontend/
├── src/
│   ├── features/              # 功能模块（按业务领域划分）
│   │   ├── games/            # 游戏管理功能
│   │   │   ├── components/   # 游戏相关组件
│   │   │   ├── hooks/        # 游戏相关 Hooks
│   │   │   ├── api/          # 游戏API调用
│   │   │   ├── types/        # 游戏类型定义
│   │   │   └── index.ts      # 模块导出
│   │   ├── events/           # 事件管理功能
│   │   ├── canvas/           # 画布编辑器
│   │   └── monitoring/       # 监控功能
│   ├── shared/               # 共享模块
│   │   ├── ui/              # 共享UI组件
│   │   │   ├── components/   # 通用组件
│   │   │   │   ├── Button/
│   │   │   │   ├── Table/
│   │   │   │   ├── Form/
│   │   │   │   └── Modal/
│   │   │   └── hooks/        # UI相关Hooks
│   │   ├── hooks/           # 通用Hooks
│   │   ├── api/             # API客户端
│   │   ├── utils/           # 工具函数
│   │   ├── types/           # 共享类型
│   │   └── constants/       # 常量定义
│   ├── stores/              # 状态管理（Zustand）
│   ├── styles/              # 全局样式
│   ├── main.tsx             # 应用入口
│   └── App.tsx              # 根组件
├── public/                  # 静态资源
├── test/                    # 测试文件
│   ├── unit/               # 单元测试
│   ├── e2e/                # E2E测试
│   │   ├── critical/       # 关键路径测试
│   │   ├── smoke/          # 冒烟测试
│   │   ├── visual/         # 视觉回归测试
│   │   └── api-contract/   # API契约测试
│   └── integration/        # 集成测试
├── docs/                   # 文档
│   ├── CONTRIBUTING.md     # 贡献指南（本文档）
│   └── CODING_STANDARDS.md # 编码规范
├── package.json
├── vite.config.ts
├── tsconfig.json
├── playwright.config.ts
└── vitest.config.ts
```

### 模块化原则

**Feature 模块**：
- 每个功能模块包含完整的 components、hooks、api、types
- 模块内高内聚，模块间低耦合
- 通过 `index.ts` 统一导出

**Shared 模块**：
- 只包含真正可复用的代码
- 避免在 shared 中放置业务逻辑
- 定期清理未使用的共享代码

---

## 开发流程

### 1. 创建功能分支

```bash
# 从 develop 分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b fix/your-bug-fix
```

### 2. 开发新功能

#### 遵循 TDD 流程

```bash
# 1. 编写测试
npm run test:watch

# 2. 实现功能
# 编写代码使测试通过

# 3. 运行测试
npm run test:unit

# 4. 运行 E2E 测试
npm run test:e2e:critical
```

#### 代码规范检查

```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 自动修复
npm run lint:fix

# 代码格式化
npm run format
```

#### API 契约验证

```bash
# 验证前后端 API 一致性
npm run test:contract
```

### 3. 提交代码

```bash
# 添加文件
git add .

# 提交（遵循提交规范）
git commit -m "feat(game): add game export feature"

# 推送分支
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

在 GitHub 上创建 PR，填写 PR 模板：

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 重构
- [ ] 文档更新
- [ ] 性能优化

## 变更说明
简要描述本次变更的内容和目的。

## 相关Issue
Closes #123

## 测试
- [ ] 单元测试通过 (`npm run test:unit`)
- [ ] E2E测试通过 (`npm run test:e2e:critical`)
- [ ] API契约测试通过 (`npm run test:contract`)
- [ ] 类型检查通过 (`npm run type-check`)
- [ ] 代码检查通过 (`npm run lint`)

## 文档
- [ ] README已更新
- [ ] API文档已更新
- [ ] 组件文档已更新

## 截图（如适用）
添加截图或演示视频。

## Checklist
- [ ] 代码遵循项目规范
- [ ] 测试覆盖率充足
- [ ] 文档已更新
- [ ] 无合并冲突
```

---

## 代码审查清单

### 功能正确性

- [ ] 功能按照需求正确实现
- [ ] 边界条件处理正确
- [ ] 错误处理完善
- [ ] 加载状态显示正确
- [ ] 空状态处理完善

### 代码质量

- [ ] 遵循编码规范（见 `CODING_STANDARDS.md`）
- [ ] 组件职责单一
- [ ] 避免重复代码（DRY）
- [ ] 使用 TypeScript 类型安全
- [ ] Props 接口定义清晰

### 性能优化

- [ ] 避免不必要的 re-render
- [ ] 使用 React.memo 优化组件
- [ ] 使用 useMemo/useCallback 优化 Hooks
- [ ] 列表渲染使用 key
- [ ] 大列表使用虚拟滚动

### 可访问性

- [ ] 语义化 HTML
- [ ] ARIA 属性完整
- [ ] 键盘导航支持
- [ ] 屏幕阅读器友好
- [ ] 颜色对比度符合标准

### 测试覆盖

- [ ] 核心逻辑有单元测试
- [ ] 关键用户流程有 E2E 测试
- [ ] 测试命名清晰
- [ ] 测试数据独立

### 文档完整性

- [ ] 组件有 JSDoc 注释
- [ ] 复杂逻辑有注释
- [ ] Props 有类型定义和注释
- [ ] README 更新（如有必要）

---

## 提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型（type）

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新增功能，也不是修复 bug）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动
- `ci`: CI/CD 配置变更

### 范围（scope）

- `game`: 游戏相关
- `event`: 事件相关
- `canvas`: 画布编辑器
- `ui`: UI 组件
- `api`: API 调用
- `test`: 测试
- `build`: 构建配置

### 示例

```bash
# 新功能
git commit -m "feat(game): add game export feature"

# 修复 bug
git commit -m "fix(event): resolve event filtering issue"

# 文档更新
git commit -m "docs(readme): update installation instructions"

# 重构
git commit -m "refactor(canvas): simplify flow editor architecture"

# 性能优化
git commit -m "perf(table): implement virtual scrolling"
```

### 完整的提交信息

```
feat(canvas): add drag-and-drop for event nodes

- Implement drag-and-drop using @dnd-kit
- Add snap-to-grid functionality
- Support multiple node selection
- Add undo/redo for drag operations

Closes #123
```

---

## 常见问题

### 如何添加新的 UI 组件？

1. 在 `src/shared/ui/components/` 下创建组件目录
2. 创建组件文件、类型文件、测试文件
3. 在组件目录的 `index.ts` 中导出
4. 在 `src/shared/ui/components/index.ts` 中统一导出

### 如何添加新的 Feature 模块？

1. 在 `src/features/` 下创建模块目录
2. 按照标准结构创建子目录（components, hooks, api, types）
3. 创建 `index.ts` 统一导出
4. 在路由中注册新模块

### 如何处理 API 请求？

使用 `@tanstack/react-query` 进行数据获取：

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

// 查询
const { data, isLoading, error } = useQuery({
  queryKey: ['games', gameGid],
  queryFn: () => fetchGameByGid(gameGid),
});

// 变更
const mutation = useMutation({
  mutationFn: (data) => updateGame(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['games'] });
  },
});
```

### 如何进行状态管理？

对于全局状态，使用 Zustand：

```typescript
import { create } from 'zustand';

interface GameStore {
  selectedGame: Game | null;
  setSelectedGame: (game: Game | null) => void;
}

export const useGameStore = create<GameStore>((set) => ({
  selectedGame: null,
  setSelectedGame: (game) => set({ selectedGame: game }),
}));
```

### 如何处理表单？

使用 React Hook Form + Zod：

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

const form = useForm({
  resolver: zodResolver(schema),
});
```

### 如何运行特定测试？

```bash
# 运行单个测试文件
npm run test -- path/to/test.spec.ts

# 运行匹配模式的测试
npm run test -- --grep "game"

# 运行 E2E 测试
npm run test:e2e -- test-name

# 运行视觉回归测试
npm run test:e2e:visual
```

---

## 获取帮助

**文档资源**：
- [编码规范](CODING_STANDARDS.md)
- [API 文档](../api/README.md)
- [架构文档](../../docs/development/architecture.md)

**社区支持**：
- GitHub Issues: 报告问题和功能请求
- GitHub Discussions: 技术讨论

---

**感谢你的贡献！**

**文档版本**: 1.0
**最后更新**: 2026-03-22
**维护者**: Event2Table Frontend Team
