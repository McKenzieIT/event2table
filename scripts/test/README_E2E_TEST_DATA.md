# E2E Test Data Setup Guide

## Overview

The `setup_e2e_test_data.py` script creates and maintains test data for E2E (End-to-End) testing. It ensures the database has the necessary data for running E2E tests.

## What Test Data is Created?

### 1. Game: STAR001
- **GID**: 10000147
- **Name**: STAR001
- **ODS Database**: ieu_ods (✅ validated - NOT "test_db")
- **DWD Prefix**: dwd

### 2. Test Events

| Event Name | Chinese Name | Parameters |
|------------|--------------|------------|
| login | 登录 | role_id, account_id, zone_id, level |
| register | 注册 | account_id, device_id, channel |
| battle | 战斗 | role_id, battle_id, result, duration |
| recharge | 充值 | (existing - 34 parameters) |

### 3. Test Parameters

Each event includes relevant parameters:
- **base** parameters: Basic fields from ODS layer
- **param** parameters: JSON fields extracted with json_path

## Usage

### Basic Usage
```bash
# Activate virtual environment first!
source backend/venv/bin/activate

# Run the script (creates test data if missing)
python3 scripts/test/setup_e2e_test_data.py
```

### Dry Run Mode
```bash
# Preview what would be created without modifying database
python3 scripts/test/setup_e2e_test_data.py --dry-run
```

### Verbose Mode
```bash
# Show detailed output
python3 scripts/test/setup_e2e_test_data.py --verbose
```

### Combined Options
```bash
# Dry run with verbose output
python3 scripts/test/setup_e2e_test_data.py --dry-run --verbose
```

## Idempotency

The script is **idempotent** - safe to run multiple times:
- ✅ Only creates data if it doesn't exist
- ✅ Skips existing data (no duplicates)
- ✅ Updates invalid data (e.g., wrong ods_db)

## What Gets Updated?

### First Run
- Creates game STAR001 (if missing)
- Creates 3 test events: login, register, battle
- Creates 11 test parameters

### Subsequent Runs
- Skips existing game
- Skips existing events
- Skips existing parameters
- Only creates missing data

## Validation

The script automatically validates:
- ✅ `ods_db` must be "ieu_ods" or "overseas_ods" (NOT "test_db")
- ✅ Game GID must be 10000147
- ✅ Events are linked to correct game
- ✅ Parameters are linked to correct events

## Output Example

```
============================================================
E2E Test Data Setup
============================================================

[1/4] Setting up game STAR001 (GID=10000147)...
  ✓ Game exists: STAR001 (GID=10000147, ODS_DB=ieu_ods)

[2/4] Setting up test events...
  ✓ Created event: login (ID=1982, 4 params)
  ✓ Created event: register (ID=1983, 3 params)
  ✓ Created event: battle (ID=1984, 4 params)

[3/4] Verifying test data...
  ✓ Game: STAR001 (GID=10000147, ODS_DB=ieu_ods)
  ✓ Event: login (登录) - 4 params
  ✓ Event: register (注册) - 3 params
  ✓ Event: battle (战斗) - 4 params
  ✓ Event: recharge (充值) - 34 params

[4/4] Setup Summary:
------------------------------------------------------------
  Games created: 0
  Games updated: 0
  Events created: 3
  Parameters created: 11

  Database state:
    Total games (GID=10000147): 1
    Total events (game_gid=10000147): 1906
    Total parameters (game_gid=10000147): 11

============================================================
E2E Test Data Setup Complete!
============================================================
```

## Integration with CI/CD

### Pre-Test Setup
Add to your test pipeline:

```bash
#!/bin/bash
# setup_e2e_tests.sh

# Activate virtual environment
source backend/venv/bin/activate

# Setup test data
python3 scripts/test/setup_e2e_test_data.py

# Run E2E tests
# ... your test commands here
```

## Troubleshooting

### Issue: "Game not found"
**Solution**: The script will automatically create the game. Just run it again.

### Issue: "Invalid ods_db value"
**Solution**: The script will automatically update ods_db from "test_db" to "ieu_ods".

### Issue: "Event already exists"
**Solution**: This is expected behavior. The script is idempotent and won't create duplicates.

## Database Location

The test data is created in:
```
/Users/mckenzie/Documents/event2table/data/dwd_generator.db
```

**⚠️ IMPORTANT**: This is the PRODUCTION database. The script uses `game_gid=10000147` which is the STAR001 test game. Do not modify the script to use other GIDs without updating the validation logic.

## Related Files

- Script: `/Users/mckenzie/Documents/event2table/scripts/test/setup_e2e_test_data.py`
- Database: `/Users/mckenzie/Documents/event2table/data/dwd_generator.db`
- Repositories: `/Users/mckenzie/Documents/event2table/backend/models/repositories/`
- Entities: `/Users/mckenzie/Documents/event2table/backend/models/entities.py`

## Support

For issues or questions:
1. Check the script output for error messages
2. Verify the database file exists and is writable
3. Ensure virtual environment is activated
4. Check that `game_gid=10000147` exists in the database
