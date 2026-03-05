#!/usr/bin/env python3
"""
Debug script for Games API 500 error

Directly tests GameRepository.find_all() to identify the exact error.
"""

import sys
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

try:
    from models.repositories.games import GameRepository
    from models.entities import GameEntity

    print("✅ 导入成功")

    # Test repository
    repo = GameRepository()
    print("✅ GameRepository 创建成功")

    # Test find_all
    games = repo.find_all()
    print(f"✅ find_all() 成功，返回 {len(games)} 个游戏")

    # Test first game
    if games:
        first_game = games[0]
        print(f"✅ 第一个游戏: {first_game.name} (GID: {first_game.gid})")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
