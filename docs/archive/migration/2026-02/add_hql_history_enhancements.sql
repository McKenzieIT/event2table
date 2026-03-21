-- ============================================================================
-- HQL History Table Enhancement Migration
-- ============================================================================
-- Purpose: Add hql_type and game_gid columns to support enhanced history management
-- Author: Event2Table Development Team
-- Date: 2026-02-17
-- ============================================================================

-- Step 1: Add new columns (must be done before creating indexes)
-- Add hql_type column to support different HQL types (select, ddl, dml, canvas)
ALTER TABLE hql_history ADD COLUMN hql_type TEXT DEFAULT 'select';

-- Add game_gid column to support filtering by game
ALTER TABLE hql_history ADD COLUMN game_gid INTEGER;

-- Add name_en and name_cn columns for better searchability
ALTER TABLE hql_history ADD COLUMN name_en TEXT;
ALTER TABLE hql_history ADD COLUMN name_cn TEXT;

-- Step 2: Create indexes for performance optimization (after columns exist)
CREATE INDEX IF NOT EXISTS idx_hql_history_type ON hql_history(hql_type);
CREATE INDEX IF NOT EXISTS idx_hql_history_user ON hql_history(user_id);
CREATE INDEX IF NOT EXISTS idx_hql_history_game ON hql_history(game_gid);
CREATE INDEX IF NOT EXISTS idx_hql_history_session ON hql_history(session_id);
CREATE INDEX IF NOT EXISTS idx_hql_history_created ON hql_history(created_at DESC);

-- Step 3: Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_hql_history_user_type ON hql_history(user_id, hql_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_hql_history_game_type ON hql_history(game_gid, hql_type, created_at DESC);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify new columns
SELECT sql FROM sqlite_master WHERE type='table' AND name='hql_history';

-- Verify indexes
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='hql_history' ORDER BY name;

-- Sample data test (optional)
-- UPDATE hql_history SET hql_type = 'select' WHERE hql_type IS NULL;
-- UPDATE hql_history SET game_gid = 10000147 WHERE game_gid IS NULL;
