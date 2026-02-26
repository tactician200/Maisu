-- ============================================
-- Seed: events (idempotent)
-- Version: 2026-02-23
-- Purpose: bootstrap 5 curated Bilbao events for the `events` table
-- Safe to rerun: YES (ON CONFLICT UPDATE)
-- ============================================

BEGIN;

-- Deterministic conflict target for rerunnable seeding.
-- Kept separate from performance indexes in migration file.
CREATE UNIQUE INDEX IF NOT EXISTS uq_events_title_start_at
    ON events (title, start_at);

INSERT INTO events (
    title,
    description,
    event_type,
    start_at,
    end_at,
    recurrence_rule,
    location_text,
    municipality,
    region,
    tags,
    price_info,
    source_url,
    source_confidence,
    status,
    last_verified_at
)
VALUES
    (
        'Aste Nagusia 2026 - Fuegos Artificiales',
        'Sesión principal de fuegos artificiales junto a la ría con zonas recomendadas de observación.',
        'fiesta_popular',
        '2026-08-22T20:30:00Z'::timestamptz,
        '2026-08-22T21:15:00Z'::timestamptz,
        NULL,
        'Paseo de Uribitarte, Bilbao',
        'Bilbao',
        'Bizkaia',
        ARRAY['fiestas','fuegos','verano','bilbao']::text[],
        'Gratis',
        'https://www.bilbao.eus/agenda',
        'high',
        'scheduled',
        NOW()
    ),
    (
        'Aste Nagusia 2026 - Concierto en Abandoibarra',
        'Concierto gratuito al aire libre dentro de la programación oficial de Aste Nagusia.',
        'concierto',
        '2026-08-24T19:00:00Z'::timestamptz,
        '2026-08-24T21:00:00Z'::timestamptz,
        NULL,
        'Abandoibarra, Bilbao',
        'Bilbao',
        'Bizkaia',
        ARRAY['musica','fiestas','aste-nagusia']::text[],
        'Gratis',
        'https://www.bilbao.eus/agenda',
        'medium',
        'scheduled',
        NOW()
    ),
    (
        'Mercado de la Ribera - Cata de producto local',
        'Cata guiada de producto vasco con enfoque en temporada y comercio local.',
        'gastronomia',
        '2026-03-14T11:00:00Z'::timestamptz,
        '2026-03-14T12:30:00Z'::timestamptz,
        NULL,
        'Mercado de la Ribera, Erribera Kalea, Bilbao',
        'Bilbao',
        'Bizkaia',
        ARRAY['gastronomia','mercado','local']::text[],
        '18 EUR',
        'https://www.bilbaoturismo.net/',
        'medium',
        'scheduled',
        NOW()
    ),
    (
        'Visita guiada - Casco Viejo histórico',
        'Recorrido interpretativo por las Siete Calles con contexto histórico y urbano.',
        'visita_guiada',
        '2026-04-11T09:30:00Z'::timestamptz,
        '2026-04-11T11:00:00Z'::timestamptz,
        'FREQ=WEEKLY;BYDAY=SA',
        'Plaza Nueva, Casco Viejo, Bilbao',
        'Bilbao',
        'Bizkaia',
        ARRAY['historia','casco-viejo','tour']::text[],
        '12 EUR',
        'https://www.bilbaoturismo.net/',
        'medium',
        'scheduled',
        NOW()
    ),
    (
        'Bilbao BBK Live 2026 - Jornada 1',
        'Primera jornada del festival con cartel internacional y programación nocturna.',
        'festival',
        '2026-07-09T16:00:00Z'::timestamptz,
        '2026-07-10T01:30:00Z'::timestamptz,
        NULL,
        'Kobetamendi, Bilbao',
        'Bilbao',
        'Bizkaia',
        ARRAY['festival','musica','verano']::text[],
        'Desde 65 EUR',
        'https://bilbaobbklive.com/',
        'high',
        'scheduled',
        NOW()
    )
ON CONFLICT (title, start_at)
DO UPDATE SET
    description = EXCLUDED.description,
    event_type = EXCLUDED.event_type,
    end_at = EXCLUDED.end_at,
    recurrence_rule = EXCLUDED.recurrence_rule,
    location_text = EXCLUDED.location_text,
    municipality = EXCLUDED.municipality,
    region = EXCLUDED.region,
    tags = EXCLUDED.tags,
    price_info = EXCLUDED.price_info,
    source_url = EXCLUDED.source_url,
    source_confidence = EXCLUDED.source_confidence,
    status = EXCLUDED.status,
    last_verified_at = NOW(),
    updated_at = NOW();

COMMIT;
