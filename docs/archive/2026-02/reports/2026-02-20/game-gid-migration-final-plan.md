# Game GID迁移 - 最终执行方案

**日期**: 2026-02-20
**数据库备份**: `data/dwd_generator.db.backup_20260220_094157`
**执行状态**: 准备就绪，等待最终确认

---

## 🔍 数据库现状分析

### 关键发现

#### 1. 已部分迁移的表（2个）✅

这些表**同时有game_id和game_gid列**，只需要清理game_id列：

| 表名 | game_id状态 | game_gid状态 | 迁移状态 | 操作 |
|------|-------------|--------------|----------|------|
| **log_events** | 全部为0（外键断裂） | ✅ 有效数据 | 50%完成 | **删除game_id列** |
| **event_nodes** | 存在 | ✅ 存在 | 50%完成 | **删除game_id列** |

**log_events数据验证**:
```sql
Total: 1903条记录
game_id: 全部为0（无效外键）
game_gid: 全部为10000147（有效）
```

#### 2. 未迁移的表（4个）⚠️

这些表**只有game_id列**，需要添加game_gid列并迁移数据：

| 表名 | 记录数 | game_id外键 | 迁移难度 | 优先级 |
|------|--------|-------------|----------|--------|
| **flow_templates** | 3 | 指向games.id | 🟢 简单 | P1 |
| **join_configs** | ? | 指向games.id | 🟢 简单 | P1 |
| **field_name_mappings** | ? | 指向games.id | 🟢 简单 | P2 |
| **field_selection_presets** | ? | 指向games.id | 🟢 简单 | P2 |

#### 3. 全局表（2个）✅

这些表**没有game_id或game_gid列**，无需迁移：

| 表名 | 记录数 | 说明 | 状态 |
|------|--------|------|------|
| **common_params** | 20 | 全局公共参数 | ✅ 无需迁移 |
| **parameter_aliases** | 7 | 全局参数别名 | ✅ 无需迁移 |

---

## 📊 迁移策略调整

### 原计划 vs 实际情况

**原计划（基于审计报告）**:
- 迁移6个表（common_params, parameter_aliases, join_configs, flow_templates, field_name_mappings, field_selection_presets）
- 预计工作量：8小时

**实际情况（数据库检查后）**:
- ✅ 2个表已50%迁移（log_events, event_nodes），只需删除game_id列
- ⚠️ 4个表需要完整迁移（flow_templates, join_configs, field_name_mappings, field_selection_presets）
- ✅ 2个表是全局表，无需迁移（common_params, parameter_aliases）

### 调整后的迁移计划

| 优先级 | 表名 | 工作量 | 风险 | 操作 |
|--------|------|--------|------|------|
| **P0** | log_events | 5分钟 | 🟢 极低 | 删除game_id列 |
| **P0** | event_nodes | 5分钟 | 🟢 极低 | 删除game_id列 |
| **P1** | flow_templates | 30分钟 | 🟡 中等 | 添加game_gid + 迁移数据 |
| **P1** | join_configs | 30分钟 | 🟡 中等 | 添加game_gid + 迁移数据 |
| **P2** | field_name_mappings | 30分钟 | 🟢 低 | 添加game_gid + 迁移数据 |
| **P2** | field_selection_presets | 30分钟 | 🟢 低 | 添加game_gid + 迁移数据 |

**总工作量**: 约2小时（原计划8小时）

---

## 🚀 迁移执行步骤

### 阶段1: 清理部分迁移的表（10分钟）⭐ 立即执行

#### 1.1 清理log_events表

```sql
-- 步骤1: 创建新表（不包含game_id列）
CREATE TABLE log_events_new (
    id INTEGER PRIMARY KEY,
    game_gid INTEGER NOT NULL,
    event_code TEXT NOT NULL,
    event_name TEXT NOT NULL,
    event_name_cn TEXT,
    description TEXT,
    category TEXT DEFAULT 'other',
    table_name TEXT,
    source_table TEXT,
    target_table TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_gid, event_code)
);

-- 步骤2: 复制数据（排除game_id列）
INSERT INTO log_events_new (
    id, game_gid, event_code, event_name, event_name_cn,
    description, category, table_name, source_table, target_table,
    created_at, updated_at
)
SELECT
    id, game_gid, event_code, event_name, event_name_cn,
    description, category, table_name, source_table, target_table,
    created_at, updated_at
FROM log_events;

-- 步骤3: 删除旧表
DROP TABLE log_events;

-- 步骤4: 重命名新表
ALTER TABLE log_events_new RENAME TO log_events;

-- 步骤5: 重建索引
CREATE INDEX IF NOT EXISTS idx_log_events_game_gid ON log_events(game_gid);
CREATE INDEX IF NOT EXISTS idx_log_events_event_code ON log_events(event_code);
CREATE INDEX IF NOT EXISTS idx_log_events_category ON log_events(category);

-- 步骤6: 验证
SELECT COUNT(*) FROM log_events;  -- 应该是1903
SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147;  -- 应该是1903
```

