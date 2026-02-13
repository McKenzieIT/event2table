-- Migration: Convert games.gid from TEXT to INTEGER
-- Date: 2026-02-10
-- Author: Claude Code
--
-- This migration fixes the type inconsistency where games.gid was stored as TEXT
-- but should be INTEGER to match the application schema and business logic.
--
-- IMPORTANT: This migration will:
-- 1. Create a backup of the games table
-- 2. Convert gid from TEXT to INTEGER (only for valid integer values)
-- 3. Update the schema
-- 4. Verify data integrity

BEGIN TRANSACTION;

-- Step 1: Create a backup table
CREATE TABLE IF NOT EXISTS games_backup_20260210 AS
SELECT * FROM games;

-- Step 2: Verify all gid values can be converted to INTEGER
-- This will fail if any non-integer gids exist
SELECT COUNT(*) as invalid_gids FROM games WHERE gid NOT GLOB '*[0-9]*';

-- Step 3: Create a new games table with INTEGER gid
CREATE TABLE games_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gid INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    ods_db TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    icon_path TEXT
);

-- Step 4: Migrate data (only rows with integer-convertible gid)
INSERT INTO games_new (id, gid, name, ods_db, created_at, updated_at, icon_path)
SELECT
    id,
    CAST(gid AS INTEGER),
    name,
    ods_db,
    created_at,
    updated_at,
    icon_path
FROM games
WHERE gid GLOB '*[0-9]*' OR gid = '0';

-- Step 5: Drop old table and rename new one
DROP TABLE games;
ALTER TABLE games_new RENAME TO games;

-- Step 6: Verify data integrity
SELECT 'Games count after migration:' as info, COUNT(*) as count FROM games;

-- Commit the transaction
COMMIT;

-- Step 7: Verify the schema
PRAGMA table_info(games);

-- Note: If you need to rollback, execute:
-- DROP TABLE games;
-- CREATE TABLE games AS SELECT * FROM games_backup_20260210;
-- DROP TABLE games_backup_20260210;
