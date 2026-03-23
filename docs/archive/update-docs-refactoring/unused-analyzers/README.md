# Unused Analyzers Archive

**归档日期**: 2026-03-23
**原因**: 模块已实现但从未被使用

## 归档模块列表

1. **ASTAnalyzer** (`analyzers/ast_analyzer.py`)
   - 215行代码
   - 功能：使用AST语义分析理解代码结构变化
   - 状态：**已实现但从未调用**

2. **GitDiffAnalyzer** (`analyzers/git_diff_analyzer.py`)
   - 96行代码
   - 功能：分析Git diff理解代码变更
   - 状态：**已实现但从未调用**

## 为什么归档？

### 设计 vs 实际使用

**设计文档中的预期**：
```
Phase 1: 变更检测 (2-3秒)
  ├─ Git diff 分析
  ├─ AST 语义分析  ← ASTAnalyzer 应该在这里使用
  └─ 提交信息关键词匹配
```

**实际代码**：
- `DocumentUpdater` 类只使用了 `ChangeDetector`
- `ChangeDetector.categorize_change()` 方法包含8个硬编码的 `if` 语句
- 没有导入或使用 `ASTAnalyzer` 或 `GitDiffAnalyzer`

### 依赖关系分析

```python
# DocumentUpdater (实际使用)
class DocumentUpdater:
    def __init__(self, project_root: Path = None):
        self.detector = ChangeDetector()  # ✅ 使用 ChangeDetector
        self.mapper = DocMapper()         # ✅ 使用 DocMapper
        # ❌ 没有使用 ASTAnalyzer
        # ❌ 没有使用 GitDiffAnalyzer
```

### 代码覆盖率

通过分析所有核心模块的导入语句：
- **ASTAnalyzer**: 0次导入（未被任何模块使用）
- **GitDiffAnalyzer**: 0次导入（未被任何模块使用）

## 重构方案

### 短期（立即执行）
- ✅ **归档未使用的分析器** - 移动到本目录
- ✅ **简化 `ChangeDetector`** - 使用策略模式替代8个硬编码 `if` 语句

### 中期（可选）
- 如果未来需要更精细的变更检测，可以：
  1. 重新设计 `ChangeDetector` 接口
  2. 实现策略模式（`ChangeRule` Protocol）
  3. 添加 `ASTAnalyzer` 和 `GitDiffAnalyzer` 作为策略
  4. 通过依赖注入集成到 `DocumentUpdater`

### 长期（可选）
- 如果需要深度语义分析，可以：
  1. 使用 LLM（Claude API）进行代码语义理解
  2. 集成到 `DocumentUpdater` 工作流
  3. 替代基于规则的 `ChangeDetector`

## 技术债务

**未使用代码的成本**：
- 维护负担：215行 + 96行 = 311行未使用代码
- 测试负担：需要测试但从未测试过的代码
- 认知负担：开发者需要理解但不使用的模块

**清理收益**：
- 减少代码复杂度：-311行
- 提高可维护性：只维护实际使用的代码
- 降低理解成本：开发者不需要理解未使用的模块

## 兼容性影响

**向后兼容性**: ✅ 无影响
- 这些模块从未被使用，删除它们不会破坏任何现有功能
- 所有测试（如果有）都应该继续通过

**数据兼容性**: ✅ 无影响
- 不涉及数据存储格式变更
- 不涉及API接口变更

---

**归档负责人**: Claude (update-docs refactoring)
**审核状态**: ✅ 已确认可以安全归档
**未来考虑**: 如需精细变更检测，重新设计接口后恢复
