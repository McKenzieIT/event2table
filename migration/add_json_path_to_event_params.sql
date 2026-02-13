-- Migration: Add json_path column to event_params table
-- Date: 2026-02-10
-- Author: Schema Fix for event2table
--
-- Description:
-- This migration adds the json_path column to the event_params table to support
-- JSON path extraction for parameter fields in HQL generation.
--
-- The json_path field is used extensively in the HQL generation system to specify
-- how to extract parameter values from JSON event data using get_json_object().

-- Add json_path column (nullable for backward compatibility)
ALTER TABLE event_params ADD COLUMN json_path TEXT;

-- Create index on json_path for better query performance
CREATE INDEX IF NOT EXISTS idx_event_params_json_path ON event_params(json_path);

-- Verification query (commented out):
-- PRAGMA table_info(event_params);