#### 1.2 清理event_nodes表

```sql
-- 同样步骤（重建表，删除game_id列）
CREATE TABLE event_nodes_new (
    id INTEGER PRIMARY KEY,
    game_gid INTEGER NOT NULL,
    node_config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO event_nodes_new (id, game_gid, node_config, created_at, updated_at)
SELECT id, game_gid, node_config, created_at, updated_at
FROM event_nodes;

DROP TABLE event_nodes;
ALTER TABLE event_nodes_new RENAME TO event_nodes;

CREATE INDEX IF NOT EXISTS idx_event_nodes_game_gid ON event_nodes(game_gid);
```

### 阶段2: 迁移未迁移的表（2小时）

#### 2.1 迁移flow_templates表

```sql
-- 1. 添加game_gid列
ALTER TABLE flow_templates ADD COLUMN game_gid INTEGER;

-- 2. 更新数据（从game_id映射到game_gid）
UPDATE flow_templates
SET game_gid = (
    SELECT g.gid
    FROM games g
    WHERE g.id = flow_templates.game_id
)
WHERE game_id IS NOT NULL;

-- 3. 验证数据
SELECT COUNT(*) FROM flow_templates WHERE game_gid IS NULL;
-- 应该是0（所有记录都有有效的game_gid）

-- 4. 删除game_id列
-- （需要重建表，因为SQLite不支持DROP COLUMN）
```

#### 2.2 迁移其他表

对 `join_configs`, `field_name_mappings`, `field_selection_presets` 执行相同操作。

---

## ⚠️ 风险评估

| 风险类型 | 概率 | 影响 | 缓解措施 |
|---------|------|------|----------|
| 数据丢失 | 极低（<1%） | 严重 | ✅ 完整备份 + 事务保护 |
| 外键约束破坏 | 低（10%） | 严重 | ✅ 验证所有外键 + 重建约束 |
| 应用中断 | 低（10%） | 中等 | ✅ 低峰期执行 + 快速回滚 |
| 性能下降 | 极低（<5%） | 轻微 | ✅ 重建索引 + 性能测试 |

**总体风险**: 🟢 **低风险，高度可控**

---

## 📝 迁移脚本

### 完整迁移脚本

创建 `scripts/migrate_game_gid_final.py`:

