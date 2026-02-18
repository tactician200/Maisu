-- ============================================
-- BILBOT - Schema de Base de Datos
-- Proyecto: Chatbot Turístico Inteligente para Bilbao
-- Versión: 1.0
-- Fecha: 11 febrero 2026
-- ============================================

-- IMPORTANTE: Activar la extensión pgvector antes de ejecutar este script
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- TABLA 1: PLACES (Datos estructurados SQL)
-- ============================================
-- NOTA: Esta tabla debe crearse ANTES de places_embeddings (FK dependency)
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL, -- 'restaurante', 'museo', 'café', 'bar', etc.
    descripcion TEXT,
    descripcion_corta VARCHAR(500),
    direccion TEXT,
    barrio VARCHAR(100),
    coordenadas POINT, -- PostGIS si necesitas geo-queries
    telefono VARCHAR(50),
    horario JSONB,
    precio_medio DECIMAL(10,2),
    rango_precio VARCHAR(20), -- '€', '€€', '€€€'
    valoracion_local DECIMAL(3,2), -- 0.00 a 5.00
    tags TEXT[], -- Array de tags
    especialidad VARCHAR(255), -- Para restaurantes
    tipo_cocina VARCHAR(100),
    por_que_es_especial TEXT, -- Diferenciador clave
    historia_breve TEXT,
    es_trampa_turistica BOOLEAN DEFAULT FALSE,
    recomendado_por_locales BOOLEAN DEFAULT FALSE,
    website VARCHAR(255),
    instagram VARCHAR(255),
    imagenes JSONB, -- Array de URLs
    horario_especial JSONB, -- Festivos, eventos
    accesibilidad JSONB,
    idiomas_atencion TEXT[],
    acepta_reservas BOOLEAN,
    created_by VARCHAR(100), -- Para tracking de colaboradores
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para búsquedas SQL rápidas
CREATE INDEX idx_places_barrio ON places(barrio);
CREATE INDEX idx_places_tipo ON places(tipo);
CREATE INDEX idx_places_tags ON places USING GIN(tags);
CREATE INDEX idx_places_precio ON places(precio_medio);
CREATE INDEX idx_places_rating ON places(valoracion_local DESC);

