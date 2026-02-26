-- ============================================
-- Migration: Option B - Dedicated events table
-- Date: 2026-02-23
-- ============================================

BEGIN;

-- 1) Events table (structured SQL source of truth)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(100) NOT NULL,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ,
    recurrence_rule TEXT,
    location_text TEXT,
    place_id UUID REFERENCES places(id) ON DELETE SET NULL,
    municipality VARCHAR(120),
    region VARCHAR(120),
    tags TEXT[] DEFAULT '{}',
    price_info VARCHAR(255),
    source_url TEXT,
    source_confidence VARCHAR(20) DEFAULT 'medium'
        CHECK (source_confidence IN ('low', 'medium', 'high')),
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'cancelled', 'completed')),
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT events_time_window_chk CHECK (end_at IS NULL OR end_at >= start_at)
);

-- 2) Query-performance indexes
CREATE INDEX IF NOT EXISTS idx_events_date_range ON events(start_at, end_at);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_municipality ON events(municipality);
CREATE INDEX IF NOT EXISTS idx_events_tags ON events USING GIN(tags);

-- 3) updated_at automation
-- Reuses shared function from schema.sql:
--   update_updated_at_column()
DROP TRIGGER IF EXISTS update_events_updated_at ON events;
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 4) RLS policy aligned with existing public-data style
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'events'
          AND policyname = 'Public read access on events'
    ) THEN
        CREATE POLICY "Public read access on events"
            ON events FOR SELECT
            USING (true);
    END IF;
END $$;

-- 5) Compatibility note (no breakage):
-- Existing n8n match function `match_places_embeddings(...)` remains unchanged.
-- This migration does not alter signature/behavior of current match functions.

COMMIT;
