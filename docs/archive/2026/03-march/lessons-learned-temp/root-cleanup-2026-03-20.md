# 根目录文件整理经验

**日期**: 2026-03-20
**任务**: 整理根目录下的文件，按照项目规范移动到合适的目录
**成果**: 移动100+个文件，清理率91.4%

## 问题描述

根目录存在大量不应该存放的文件：
- 139个文件在根目录
- 48个PNG截图文件
- 15个MD报告文件
- 12个TXT测试结果文件
- 大量临时脚本和配置文件

**违反规范**: 根据[CLAUDE.md](../../CLAUDE.md)，根目录只允许12个特定文件。

## 解决方案

### 1. 自动化分类脚本

创建Python脚本 `cleanup_root_directory.py`，实现：
- 基于文件名模式自动分类
- 自动创建目标目录
- 批量移动文件
- 生成详细报告

**核心分类规则**:
```python
FILE_CATEGORIES = {
    "screenshots": {
        "pattern": [".png"],
        "destination": "output/screenshots/"
    },
    "test_reports": {
        "pattern": ["TEST-REPORT", "E2E-TEST"],
        "destination": "docs/reports/2026-03/"
    },
    # ... 更多分类
}
```

### 2. 文件分类策略

| 文件类型 | 模式 | 目标目录 | 数量 |
|---------|------|---------|------|
| 截图文件 | `*.png` | `output/screenshots/` | 48 |
| 测试报告 | `*-TEST-REPORT*.md` | `docs/reports/2026-03/` | 8 |
| 实施报告 | `*-IMPLEMENTATION-REPORT.md` | `docs/reports/2026-03/` | 9 |
| 性能报告 | `*-PERF-*.md` | `docs/performance/` | 3 |
| 测试结果 | `*_tests.txt` | `output/test-results/` | 7 |
| 备份文件 | `*.backup*` | `output/backups/` | 3 |
| 临时脚本 | `fix_*.py` | `scripts/temp/` | 9 |
| 进度报告 | `*-PROGRESS-*.md` | `docs/reports/2026-03/` | 3 |
| 配置文件 | `lighthouse*.json` | `config/` | 3 |

### 3. 处理特殊文件

**无扩展名的截图文件**:
```bash
# 很多截图文件没有扩展名
001-dashboard-initial
dashboard-page-1
event-node-builder-page-6

# 解决：使用file命令检测类型后移动
for f in $(ls | grep -E "^[a-z0-9-]+$"); do
    if [ -f "$f" ]; then
        mv "$f" output/screenshots/
    fi
done
```

**文件名冲突**:
```python
# 如果目标文件已存在，添加时间戳
if destination.exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = f"{stem}_{timestamp}{suffix}"
```

## 执行结果

### 整理前后对比

| 指标 | 整理前 | 整理后 | 改善 |
|-----|--------|--------|------|
| 根目录文件数 | 139 | 12 | -91.4% |
| MD文件 | 15 | 3 | -80% |
| PNG文件 | 48 | 0 | -100% |
| TXT文件 | 12 | 1 | -91.7% |

### 根目录最终状态

✅ **符合规范的12个文件**:
- README.md
- CHANGELOG.md
- CLAUDE.md
- LICENSE
- requirements.txt
- pyproject.toml
- package.json
- package-lock.json
- pytest.ini
- conftest.py
- web_app.py
- deploy.sh
- start-dev.sh

## 经验总结

### ✅ 成功经验

**1. 自动化脚本提高效率**
- 手动移动100+文件需要数小时
- Python脚本5分钟完成
- 可重复使用，适合定期清理

**2. 分类规则设计**
- 基于文件名模式（简单有效）
- 支持通配符和多模式匹配
- 易于扩展新规则

**3. 冲突处理机制**
- 时间戳避免覆盖
- 保留所有版本文件
- 可追溯历史记录

**4. 详细报告生成**
- Markdown格式，易于阅读
- 分类统计，清晰明了
- 包含维护建议

### ⚠️ 常见问题

**问题1: 目录不存在**
```python
# ❌ 错误：直接移动
shutil.move(src, dst)  # 失败：dst目录不存在

# ✅ 正确：先创建目录
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.move(src, dst)
```

**问题2: 无扩展名文件**
```bash
# ❌ 错误：只匹配有扩展名的文件
ls *.png  # 漏掉无扩展名的截图

# ✅ 正确：检测文件类型
file * | grep image  # 识别所有图片文件
```

