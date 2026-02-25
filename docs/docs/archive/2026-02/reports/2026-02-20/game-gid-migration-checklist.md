# Game GID迁移检查清单

**日期**: 2026-02-20
**迁移范围**: 6个数据库表 + 相关代码
**预计时间**: 2-3个工作日

---

## 使用说明

### 如何使用此检查清单

1. **打印或复制此清单**
2. **每完成一项，勾选对应的checkbox**
3. **记录遇到的问题和解决方案**
4. **完成每个阶段后，进行验收**
5. **保存此清单作为迁移记录**

### 里程碑验收

- [ ] **准备阶段完成** → 才能开始Schema迁移
- [ ] **Schema迁移完成** → 才能开始代码迁移
- [ ] **代码迁移完成** → 才能开始测试
- [ ] **测试全部通过** → 才能部署到生产

---

## 阶段1: 准备 (预计2小时)

### 1.1 环境准备

- [ ] 备份生产数据库
  ```bash
  cp data/dwd_generator.db data/dwd_generator.db.backup_20260220
  ```
  - [ ] 验证备份文件存在
  - [ ] 检查备份文件大小（应该与原文件相近）
  - [ ] 备份文件路径: `__________________________`

- [ ] 创建迁移分支
  ```bash
  git checkout -b feature/game-gid-migration
  ```
  - [ ] 分支名称: `feature/game-gid-migration`
  - [ ] 分支创建自: `main`

- [ ] 创建开发数据库副本
  ```bash
  cp data/dwd_generator.db data/dwd_generator_dev.db
  ```
  - [ ] 用于开发和测试

### 1.2 工具准备

- [ ] 创建回滚脚本
  - [ ] 文件路径: `scripts/migrate/rollback_game_gid.py`
  - [ ] 测试回滚脚本可执行
  - [ ] 记录回滚步骤: `__________________________`

- [ ] 创建迁移追踪表
  ```sql
  CREATE TABLE migration_tracker (
      table_name TEXT PRIMARY KEY,
      migration_status TEXT,
      migrated_at TIMESTAMP,
      rollback_sql TEXT
  );
  ```

- [ ] 准备测试数据
  - [ ] 使用测试GID: `90000001`
  - [ ] 创建测试游戏记录
  - [ ] 创建测试事件记录
  - [ ] 创建测试参数记录

### 1.3 文档准备

- [ ] 阅读迁移分析报告
  - [ ] `docs/reports/2026-02-20/game-gid-migration-analysis.md`
  - [ ] 理解迁移步骤
  - [ ] 理解风险和缓解措施

- [ ] 阅读问题分类清单
  - [ ] `docs/reports/2026-02-20/game-gid-issues-classification.md`
  - [ ] 确认需要修复的18个问题
  - [ ] 确认275个假阳性无需修复

- [ ] 创建迁移日志
  - [ ] 文件路径: `docs/migration-log-20260220.md`
  - [ ] 记录迁移过程
  - [ ] 记录遇到的问题

### 阶段1验收

- [ ] 数据库备份完成
- [ ] 回滚脚本可执行
- [ ] 测试数据准备完成
- [ ] 迁移日志已创建
- [ ] 团队成员已通知

**验收人**: _______________
**验收时间**: _______________

---

## 阶段2: Schema迁移 (预计4小时)

### 2.1 P0表 - common_params (预计1小时)

- [ ] 2.1.1 添加game_gid列
  ```sql
  ALTER TABLE common_params ADD COLUMN game_gid TEXT;
  ```
  - [ ] 验证列已添加: `PRAGMA table_info(common_params)`
  - [ ] 记录列信息: `__________________________`

- [ ] 2.1.2 迁移数据
  ```sql
  UPDATE common_params cp
  SET game_gid = (
      SELECT g.gid FROM games g WHERE g.id = cp.game_id
  );
  ```
  - [ ] 验证数据完整性
  ```sql
  SELECT COUNT(*) FROM common_params WHERE game_gid IS NULL;
  ```
  - [ ] 预期结果: 0
  - [ ] 实际结果: _____

