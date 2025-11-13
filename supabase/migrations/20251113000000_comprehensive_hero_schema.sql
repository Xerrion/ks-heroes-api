-- Comprehensive Hero API Schema
-- Optimized for battle simulator data consumption
-- Created: 2025-11-13

BEGIN;

-- =============================================================================
-- CLEANUP
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS hero_complete_stats CASCADE;
DROP VIEW IF EXISTS hero_expedition_complete CASCADE;
DROP VIEW IF EXISTS hero_conquest_complete CASCADE;

DROP FUNCTION IF EXISTS calculate_skill_tier(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS validate_skill_level_sequence() CASCADE;
DROP FUNCTION IF EXISTS validate_gear_level_sequence() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS set_hero_id_slug() CASCADE;
DROP FUNCTION IF EXISTS slugify(TEXT) CASCADE;

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

DROP TYPE IF EXISTS combat_type CASCADE;
DROP TYPE IF EXISTS battle_type CASCADE;
DROP TYPE IF EXISTS skill_type CASCADE;
DROP TYPE IF EXISTS hero_class CASCADE;
DROP TYPE IF EXISTS hero_rarity CASCADE;

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE hero_rarity AS ENUM ('Rare', 'Epic', 'Mythic');
CREATE TYPE hero_class AS ENUM ('Infantry', 'Cavalry', 'Archer');
CREATE TYPE skill_type AS ENUM ('Active', 'Passive', 'Rage', 'Talent', 'Expedition');
CREATE TYPE battle_type AS ENUM ('Conquest', 'Expedition');

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

CREATE OR REPLACE FUNCTION slugify(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN trim(both '-' from regexp_replace(lower(trim(input_text)), '[^a-z0-9]+', '-', 'g'));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION set_hero_id_slug()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.hero_id_slug IS NULL OR NEW.hero_id_slug = '' THEN
    NEW.hero_id_slug := slugify(NEW.name);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CORE HERO TABLE
-- =============================================================================

CREATE TABLE heroes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id_slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  rarity hero_rarity NOT NULL,
  generation INTEGER CHECK (generation > 0),
  class hero_class NOT NULL,
  image_path TEXT,
  sources JSONB, -- Array of acquisition sources
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT heroes_name_not_empty CHECK (trim(name) <> '')
);

COMMENT ON TABLE heroes IS 'Core hero information';
COMMENT ON COLUMN heroes.hero_id_slug IS 'URL-safe unique identifier derived from hero name';
COMMENT ON COLUMN heroes.sources IS 'JSON array of ways to acquire this hero (e.g., ["Hero Recruitment", "Conquest Battles"])';

-- =============================================================================
-- COMBAT STATS TABLES
-- =============================================================================

-- Conquest base stats (for Conquest battles)
CREATE TABLE hero_conquest_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  attack INTEGER NOT NULL CHECK (attack >= 0),
  defense INTEGER NOT NULL CHECK (defense >= 0),
  health INTEGER NOT NULL CHECK (health >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE hero_conquest_stats IS 'Base conquest battle stats for heroes';
COMMENT ON COLUMN hero_conquest_stats.attack IS 'Base attack stat for conquest mode';
COMMENT ON COLUMN hero_conquest_stats.defense IS 'Base defense stat for conquest mode';
COMMENT ON COLUMN hero_conquest_stats.health IS 'Base health stat for conquest mode';

-- Expedition base stats (for Expedition battles)
CREATE TABLE hero_expedition_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  troop_type hero_class NOT NULL,
  attack_pct NUMERIC(10,2) NOT NULL CHECK (attack_pct >= 0),
  defense_pct NUMERIC(10,2) NOT NULL CHECK (defense_pct >= 0),
  lethality_pct NUMERIC(10,2) DEFAULT 0 CHECK (lethality_pct >= 0),
  health_pct NUMERIC(10,2) DEFAULT 0 CHECK (health_pct >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE hero_expedition_stats IS 'Base expedition stats - percentage bonuses to specific troop types';
COMMENT ON COLUMN hero_expedition_stats.troop_type IS 'The troop type this hero buffs (Infantry, Cavalry, Archer)';
COMMENT ON COLUMN hero_expedition_stats.attack_pct IS 'Attack percentage bonus for the specified troop type';
COMMENT ON COLUMN hero_expedition_stats.defense_pct IS 'Defense percentage bonus for the specified troop type';
COMMENT ON COLUMN hero_expedition_stats.lethality_pct IS 'Lethality percentage bonus for the specified troop type';
COMMENT ON COLUMN hero_expedition_stats.health_pct IS 'Health percentage bonus for the specified troop type';

-- =============================================================================
-- SKILLS TABLES
-- =============================================================================

CREATE TABLE hero_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  skill_type skill_type NOT NULL,
  battle_type battle_type NOT NULL,
  description TEXT,
  icon_path TEXT,
  effect_category TEXT, -- e.g., 'DamageUp', 'DefenseDown', 'OppDamageDown', 'OppDefenseDown'
  effect_op INTEGER, -- Unique identifier for skill stacking behavior
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_skills_unique_per_hero UNIQUE (hero_id, name, battle_type),
  CONSTRAINT hero_skills_name_not_empty CHECK (trim(name) <> '')
);

COMMENT ON TABLE hero_skills IS 'Hero skills for different battle types';
COMMENT ON COLUMN hero_skills.effect_category IS 'Category of effect for battle calculations (DamageUp, DefenseDown, etc.)';
COMMENT ON COLUMN hero_skills.effect_op IS 'Effect operator ID - skills with different effect_ops multiply, same effect_ops add';

CREATE TABLE hero_skill_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL REFERENCES hero_skills(id) ON DELETE CASCADE,
  level INTEGER NOT NULL CHECK (level >= 1 AND level <= 5),
  effects JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_skill_levels_unique UNIQUE (skill_id, level)
);

COMMENT ON TABLE hero_skill_levels IS 'Skill effects at each level (1-5)';
COMMENT ON COLUMN hero_skill_levels.effects IS 'JSON object containing stat effects (e.g., {"damage_pct": 25, "duration_s": 3})';

-- =============================================================================
-- TALENTS
-- =============================================================================

CREATE TABLE hero_talents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  icon_path TEXT,
  max_level_effects JSONB, -- Effects when talent is maxed
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_talents_name_not_empty CHECK (trim(name) <> '')
);

