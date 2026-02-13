#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed default categories for event classification

This script creates default event categories in the database.
These categories are essential for event creation and classification.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.utils import execute_write, fetch_all_as_dict
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Default categories for data warehouse events
DEFAULT_CATEGORIES = [
    {
        "name": "登录/认证",
        "name_en": "Login",
        "description": "用户登录和认证事件，包括登录、登出、注册等"
    },
    {
        "name": "游戏进度",
        "name_en": "Progress",
        "description": "玩家游戏进度事件，包括升级、任务完成、关卡解锁等"
    },
    {
        "name": "经济/交易",
        "name_en": "Economy",
        "description": "游戏经济和交易事件，包括货币获取、消费、交易等"
    },
    {
        "name": "社交/聊天",
        "name_en": "Social",
        "description": "社交互动事件，包括聊天、好友、公会、组队等"
    },
    {
        "name": "战斗/PVP",
        "name_en": "Battle",
        "description": "战斗相关事件，包括PVP战斗、PVE战斗、竞技场等"
    },
    {
        "name": "系统",
        "name_en": "System",
        "description": "系统事件，包括配置更新、系统通知、错误日志等"
    },
    {
        "name": "充值/付费",
        "name_en": "Payment",
        "description": "充值和付费相关事件，包括购买、订单、支付回调等"
    },
    {
        "name": "行为/点击",
        "name_en": "Behavior",
        "description": "用户行为追踪事件，包括UI点击、页面访问、功能使用等"
    }
]


def seed_categories():
    """Seed default categories into the database"""
    print("=" * 60)
    print("Seeding Default Event Categories")
    print("=" * 60)

    # Check existing categories
    existing = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY id")
    if existing:
        print(f"\nFound {len(existing)} existing categories:")
        for cat in existing:
            print(f"  - ID {cat['id']}: {cat['name']}")
        print("\nSkipping seeding. To re-seed, delete existing categories first.")
        return False

    # Insert default categories
    print(f"\nInserting {len(DEFAULT_CATEGORIES)} default categories:\n")

    for i, category in enumerate(DEFAULT_CATEGORIES, 1):
        try:
            execute_write(
                "INSERT INTO event_categories (name) VALUES (?)",
                (category["name"],)
            )
            print(f"  {i}. {category['name']} ({category['name_en']})")
            print(f"     {category['description']}\n")
        except Exception as e:
            logger.error(f"Failed to insert category '{category['name']}': {e}")
            print(f"  ERROR: Failed to insert {category['name']}: {e}\n")
            return False

    # Verify insertion
    result = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY id")
    print(f"Successfully seeded {len(result)} categories!")
    print("\nAvailable category IDs:")
    for cat in result:
        print(f"  - ID {cat['id']}: {cat['name']}")

    print("\n" + "=" * 60)
    print("Category seeding completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = seed_categories()
    sys.exit(0 if success else 1)
