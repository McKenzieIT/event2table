# Backend临时测试脚本归档

**归档日期**: 2026-03-21
**归档原因**: 这些是一次性验证脚本，已完成其历史使命

## 归档文件列表

### 临时验证脚本 (verify_*.py)

1. **verify_all_fixes.py** (3.2KB)
   - 用途: 综合验证所有TDD修复
   - 完成时间: 2026-03-10
   - 状态: ✅ 已完成，所有修复已验证

2. **verify_event_nodes_fix.py** (5.2KB)
   - 用途: 验证Event Node Builder修复
   - 完成时间: 2026-03-10
   - 状态: ✅ 已完成

3. **verify_events_search_fix.py** (5.7KB)
   - 用途: 验证Events搜索修复
   - 完成时间: 2026-03-10
   - 状态: ✅ 已完成

4. **verify_input_alignment_fix.py** (7.6KB)
   - 用途: 验证输入对齐修复
   - 完成时间: 2026-03-10
   - 状态: ✅ 已完成

### 临时API测试 (test_*.py)

5. **test_api_directly.py** (1.8KB)
   - 用途: 直接API测试（非正式）
   - 状态: 已被正式单元测试替代

6. **test_api_with_error_detail.py** (2.1KB)
   - 用途: API错误详情测试（非正式）
   - 状态: 已被正式单元测试替代

7. **test_batch_mutations.py** (5.7KB)
   - 用途: 批量变更测试（临时）
   - 状态: 已被正式集成测试替代

8. **test_event_nodes_api_fix.py** (2.3KB)
   - 用途: Event Nodes API修复验证（临时）
   - 状态: 已被正式单元测试替代

## 保留策略

这些文件将在此归档目录中保留6个月（至2026-09-21），之后将被永久删除。

如需参考这些脚本，请查看以下正式测试：
- 单元测试: `backend/test/unit/`
- 集成测试: `backend/test/integration/`
- E2E测试: `backend/test/e2e/`

## 归档原因总结

这些脚本不符合项目测试规范：
- ❌ 非标准命名 (verify_*, test_*_fix.py)
- ❌ 一次性执行，无持续价值
- ❌ 与正式测试重复
- ❌ 缺乏清晰的测试结构和文档

正式测试套件已完全覆盖这些脚本的功能。
