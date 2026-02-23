# Event2Table 开发报告索引

> **最后更新**: 2026-02-14 16:50
> **状态**: ✅ 测试报告已重组到docs/testing/reports/

---

## 📚 快速导航

### 🎯 核心报告

| 类别 | 目录 | 描述 |
|------|------|------|
| **测试报告** | [docs/testing/reports/](docs/testing/reports/) | E2E测试报告 |
| **开发指南** | [docs/development/](docs/development/) | 开发指南 |
| **API文档** | [docs/api/](docs/api/) | API文档 |
| **架构决策** | [docs/adr/](docs/adr/) | 架构决策记录 |
| **所有报告** | [docs/reports/](docs/reports/) | 所有开发报告 |

---

## 📋 按主题归档

| 主题 | 目录 | 说明 |
|------|------|----------|
| **E2E测试** | [docs/testing/reports/e2e/](docs/testing/reports/e2e/) | E2E测试失败分析 |
| **性能优化** | [docs/reports/performance/](docs/reports/performance/) | 性能优化报告 |
| **按日期** | [docs/testing/reports/ports/by-date/](docs/testing/reports/ports/by-date/) | 按日期归档 |
| **归档** | [docs/testing/reports/ports/archived/](docs/testing/reports/ports/archived/) | 归档的旧报告 |

---

## 📊 新增内容（2026）

### 测试报告重组 ✨

**重要更新**：所有测试报告已迁移到 [`docs/testing/reports/`](docs/testing/reports/)！

**新的位置**：
- E2E测试失败分析：[docs/testing/reports/e2e/E2E_TEST_FAILURE_ANALYSIS.md](docs/testing/reports/e2e/E2E_TEST_FAILURE_ANALYSIS.md)
- E2E测试修复验证：[docs/testing/reports/e2e/E2E_TEST_FIXES_VERIFICATION_REPORT.md](docs/testing/reports/e2e/E2E_TEST_FIXES_VERIFICATION_REPORT.md)
- 最终工作总结：[docs/testing/reports/FINAL_SUMMARY_TEST_CLEANUP_AND_FIXES.md](docs/testing/reports/FINAL_SUMMARY_TEST_CLEANUP_AND_FIXES.md)

**旧的test-reports/目录**：保留用于向后兼容

---

## 🎯 测试报告类别

### 1. E2E测试报告

**目录**: [docs/testing/reports/e2e/](docs/testing/reports/e2e/)

**包含报告**：
- E2E测试失败分析报告
- E2E测试修复验证报告
- （未来）更多E2E测试报告...

### 2. Backend测试报告（待创建）

**目录**: [docs/testing/reports/backend/](docs/testing/reports/backend/)

**计划内容**：
- Backend单元测试报告
- Backend集成测试报告
- Backend性能测试报告

### 3. 性能测试报告（待创建）

**目录**: [docs/testing/reports/performance/](docs/testing/reports/performance/)

**计划内容**：
- 前端性能优化报告
- 后端性能测试报告
- 测试覆盖率报告

### 4. 综合测试报告（待创建）

**目录**: [docs/testing/reports/integration/](docs/testing/reports/integration/)

**计划内容**：
- API契约测试报告
- 端到端流程测试报告
- 系统集成测试报告

---

## 🔗 维护指南

### 添加新报告时

1. **放在正确目录**：
   - E2E测试 → `docs/testing/reports/e2e/`
   - Backend → `docs/testing/reports/backend/`
   - 性能 → `docs/testing/reports/performance/`

2. **更新此索引（docs/reports/index.md）**：
   - 添加报告标题、日期、简短描述
   - 确保链接正确

3. **更新CLAUDE.md**：
   - 如果有链接到test-reports/，更新为docs/testing/reports/

### 归档策略

1. **定期清理**：每季度将旧报告移至archived/
2. **按年份归档**：每年的12月31日后移至by-date/YYYY/

---

## 📋 查找测试报告

**快速链接**：
- 📁 [E2E测试报告](docs/testing/reports/e2e/) - 最新E2E测试报告
- 📁 [最终总结](docs/testing/reports/FINAL_SUMMARY_TEST_CLEANUP_AND_FIXES.md) - 完整工作总结

**完整列表**：查看 [docs/testing/reports/](docs/testing/reports/) 目录

---

**最后更新**: 2026-02-14 16:50