- [ ] 2.1.3 创建新表
  ```sql
  CREATE TABLE common_params_new (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      game_gid TEXT NOT NULL,
      param_name TEXT NOT NULL,
      param_name_cn TEXT,
      param_type TEXT,
      param_description TEXT,
      table_name TEXT,
      status TEXT DEFAULT 'active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      display_name TEXT,
      FOREIGN KEY (game_gid) REFERENCES games(gid) ON DELETE CASCADE,
      UNIQUE(game_gid, param_name)
  );
  ```
  - [ ] 验证表已创建

- [ ] 2.1.4 迁移数据到新表
  ```sql
  INSERT INTO common_params_new
  SELECT id, game_gid, param_name, param_name_cn, param_type,
         param_description, table_name, status, created_at,
         updated_at, display_name
  FROM common_params;
  ```
  - [ ] 验证行数: `SELECT COUNT(*) FROM common_params_new;`
  - [ ] 预期行数: _____
  - [ ] 实际行数: _____

- [ ] 2.1.5 删除旧表，重命名新表
  ```sql
  DROP TABLE common_params;
  ALTER TABLE common_params_new RENAME TO common_params;
  ```
  - [ ] 验证表结构: `PRAGMA table_info(common_params)`
  - [ ] 验证无game_id列
  - [ ] 验证有game_gid列

- [ ] 2.1.6 创建索引
  ```sql
  CREATE INDEX idx_common_params_game_gid ON common_params(game_gid);
  ```
  - [ ] 验证索引: `PRAGMA index_list(common_params)`

- [ ] 2.1.7 测试功能
  - [ ] 参数列表查询正常
  - [ ] 参数创建正常
  - [ ] 参数更新正常
  - [ ] 参数删除正常
  - [ ] 外键约束生效

### 2.2 P0表 - parameter_aliases (预计1小时)

- [ ] 2.2.1 添加game_gid列
- [ ] 2.2.2 迁移数据
- [ ] 2.2.3 创建新表
- [ ] 2.2.4 迁移数据到新表
- [ ] 2.2.5 删除旧表，重命名新表
- [ ] 2.2.6 创建索引
- [ ] 2.2.7 测试功能

**详细步骤**: 参考2.1（common_params）

### 2.3 P1表 - join_configs (预计30分钟)

- [ ] 2.3.1 添加game_gid列
- [ ] 2.3.2 迁移数据
- [ ] 2.3.3 创建新表（注意：无外键约束）
- [ ] 2.3.4 迁移数据到新表
- [ ] 2.3.5 删除旧表，重命名新表
- [ ] 2.3.6 创建索引
- [ ] 2.3.7 测试功能

**注意事项**: 此表无外键约束，迁移更简单

### 2.4 P1表 - flow_templates (预计30分钟)

- [ ] 2.4.1 添加game_gid列
- [ ] 2.4.2 迁移数据
- [ ] 2.4.3 创建新表（注意：无外键约束）
- [ ] 2.4.4 迁移数据到新表
- [ ] 2.4.5 删除旧表，重命名新表
- [ ] 2.4.6 创建索引
- [ ] 2.4.7 测试功能

**注意事项**: 此表无外键约束，迁移更简单

### 2.5 P2表 - field_name_mappings (预计30分钟)

- [ ] 2.5.1 添加game_gid列
- [ ] 2.5.2 迁移数据
- [ ] 2.5.3 创建新表
- [ ] 2.5.4 迁移数据到新表
- [ ] 2.5.5 删除旧表，重命名新表
- [ ] 2.5.6 创建索引
- [ ] 2.5.7 测试功能

### 2.6 P2表 - field_selection_presets (预计30分钟)

- [ ] 2.6.1 添加game_gid列
- [ ] 2.6.2 迁移数据
- [ ] 2.6.3 创建新表
- [ ] 2.6.4 迁移数据到新表
- [ ] 2.6.5 删除旧表，重命名新表
- [ ] 2.6.6 创建索引
- [ ] 2.6.7 测试功能