COMMENT ON TABLE hero_talents IS 'Hero talents - special passive abilities';
COMMENT ON COLUMN hero_talents.max_level_effects IS 'Effects at maximum talent level';

-- =============================================================================
-- EXCLUSIVE GEAR TABLES
-- =============================================================================

CREATE TABLE hero_exclusive_gear (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hero_id UUID NOT NULL UNIQUE REFERENCES heroes(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  image_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_name_not_empty CHECK (trim(name) <> '')
);

COMMENT ON TABLE hero_exclusive_gear IS 'Hero-specific exclusive gear';

CREATE TABLE hero_exclusive_gear_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  level INTEGER NOT NULL CHECK (level >= 1 AND level <= 10),
  power INTEGER NOT NULL CHECK (power >= 0),
  hero_attack INTEGER NOT NULL DEFAULT 0 CHECK (hero_attack >= 0),
  hero_defense INTEGER NOT NULL DEFAULT 0 CHECK (hero_defense >= 0),
  hero_health INTEGER NOT NULL DEFAULT 0 CHECK (hero_health >= 0),
  troop_lethality_bonus JSONB,
  troop_health_bonus JSONB,
  conquest_skill_effect JSONB,
  expedition_skill_effect JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_levels_unique UNIQUE (gear_id, level)
);

COMMENT ON TABLE hero_exclusive_gear_levels IS 'Stats and bonuses at each gear level (1-10)';
COMMENT ON COLUMN hero_exclusive_gear_levels.troop_lethality_bonus IS 'Troop lethality bonus (e.g., {"type": "Cavalry", "value_pct": 15})';
COMMENT ON COLUMN hero_exclusive_gear_levels.troop_health_bonus IS 'Troop health bonus (e.g., {"type": "Cavalry", "value_pct": 15})';
COMMENT ON COLUMN hero_exclusive_gear_levels.conquest_skill_effect IS 'Conquest skill effect at this level';
COMMENT ON COLUMN hero_exclusive_gear_levels.expedition_skill_effect IS 'Expedition skill effect at this level';

CREATE TABLE hero_exclusive_gear_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  battle_type battle_type NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  max_effect JSONB, -- Effect at gear level 10
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_skills_unique UNIQUE (gear_id, battle_type),
  CONSTRAINT hero_exclusive_gear_skills_name_not_empty CHECK (trim(name) <> '')
);

