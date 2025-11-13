-- Consolidated schema migration
-- This replaces the fragmented migrations with a complete, well-structured schema

BEGIN;

-- =============================================================================
-- CLEANUP (Drop existing objects in correct order)
-- =============================================================================

-- Drop views and materialized views
DROP MATERIALIZED VIEW IF EXISTS hero_complete_stats CASCADE;
DROP VIEW IF EXISTS hero_exclusive_gear_progression CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS calculate_skill_tier(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS validate_skill_level_sequence() CASCADE;
DROP FUNCTION IF EXISTS validate_gear_level_sequence() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS set_hero_id_slug() CASCADE;
DROP FUNCTION IF EXISTS slugify(TEXT) CASCADE;

-- Drop tables (respecting foreign key dependencies)
DROP TABLE IF EXISTS hero_exclusive_gear_skill_levels CASCADE;
DROP TABLE IF EXISTS hero_exclusive_gear_skills CASCADE;
DROP TABLE IF EXISTS hero_exclusive_gear_levels CASCADE;
DROP TABLE IF EXISTS hero_exclusive_gear CASCADE;
DROP TABLE IF EXISTS hero_skill_levels CASCADE;
DROP TABLE IF EXISTS hero_skills CASCADE;
DROP TABLE IF EXISTS hero_talents CASCADE;
DROP TABLE IF EXISTS hero_expedition_stats CASCADE;
DROP TABLE IF EXISTS hero_conquest_stats CASCADE;
DROP TABLE IF EXISTS heroes CASCADE;

-- Drop types
DROP TYPE IF EXISTS combat_type CASCADE;
DROP TYPE IF EXISTS battle_type CASCADE;
DROP TYPE IF EXISTS skill_type CASCADE;
DROP TYPE IF EXISTS hero_class CASCADE;
DROP TYPE IF EXISTS hero_rarity CASCADE;

-- =============================================================================
-- CUSTOM TYPES
-- =============================================================================

CREATE TYPE hero_rarity AS ENUM ('Rare', 'Epic', 'Mythic');
CREATE TYPE hero_class AS ENUM ('Infantry', 'Cavalry', 'Archer');
CREATE TYPE skill_type AS ENUM ('Active', 'Passive', 'Rage', 'Talent');
CREATE TYPE battle_type AS ENUM ('Base', 'Conquest', 'Expedition');
CREATE TYPE combat_type AS ENUM ('Conquest', 'Expedition');

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Helper function to create URL-safe slug from text
CREATE OR REPLACE FUNCTION slugify(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN trim(both '-' from regexp_replace(lower(trim(input_text)), '[^a-z0-9]+', '-', 'g'));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger function to automatically create hero_id_slug on insert
CREATE OR REPLACE FUNCTION set_hero_id_slug()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.hero_id_slug IS NULL OR NEW.hero_id_slug = '' THEN
    NEW.hero_id_slug := slugify(NEW.name);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Heroes table
CREATE TABLE heroes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id_slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  rarity hero_rarity NOT NULL,
  generation INTEGER CHECK (generation > 0),
  class hero_class NOT NULL,
  image_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT heroes_name_not_empty CHECK (trim(name) <> '')
);

-- Conquest stats
CREATE TABLE hero_conquest_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  attack INTEGER NOT NULL CHECK (attack >= 0),
  defense INTEGER NOT NULL CHECK (defense >= 0),
  health INTEGER NOT NULL CHECK (health >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Expedition stats
CREATE TABLE hero_expedition_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  troop_type hero_class NOT NULL,
  attack_pct NUMERIC(10,2) CHECK (attack_pct >= 0 AND attack_pct <= 1000),
  defense_pct NUMERIC(10,2) CHECK (defense_pct >= 0 AND defense_pct <= 1000),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- SKILLS TABLES
-- =============================================================================

-- Hero skills
CREATE TABLE hero_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  skill_type skill_type NOT NULL,
  battle_type battle_type NOT NULL,
  description TEXT,
  icon_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_skills_unique_per_hero UNIQUE (hero_id, name),
  CONSTRAINT hero_skills_name_not_empty CHECK (trim(name) <> '')
);

-- Skill levels (1-5)
CREATE TABLE hero_skill_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL REFERENCES hero_skills(id) ON DELETE CASCADE,
  level INTEGER NOT NULL CHECK (level >= 1 AND level <= 5),
  effects JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_skill_levels_unique UNIQUE (skill_id, level)
);

