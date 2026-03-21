#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：从原项目迁移数据到当前项目

原项目：/Users/mckenzie/Documents/opencode test/dwd_generator/dwd_generator.db
目标数据库：
  - 测试数据库：data/test_database.db
  - 开发数据库：data/dwd_generator_dev.db
"""

import sys
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.database.database import get_db_connection, get_db_path


def migrate_database(source_db_path: Path, target_db_path: Path, db_name: str):
    """
    迁移数据库从源到目标

    Args:
        source_db_path: 源数据库文件路径
        target_db_path: 目标数据库文件路径
        db_name: 数据库名称（用于日志）
    """
    print(f"\n{'='*60}")
    print(f"开始迁移：{db_name}")
    print(f"{'='*60}")
    print(f"源数据库: {source_db_path}")
    print(f"目标数据库: {target_db_path}")
    print(f"源文件大小: {source_db_path.stat().st_size / 1024 / 1024:.2f} MB")

    # 检查源数据库是否存在
    if not source_db_path.exists():
        print(f"❌ 源数据库不存在: {source_db_path}")
        return False

    # 备份目标数据库（如果存在）
    if target_db_path.exists():
        backup_path = target_db_path.with_suffix('.db.backup')
        print(f"📦 备份现有数据库到: {backup_path}")
        shutil.copy2(target_db_path, backup_path)

    # 复制数据库文件
    print(f"📋 复制数据库文件...")
    try:
        shutil.copy2(source_db_path, target_db_path)
        print(f"✅ 迁移完成: {db_name}")

        # 验证数据
        print(f"🔍 验证数据...")
        conn = get_db_connection(target_db_path)
        cursor = conn.cursor()

        # 统计游戏数量
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]

        # 统计事件数量
        cursor.execute("SELECT COUNT(*) FROM log_events")
        event_count = cursor.fetchone()[0]

        # 统计参数数量
        cursor.execute("SELECT COUNT(*) FROM event_params")
        param_count = cursor.fetchone()[0]

        conn.close()

        print(f"📊 数据验证:")
        print(f"   - 游戏数: {game_count}")
        print(f"   - 事件数: {event_count}")
        print(f"   - 参数数: {param_count}")

        if game_count > 0 and event_count > 0:
            print(f"✅ {db_name} 数据迁移成功！")
            return True
        else:
            print(f"⚠️  {db_name} 数据验证失败（数据为空）")
            return False

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False


def main():
    """主迁移流程"""
    print("\n" + "="*60)
    print("Event2Table 数据迁移工具")
    print("从原项目迁移数据到测试和开发数据库")
    print("="*60)

    # 源数据库（原项目）
    source_db = Path("/Users/mckenzie/Documents/opencode test/dwd_generator/dwd_generator.db")

    # 目标数据库
    test_db = PROJECT_ROOT / "data" / "test_database.db"
    dev_db = PROJECT_ROOT / "data" / "dwd_generator_dev.db"

    # 迁移到测试数据库
    test_success = migrate_database(source_db, test_db, "测试数据库")

    # 迁移到开发数据库
    dev_success = migrate_database(source_db, dev_db, "开发数据库")

    # 总结
    print(f"\n{'='*60}")
    print("迁移总结")
    print(f"{'='*60}")
    print(f"测试数据库: {'✅ 成功' if test_success else '❌ 失败'}")
    print(f"开发数据库: {'✅ 成功' if dev_success else '❌ 失败'}")

    if test_success and dev_success:
        print("\n🎉 所有数据库迁移完成！")
        print("\n📝 后续步骤:")
        print("1. 重启Flask服务器以使用新数据")
        print("2. 在浏览器中验证Dashboard显示正确的游戏和事件数量")
        print("3. 运行测试验证数据完整性")
        return 0
    else:
        print("\n❌ 部分迁移失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit(main())
