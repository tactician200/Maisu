-- Migration: user personalization context storage
-- Target: Supabase / PostgreSQL

CREATE TABLE IF NOT EXISTS public.user_context (
  session_id text PRIMARY KEY,
  user_id uuid NULL,
  name text NULL,
  language text NULL,
  preferences jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Helpful lookup indexes
CREATE INDEX IF NOT EXISTS idx_user_context_user_id
  ON public.user_context (user_id)
  WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_context_language
  ON public.user_context (language)
  WHERE language IS NOT NULL;

-- JSONB index for preference-key lookups (e.g. preferences ? 'tone')
CREATE INDEX IF NOT EXISTS idx_user_context_preferences_gin
  ON public.user_context
  USING gin (preferences);

-- Keep updated_at fresh on updates
CREATE OR REPLACE FUNCTION public.set_user_context_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_user_context_updated_at ON public.user_context;

CREATE TRIGGER trg_user_context_updated_at
BEFORE UPDATE ON public.user_context
FOR EACH ROW
EXECUTE FUNCTION public.set_user_context_updated_at();