-- Hero talents (special passive skills)
CREATE TABLE hero_talents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  icon_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_talents_name_not_empty CHECK (trim(name) <> '')
);

-- =============================================================================
-- EXCLUSIVE GEAR TABLES
-- =============================================================================

-- Exclusive gear base
CREATE TABLE hero_exclusive_gear (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  image_path TEXT,
  is_unlocked BOOLEAN DEFAULT FALSE NOT NULL,
  current_level INTEGER DEFAULT 0 CHECK (current_level >= 0 AND current_level <= 10) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_name_not_empty CHECK (trim(name) <> '')
);

-- Gear levels (0-10, level 0 means locked but not yet unlocked)
CREATE TABLE hero_exclusive_gear_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
  power INTEGER NOT NULL CHECK (power >= 0),
  hero_attack INTEGER NOT NULL CHECK (hero_attack >= 0),
  hero_defense INTEGER NOT NULL CHECK (hero_defense >= 0),
  hero_health INTEGER NOT NULL CHECK (hero_health >= 0),
  troop_lethality_bonus JSONB,
  troop_health_bonus JSONB,
  conquest_skill_effect JSONB,
  expedition_skill_effect JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_levels_unique UNIQUE (gear_id, level)
);

-- Gear skills (conquest/expedition specific)
CREATE TABLE hero_exclusive_gear_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  combat_type combat_type NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_skills_unique UNIQUE (gear_id, combat_type),
  CONSTRAINT hero_exclusive_gear_skills_name_not_empty CHECK (trim(name) <> '')
);

