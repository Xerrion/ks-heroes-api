-- Troops System
-- Normalized naming based on in-game terminology
-- Created: 2025-11-13

BEGIN;

-- =============================================================================
-- ENUMS
-- =============================================================================

-- Reuse hero_class enum for troop types (Infantry, Cavalry, Archer)
-- If hero_class doesn't exist yet, create a dedicated troop_type enum
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hero_class') THEN
        CREATE TYPE troop_type AS ENUM ('Infantry', 'Cavalry', 'Archer');
    END IF;
END $$;

-- =============================================================================
-- TROOPS TABLE
-- =============================================================================

CREATE TABLE troops (
    id SERIAL PRIMARY KEY,
    
    -- Troop identification
    -- Use hero_class type if available, otherwise use troop_type
    troop_type hero_class NOT NULL,
    troop_level INTEGER NOT NULL CHECK (troop_level >= 1 AND troop_level <= 11),
    
    -- True Gold (FC) tier - 0 means no True Gold bonuses
    true_gold_level INTEGER NOT NULL DEFAULT 0 CHECK (true_gold_level >= 0 AND true_gold_level <= 10),
    
    -- Base combat stats (flat numbers)
    -- These are the base values before any percentage bonuses
    attack INTEGER NOT NULL CHECK (attack >= 0),
    defense INTEGER NOT NULL CHECK (defense >= 0),
    health INTEGER NOT NULL CHECK (health >= 0),
    lethality INTEGER NOT NULL CHECK (lethality >= 0),
    
    -- Other base stats
    power INTEGER NOT NULL CHECK (power >= 0),
    load INTEGER NOT NULL CHECK (load >= 0),
    speed INTEGER NOT NULL CHECK (speed >= 0),
    
    -- Image
    image_path TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure unique combination of troop type, level, and TG tier
    UNIQUE(troop_type, troop_level, true_gold_level)
);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE troops IS 'Base troop stats by type, level, and True Gold tier. Stats are flat numbers before percentage modifiers.';

COMMENT ON COLUMN troops.troop_type IS 'Infantry, Cavalry, or Archer';
COMMENT ON COLUMN troops.troop_level IS 'Troop level (1-10 regular, 11 is Helios)';
COMMENT ON COLUMN troops.true_gold_level IS 'True Gold level (0 = no TG bonuses, 1-10 = TG tiers). Game currently uses 0-5, but storing up to 10 for future-proofing.';
COMMENT ON COLUMN troops.attack IS 'Base attack value (flat number)';
COMMENT ON COLUMN troops.defense IS 'Base defense value (flat number)';
COMMENT ON COLUMN troops.health IS 'Base health value (flat number)';
COMMENT ON COLUMN troops.lethality IS 'Base lethality value (flat number)';
COMMENT ON COLUMN troops.power IS 'Troop power - used for overall power calculations';
COMMENT ON COLUMN troops.load IS 'Resource carrying capacity per troop';
COMMENT ON COLUMN troops.speed IS 'March speed on the map';
COMMENT ON COLUMN troops.image_path IS 'Path to troop icon in Supabase storage (e.g., troops/infantry_10.png)';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Primary lookup: get stats for specific troop configuration
CREATE INDEX idx_troops_type_level ON troops(troop_type, troop_level);

-- Filter by True Gold level (for querying TG-enabled troops)
CREATE INDEX idx_troops_tg_level ON troops(true_gold_level);

-- Combat stat lookups for battle calculations
CREATE INDEX idx_troops_combat_stats ON troops(attack, defense, health, lethality);

-- Composite index for complete troop lookup
CREATE INDEX idx_troops_complete_lookup ON troops(troop_type, troop_level, true_gold_level);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_troops_updated_at
    BEFORE UPDATE ON troops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