-- ============================================
-- TABLA 2: EMBEDDINGS (RAG Vector Search)
-- ============================================
CREATE TABLE places_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'place', 'history', 'experience'
    source_id UUID REFERENCES places(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsqueda vectorial (HNSW = más rápido)
CREATE INDEX idx_places_embeddings_vector
ON places_embeddings
USING hnsw (embedding vector_cosine_ops);

-- Índice para filtros por metadata
CREATE INDEX idx_places_embeddings_metadata
ON places_embeddings
USING GIN (metadata);

-- ============================================
-- TABLA 3: HISTORIA VASCA (Contenido cultural)
-- ============================================
CREATE TABLE historia_vasca (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tema VARCHAR(255) NOT NULL,
    titulo VARCHAR(500) NOT NULL,
    contenido TEXT NOT NULL,
    contenido_corto TEXT,
    epoca VARCHAR(100), -- 'Medieval', 'Industrialización', 'Siglo XX', etc.
    fecha_inicio DATE,
    fecha_fin DATE,
    personajes_clave TEXT[],
    lugares_relacionados UUID[], -- Referencias a places
    tags TEXT[],
    categoria VARCHAR(100), -- 'historia', 'gastronomía', 'tradición', 'deporte'
    nivel_detalle VARCHAR(50), -- 'resumen', 'detallado', 'académico'
    fuentes TEXT[], -- Bibliografía
    idioma VARCHAR(10) DEFAULT 'es',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_historia_categoria ON historia_vasca(categoria);
CREATE INDEX idx_historia_epoca ON historia_vasca(epoca);
CREATE INDEX idx_historia_tags ON historia_vasca USING GIN(tags);

-- ============================================
-- TABLA 4: CHAT HISTORY (Memoria conversacional)
-- ============================================
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL, -- Identifica usuario/sesión
    message_type VARCHAR(20) NOT NULL, -- 'human' o 'ai'
    content TEXT NOT NULL,
    metadata JSONB, -- Idioma, intención detectada, etc.
    tokens_used INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_session ON chat_history(session_id, created_at DESC);

-- ============================================
-- TABLA 5: ANALYTICS (Métricas del chatbot)
-- ============================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL, -- 'conversation_start', 'query', 'recommendation', etc.
    event_data JSONB,
    user_satisfaction INTEGER, -- 1-5 rating (opcional)
    user_feedback TEXT,
    rag_retrieval_count INTEGER,
    rag_relevance_score DECIMAL(3,2),
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analytics_session ON analytics(session_id);
CREATE INDEX idx_analytics_event ON analytics(event_type, created_at DESC);

-- ============================================
-- TABLA 6: EXPRESIONES VASCAS (Personalidad)
-- ============================================
CREATE TABLE expresiones_vascas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expresion VARCHAR(255) NOT NULL,
    significado TEXT NOT NULL,
    contexto_uso TEXT, -- Cuándo/cómo usarla
    tipo VARCHAR(50), -- 'saludo', 'exclamación', 'coloquial', 'humor'
    frecuencia_uso VARCHAR(20), -- 'muy_común', 'común', 'ocasional'
    ejemplos JSONB, -- Array de ejemplos de uso
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- FUNCIONES AUXILIARES
-- ============================================

-- Función para búsqueda híbrida (vector + filtros SQL)
CREATE OR REPLACE FUNCTION search_places_hybrid(
    query_embedding VECTOR(1536),
    filter_barrio VARCHAR DEFAULT NULL,
    filter_tipo VARCHAR DEFAULT NULL,
    min_rating DECIMAL DEFAULT 0.0,
    max_precio DECIMAL DEFAULT 999.99,
    similarity_threshold DECIMAL DEFAULT 0.7,
    result_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    nombre VARCHAR,
    similarity DECIMAL,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pe.source_id,
        p.nombre,
        (1 - (pe.embedding <=> query_embedding))::DECIMAL(3,2) AS similarity,
        pe.metadata
    FROM places_embeddings pe
    JOIN places p ON pe.source_id = p.id
    WHERE
        (filter_barrio IS NULL OR p.barrio = filter_barrio)
        AND (filter_tipo IS NULL OR p.tipo = filter_tipo)
        AND p.valoracion_local >= min_rating
        AND p.precio_medio <= max_precio
        AND (1 - (pe.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY similarity DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener memoria conversacional
CREATE OR REPLACE FUNCTION get_chat_memory(
    p_session_id VARCHAR,
    message_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    message_type VARCHAR,
    content TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ch.message_type,
        ch.content,
        ch.created_at
    FROM chat_history ch
    WHERE ch.session_id = p_session_id
    ORDER BY ch.created_at DESC
    LIMIT message_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS PARA UPDATED_AT
-- ============================================

-- Función genérica para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para tablas con updated_at
CREATE TRIGGER update_places_updated_at BEFORE UPDATE ON places
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_places_embeddings_updated_at BEFORE UPDATE ON places_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_historia_vasca_updated_at BEFORE UPDATE ON historia_vasca
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VERIFICACIÓN DE INSTALACIÓN
-- ============================================

-- ============================================
-- FUNCIÓN MATCH PARA N8N VECTOR STORE
-- ============================================
-- Requerida por el nodo vectorStoreSupabase de n8n
CREATE OR REPLACE FUNCTION match_places_embeddings(
    query_embedding VECTOR(1536),
    match_count INTEGER DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pe.id,
        pe.content,
        pe.metadata,
        (1 - (pe.embedding <=> query_embedding))::FLOAT AS similarity
    FROM places_embeddings pe
    WHERE pe.metadata @> filter
    ORDER BY pe.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on sensitive tables
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Policy: service_role can do everything (n8n uses service_role key)
CREATE POLICY "Service role full access on chat_history"
    ON chat_history FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on analytics"
    ON analytics FOR ALL
    USING (auth.role() = 'service_role');

-- Policy: anon can only read places and historia (public data)
ALTER TABLE places ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access on places"
    ON places FOR SELECT
    USING (true);

ALTER TABLE historia_vasca ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access on historia_vasca"
    ON historia_vasca FOR SELECT
    USING (true);

ALTER TABLE expresiones_vascas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access on expresiones_vascas"
    ON expresiones_vascas FOR SELECT
    USING (true);

ALTER TABLE places_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read access on places_embeddings"
    ON places_embeddings FOR SELECT
    USING (true);

-- ============================================
-- VERIFICACIÓN FINAL
-- ============================================

-- Mensaje de éxito
DO $$
BEGIN
    RAISE NOTICE '✅ Schema de BILBOT creado exitosamente';
    RAISE NOTICE '📊 Tablas creadas: 6';
    RAISE NOTICE '🔍 Índices creados: 11';
    RAISE NOTICE '⚡ Funciones creadas: 3 (search_places_hybrid, get_chat_memory, match_places_embeddings)';
    RAISE NOTICE '🔒 RLS habilitado en: chat_history, analytics, places, historia_vasca, expresiones_vascas, places_embeddings';
    RAISE NOTICE '🎯 Listo para seed data';
END $$;