### 阶段2验收

- [ ] 所有6个表都有game_gid列
- [ ] 所有表都删除了game_id列
- [ ] 所有数据都已迁移
- [ ] 所有外键约束已创建
- [ ] 所有索引已创建
- [ ] 数据完整性检查通过
- [ ] 每个表的功能测试通过

**验收SQL**:
```sql
-- 检查所有表
SELECT name FROM sqlite_master WHERE type='table' AND name IN (
    'common_params', 'parameter_aliases', 'join_configs',
    'flow_templates', 'field_name_mappings', 'field_selection_presets'
);

-- 检查外键
SELECT * FROM pragma_foreign_key_list('common_params');
SELECT * FROM pragma_foreign_key_list('parameter_aliases');

-- 检查数据完整性
SELECT 'common_params' as table_name, COUNT(*) as total,
       SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END) as null_gid
FROM common_params
UNION ALL
SELECT 'parameter_aliases', COUNT(*),
       SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END)
FROM parameter_aliases;
```

**验收人**: _______________
**验收时间**: _______________

---

## 阶段3: 完成log_events和event_nodes迁移 (预计1小时)

### 3.1 log_events表

- [ ] 3.1.1 创建新表（只使用game_gid）
  ```sql
  CREATE TABLE log_events_new (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      game_gid TEXT NOT NULL,
      event_name TEXT NOT NULL,
      event_name_cn TEXT NOT NULL,
      category_id INTEGER,
      source_table TEXT NOT NULL,
      target_table TEXT NOT NULL,
      include_in_common_params INTEGER DEFAULT 1,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (game_gid) REFERENCES games(gid) ON DELETE CASCADE,
      FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE
  );
  ```

- [ ] 3.1.2 迁移数据
  ```sql
  INSERT INTO log_events_new
  SELECT id, game_gid, event_name, event_name_cn, category_id,
         source_table, target_table, include_in_common_params,
         created_at, updated_at
  FROM log_events;
  ```

- [ ] 3.1.3 删除旧表，重命名新表
  ```sql
  DROP TABLE log_events;
  ALTER TABLE log_events_new RENAME TO log_events;
  ```

- [ ] 3.1.4 创建索引
  ```sql
  CREATE INDEX idx_log_events_game_gid ON log_events(game_gid);
  ```

- [ ] 3.1.5 测试功能
  - [ ] 事件列表查询正常
  - [ ] 事件创建正常
  - [ ] 事件更新正常
  - [ ] 事件删除正常

### 3.2 event_nodes表

- [ ] 3.2.1 创建新表（只使用game_gid）
- [ ] 3.2.2 迁移数据
- [ ] 3.2.3 删除旧表，重命名新表
- [ ] 3.2.4 创建索引
- [ ] 3.2.5 测试功能

**详细步骤**: 参考3.1（log_events）

### 阶段3验收

- [ ] log_events只使用game_gid
- [ ] event_nodes只使用game_gid
- [ ] 两个表的game_id列已删除
- [ ] 外键约束正确（game_gid → games.gid）
- [ ] 功能测试通过

**验收人**: _______________
**验收时间**: _______________

---

## 阶段4: 代码迁移 (预计2小时)

### 4.1 Repository层

- [ ] 4.1.1 `backend/models/repositories/parameters.py`
  - [ ] 搜索所有`game_id`使用
  - [ ] 改为使用`game_gid`
  - [ ] 更新查询语句
  - [ ] 测试Repository方法

- [ ] 4.1.2 `backend/models/repositories/events.py`
  - [ ] 搜索所有`game_id`使用
  - [ ] 改为使用`game_gid`
  - [ ] 更新查询语句
  - [ ] 测试Repository方法

- [ ] 4.1.3 `backend/models/repositories/games.py`
  - [ ] 移除`get_game_for_update`等方法（如果使用game_id）
  - [ ] 简化查询逻辑

### 4.2 Service层

- [ ] 4.2.1 `backend/services/parameters/common_params.py`
  - [ ] 移除`game_id = game['id']`转换
  - [ ] 直接使用`game_gid`
  - [ ] 简化逻辑