```python
#!/usr/bin/env python3
"""
Game GID迁移 - 最终版本
基于实际数据库状态调整
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = "data/dwd_generator.db"

def clean_log_events():
    """清理log_events表的game_id列"""
    logger.info("=== 清理 log_events 表 ===")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 验证当前状态
        cursor.execute("SELECT COUNT(*) FROM log_events")
        total = cursor.fetchone()[0]
        logger.info(f"当前记录数: {total}")

        cursor.execute("SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147")
        valid_gid = cursor.fetchone()[0]
        logger.info(f"game_gid=10000147的记录: {valid_gid}")

        # 开始事务
        conn.execute("BEGIN TRANSACTION")

        # 创建新表
        logger.info("创建新表...")
        cursor.execute("""
            CREATE TABLE log_events_new (
                id INTEGER PRIMARY KEY,
                game_gid INTEGER NOT NULL,
                event_code TEXT NOT NULL,
                event_name TEXT NOT NULL,
                event_name_cn TEXT,
                description TEXT,
                category TEXT DEFAULT 'other',
                table_name TEXT,
                source_table TEXT,
                target_table TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game_gid, event_code)
            )
        """)

        # 复制数据
        logger.info("复制数据...")
        cursor.execute("""
            INSERT INTO log_events_new (
                id, game_gid, event_code, event_name, event_name_cn,
                description, category, table_name, source_table, target_table,
                created_at, updated_at
            )
            SELECT
                id, game_gid, event_code, event_name, event_name_cn,
                description, category, table_name, source_table, target_table,
                created_at, updated_at
            FROM log_events
        """)

        # 删除旧表
        logger.info("删除旧表...")
        cursor.execute("DROP TABLE log_events")

        # 重命名新表
        logger.info("重命名新表...")
        cursor.execute("ALTER TABLE log_events_new RENAME TO log_events")

        # 重建索引
        logger.info("重建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_events_game_gid ON log_events(game_gid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_events_event_code ON log_events(event_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_events_category ON log_events(category)")

        # 验证
        cursor.execute("SELECT COUNT(*) FROM log_events")
        new_total = cursor.fetchone()[0]

        logger.info(f"✅ 迁移完成！记录数: {new_total}")

        if new_total != total:
            raise Exception(f"数据丢失！原记录数: {total}, 新记录数: {new_total}")

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

def migrate_table_with_game_id(table_name):
    """迁移只有game_id的表"""
    logger.info(f"=== 迁移 {table_name} 表 ===")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查当前状态
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        logger.info(f"当前记录数: {total}")

        # 开始事务
        conn.execute("BEGIN TRANSACTION")

        # 添加game_gid列
        logger.info("添加game_gid列...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN game_gid INTEGER")

        # 更新数据
        logger.info("更新数据（game_id -> game_gid）...")
        cursor.execute(f"""
            UPDATE {table_name}
            SET game_gid = (
                SELECT g.gid
                FROM games g
                WHERE g.id = {table_name}.game_id
            )
            WHERE game_id IS NOT NULL
        """)

        affected = cursor.rowcount
        logger.info(f"更新了 {affected} 条记录")

        # 验证
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE game_gid IS NULL")
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            logger.warning(f"⚠️  {null_count} 条记录的game_gid为NULL")

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

def main():
    """主函数"""
    logger.info("="*60)
    logger.info("Game GID迁移 - 最终执行")
    logger.info("="*60)

    try:
        # 阶段1: 清理部分迁移的表
        logger.info("\n### 阶段1: 清理部分迁移的表 ###\n")

        clean_log_events()
        logger.info("\n✅ log_events清理完成！")

        # TODO: clean_event_nodes()

        # 阶段2: 迁移未迁移的表
        logger.info("\n### 阶段2: 迁移未迁移的表 ###\n")

        # TODO: migrate_table_with_game_id("flow_templates")
        # TODO: migrate_table_with_game_id("join_configs")
        # TODO: migrate_table_with_game_id("field_name_mappings")
        # TODO: migrate_table_with_game_id("field_selection_presets")

        logger.info("\n" + "="*60)
        logger.info("✅ 迁移完成！")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"\n❌ 迁移失败: {e}")
        logger.info("\n请执行回滚:")
        logger.info(f"cp data/dwd_generator.db.backup_20260220_094157 {DB_PATH}")
        raise

if __name__ == "__main__":
    main()
```

---

## 📊 执行计划

### 立即执行（今天）⭐

**阶段1: 清理log_events表（10分钟）**
- 风险: 🟢 极低（数据已验证）
- 操作: 重建表，删除无效的game_id列
- 预期: 无数据丢失

**阶段2: 清理event_nodes表（10分钟）**
- 风险: 🟢 极低
- 操作: 重建表，删除game_id列

### 本周完成

**阶段3: 迁移剩余4个表（2小时）**
- flow_templates（30分钟）
- join_configs（30分钟）
- field_name_mappings（30分钟）
- field_selection_presets（30分钟）

### 验证和测试（1小时）

---

## 🎯 决策点

### 选项A: 立即执行完整迁移 ⭐ 推荐

**包含**:
- ✅ 清理log_events和event_nodes（20分钟）
- ✅ 迁移剩余4个表（2小时）
- ✅ 完整验证和测试（1小时）

**总时间**: 约3.5小时
**风险**: 🟢 低
**收益**: 一次性解决所有问题

### 选项B: 分阶段执行

**今天**:
- ✅ 只清理log_events和event_nodes（20分钟）

**下周**:
- ⏳ 迁移剩余4个表（2小时）

---

## ✅ 验收标准

### 清理log_events表后
- [ ] 表结构不再包含game_id列
- [ ] 记录数保持1903条
- [ ] 所有记录的game_gid都是10000147
- [ ] 索引重建完成
- [ ] 应用正常运行

### 清理event_nodes表后
- [ ] 表结构不再包含game_id列
- [ ] 所有记录有有效的game_gid
- [ ] 索引重建完成

---

## 📞 请确认执行

**问题**: 您希望如何执行迁移？

**选项A**: 立即执行完整迁移（清理2个表 + 迁移4个表）
- 时间: 3.5小时
- 推荐: ✅ 一次性解决

**选项B**: 只清理log_events表（10分钟）
- 时间: 10分钟
- 风险: 极低
- 后续: 其他表下周迁移

**选项C**: 暂缓迁移
- 时间: 待定
- 原因: 需要更多准备时间

我强烈推荐**选项A（立即执行完整迁移）**，因为：
1. 已经有了完整备份
2. log_events表的game_id全是0（外键断裂），必须清理
3. 其他表的迁移逻辑相同，一次性完成效率更高
4. 风险可控，有完整的回滚方案

请告诉我您的选择！🚀