COMMENT ON TABLE hero_exclusive_gear_skills IS 'Exclusive gear skills for Conquest and Expedition';
COMMENT ON COLUMN hero_exclusive_gear_skills.max_effect IS 'Maximum effect description for reference';

CREATE TABLE hero_exclusive_gear_skill_levels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL REFERENCES hero_exclusive_gear_skills(id) ON DELETE CASCADE,
  gear_id UUID NOT NULL REFERENCES hero_exclusive_gear(id) ON DELETE CASCADE,
  gear_level INTEGER NOT NULL CHECK (gear_level >= 1 AND gear_level <= 10),
  skill_tier INTEGER NOT NULL CHECK (skill_tier >= 0 AND skill_tier <= 5),
  upgrade_value NUMERIC(10,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  
  CONSTRAINT hero_exclusive_gear_skill_levels_unique UNIQUE (skill_id, gear_level)
);

COMMENT ON TABLE hero_exclusive_gear_skill_levels IS 'Skill progression through gear levels';
COMMENT ON COLUMN hero_exclusive_gear_skill_levels.skill_tier IS 'Skill tier at this gear level (0-5, where 0 means not yet unlocked)';
COMMENT ON COLUMN hero_exclusive_gear_skill_levels.upgrade_value IS 'The numeric value of the skill effect at this level';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Heroes
CREATE INDEX idx_heroes_class ON heroes(class);
CREATE INDEX idx_heroes_rarity ON heroes(rarity);
CREATE INDEX idx_heroes_generation ON heroes(generation) WHERE generation IS NOT NULL;
CREATE INDEX idx_heroes_name_trgm ON heroes USING gin(name gin_trgm_ops);

-- Stats
CREATE INDEX idx_conquest_stats_hero_id ON hero_conquest_stats(hero_id);
CREATE INDEX idx_expedition_stats_hero_id ON hero_expedition_stats(hero_id);
CREATE INDEX idx_expedition_stats_troop_type ON hero_expedition_stats(troop_type);

-- Skills
CREATE INDEX idx_hero_skills_hero_id ON hero_skills(hero_id);
CREATE INDEX idx_hero_skills_battle_type ON hero_skills(battle_type);
CREATE INDEX idx_hero_skills_composite ON hero_skills(hero_id, battle_type);
CREATE INDEX idx_hero_skill_levels_skill_id ON hero_skill_levels(skill_id);

-- Talents
CREATE INDEX idx_hero_talents_hero_id ON hero_talents(hero_id);

-- Gear
CREATE INDEX idx_exclusive_gear_hero_id ON hero_exclusive_gear(hero_id);
CREATE INDEX idx_gear_levels_gear_id ON hero_exclusive_gear_levels(gear_id);
CREATE INDEX idx_gear_levels_composite ON hero_exclusive_gear_levels(gear_id, level);
CREATE INDEX idx_gear_skills_gear_id ON hero_exclusive_gear_skills(gear_id);
CREATE INDEX idx_gear_skills_battle_type ON hero_exclusive_gear_skills(battle_type);
CREATE INDEX idx_gear_skill_levels_skill_id ON hero_exclusive_gear_skill_levels(skill_id);
CREATE INDEX idx_gear_skill_levels_composite ON hero_exclusive_gear_skill_levels(gear_id, gear_level);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_set_hero_id_slug
  BEFORE INSERT ON heroes
  FOR EACH ROW EXECUTE FUNCTION set_hero_id_slug();

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

CREATE TRIGGER trigger_hero_talents_updated_at
  BEFORE UPDATE ON hero_talents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_exclusive_gear_updated_at
  BEFORE UPDATE ON hero_exclusive_gear
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_exclusive_gear_skills_updated_at
  BEFORE UPDATE ON hero_exclusive_gear_skills
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VALIDATION TRIGGERS (disabled during bulk seed)
-- =============================================================================

CREATE OR REPLACE FUNCTION validate_skill_level_sequence()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE schemaname = 'pg_temp' AND tablename = 'disable_level_validation') THEN
    RETURN NEW;
  END IF;
  
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

CREATE OR REPLACE FUNCTION validate_gear_level_sequence()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_catalog.pg_tables WHERE schemaname = 'pg_temp' AND tablename = 'disable_level_validation') THEN
    RETURN NEW;
  END IF;
  
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