- [ ] 4.2.2 `backend/services/parameters/parameter_aliases.py`
  - [ ] 移除`game_id = game['id']`转换
  - [ ] 直接使用`game_gid`
  - [ ] 简化逻辑

- [ ] 4.2.3 `backend/services/events/event_nodes.py`
  - [ ] 移除`game_id = game['id']`转换
  - [ ] 直接使用`game_gid`
  - [ ] 简化逻辑

- [ ] 4.2.4 `backend/services/event_node_builder/__init__.py`
  - [ ] 移除`game_id = game['id']`转换
  - [ ] 直接使用`game_gid`
  - [ ] 简化逻辑

### 4.3 API层

- [ ] 4.3.1 `backend/api/routes/parameters.py`
  - [ ] 移除`game_id`向后兼容参数
  - [ ] 只接受`game_gid`参数
  - [ ] 简化`resolve_game_context`调用
  - [ ] 更新API文档

- [ ] 4.3.2 `backend/api/routes/join_configs.py`
  - [ ] 移除`game_id`向后兼容参数
  - [ ] 只接受`game_gid`参数
  - [ ] 简化逻辑
  - [ ] 更新API文档

- [ ] 4.3.3 `backend/api/routes/_param_helpers.py`
  - [ ] 简化`resolve_game_context`函数
  - [ ] 移除`game_id`处理逻辑
  - [ ] 只返回`game_gid`

### 4.4 前端代码

- [ ] 4.4.1 搜索所有`game_id`使用
  ```bash
  cd frontend
  grep -r "game_id" src/
  ```

- [ ] 4.4.2 更新API调用
  - [ ] 将`game_id`参数改为`game_gid`
  - [ ] 更新响应处理
  - [ ] 更新类型定义

- [ ] 4.4.3 更新变量命名（可选）
  - [ ] `selected_game_id` → `selectedGameGid`
  - [ ] `game_id` → `gameGid`

### 阶段4验收

- [ ] 所有代码使用`game_gid`
- [ ] 向后兼容参数已移除
- [ ] 代码审查通过
- [ ] 单元测试通过

**验收命令**:
```bash
# 检查剩余game_id使用（应该只有注释和文档）
grep -r "game_id" backend/api/routes/ | grep -v "# " | grep -v "deprecated"
grep -r "game_id" backend/services/ | grep -v "# " | grep -v "deprecated"
```

**验收人**: _______________
**验收时间**: _______________

---

## 阶段5: 测试验证 (预计3小时)

### 5.1 单元测试

- [ ] 5.1.1 运行所有后端单元测试
  ```bash
  pytest backend/test/unit/ -v
  ```
  - [ ] 测试结果: _____ / _____ 通过
  - [ ] 失败测试: `__________________________`
  - [ ] 修复失败测试

- [ ] 5.1.2 运行Repository测试
  ```bash
  pytest backend/test/unit/repositories/ -v
  ```
  - [ ] 测试结果: _____ / _____ 通过

- [ ] 5.1.3 运行Service测试
  ```bash
  pytest backend/test/unit/services/ -v
  ```
  - [ ] 测试结果: _____ / _____ 通过

### 5.2 集成测试

- [ ] 5.2.1 运行所有集成测试
  ```bash
  pytest backend/test/integration/ -v
  ```
  - [ ] 测试结果: _____ / _____ 通过

- [ ] 5.2.2 API集成测试
  ```bash
  pytest backend/test/integration/api/ -v
  ```
  - [ ] 测试结果: _____ / _____ 通过

### 5.3 E2E测试

- [ ] 5.3.1 启动开发服务器
  ```bash
  # 后端
  python web_app.py

  # 前端
  cd frontend
  npm run dev
  ```

- [ ] 5.3.2 运行E2E测试
  ```bash
  cd frontend
  npm run test:e2e
  ```
  - [ ] 测试结果: _____ / _____ 通过
  - [ ] 失败测试: `__________________________`
  - [ ] 修复失败测试