-- Gear skill level upgrades (tracking skill tier at each gear level)
CREATE TABLE hero_exclusive_gear_skill_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL REFERENCES hero_exclusive_gear_skills(id) ON DELETE CASCADE,
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  gear_level INTEGER NOT NULL CHECK (gear_level >= 1 AND gear_level <= 10),
  skill_tier INTEGER NOT NULL CHECK (skill_tier >= 1 AND skill_tier <= 5),
  upgrade_value NUMERIC(10,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_skill_levels_unique UNIQUE (skill_id, gear_level)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Heroes indexes
CREATE INDEX idx_heroes_class ON heroes(class);
CREATE INDEX idx_heroes_rarity ON heroes(rarity);
CREATE INDEX idx_heroes_generation ON heroes(generation) WHERE generation IS NOT NULL;
CREATE INDEX idx_heroes_slug ON heroes(hero_id_slug);
CREATE INDEX idx_heroes_name ON heroes(name);

-- Skills indexes
CREATE INDEX idx_hero_skills_hero_id ON hero_skills(hero_id);
CREATE INDEX idx_hero_skills_type ON hero_skills(skill_type);
CREATE INDEX idx_hero_skills_battle_type ON hero_skills(battle_type);
CREATE INDEX idx_hero_skills_composite ON hero_skills(hero_id, skill_type, battle_type);
CREATE INDEX idx_hero_skill_levels_skill_id ON hero_skill_levels(skill_id);

-- Stats indexes
CREATE INDEX idx_conquest_stats_hero_id ON hero_conquest_stats(hero_id);
CREATE INDEX idx_expedition_stats_hero_id ON hero_expedition_stats(hero_id);
CREATE INDEX idx_expedition_stats_troop_type ON hero_expedition_stats(troop_type);

-- Talents indexes
CREATE INDEX idx_hero_talents_hero_id ON hero_talents(hero_id);

-- Gear indexes
CREATE INDEX idx_exclusive_gear_hero_id ON hero_exclusive_gear(hero_id);
CREATE INDEX idx_exclusive_gear_unlocked ON hero_exclusive_gear(is_unlocked) WHERE is_unlocked = TRUE;
CREATE INDEX idx_gear_levels_gear_id ON hero_exclusive_gear_levels(gear_id);
CREATE INDEX idx_gear_levels_composite ON hero_exclusive_gear_levels(gear_id, level);
CREATE INDEX idx_gear_skills_gear_id ON hero_exclusive_gear_skills(gear_id);
CREATE INDEX idx_gear_skill_levels_skill_id ON hero_exclusive_gear_skill_levels(skill_id);
CREATE INDEX idx_gear_skill_levels_composite ON hero_exclusive_gear_skill_levels(gear_id, gear_level);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-generate hero slugs
CREATE TRIGGER trigger_set_hero_id_slug
  BEFORE INSERT ON heroes
  FOR EACH ROW EXECUTE FUNCTION set_hero_id_slug();

-- Auto-update updated_at columns
CREATE TRIGGER trigger_heroes_updated_at
  BEFORE UPDATE ON heroes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_conquest_stats_updated_at
  BEFORE UPDATE ON hero_conquest_stats
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_expedition_stats_updated_at
  BEFORE UPDATE ON hero_expedition_stats
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_hero_skills_updated_at
  BEFORE UPDATE ON hero_skills
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_exclusive_gear_updated_at
  BEFORE UPDATE ON hero_exclusive_gear
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VALIDATION TRIGGERS
-- =============================================================================

-- Enforce that skill levels must be created sequentially (1, 2, 3, 4, 5)
-- Skipped during bulk seeding operations
CREATE OR REPLACE FUNCTION validate_skill_level_sequence()
RETURNS TRIGGER AS $$
BEGIN
  -- Skip all validation if we're in a bulk seed operation (detected by temp table)
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE schemaname = 'pg_temp' AND tablename = 'disable_level_validation') THEN
    RETURN NEW;
  END IF;
  
  -- Skip validation on UPDATE (triggered by ON CONFLICT DO UPDATE)
  IF TG_OP = 'UPDATE' THEN
    RETURN NEW;
  END IF;
  
  IF NEW.level > 1 THEN
    IF NOT EXISTS (
      SELECT 1 FROM hero_skill_levels
      WHERE skill_id = NEW.skill_id AND level = NEW.level - 1
    ) THEN
      RAISE EXCEPTION 'Skill level % cannot be created before level %', NEW.level, NEW.level - 1;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_skill_level_sequence
  BEFORE INSERT OR UPDATE ON hero_skill_levels
  FOR EACH ROW EXECUTE FUNCTION validate_skill_level_sequence();

-- Enforce that gear levels must be created sequentially (1-10)
CREATE OR REPLACE FUNCTION validate_gear_level_sequence()
RETURNS TRIGGER AS $$
BEGIN
  -- Skip all validation if we're in a bulk seed operation (detected by temp table)
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE schemaname = 'pg_temp' AND tablename = 'disable_level_validation') THEN
    RETURN NEW;
  END IF;
  
  -- Skip validation on UPDATE (triggered by ON CONFLICT DO UPDATE)
  IF TG_OP = 'UPDATE' THEN
    RETURN NEW;
  END IF;
  
  IF NEW.level > 1 THEN
    IF NOT EXISTS (
      SELECT 1 FROM hero_exclusive_gear_levels
      WHERE gear_id = NEW.gear_id AND level = NEW.level - 1
    ) THEN
      RAISE EXCEPTION 'Gear level % cannot be created before level %', NEW.level, NEW.level - 1;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_gear_level_sequence
  BEFORE INSERT OR UPDATE ON hero_exclusive_gear_levels
  FOR EACH ROW EXECUTE FUNCTION validate_gear_level_sequence();

COMMIT;
