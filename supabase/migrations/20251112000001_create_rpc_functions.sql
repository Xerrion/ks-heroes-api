-- RPC functions for efficient querying with filters and pagination

BEGIN;

-- =============================================================================
-- EXCLUSIVE GEAR SKILL TIER CALCULATION
-- =============================================================================

-- Calculate skill tier based on gear level and skill number
-- Skill 1 (Conquest): Unlocks at level 1, upgrades at 3, 5, 7, 9 (odd levels)
-- Skill 2 (Expedition): Unlocks at level 2, upgrades at 4, 6, 8, 10 (even levels)
CREATE OR REPLACE FUNCTION calculate_skill_tier(gear_level INTEGER, skill_number INTEGER)
RETURNS INTEGER AS $$
BEGIN
  IF gear_level = 0 THEN
    RETURN 0; -- Not unlocked
  END IF;
  
  -- Skill 1 unlocks at level 1, upgrades at 3,5,7,9
  IF skill_number = 1 THEN
    IF gear_level % 2 = 1 THEN
      RETURN (gear_level + 1) / 2;
    ELSE
      -- Even level, skill 1 stays at previous tier
      RETURN gear_level / 2;
    END IF;
  
  -- Skill 2 unlocks at level 2, upgrades at 4,6,8,10
  ELSIF skill_number = 2 THEN
    IF gear_level >= 2 THEN
      IF gear_level % 2 = 0 THEN
        RETURN gear_level / 2;
      ELSE
        -- Odd level, skill 2 stays at previous tier
        RETURN (gear_level - 1) / 2;
      END IF;
    ELSE
      RETURN 0; -- Not unlocked yet
    END IF;
  END IF;
  
  RETURN 0;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================================================
-- HERO FILTERED QUERIES
-- =============================================================================

-- Get heroes with flexible filtering, sorting, and pagination
CREATE OR REPLACE FUNCTION get_heroes_filtered(
  p_name TEXT DEFAULT NULL,
  p_rarity hero_rarity DEFAULT NULL,
  p_class hero_class DEFAULT NULL,
  p_generation INTEGER DEFAULT NULL,
  p_sort_by TEXT DEFAULT 'name',
  p_sort_order TEXT DEFAULT 'asc',
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
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  total_count BIGINT
) AS $$
DECLARE
  order_clause TEXT;
  allowed_sort_columns TEXT[] := ARRAY['name', 'rarity', 'generation', 'class', 'created_at'];
