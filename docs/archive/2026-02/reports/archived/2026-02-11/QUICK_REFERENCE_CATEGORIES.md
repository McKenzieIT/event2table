# Quick Reference: Event Categories

## Available Category IDs

| ID | Category Name | Description | Typical Events |
|----|---------------|-------------|----------------|
| 1 | 登录/认证 | Login/Auth | user_login, user_logout, user_register |
| 2 | 游戏进度 | Progress | level_up, quest_complete, achievement_unlock |
| 3 | 经济/交易 | Economy/Trade | currency_get, currency_spend, item_trade |
| 4 | 社交/聊天 | Social/Chat | chat_message, friend_add, guild_join |
| 5 | 战斗/PVP | Battle/PVP | pvp_battle_end, pve_battle_end, arena_match |
| 6 | 系统 | System | config_update, system_notification, error_log |
| 7 | 充值/付费 | Payment | purchase_start, payment_success, order_create |
| 8 | 行为/点击 | Behavior | ui_click, page_view, feature_use |

## API Usage Examples

### Create Event with Category

```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "event_name": "user_login",
    "event_name_cn": "用户登录",
    "category_id": 1,
    "source_table": "ieu_ods.ods_log_login",
    "target_table": "dwd.dwd_user_login_di"
  }'
```

### List All Categories

```bash
curl -X GET http://localhost:5000/api/categories
```

### Create Custom Category

```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "自定义分类"
  }'
```

## Database Direct Query

```sql
-- View all categories with event counts
SELECT
    ec.id,
    ec.name,
    COUNT(DISTINCT le.id) as event_count
FROM event_categories ec
LEFT JOIN log_events le ON ec.id = le.category_id
GROUP BY ec.id
ORDER BY ec.id;
```

## Scripts

### Seed Categories (if needed)
```bash
python3 scripts/seed_categories.py
```

### Initialize Database with Categories
```python
from backend.core.database import init_db
init_db()  # Automatically seeds categories
```

---
For detailed documentation, see: `CATEGORIES_SEED_SUMMARY.md`
