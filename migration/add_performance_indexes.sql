-- Performance Optimization Indexes for Parameters API
-- Created: 2026-02-11
-- Purpose: Optimize GET /api/parameters/all endpoint (70% performance improvement target)

-- ============================================================================
-- Index 1: Optimize the main GROUP BY query in /api/parameters/all
-- ============================================================================
-- Query pattern:
--   SELECT ep.param_name, MIN(ep.param_name_cn), pt.base_type, COUNT(*)
--   FROM event_params ep
--   JOIN log_events le ON ep.event_id = le.id
--   LEFT JOIN param_templates pt ON ep.template_id = pt.id
--   WHERE le.game_gid = ? AND ep.is_active = 1
--   GROUP BY ep.param_name, pt.base_type
--
-- This composite index optimizes:
-- 1. WHERE clause filtering (is_active)
-- 2. JOIN with log_events (event_id)
-- 3. JOIN with param_templates (template_id)
-- 4. GROUP BY clustering (param_name)
--
-- Expected benefit: 70-80% query time reduction by avoiding full table scans
CREATE INDEX IF NOT EXISTS idx_event_params_active_event_template_name
ON event_params(is_active, event_id, template_id, param_name);

-- ============================================================================
-- Index 2: Covering index for common parameter queries
-- ============================================================================
-- Optimizes queries that filter by game + active status and retrieve param details
-- Used by: /api/parameters/all, /api/parameters/common
CREATE INDEX IF NOT EXISTS idx_event_params_active_event_name
ON event_params(is_active, param_name, param_name_cn, template_id);

-- ============================================================================
-- Index 3: Optimize log_events table for game_gid lookups
-- ============================================================================
-- The log_events table needs fast lookup by game_gid for the JOIN
CREATE INDEX IF NOT EXISTS idx_log_events_game_gid_id
ON log_events(game_gid, id);

-- ============================================================================
-- Index 4: Optimize param_templates for base_type lookups
-- ============================================================================
-- Used by: /api/parameters/all type filter
CREATE INDEX IF NOT EXISTS idx_param_templates_base_type
ON param_templates(base_type);

-- ============================================================================
-- Performance Monitoring Query
-- ============================================================================
-- Run this to verify index usage:
-- EXPLAIN QUERY PLAN
-- SELECT
--     ep.param_name,
--     MIN(ep.param_name_cn) as param_name_cn,
--     pt.base_type,
--     COUNT(DISTINCT ep.event_id) as events_count,
--     COUNT(*) as usage_count
-- FROM event_params ep
-- JOIN log_events le ON ep.event_id = le.id
-- LEFT JOIN param_templates pt ON ep.template_id = pt.id
-- WHERE le.game_gid = '10000147' AND ep.is_active = 1
-- GROUP BY ep.param_name, pt.base_type
-- ORDER BY usage_count DESC
-- LIMIT 50;

-- Expected output should show:
-- |--SEARCH ep USING INDEX idx_event_params_active_event_template_name
-- |--SEARCH le USING INDEX idx_log_events_game_gid_id
