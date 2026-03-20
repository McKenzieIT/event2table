# 组件迁移工具使用指南

本文档提供了组件迁移工具的详细使用说明，包括安装、配置、执行和故障排除。

## 目录

- [工具概述](#工具概述)
- [安装和准备](#安装和准备)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)
- [FAQ](#faq)

---

## 工具概述

### 工具组件

迁移工具套件包含三个核心工具：

1. **migrate-components.ts** - AST 代码转换工具
   - 使用 Babel AST 解析和转换代码
   - 支持精确的组件 API 转换
   - 生成详细的变更报告

2. **batch-replace.sh** - 批量替换脚本
   - 自动查找所有需要迁移的文件
   - 执行批量替换操作
   - 支持备份和回滚

3. **validate-migration.ts** - 验证工具
   - 检查 API 使用正确性
   - 验证导入语句
   - 检查类型兼容性
   - 自动修复可修复的问题

### 支持的组件

- ✅ Modal → BaseModal
- ✅ Form (及表单字段组件)
- ✅ Table

---

## 安装和准备

### 前置要求

```bash
# Node.js 版本要求
node --version  # >= 16.0.0

# 检查 npx 是否可用
npx --version
```

### 安装依赖

```bash
# 进入项目根目录
cd /path/to/event2table

# 安装必要的依赖
npm install --save-dev @babel/parser @babel/traverse @babel/generator @babel/types
npm install --save-dev tsx typescript
```

### 准备工作

1. **确保代码已提交**

```bash
# 在开始迁移前，确保所有更改已提交
git status
git add .
git commit -m "Pre-migration commit"
```

2. **创建迁移分支**（推荐）

```bash
git checkout -b feature/component-migration
```

3. **检查项目结构**

```bash
# 确认前端源码目录存在
ls -la frontend/src
```

---

## 快速开始

### 1. 预览迁移（Dry Run）

```bash
# 预览整个前端目录的迁移
./scripts/batch-replace.sh --dry-run --directory frontend/src

# 预览特定组件的迁移
./scripts/batch-replace.sh --dry-run --components Modal --directory frontend/src/features
```

### 2. 执行迁移

```bash
# 带备份的完整迁移
./scripts/batch-replace.sh --execute --backup --directory frontend/src

# 迁移特定组件
./scripts/batch-replace.sh --execute --components Modal,Form --directory frontend/src
```

### 3. 验证迁移

```bash
# 验证整个目录
npx tsx scripts/validate-migration.ts --directory frontend/src

# 验证并自动修复
npx tsx scripts/validate-migration.ts --fix --directory frontend/src
```

---

## 详细使用说明

### migrate-components.ts

#### 基本用法

```bash
# 迁移单个文件
npx tsx scripts/migrate-components.ts --file frontend/src/components/MyComponent.tsx

# 迁移整个目录
npx tsx scripts/migrate-components.ts --directory frontend/src/features

# 预览模式（不实际修改文件）
npx tsx scripts/migrate-components.ts --dry-run --directory frontend/src

# 只迁移特定组件
npx tsx scripts/migrate-components.ts --components Modal --directory frontend/src
```

#### 命令行选项

| 选项 | 简写 | 说明 | 示例 |
|-----|------|------|------|
| `--file` | `-f` | 指定单个文件 | `--file path/to/file.tsx` |
| `--directory` | `-d` | 指定目录 | `--directory frontend/src` |
| `--dry-run` | `-n` | 预览模式，不修改文件 | `--dry-run` |
| `--verbose` | `-v` | 详细输出 | `--verbose` |
| `--components` | `-c` | 指定组件（逗号分隔） | `--components Modal,Form` |

#### 输出示例

```
🚀 Starting component migration...

Found 15 files to process

📄 frontend/src/components/ModalExample.tsx
  Changes:
    ✓ Import: @/components/Modal → @shared/ui/BaseModal/BaseModal
    ✓ Component: Modal transformed
    ✓ Prop: visible → isOpen

========================================
Migration Report
========================================
Total Files: 15
Successful: 14
Failed: 1
Total Changes: 42
Total Warnings: 3
========================================

📝 Rollback script generated: scripts/rollback-migration.sh
```

### batch-replace.sh

#### 基本用法

```bash
# 显示帮助
./scripts/batch-replace.sh --help

# 预览迁移
./scripts/batch-replace.sh --dry-run --directory frontend/src

# 执行迁移（带备份）
./scripts/batch-replace.sh --execute --backup --directory frontend/src

# 迁移特定组件
./scripts/batch-replace.sh --execute --components Modal,Table --directory frontend/src

# 回滚迁移
./scripts/batch-replace.sh --rollback backups/migration/20240320_120000
```

#### 命令行选项

| 选项 | 简写 | 说明 | 示例 |
|-----|------|------|------|
| `--directory` | `-d` | 目标目录 | `--directory frontend/src` |
| `--components` | `-c` | 组件列表（逗号分隔） | `--components Modal,Form` |
| `--dry-run` | `-n` | 预览模式 | `--dry-run` |
| `--execute` | `-e` | 执行迁移（需要确认） | `--execute` |
| `--backup` | `-b` | 创建备份 | `--backup` |
| `--rollback` | `-r` | 回滚到指定备份 | `--rollback path/to/backup` |
| `--verbose` | `-v` | 详细输出 | `--verbose` |
| `--help` | `-h` | 显示帮助 | `--help` |

#### 安全特性

1. **自动备份**
   - 在执行前自动创建完整备份
   - 备份包含时间戳
   - 支持一键回滚

2. **确认提示**
   - 执行前需要用户确认
   - 显示将要修改的文件数量
   - 防止误操作

3. **详细日志**
   - 所有操作都记录到日志文件
   - 日志保存在 `logs/migration/` 目录
   - 包含时间戳和详细错误信息

4. **验证集成**
   - 迁移后自动运行验证
   - 验证失败自动回滚
   - 确保代码质量

### validate-migration.ts

#### 基本用法

```bash
# 验证单个文件
npx tsx scripts/validate-migration.ts --file frontend/src/components/MyComponent.tsx

# 验证整个目录
npx tsx scripts/validate-migration.ts --directory frontend/src

# 验证并自动修复
npx tsx scripts/validate-migration.ts --fix --directory frontend/src

# 详细输出
npx tsx scripts/validate-migration.ts --verbose --directory frontend/src
```

#### 命令行选项

| 选项 | 简写 | 说明 | 示例 |
|-----|------|------|------|
| `--file` | `-f` | 指定单个文件 | `--file path/to/file.tsx` |
| `--directory` | `-d` | 指定目录 | `--directory frontend/src` |
| `--fix` | | 自动修复可修复的问题 | `--fix` |
| `--verbose` | `-v` | 详细输出 | `--verbose` |

#### 验证规则

1. **导入验证**
   - 检查旧导入路径
   - 验证新导入路径
   - 确保导入结构正确

2. **API 使用验证**
   - 检查已弃用的 props
   - 验证必需的 props
   - 检查 prop 类型

3. **类型验证**
   - 检查类型兼容性
   - 验证泛型类型
   - 检查事件处理器类型

#### 输出示例

```
🔍 Starting validation...

Validating 15 files...

========================================
Validation Report
========================================
Total Files: 15
Valid: 13
Invalid: 2
Errors: 3
Warnings: 5
Fixes Applied: 2
========================================

Invalid Files:

  📄 frontend/src/components/OldModal.tsx
    ✗ [import] Old import path detected for Modal: @/components/Modal (line 3) [fixable]
    ✗ [deprecated] Deprecated prop 'visible' used in Modal (line 15) [fixable]

  📄 frontend/src/components/BadForm.tsx
    ⚠ [api] Missing required prop 'onSubmit' in Form (line 8)

Fixes Applied:

  📄 frontend/src/components/OldModal.tsx
    ✓ Updated import for Modal: @/components/Modal → @shared/ui/BaseModal/BaseModal
    ✓ Renamed prop: visible → isOpen
```

---

## 最佳实践

### 1. 迁移策略

#### 渐进式迁移

```bash
# 第一阶段：迁移 Modal 组件
./scripts/batch-replace.sh --execute --backup --components Modal --directory frontend/src

# 验证并测试
npx tsx scripts/validate-migration.ts --fix --directory frontend/src
npm test

# 第二阶段：迁移 Form 组件
./scripts/batch-replace.sh --execute --backup --components Form --directory frontend/src

# 第三阶段：迁移 Table 组件
./scripts/batch-replace.sh --execute --backup --components Table --directory frontend/src
```

#### 分模块迁移

```bash
# 先迁移 features 目录
./scripts/batch-replace.sh --execute --backup --directory frontend/src/features

# 再迁移 components 目录
./scripts/batch-replace.sh --execute --backup --directory frontend/src/components

# 最后迁移 pages 目录
./scripts/batch-replace.sh --execute --backup --directory frontend/src/pages
```

### 2. 安全措施

#### 始终使用备份

```bash
# 推荐：始终使用 --backup 选项
./scripts/batch-replace.sh --execute --backup --directory frontend/src
```

#### 先预览再执行

```bash
# 第一步：预览
./scripts/batch-replace.sh --dry-run --directory frontend/src

# 第二步：审查输出
# 检查日志文件：logs/migration/migration_*.log

# 第三步：执行
./scripts/batch-replace.sh --execute --backup --directory frontend/src
```

#### 使用版本控制

```bash
# 创建迁移分支
git checkout -b feature/component-migration

# 执行迁移
./scripts/batch-replace.sh --execute --backup --directory frontend/src

# 提交更改
git add .
git commit -m "Migrate components to new library"

# 创建 PR 进行代码审查
```

### 3. 测试策略

#### 迁移前测试

```bash
# 确保所有测试通过
npm test

# 运行 E2E 测试
npm run test:e2e
```

#### 迁移后验证

```bash
# 运行验证工具
npx tsx scripts/validate-migration.ts --fix --directory frontend/src

# 运行类型检查
npm run type-check

# 运行所有测试
npm test

# 运行 E2E 测试
npm run test:e2e
```

#### 手动测试

- 在开发环境中启动应用
- 测试所有迁移的组件
- 检查视觉样式是否正确
- 验证功能是否正常工作

### 4. 团队协作

#### 代码审查

```bash
# 创建 PR 后，团队成员应该审查：
# 1. 组件 API 使用是否正确
# 2. 类型定义是否完整
# 3. 样式是否正确
# 4. 功能是否正常
```

#### 文档更新

- 更新组件使用文档
- 记录迁移过程中的问题
- 分享最佳实践

---

## 故障排除

### 常见问题

#### 1. 解析错误

**问题：**
```
Failed to parse frontend/src/components/MyComponent.tsx
```

**解决方案：**
```bash
# 检查文件语法
npx tsc --noEmit frontend/src/components/MyComponent.tsx

# 修复语法错误后重试
npx tsx scripts/migrate-components.ts --file frontend/src/components/MyComponent.tsx
```

#### 2. 导入路径错误

**问题：**
```
Error: Cannot find module '@shared/ui/BaseModal/BaseModal'
```

**解决方案：**
```bash
# 检查新组件库是否已安装
npm list @shared/ui

# 如果未安装，安装依赖
npm install

# 重新构建
npm run build
```

#### 3. 类型错误

**问题：**
```
Type error: Property 'isOpen' does not exist on type 'ModalProps'
```

**解决方案：**
```bash
# 运行验证工具
npx tsx scripts/validate-migration.ts --fix --directory frontend/src

# 手动检查类型定义
npx tsc --noEmit
```

#### 4. 样式丢失

**问题：**
迁移后组件样式不正确。

**解决方案：**
```bash
# 检查样式文件是否正确导入
# 确保使用新的样式路径
import '@shared/ui/BaseModal/BaseModal.css';

# 如果使用 CSS Modules
import styles from '@shared/ui/BaseModal/BaseModal.module.css';
```

#### 5. 回滚失败

**问题：**
回滚时出现错误。

**解决方案：**
```bash
# 使用 Git 回滚
git checkout HEAD -- frontend/src

# 或者从备份恢复
cp -r backups/migration/20240320_120000/src/* frontend/src/
```

### 调试技巧

#### 启用详细日志

```bash
# 使用 --verbose 选项
./scripts/batch-replace.sh --verbose --execute --directory frontend/src

# 查看日志文件
cat logs/migration/migration_*.log
```

#### 单步调试

```bash
# 迁移单个文件进行测试
npx tsx scripts/migrate-components.ts --file frontend/src/components/TestComponent.tsx

# 检查输出
git diff frontend/src/components/TestComponent.tsx
```

#### 使用 Git 查看更改

```bash
# 查看所有更改
git diff

# 查看特定文件的更改
git diff frontend/src/components/MyComponent.tsx

# 查看更改统计
git diff --stat
```

---

## FAQ

### Q1: 可以迁移自定义组件吗？

A: 当前工具只支持预定义的组件（Modal、Form、Table）。对于自定义组件，需要手动迁移或扩展工具规则。

### Q2: 迁移会丢失代码格式吗？

A: 工具会尽量保持原有格式，但可能会进行一些标准化。建议在迁移后运行格式化工具：

```bash
npm run format
```

### Q3: 如何处理迁移失败的文件？

A: 
1. 查看错误日志
2. 手动修复问题
3. 重新运行验证工具
4. 如果无法修复，可以跳过该文件

### Q4: 可以部分迁移吗？

A: 可以。使用 `--components` 选项指定要迁移的组件，或使用 `--directory` 选项指定特定目录。

### Q5: 迁移后需要更新测试吗？

A: 是的。需要更新测试文件中的导入和组件使用。建议：

```bash
# 运行测试查看失败情况
npm test

# 手动更新测试文件
# 然后重新运行测试
```

### Q6: 如何确保迁移的安全性？

A: 
1. 始终使用 `--backup` 选项
2. 先运行 `--dry-run` 预览
3. 在开发环境测试
4. 使用版本控制
5. 代码审查

### Q7: 迁移需要多长时间？

A: 取决于项目大小：
- 小型项目（< 100 文件）：几分钟
- 中型项目（100-500 文件）：15-30 分钟
- 大型项目（> 500 文件）：1-2 小时

### Q8: 可以在 CI/CD 中使用吗？

A: 可以。建议：
1. 在 CI 中运行验证工具
2. 在 PR 中检查迁移结果
3. 在合并前运行完整测试

---

## 获取帮助

如果遇到问题：

1. 查看本文档的故障排除部分
2. 检查日志文件：`logs/migration/`
3. 查看转换规则文档：`docs/migration/MIGRATION-RULES.md`
4. 联系技术支持团队

---

## 版本历史

- **v1.0.0** (2024-03-20)
  - 初始版本
  - 支持 Modal、Form、Table 组件迁移
  - 自动验证和修复功能
  - 备份和回滚支持
