-- 005_add_kpi_entities.sql — GraphRAG-lite sidecar table.
-- Entities are extracted from each KPI record at ingestion time (see src/data/seed.py
-- and pg_store.store_kpi_entities) and used for multi-hop entity-overlap retrieval
-- when USE_GRAPH_RAG is enabled. Also created idempotently by pg_store.init_pg_tables().

CREATE TABLE IF NOT EXISTS kpi_entities (
    id            SERIAL PRIMARY KEY,
    record_ref    TEXT NOT NULL,   -- "category|metric|period"
    entity_type   TEXT NOT NULL,   -- department | category | period | metric sub-entity
    entity_value  TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kpi_entities_ref ON kpi_entities(record_ref);
