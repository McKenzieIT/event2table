# 临时文件管理规范

**版本**: 1.0
**创建日期**: 2026-03-20
**目的**: 保持项目根目录整洁，防止临时文件污染版本控制

---

## 📋 目录

1. [规范概述](#规范概述)
2. [文件分类](#文件分类)
3. [存储位置](#存储位置)
4. [.gitignore配置](#gitignore配置)
5. [Pre-commit检查](#pre-commit检查)
6. [清理脚本](#清理脚本)
7. [最佳实践](#最佳实践)

---

## 规范概述

### 为什么需要临时文件管理？

**问题**:
- ❌ 根目录积累大量临时文件（截图、报告、日志）
- ❌ 临时文件被意外提交到git
- ❌ 项目结构混乱，难以维护
- ❌ 文件系统性能下降

**解决方案**:
- ✅ 统一的临时文件存储位置
- ✅ 自动化的pre-commit检查
- ✅ 定期清理机制
- ✅ 明确的文件命名规范

---

## 文件分类

### 1. 测试截图文件

**类型**: UI测试、E2E测试、手动测试截图
**格式**: `.png`, `.jpg`, `.jpeg`, `.gif`
**示例**:
```
01-homepage.png
02-games-page.png
event-node-builder-test-state.png
```

**存储位置**: `output/screenshots/`

---

### 2. 临时报告文件

**类型**: 实施报告、测试报告、分析报告
**格式**: `.md`, `.txt`, `.json`, `.html`
**命名模式**: `*REPORT*.md`, `*IMPLEMENTATION-REPORT*.md`
**示例**:
```
API-RESPONSE-OPTIMIZATION-IMPLEMENTATION-REPORT.md
BUG-FIX-PROGRESS-2026-03-14.md
E2E-TEST-REPORT-BASE-FIELD-TYPE-FIX.md
```

**存储位置**: `output/reports/`

---

### 3. 日志文件

**类型**: 应用日志、错误日志、调试日志
**格式**: `.log`, `::log_file`
**示例**:
```
::log_file
backend.log
error.log
```

**存储位置**: `logs/`

---

### 4. 数据库临时文件

**类型**: SQLite WAL、SHM文件
**格式**: `.db-wal`, `.db-shm`
**示例**:
```
dwd_generator.db-wal
dwd_generator.db-shm
test_database.db-wal
```

**存储位置**: `data/` (已在.gitignore中)

---

### 5. 编译/构建临时文件

**类型**: 缓存、临时输出、构建产物
**格式**: `.pyc`, `.o`, `.class`, `.tmp`
**存储位置**: 各自的构建目录

---

## 存储位置

### 目录结构

```
event2table/
├── output/                    # 输出文件目录
│   ├── screenshots/          # 测试截图 ⭐
│   │   ├── ui/
│   │   ├── e2e/
│   │   └── manual/
│   └── reports/              # 临时报告 ⭐
│       ├── implementation/
│       ├── testing/
│       └── analysis/
├── logs/                     # 日志文件
│   ├── backend.log
│   └── error.log
├── data/                     # 数据库文件
│   ├── dwd_generator.db
│   ├── dwd_generator.db-wal
│   └── test_database.db
└── temp/                     # 其他临时文件
    ├── cache/
    └── uploads/
```

### 文件命名规范

**截图文件**:
```
{模块名}-{测试类型}-{时间戳}.{ext}
```

**示例**:
```
games-ui-e2e-20260320-061500.png
events-manual-20260320-061500.jpg
```

**报告文件**:
```
{类型}-{主题}-{日期}.{ext}
```

**示例**:
```
implementation-event-nodes-2026-03-20.md
testing-e2e-regression-2026-03-20.md
analysis-performance-2026-03-20.md
```

---

## .gitignore配置

### 更新后的.gitignore

```gitignore
# ==================== 临时文件管理 ====================

# 测试截图（根目录）
*.png
*.jpg
*.jpeg
*.gif
*.svg

# 但保留output/screenshots/目录
!output/screenshots/**/*.png
!output/screenshots/**/*.jpg
!output/screenshots/**/*.jpeg

# 临时报告（根目录）
REPORT.md
*REPORT.md
*IMPLEMENTATION-REPORT.md
*PROGRESS*.md
*SUMMARY.md
*_TEST-*.md
*TEST-*.md

# 但保留output/reports/目录
!output/reports/**/*.md

# 日志文件
::log_file
*.log
logs/*.log

# 临时文件
*.tmp
*.temp
*.cache
.DS_Store
Thumbs.db

# ==================== 数据库文件 ====================

# SQLite WAL和SHM文件
*.db-wal
*.db-shm

# 但保留data/目录的结构文件
!data/.gitkeep

# ==================== Python ====================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# ==================== Node.js ====================

# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# ==================== IDE ====================

# VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# JetBrains IDEs
.idea/
*.iml

# ==================== 构建产物 ====================

# Python
build/
dist/
*.egg-info/

# Frontend
frontend/dist/
frontend/.next/
frontend/out/

# ==================== 其他 ====================

# 环境变量
.env
.env.local
.env.*.local

# 操作系统
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

---

## Pre-commit检查

### 检查脚本

创建 `scripts/git-hooks/check-temp-files.sh`:

```bash
#!/bin/bash
# Pre-commit检查：防止临时文件提交

echo "🔍 检查临时文件..."

# 检查根目录的截图文件
SCREENSHOTS=$(git diff --cached --name-only | grep -E '\.(png|jpg|jpeg|gif)$' | grep -v '^output/screenshots/')
if [ -n "$SCREENSHOTS" ]; then
    echo "❌ 错误：检测到根目录的截图文件"
    echo "请将截图移动到 output/screenshots/ 目录："
    echo "$SCREENSHOTS"
    exit 1
fi

# 检查根目录的临时报告
REPORTS=$(git diff --cached --name-only | grep -E 'REPORT\.md$|IMPLEMENTATION-REPORT\.md$|PROGRESS.*\.md$|SUMMARY\.md$' | grep -v '^output/reports/')
if [ -n "$REPORTS" ]; then
    echo "❌ 错误：检测到根目录的临时报告文件"
    echo "请将报告移动到 output/reports/ 目录："
    echo "$REPORTS"
    exit 1
fi

# 检查日志文件
LOGS=$(git diff --cached --name-only | grep -E '::log_file$|\.log$')
if [ -n "$LOGS" ]; then
    echo "❌ 错误：检测到日志文件"
    echo "日志文件不应提交到git："
    echo "$LOGS"
    exit 1
fi

echo "✅ 临时文件检查通过"
exit 0
```

### 安装Pre-commit Hook

```bash
# 复制检查脚本到.git/hooks/
cp scripts/git-hooks/check-temp-files.sh .git/hooks/pre-commit-check-temp
chmod +x .git/hooks/pre-commit-check-temp

# 在现有pre-commit hook中添加检查
echo -e "\n# 临时文件检查\nbash .git/hooks/pre-commit-check-temp" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## 清理脚本

### 自动清理脚本

创建 `scripts/tools/cleanup-temp-files.sh`:

```bash
#!/bin/bash
# 临时文件清理脚本

echo "🧹 清理临时文件..."

# 创建必要的目录
mkdir -p output/screenshots/ui
mkdir -p output/screenshots/e2e
mkdir -p output/screenshots/manual
mkdir -p output/reports/implementation
mkdir -p output/reports/testing
mkdir -p output/reports/analysis

# 移动根目录的截图到output/screenshots/
find . -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" \) -exec mv {} output/screenshots/manual/ \; 2>/dev/null

# 移动根目录的临时报告到output/reports/
find . -maxdepth 1 -type f -name "*REPORT*.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null
find . -maxdepth 1 -type f -name "*PROGRESS*.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null
find . -maxdepth 1 -type f -name "*SUMMARY.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null

# 删除日志文件
find . -maxdepth 1 -type f -name "::log_file" -delete 2>/dev/null

echo "✅ 清理完成"
echo "📊 统计："
echo "  - output/screenshots/: $(find output/screenshots/ -type f | wc -l) 个文件"
echo "  - output/reports/: $(find output/reports/ -type f | wc -l) 个文件"
```

---

## 最佳实践

### 1. 开发工作流

**创建新报告时**:
```bash
# 创建报告到正确的位置
vim output/reports/implementation/my-feature-report.md
```

**保存截图时**:
```bash
# 保存截图到正确的位置
mv screenshot.png output/screenshots/manual/screenshot-$(date +%Y%m%d-%H%M%S).png
```

**清理临时文件**:
```bash
# 运行清理脚本
bash scripts/tools/cleanup-temp-files.sh
```

### 2. Git提交前检查

**手动检查**:
```bash
# 查看将要提交的文件
git status

# 查看是否有临时文件
git status | grep -E '\.(png|jpg|jpeg|gif|log)$'
```

**自动检查**:
- Pre-commit hook会自动检查
- 发现临时文件会阻止提交
- 按照提示移动文件后重新提交

### 3. 定期维护

**每周**:
```bash
# 运行清理脚本
bash scripts/tools/cleanup-temp-files.sh

# 检查.gitignore是否最新
git status --ignored
```

**每月**:
- 审查output/目录的大小
- 归档旧报告到docs/archive/
- 删除过期的截图

---

## 常见问题

### Q1: 为什么不能在根目录保存截图？

**A**:
- ❌ 根目录应该保持整洁，只包含核心文件
- ✅ 截图是有价值的测试证据，应该组织存储
- ✅ 便于查找和归档

### Q2: 如何快速移动现有的临时文件？

**A**:
```bash
# 运行自动清理脚本
bash scripts/tools/cleanup-temp-files.sh

# 或手动移动
mv *.png output/screenshots/manual/
mv *REPORT*.md output/reports/analysis/
```

### Q3: Pre-commit检查阻止了提交怎么办？

**A**:
1. 查看错误信息，了解哪些文件有问题
2. 移动文件到正确的位置
3. 重新执行git add和git commit

### Q4: 如何跳过pre-commit检查？

**A**:
```bash
# 不推荐，但紧急情况下可以使用
git commit --no-verify -m "message"
```

---

## 相关文档

- [Pre-commit Hooks指南](../development/git-hooks-guide.md)
- [项目结构规范](../development/project-structure.md)
- [Git工作流程](../development/github-setup-guide.md)

---

**维护者**: Event2Table Development Team
**最后更新**: 2026-03-20
**版本**: 1.0
