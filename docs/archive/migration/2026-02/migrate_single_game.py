#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：只保留游戏10000147的数据

原项目：/Users/mckenzie/Documents/opencode test/dwd_generator/dwd_generator.db
目标：清理数据，只保留游戏10000147及其关联的事件和参数
"""

import sys
import sqlite3
from pathlib import Path

# 添加项目根路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def clean_database(db_path: Path, db_name: str):
    """
    清理数据库，只保留游戏10000147的数据

    Args:
        db_path: 数据库文件路径
        db_name: 数据库名称
    """
    print(f"\n{'='*60}")
    print(f"清理数据库：{db_name}")
    print(f"{'='*60}")
    print(f"数据库: {db_path}")

    # 连接数据库
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 1. 统计清理前的数据
        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM log_events")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM event_params")
        total_params = cursor.fetchone()[0]

        print(f"\n📊 清理前统计:")
        print(f"   - 游戏数: {total_games}")
        print(f"   - 事件数: {total_events}")
        print(f"   - 参数数: {total_params}")

        # 2. 删除游戏10000147以外的游戏
        print(f"\n🗑️  删除游戏10000147以外的数据...")
        cursor.execute("DELETE FROM games WHERE gid != 10000147")
        deleted_games = cursor.rowcount

        # 3. 删除孤立的事件（通过game_gid关联）
        cursor.execute("""DELETE FROM log_events
            WHERE game_gid != 10000147
        """)
        deleted_events = cursor.rowcount

        # 4. 删除孤立的参数（通过event_id关联）
        cursor.execute("""DELETE FROM event_params
            WHERE event_id NOT IN (
                SELECT id FROM log_events WHERE game_gid = 10000147
            )
        """)
        deleted_params = cursor.rowcount

        # 5. 清理其他关联表
        # 清理event_node_configs
        cursor.execute("DELETE FROM event_node_configs WHERE game_gid != 10000147")

        # 清理flow_templates（使用game_id）
        cursor.execute("""DELETE FROM flow_templates
            WHERE game_id NOT IN (SELECT id FROM games WHERE gid = 10000147)
        """)

        # 提交更改
        conn.commit()

        print(f"\n✅ 清理完成:")
        print(f"   - 删除游戏: {deleted_games} 个")
        print(f"   - 删除事件: {deleted_events} 个")
        print(f"   - 删除参数: {deleted_params} 个")

        # 6. 验证清理后的数据
        print(f"\n🔍 验证清理后数据...")
        cursor.execute("SELECT COUNT(*) FROM games")
        final_games = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM log_events WHERE game_gid = 10000147")
        final_events = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT ep.id) FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = 10000147
        """)
        final_params = cursor.fetchone()[0]

        print(f"📊 清理后统计:")
        print(f"   - 游戏数: {final_games} (应为1)")
        print(f"   - 事件数: {final_events} (应为1903)")
        print(f"   - 参数数: {final_params}")

        if final_games == 1 and final_events == 1903:
            print(f"\n✅ {db_name} 数据清理成功！")
            return True
        else:
            print(f"\n⚠️  {db_name} 数据验证失败")
            return False

    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def main():
    """主清理流程"""
    print("\n" + "="*60)
    print("Event2Table 数据清理工具")
    print("只保留游戏10000147的数据，删除其他所有游戏")
    print("="*60)

    # 原项目数据库（完整数据源）
    source_db = Path("/Users/mckenzie/Documents/opencode test/dwd_generator/dwd_generator.db")

    # 目标数据库
    test_db = PROJECT_ROOT / "data" / "test_database.db"
    dev_db = PROJECT_ROOT / "data" / "dwd_generator_dev.db"

    # 从原项目复制完整数据
    print(f"\n📋 从原项目复制完整数据...")
    print(f"源: {source_db}")

    import shutil
    for target_db in [test_db, dev_db]:
        if target_db.exists():
            backup_path = target_db.with_suffix('.db.backup')
            print(f"备份现有 {target_db.name} -> {backup_path.name}")
            shutil.copy2(target_db, backup_path)

        print(f"复制到: {target_db}")
        shutil.copy2(source_db, target_db)

    # 清理测试数据库
    test_success = clean_database(test_db, "测试数据库")

    # 清理开发数据库
    dev_success = clean_database(dev_db, "开发数据库")

    # 总结
    print(f"\n{'='*60}")
    print("清理总结")
    print(f"{'='*60}")
    print(f"测试数据库: {'✅ 成功' if test_success else '❌ 失败'}")
    print(f"开发数据库: {'✅ 成功' if dev_success else '❌ 失败'}")

    if test_success and dev_success:
        print("\n🎉 所有数据库清理完成！")
        print("\n📝 后续步骤:")
        print("1. 重启Flask服务器")
        print("2. 验证Dashboard显示游戏10000147和1903个事件")
        print("3. 进行Dashboard页面性能优化")
        return 0
    else:
        print("\n❌ 部分清理失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit(main())
