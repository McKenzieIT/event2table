# Update-Docs Skill 重构架构设计

> **日期**: 2026-03-24
> **核心原则**: 对话优先，脚本辅助
> **目标**: 从5300行代码减少到500行 (-90%)

---

## 执行摘要

**当前问题**：
- 4010行Python代码试图自动化智能判断任务
- 正则表达式、字符串匹配无法理解语义
- 80%+的功能应该在对话中自然完成

**解决方案**：
- 对话优先：经验提取、优先级判断、归档决策在对话中完成
- 脚本辅助：文件移动、格式转换等机械操作
- 知识图谱：作为查询工具，辅助快速定位

---

## 新架构设计

### 核心理念

```
对话驱动 > 自动化

人类判断 → 脚本执行 → 结果反馈
    ↑           ↓
    └──── 对话循环
```

**关键区别**：
- ❌ **旧架构**: 脚本自动判断 → 执行 → 用户审核
- ✅ **新架构**: 对话理解意图 → 用户决策 → 脚本执行机械操作

---

## 三层架构

### 第1层：对话引导层 (SKILL.md)

**职责**：
- 引导用户通过对话完成文档管理
- 告诉用户如何使用知识图谱查询
- 提供对话模板和示例

**不包含**：
- ❌ 复杂的自动化工作流
- ❌ 判断逻辑（优先级、归档决策）
- ❌ 正则表达式和模式匹配

**示例**：
```markdown
## 场景1: 提取经验

**对话流程**：

用户: "我刚修复了React Hooks的bug，学到了一个经验"

Claude: "我理解了。让我帮你记录这个经验。首先，让我查询知识图谱看看是否有相关经验..."

/kg:query "React Hooks"

Claude: "我找到了3个相关经验：
- 经验1: Hooks规则遵守
- 经验2: 顺序很重要
- 经验3: 避免条件返回

这是新经验还是与现有经验相关？"
```

### 第2层：知识图谱查询层 (kg_helper.py)

**保留的脚本功能**：

```python
# kg_helper.py (~200行)

def query_related_context(query: str) -> List[Dict]:
    """
    查询相关知识图谱节点

    用于对话中快速定位相关文档、解决方案、概念
    """
    from kg.core.query_engine import QueryEngine
    engine = QueryEngine(project_root)

    # 查找相关文档、解决方案、概念
    related_docs = engine.search_by_keyword(query, "document")[:5]
    related_solutions = engine.search_by_keyword(query, "solution")[:5]
    related_concepts = engine.search_by_keyword(query, "concept")[:5]

    return {
        "documents": related_docs,
        "solutions": related_solutions,
        "concepts": related_concepts
    }

def visualize_connections(node_id: str, depth: int = 2):
    """
    可视化节点的关联关系

    帮助用户理解文档之间的关系
    """
    # 获取相关节点
    # 生成可视化图表
    pass

def add_solution_node(
    title: str,
    problem: str,
    solution: str,
    category: str,
    priority: str,
    tags: List[str]
):
    """
    添加解决方案节点到知识图谱

    在对话中添加经验后调用此函数
    """
    # 创建节点
    # 创建边
    # 保存到JSON
    pass
```

**保留原因**：
- ✅ 知识图谱查询是机械操作（搜索、过滤）
- ✅ 不涉及判断和决策
- ✅ 辅助对话，不替代对话

### 第3层：文件操作层 (file_operations.py)

**保留的脚本功能**：

```python
# file_operations.py (~100行)

def move_to_archive(doc_path: Path, archive_dir: Path):
    """
    移动文档到归档目录

    机械操作：不判断是否应该归档
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(doc_path), str(archive_dir / doc_path.name))
    print(f"✅ 已归档: {doc_path.name} → {archive_dir}")

def update_index_file(docs_dir: Path, index_path: Path):
    """
    更新索引文件

    机械操作：列出文件，不做"智能"解析
    """
    md_files = list(docs_dir.rglob("*.md"))

    content = "# 文档索引\n\n"
    for md_file in sorted(md_files):
        relative_path = md_file.relative_to(docs_dir)
        content += f"- {relative_path}\n"

    index_path.write_text(content, encoding="utf-8")
    print(f"✅ 已更新索引: {len(md_files)} 个文档")

def add_experience_to_doc(
    experience: Dict[str, Any],
    target_doc: Path
):
    """
    添加经验到文档

    机械操作：格式化并追加内容
    """
    content = format_experience(experience)

    # 读取现有内容
    existing = target_doc.read_text(encoding="utf-8")

    # 插入到 ## Archive 之前
    if "## Archive" in existing:
        new_content = existing.replace("## Archive", content + "\n\n## Archive")
    else:
        new_content = existing + "\n\n" + content

    target_doc.write_text(new_content, encoding="utf-8")
    print(f"✅ 已添加经验到: {target_doc.name}")
```

**保留原因**：
- ✅ 文件移动是机械操作
- ✅ 格式转换是机械操作
- ✅ 不涉及判断和决策

---

## 删除的组件

### ❌ Experience Extractor (888行)

**问题**：
```python
# 用正则表达式提取优先级
if "P0" in content[:500]:
    return "P0"
```

**应该方式**：
```
用户: "这是P0级别的经验"
```

### ❌ Auto Archiver (371行)

**问题**：
```python
# 用正则匹配文件名判断是否临时
if re.search(r"temp", name):
    return True
```

**应该方式**：
```
用户: "这个报告是临时的，归档它"
```

### ❌ Index Generator (448行)

