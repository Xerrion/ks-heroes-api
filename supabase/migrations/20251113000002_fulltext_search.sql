-- Enable full-text search and additional performance features
-- Created: 2025-11-13

BEGIN;

-- Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN index for full-text search on hero names
CREATE INDEX IF NOT EXISTS idx_heroes_name_trgm ON heroes USING gin(name gin_trgm_ops);

-- Create GIN index for skill descriptions (useful for searching by effect)
CREATE INDEX IF NOT EXISTS idx_hero_skills_description_trgm ON hero_skills USING gin(description gin_trgm_ops);

-- Add text search configuration
ALTER TABLE heroes ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create function to update search vector
CREATE OR REPLACE FUNCTION heroes_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := 
    setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.hero_id_slug, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.class::text, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(NEW.rarity::text, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic search vector updates
DROP TRIGGER IF EXISTS heroes_search_vector_trigger ON heroes;
CREATE TRIGGER heroes_search_vector_trigger
  BEFORE INSERT OR UPDATE ON heroes
  FOR EACH ROW EXECUTE FUNCTION heroes_search_vector_update();

-- Create GIN index on search vector
CREATE INDEX IF NOT EXISTS idx_heroes_search_vector ON heroes USING gin(search_vector);

-- Update existing rows
UPDATE heroes SET search_vector = 
  setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
  setweight(to_tsvector('english', COALESCE(hero_id_slug, '')), 'B') ||
  setweight(to_tsvector('english', COALESCE(class::text, '')), 'C') ||
  setweight(to_tsvector('english', COALESCE(rarity::text, '')), 'C');

COMMIT;