BEGIN
  -- Validate sort column to prevent SQL injection
  IF p_sort_by = ANY(allowed_sort_columns) THEN
    order_clause := p_sort_by;
  ELSE
    order_clause := 'name';
  END IF;
  
  -- Validate sort order
  IF LOWER(p_sort_order) NOT IN ('asc', 'desc') THEN
    p_sort_order := 'asc';
  END IF;
  
  -- Build and execute query
  RETURN QUERY EXECUTE format('
    SELECT 
      h.id,
      h.hero_id_slug,
      h.name,
      h.rarity,
      h.generation,
      h.class,
      h.image_path,
      h.created_at,
      h.updated_at,
      COUNT(*) OVER() AS total_count
    FROM heroes h
    WHERE 
      ($1 IS NULL OR h.name ILIKE ''%%'' || $1 || ''%%'')
      AND ($2 IS NULL OR h.rarity = $2)
      AND ($3 IS NULL OR h.class = $3)
      AND ($4 IS NULL OR h.generation = $4)
    ORDER BY %I %s
    LIMIT $5 OFFSET $6
  ', order_clause, p_sort_order)
  USING p_name, p_rarity, p_class, p_generation, p_limit, p_offset;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- =============================================================================
-- STATS FILTERED QUERIES
-- =============================================================================

-- Get conquest stats with filtering
CREATE OR REPLACE FUNCTION get_conquest_stats_filtered(
  p_hero_slug TEXT DEFAULT NULL,
  p_min_attack INTEGER DEFAULT NULL,
  p_min_defense INTEGER DEFAULT NULL,
  p_min_health INTEGER DEFAULT NULL,
  p_sort_by TEXT DEFAULT 'attack',
  p_sort_order TEXT DEFAULT 'desc',
  p_limit INTEGER DEFAULT 20,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
  id UUID,
  hero_id UUID,
  attack INTEGER,
  defense INTEGER,
  health INTEGER,
  hero_slug TEXT,
  hero_name TEXT,
  total_count BIGINT
) AS $$
DECLARE
  order_clause TEXT;
  allowed_sort_columns TEXT[] := ARRAY['attack', 'defense', 'health'];
BEGIN
  IF p_sort_by = ANY(allowed_sort_columns) THEN
    order_clause := 'cs.' || p_sort_by;
  ELSE
    order_clause := 'cs.attack';
  END IF;
  
  IF LOWER(p_sort_order) NOT IN ('asc', 'desc') THEN
    p_sort_order := 'desc';
  END IF;
  
  RETURN QUERY EXECUTE format('
    SELECT 
      cs.id,
      cs.hero_id,
      cs.attack,
      cs.defense,
      cs.health,
      h.hero_id_slug AS hero_slug,
      h.name AS hero_name,
      COUNT(*) OVER() AS total_count
    FROM hero_conquest_stats cs
    JOIN heroes h ON h.id = cs.hero_id
    WHERE 
      ($1 IS NULL OR h.hero_id_slug = $1)
      AND ($2 IS NULL OR cs.attack >= $2)
      AND ($3 IS NULL OR cs.defense >= $3)
      AND ($4 IS NULL OR cs.health >= $4)
    ORDER BY %s %s
    LIMIT $5 OFFSET $6
  ', order_clause, p_sort_order)
  USING p_hero_slug, p_min_attack, p_min_defense, p_min_health, p_limit, p_offset;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Get expedition stats with filtering
CREATE OR REPLACE FUNCTION get_expedition_stats_filtered(
  p_hero_slug TEXT DEFAULT NULL,
  p_troop_type hero_class DEFAULT NULL,
  p_sort_by TEXT DEFAULT 'attack_pct',
  p_sort_order TEXT DEFAULT 'desc',
  p_limit INTEGER DEFAULT 20,
  p_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
  id UUID,
  hero_id UUID,
  troop_type hero_class,
  attack_pct NUMERIC,
  defense_pct NUMERIC,
  hero_slug TEXT,
  hero_name TEXT,
  total_count BIGINT
) AS $$
DECLARE
  order_clause TEXT;
  allowed_sort_columns TEXT[] := ARRAY['attack_pct', 'defense_pct'];
BEGIN
  IF p_sort_by = ANY(allowed_sort_columns) THEN
    order_clause := 'es.' || p_sort_by;
  ELSE
    order_clause := 'es.attack_pct';
  END IF;
  
  IF LOWER(p_sort_order) NOT IN ('asc', 'desc') THEN
    p_sort_order := 'desc';
  END IF;
  
  RETURN QUERY EXECUTE format('
    SELECT 
      es.id,
      es.hero_id,
      es.troop_type,
      es.attack_pct,
      es.defense_pct,
      h.hero_id_slug AS hero_slug,
      h.name AS hero_name,
      COUNT(*) OVER() AS total_count
    FROM hero_expedition_stats es
    JOIN heroes h ON h.id = es.hero_id
    WHERE 
      ($1 IS NULL OR h.hero_id_slug = $1)
      AND ($2 IS NULL OR es.troop_type = $2)
    ORDER BY %s %s
    LIMIT $3 OFFSET $4
  ', order_clause, p_sort_order)
  USING p_hero_slug, p_troop_type, p_limit, p_offset;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Exclusive gear progression view with skill tier calculations
CREATE OR REPLACE VIEW hero_exclusive_gear_progression AS
SELECT 
  eg.id AS gear_id,
  eg.hero_id,
  eg.name AS gear_name,
  eg.is_unlocked,
  eg.current_level,
  egl.level AS available_level,
  egl.power,
  egl.hero_attack,
  egl.hero_defense,
  egl.hero_health,
  egl.troop_lethality_bonus,
  egl.troop_health_bonus,
  egl.conquest_skill_effect,
  egl.expedition_skill_effect,
  -- Skill 1 info (typically Conquest)
  s1.id AS skill_1_id,
  s1.combat_type AS skill_1_combat_type,
  s1.name AS skill_1_name,
  s1.description AS skill_1_description,
  calculate_skill_tier(egl.level, 1) AS skill_1_tier,
  -- Skill 2 info (typically Expedition)
  s2.id AS skill_2_id,
  s2.combat_type AS skill_2_combat_type,
  s2.name AS skill_2_name,
  s2.description AS skill_2_description,
  calculate_skill_tier(egl.level, 2) AS skill_2_tier
FROM hero_exclusive_gear eg
LEFT JOIN hero_exclusive_gear_levels egl ON egl.gear_id = eg.id
LEFT JOIN LATERAL (
  SELECT * FROM hero_exclusive_gear_skills 
  WHERE gear_id = eg.id 
  ORDER BY combat_type 
  LIMIT 1
) s1 ON true
LEFT JOIN LATERAL (
  SELECT * FROM hero_exclusive_gear_skills 
  WHERE gear_id = eg.id 
  ORDER BY combat_type DESC 
  LIMIT 1
) s2 ON true
ORDER BY eg.id, egl.level;

-- Materialized view for complete hero stats (for dashboard/overview pages)
CREATE MATERIALIZED VIEW hero_complete_stats AS
SELECT 
  h.id,
  h.hero_id_slug,
  h.name,
  h.rarity,
  h.generation,
  h.class,
  h.image_path,
  h.created_at,
  h.updated_at,
  -- Conquest stats
  cs.attack AS conquest_attack,
  cs.defense AS conquest_defense,
  cs.health AS conquest_health,
  -- Expedition stats
  es.troop_type AS expedition_troop_type,
  es.attack_pct AS expedition_attack_pct,
  es.defense_pct AS expedition_defense_pct,
  -- Gear info
  eg.name AS exclusive_gear_name,
  eg.image_path AS exclusive_gear_image,
  eg.is_unlocked AS gear_unlocked,
  eg.current_level AS gear_level,
  -- Counts
  (SELECT COUNT(*) FROM hero_skills sk WHERE sk.hero_id = h.id) AS skill_count,
  (SELECT COUNT(*) FROM hero_talents t WHERE t.hero_id = h.id) AS has_talent
FROM heroes h
LEFT JOIN hero_conquest_stats cs ON cs.hero_id = h.id
LEFT JOIN hero_expedition_stats es ON es.hero_id = h.id
LEFT JOIN hero_exclusive_gear eg ON eg.hero_id = h.id;

-- Indexes for materialized view
CREATE UNIQUE INDEX idx_hero_complete_stats_id ON hero_complete_stats(id);
CREATE INDEX idx_hero_complete_stats_slug ON hero_complete_stats(hero_id_slug);
CREATE INDEX idx_hero_complete_stats_class ON hero_complete_stats(class);
CREATE INDEX idx_hero_complete_stats_rarity ON hero_complete_stats(rarity);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_hero_complete_stats()
RETURNS VOID AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY hero_complete_stats;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;