**问题**：
```python
# 读取前10行查找 "# " 标记
for line in content.split("\n")[:10]:
    if line.startswith("# "):
        return line.lstrip("# ").strip()
```

**应该方式**：
```
Claude: "我发现这个文档的标题是'XXX'，是否正确？"
用户: "正确" 或 "应该是'YYY'"
```

### ❌ Workflow Orchestrator (557行)

**问题**：
```python
# 试图自动化所有7个阶段
phases = [
    "experience_extraction",  # ❌ 自动提取
    "auto_archiving",           # ❌ 自动归档
    "index_updates",           # ❌ 自动更新索引
]
```

**应该方式**：
```
用户: "帮我归档这个文档"
Claude: "好的，我帮你归档。需要归档到哪个目录？"
```

---

## 对话流程设计

### 场景1: 提取新经验

```markdown
**用户**: "我刚修复了React Hooks的bug，学到了一个经验"

**Claude**:
"我理解了。让我帮你记录这个经验。

首先，让我查询知识图谱看看是否有相关经验...

/kg:query "React Hooks"

找到了3个相关经验：
1. Hooks规则遵守 (react-best-practices.md)
2. 顺序很重要 (react-best-practices.md)
3. 避免条件返回 (react-best-practices.md)

请描述一下：
1. **问题症状**是什么？
2. **根本原因**是什么？
3. **解决方案**是什么？"

**用户**: "症状是组件崩溃，原因是Hook在条件返回之后调用，解决方案是把所有Hook移到条件返回之前"

**Claude**:
"明白了。让我确认一下经验信息：

**标题**: React Hooks调用顺序
**问题**: Hook在条件返回之后调用导致React检测到Hooks数量不一致
**解决方案**: 将所有Hook调用移到条件返回之前
**类别**: React Best Practices
**优先级**: P0（常见且严重的问题）
**标签**: ['react', 'hooks', 'crash']

是否正确？我添加到经验文档后，会更新知识图谱。"

**用户**: "正确"

**Claude**:
"好的，让我添加经验...

[调用 file_operations.add_experience_to_doc()]

✅ 已添加经验到: docs/lessons-learned/react-best-practices.md

现在更新知识图谱...
[调用 kg_helper.add_solution_node()]

✅ 已更新知识图谱: +1节点, +3条边

完成！"
```

### 场景2: 归档文档

```markdown
**用户**: "这个报告过时了，需要归档"

**Claude**:
"好的。让我查询知识图谱看看这个文档的引用情况...

/kg:related doc:old-report

找到了2个引用：
1. api-design-patterns.md 引用了这个报告
2. test-fix-iteration.md 引用了这个报告

归档后需要：
1. 移动到 docs/archive/reports/2026-03/
2. 更新引用文档
3. 更新文档索引

是否继续？"

**用户**: "继续"

**Claude**:
"好的，开始归档...

[调用 file_operations.move_to_archive()]

✅ 已归档: old-report.md → docs/archive/reports/2026-03/

现在更新引用...
[手动更新引用文档或调用脚本]

✅ 已更新引用

完成！"
```

---

## 知识图谱的正确使用

### ✅ 正确使用

**1. 快速定位相关内容**
```
/kg:query "React Hooks"
→ 返回相关文档、解决方案、概念
```

**2. 发现关联关系**
```
/kg:related doc:react-best-practices
→ 返回引用的文档、相关的解决方案
```

**3. 可视化知识网络**
```
/kg:visualize --center doc:react-best
→ 显示以该文档为中心的关联网络
```

### ❌ 错误使用

**1. 不要用知识图谱自动判断优先级**
```python
# ❌ 错误
priority = calculate_priority_from_graph(node)
# 应该：用户在对话中说明优先级
```

**2. 不要用知识图谱自动决定归档**
```python
# ❌ 错误
if is_old_document(node):
    archive_document(node)
# 应该：用户在对话中决定是否归档
```

**3. 不要用知识图谱自动提取经验**
```python
# ❌ 错误
experiences = extract_from_graph_structure(doc)
# 应该：对话中理解和提取经验
```

---

## 实施计划

### Phase 1: 重写SKILL.md (第1天)
- 删除自动化工作流描述
- 添加对话引导流程
- 添加知识图谱查询示例
- 添加对话模板

### Phase 2: 简化脚本 (第2天)
- 删除: experience_extractor.py (888行)
- 删除: auto_archiver.py (371行)
- 删除: index_generator.py (448行)
- 删除: workflow_orchestrator.py (557行)
- 保留: kg_helper.py (新建, ~200行)
- 保留: file_operations.py (新建, ~100行)

### Phase 3: 测试验证 (第3天)
- 测试对话流程
- 测试知识图谱查询
- 测试文件操作脚本
- 验证功能完整性

---

## 成功标准

### 代码量
- ✅ 从5300行减少到500行 (-90%)
- ✅ SKILL.md从1284行减少到~500行
- ✅ 删除4个核心脚本 (2214行)

### 质量提升
- ✅ 优先级: 字符串匹配 → 用户判断
- ✅ 归档决策: 路径匹配 → 用户决策
- ✅ 经验质量: 正则提取 → 对话理解

### 维护成本
- ✅ 新增经验: 对话中添加 → 无需修改代码
- ✅ 适应新结构: 自动适应 → 无需修改规则
- ✅ 调试难度: 对话透明 → 降低调试难度

---

**文档版本**: 1.0.0
**生成时间**: 2026-03-24
**作者**: Claude (架构设计)