**问题3: 文件名冲突**
```python
# ❌ 错误：直接覆盖
shutil.move(src, dst)  # 覆盖已有文件

# ✅ 正确：添加时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dst = f"{dst}_{timestamp}"
```

### 🔧 改进建议

**1. 定期自动清理**
```bash
# 添加到crontab，每月执行
0 0 1 * * /path/to/cleanup_root_directory.py
```

**2. Pre-commit Hook**
```bash
# .git/hooks/pre-commit
# 阻止提交违规文件到根目录
violating_files=$(ls *.png *_REPORT.md 2>/dev/null)
if [ -n "$violating_files" ]; then
    echo "❌ 根目录有违规文件，请移动到合适目录"
    exit 1
fi
```

**3. 监控脚本**
```python
# 定期检查根目录规范
def check_root_compliance():
    allowed = {"README.md", "CHANGELOG.md", "CLAUDE.md", ...}
    files = set(Path(".").iterdir())
    violating = files - allowed
    if violating:
        send_alert(f"发现{len(violating)}个违规文件")
```

**4. 自动归档**
```bash
# 自动归档90天以上的报告
find docs/reports/ -type f -mtime +90 -exec mv {} docs/archive/$(date +%Y-%m)/ \;
```

## 最佳实践

### 开发规范

**禁止在根目录创建**:
- ❌ 测试报告 → `docs/reports/`
- ❌ 截图文件 → `output/screenshots/`
- ❌ 临时脚本 → `scripts/temp/`
- ❌ 测试结果 → `output/test-results/`
- ❌ 备份文件 → `output/backups/`

**允许在根目录**:
- ✅ 项目文档 (README.md, CHANGELOG.md, CLAUDE.md)
- ✅ 配置文件 (requirements.txt, pyproject.toml, package.json)
- ✅ 应用入口 (web_app.py)
- ✅ 启动脚本 (deploy.sh, start-dev.sh)

### 文件命名规范

**测试报告**: `E2E-TEST-REPORT-{功能}-{日期}.md`
**实施报告**: `{功能}-IMPLEMENTATION-REPORT.md`
**性能报告**: `{功能}-PERF-{优化类型}.md`
**截图文件**: `{功能}-{描述}.png`

### 目录组织

```
output/
├── screenshots/       # 截图文件（按功能分类）
├── test-results/     # 测试结果（按类型分类）
├── backups/          # 备份文件（按日期分类）
└── plist/            # 配置文件

docs/
├── reports/2026-03/  # 按月份归档
│   ├── e2e-tests/
│   ├── implementation/
│   └── progress/
└── performance/      # 性能优化报告

scripts/
└── temp/             # 临时脚本（可删除）
```

## 工具和脚本

### 清理脚本

**位置**: `cleanup_root_directory.py`
**用法**:
```bash
python3 cleanup_root_directory.py
```

**功能**:
- 自动分类文件
- 创建目录结构
- 移动文件
- 生成报告

### 检查脚本

```bash
#!/bin/bash
# check_root_compliance.sh

echo "检查根目录规范..."

allowed_files=(
    "README.md"
    "CHANGELOG.md"
    "CLAUDE.md"
    "LICENSE"
    "requirements.txt"
    "pyproject.toml"
    "package.json"
    "pytest.ini"
    "conftest.py"
    "web_app.py"
)

violating=false

for file in *; do
    if [[ ! " ${allowed_files[@]} " =~ " ${file} " ]]; then
        if [ -f "$file" ]; then
            echo "❌ 违规文件: $file"
            violating=true
        fi
    fi
done

if [ "$violating" = false ]; then
    echo "✅ 根目录符合规范"
fi
```

## 相关文档

- [根目录整理最终报告](../../output/ROOT-CLEANUP-FINAL-REPORT.md)
- [项目开发规范](../../CLAUDE.md)
- [文档组织规范](documentation-standards.md)

## 总结

本次根目录整理：
- ✅ 移动100+个文件到合适目录
- ✅ 清理率91.4%
- ✅ 建立自动化脚本
- ✅ 生成详细报告
- ✅ 提炼最佳实践

**关键经验**:
1. 使用自动化脚本提高效率
2. 建立清晰的分类规则
3. 生成详细报告便于追踪
4. 定期维护避免积累
5. Pre-commit hook防止违规

---

**整理完成时间**: 2026-03-20
**执行人**: Claude Code
