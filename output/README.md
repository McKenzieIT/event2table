# Output Directory

## 目录结构

```
output/
├── reports/           # 正式报告（保留）
│   ├── COMPREHENSIVE-TEST-ANALYSIS-2026-03-20.md
│   ├── SUPPLEMENTARY-TEST-PLAN.md
│   ├── WEBKIT-COMPATIBILITY-ANALYSIS.md
│   └── PLAYWRIGHT-IMPLEMENTATION-FINAL-SUMMARY.md
├── test-results/      # 测试结果（gitignore）
│   ├── playwright/
│   ├── unit/
│   └── e2e/
├── screenshots/       # 测试截图（gitignore）
│   ├── chrome/
│   ├── firefox/
│   └── webkit/
└── *.md              # 其他临时报告（gitignore）
```

## 文件保留策略

### ✅ 保留的文件（正式报告）

- `PLAYWRIGHT-IMPLEMENTATION-FINAL-SUMMARY.md` - Playwright实施总结
- `COMPREHENSIVE-TEST-ANALYSIS-2026-03-20.md` - 全面测试分析
- `SUPPLEMENTARY-TEST-PLAN.md` - 补充测试方案
- `WEBKIT-COMPATIBILITY-ANALYSIS.md` - WebKit兼容性分析

### ❌ 排除的文件（临时/自动生成）

- 所有 `test-results/` 目录
- 所有 `screenshots/` 目录
- 所有 `*.log` 文件
- 所有临时 `*TEST-*.md` 报告

## 清理脚本

```bash
# 清理测试输出（保留报告）
cd /Users/mckenzie/Documents/event2table
rm -rf output/test-results/
rm -rf output/screenshots/
rm -f output/*.log

# 清理playwright测试输出
rm -rf playwright-tests/test-results/
rm -rf playwright-tests/screenshots/
```

## Git提交

```bash
# 提交正式报告
git add output/reports/*.md
git commit -m "docs(test): add comprehensive test analysis reports"

# 不要提交测试输出
# output/test-results/ 和 output/screenshots/ 已在.gitignore中
```