### 5.4 功能测试

- [ ] 5.4.1 游戏管理
  - [ ] 游戏列表显示正常
  - [ ] 游戏创建正常
  - [ ] 游戏更新正常
  - [ ] 游戏删除正常

- [ ] 5.4.2 事件管理
  - [ ] 事件列表显示正常
  - [ ] 事件创建正常
  - [ ] 事件更新正常
  - [ ] 事件删除正常
  - [ ] 游戏过滤正常

- [ ] 5.4.3 参数管理
  - [ ] 参数列表显示正常
  - [ ] 参数创建正常
  - [ ] 参数更新正常
  - [ ] 参数删除正常
  - [ ] 游戏过滤正常

- [ ] 5.4.4 Canvas功能
  - [ ] Canvas加载正常
  - [ ] 节点创建正常
  - [ ] 节点连接正常
  - [ ] JOIN配置正常
  - [ ] HQL生成正常

- [ ] 5.4.5 HQL生成
  - [ ] 单事件HQL生成正常
  - [ ] JOIN事件HQL生成正常
  - [ ] UNION事件HQL生成正常

### 5.5 性能测试

- [ ] 5.5.1 查询性能对比
  - [ ] 游戏列表查询: _____ ms (迁移前) → _____ ms (迁移后)
  - [ ] 事件列表查询: _____ ms (迁移前) → _____ ms (迁移后)
  - [ ] 参数列表查询: _____ ms (迁移前) → _____ ms (迁移后)

- [ ] 5.5.2 外键约束性能
  - [ ] 插入性能: _____ ms (迁移前) → _____ ms (迁移后)
  - [ ] 更新性能: _____ ms (迁移前) → _____ ms (迁移后)
  - [ ] 删除性能: _____ ms (迁移前) → _____ ms (迁移后)

### 阶段5验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] E2E测试通过
- [ ] 功能测试通过
- [ ] 性能无明显下降

**验收人**: _______________
**验收时间**: _______________

---

## 阶段6: 清理和文档 (预计1小时)

### 6.1 清理

- [ ] 6.1.1 删除临时脚本
  - [ ] 删除测试脚本
  - [ ] 归档迁移脚本到`docs/archive/migration-20260220/`

- [ ] 6.1.2 清理代码注释
  - [ ] 移除`TODO: migration`注释
  - [ ] 移除`FIXME: game_id`注释
  - [ ] 移除调试代码

- [ ] 6.1.3 提交代码
  ```bash
  git add .
  git commit -m "feat: complete game_gid migration

  - Migrated 6 tables from game_id to game_gid
  - Updated all code to use game_gid
  - Removed backward compatibility parameters
  - All tests passing
  "
  ```

### 6.2 文档更新

- [ ] 6.2.1 更新CLAUDE.md
  - [ ] 移除game_id相关规范
  - [ ] 更新数据库schema文档
  - [ ] 更新迁移状态

- [ ] 6.2.2 更新架构文档
  - [ ] `docs/development/architecture.md`
  - [ ] 更新数据库schema图
  - [ ] 更新外键约束说明

- [ ] 6.2.3 更新API文档
  - [ ] `docs/api/README.md`
  - [ ] 移除game_id参数
  - [ ] 更新请求示例

- [ ] 6.2.4 创建迁移报告
  - [ ] `docs/reports/2026-02-20/migration-complete-report.md`
  - [ ] 记录迁移过程
  - [ ] 记录遇到的问题
  - [ ] 记录解决方案

### 6.3 团队培训

- [ ] 6.3.1 准备培训材料
  - [ ] 迁移概述PPT
  - [ ] 代码变更说明
  - [ ] 常见问题FAQ

- [ ] 6.3.2 团队培训会议
  - [ ] 日期: _______________
  - [ ] 参与人员: `__________________________`
  - [ ] 培训内容:
    - [ ] 迁移背景和目的
    - [ ] 数据库schema变更
    - [ ] 代码变更说明
    - [ ] 开发规范更新

