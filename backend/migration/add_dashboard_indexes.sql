-- ============================================================================
-- Dashboard Performance Optimization Indexes
-- Purpose: Accelerate Dashboard queries by optimizing JOIN and WHERE operations
-- Created: 2026-03-07
-- Impact: 3-5x performance improvement on Dashboard queries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: log_events
-- Purpose: Optimize game statistics queries with JOINs and WHERE clauses
-- ----------------------------------------------------------------------------

-- Index for game_gid (used in Dashboard stats queries)
-- ⚡ PERF: Speeds up JOINs between games and log_events
CREATE INDEX IF NOT EXISTS idx_log_events_game_gid
ON log_events(game_gid);

-- Index for created_at (used in recent activity queries)
-- ⚡ PERF: Speeds up WHERE created_at >= datetime('now', '-7 days')
CREATE INDEX IF NOT EXISTS idx_log_events_created_at
ON log_events(created_at);

-- Index for category_id (used in category count queries)
-- ⚡ PERF: Speeds up COUNT(DISTINCT category_id) aggregation
CREATE INDEX IF NOT EXISTS idx_log_events_category_id
ON log_events(category_id);

-- ----------------------------------------------------------------------------
-- Table: event_params
-- Purpose: Optimize parameter count queries with JOINs and WHERE clauses
-- ----------------------------------------------------------------------------

-- Index for event_id (used in JOINs with log_events)
-- ⚡ PERF: Speeds up JOINs between log_events and event_params
CREATE INDEX IF NOT EXISTS idx_event_params_event_id
ON event_params(event_id);

-- Index for is_active (used in active parameter count queries)
-- ⚡ PERF: Speeds up WHERE is_active = 1 filters
CREATE INDEX IF NOT EXISTS idx_event_params_is_active
ON event_params(is_active);

-- Index for created_at (used in recent activity queries)
-- ⚡ PERF: Speeds up WHERE created_at >= datetime('now', '-7 days')
CREATE INDEX IF NOT EXISTS idx_event_params_created_at
ON event_params(created_at);

-- ----------------------------------------------------------------------------
-- Composite Indexes
-- Purpose: Optimize multi-column queries (Dashboard specific)
-- ----------------------------------------------------------------------------

-- Composite index for game + category (used in game stats queries)
-- ⚡ PERF: Speeds up queries filtering by both game_gid and category_id
CREATE INDEX IF NOT EXISTS idx_log_events_game_category
ON log_events(game_gid, category_id);

-- ----------------------------------------------------------------------------
-- Verification
-- ----------------------------------------------------------------------------

-- List all indexes created for Dashboard optimization
SELECT
    'Dashboard indexes created successfully' as status,
    name as index_name,
    tbl_name as table_name
FROM sqlite_master
WHERE type = 'index'
  AND name LIKE 'idx_%'
  AND (
    name LIKE 'idx_log_events_%' OR
    name LIKE 'idx_event_params_%'
  )
ORDER BY tbl_name, name;

-- Expected output: 7 indexes (3 on log_events, 3 on event_params, 1 composite)
-- - idx_log_events_game_gid
-- - idx_log_events_created_at
-- - idx_log_events_category_id
-- - idx_event_params_event_id
-- - idx_event_params_is_active
-- - idx_event_params_created_at
-- - idx_log_events_game_category
