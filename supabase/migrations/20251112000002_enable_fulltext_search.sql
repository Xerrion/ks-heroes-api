-- Enable full-text search capabilities for hero names

BEGIN;

-- Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Add trigram index for hero name search (fuzzy matching)
CREATE INDEX IF NOT EXISTS idx_heroes_name_trgm ON heroes USING gin(name gin_trgm_ops);

-- Add full-text search column with auto-update
ALTER TABLE heroes ADD COLUMN IF NOT EXISTS search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(hero_id_slug, '')), 'B')
  ) STORED;

-- Create GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_heroes_search_vector ON heroes USING gin(search_vector);

-- Full-text search RPC function
CREATE OR REPLACE FUNCTION search_heroes(
  p_query TEXT,
  p_limit INTEGER DEFAULT 20,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
  id UUID,
  hero_id_slug TEXT,
  name TEXT,
  rarity hero_rarity,
  generation INTEGER,
  class hero_class,
  image_path TEXT,
  rank REAL,
  total_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    h.id,
    h.hero_id_slug,
    h.name,
    h.rarity,
    h.generation,
    h.class,
    h.image_path,
    ts_rank(h.search_vector, plainto_tsquery('english', p_query)) AS rank,
    COUNT(*) OVER() AS total_count
  FROM heroes h
  WHERE h.search_vector @@ plainto_tsquery('english', p_query)
     OR h.name ILIKE '%' || p_query || '%'
     OR h.hero_id_slug ILIKE '%' || p_query || '%'
  ORDER BY rank DESC, h.name ASC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

COMMIT;