- [ ] 6.3.3 培训反馈
  - [ ] 收集问题
  - [ ] 更新FAQ
  - [ ] 分享培训录像

### 阶段6验收

- [ ] 临时文件已清理
- [ ] 代码已提交
- [ ] 文档已更新
- [ ] 团队培训完成
- [ ] 迁移日志完整

**验收人**: _______________
**验收时间**: _______________

---

## 总体验收

### 数据库验收

- [ ] 所有10个核心表都已迁移
- [ ] 所有表都使用game_gid
- [ ] 所有外键约束正确
- [ ] 所有索引已创建
- [ ] 数据完整性100%
- [ ] 性能无明显下降

### 代码验收

- [ ] 0个game_id相关警告
- [ ] 向后兼容参数已移除
- [ ] 代码审查100%通过
- [ ] 单元测试100%通过
- [ ] 集成测试100%通过

### 功能验收

- [ ] 所有功能正常
- [ ] E2E测试100%通过
- [ ] 性能测试通过
- [ ] 用户验收测试通过

### 文档验收

- [ ] 所有文档已更新
- [ ] 迁移报告完整
- [ ] 团队培训完成
- [ ] 知识已传递

---

## 问题记录

### 遇到的问题

| # | 问题描述 | 发生时间 | 解决方案 | 解决时间 |
|---|---------|---------|---------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### 经验教训

1. `__________________________`
2. `__________________________`
3. `__________________________`

### 改进建议

1. `__________________________`
2. `__________________________`
3. `__________________________`

---

## 签名

**迁移负责人**: _______________
**完成日期**: _______________

**技术审查**: _______________
**审查日期**: _______________

**最终批准**: _______________
**批准日期**: _______________

---

## 附录

### A. 验收SQL脚本

```sql
-- 1. 检查所有表结构
SELECT
    name,
    sql
FROM sqlite_master
WHERE type='table'
AND name IN ('log_events', 'event_nodes', 'common_params',
             'parameter_aliases', 'join_configs', 'flow_templates',
             'field_name_mappings', 'field_selection_presets')
ORDER BY name;

-- 2. 检查外键约束
SELECT
    m.name as table_name,
    fk.*
FROM sqlite_master m
JOIN pragma_foreign_key_list(m.name) fk
WHERE m.type='table'
AND m.name IN ('log_events', 'event_nodes', 'common_params',
             'parameter_aliases', 'join_configs', 'flow_templates',
             'field_name_mappings', 'field_selection_presets');

-- 3. 检查数据完整性
SELECT
    'log_events' as table_name,
    COUNT(*) as total,
    SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END) as null_gid
FROM log_events
UNION ALL
SELECT 'event_nodes', COUNT(*),
       SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END)
FROM event_nodes
UNION ALL
SELECT 'common_params', COUNT(*),
       SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END)
FROM common_params
UNION ALL
SELECT 'parameter_aliases', COUNT(*),
       SUM(CASE WHEN game_gid IS NULL THEN 1 ELSE 0 END)
FROM parameter_aliases;

-- 4. 检查索引
SELECT
    name,
    tbl_name,
    sql
FROM sqlite_master
WHERE type='index'
AND tbl_name IN ('log_events', 'event_nodes', 'common_params',
                 'parameter_aliases', 'join_configs', 'flow_templates',
                 'field_name_mappings', 'field_selection_presets')
AND name LIKE '%game_gid%';
```

### B. 回滚脚本模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rollback Game GID Migration

This script rolls back the game_gid migration if needed.
"""

import sqlite3
import sys
from pathlib import Path

def rollback_migration(db_path: Path):
    """Rollback the migration"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # TODO: Implement rollback logic
        pass

        conn.commit()
        print("✅ Migration rolled back successfully")

    except Exception as e:
        conn.rollback()
        print(f"❌ Rollback failed: {e}")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    db_path = Path("data/dwd_generator.db")
    rollback_migration(db_path)
```

---

**检查清单版本**: 1.0
**最后更新**: 2026-02-20
**维护者**: Claude Code
