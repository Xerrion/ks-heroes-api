-- Governor Gear System
-- Normalized naming based on in-game terminology
-- Created: 2025-11-15

BEGIN;

-- =============================================================================
-- ENUMS
-- =============================================================================

-- Create rarity enum for governor gear (broader than hero_rarity)
-- Includes Uncommon and Legendary which heroes don't use
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rarity') THEN
        CREATE TYPE rarity AS ENUM ('Uncommon', 'Rare', 'Epic', 'Mythic', 'Legendary');
    END IF;
END $$;

-- Reuse hero_class enum for troop types (Infantry, Cavalry, Archer)
-- If hero_class doesn't exist yet, create it
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hero_class') THEN
        CREATE TYPE hero_class AS ENUM ('Infantry', 'Cavalry', 'Archer');
    END IF;
END $$;

-- =============================================================================
-- GOVERNOR GEAR BASE TABLE
-- =============================================================================

CREATE TABLE governor_gear (
    gear_id TEXT PRIMARY KEY,
    
    -- Gear identification
    slot TEXT NOT NULL,
    troop_type hero_class NOT NULL,
    
    -- Charm configuration
    max_charms INTEGER NOT NULL DEFAULT 3 CHECK (max_charms > 0),
    
    -- Metadata
    description TEXT,
    default_bonus_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- GOVERNOR GEAR LEVELS TABLE
-- =============================================================================

CREATE TABLE governor_gear_levels (
    level INTEGER PRIMARY KEY CHECK (level >= 1 AND level <= 46),
    
    -- Progression identifiers
    rarity rarity NOT NULL,
    tier INTEGER NOT NULL DEFAULT 0 CHECK (tier >= 0 AND tier <= 4),
    stars INTEGER NOT NULL DEFAULT 0 CHECK (stars >= 0 AND stars <= 5),
    
    -- Display name (varies by rarity only)
    name TEXT,
    
    -- Combat bonuses (JSONB for flexibility)
    -- Typical keys: attack_pct, defense_pct
    bonuses JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure unique combination
    UNIQUE(rarity, tier, stars)
);

-- =============================================================================
-- GOVERNOR GEAR CHARM SLOTS TABLE
-- =============================================================================

CREATE TABLE governor_gear_charm_slots (
    id SERIAL PRIMARY KEY,
    
    -- References base gear
    gear_id TEXT NOT NULL REFERENCES governor_gear(gear_id) ON DELETE CASCADE,
    
    -- Slot identification
    slot_index INTEGER NOT NULL CHECK (slot_index >= 1 AND slot_index <= 3),
    troop_type hero_class NOT NULL,
    
    -- Bonus configuration
    -- Typical keys: troop_lethality_pct, troop_health_pct
    bonus_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure unique slot per gear
    UNIQUE(gear_id, slot_index)
);

-- =============================================================================
-- GOVERNOR GEAR CHARM LEVELS TABLE
-- =============================================================================

CREATE TABLE governor_gear_charm_levels (
    level INTEGER PRIMARY KEY CHECK (level >= 1 AND level <= 16),
    
    -- Combat bonuses (JSONB for flexibility)
    -- Typical keys: troop_lethality_pct, troop_health_pct
    bonuses JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE governor_gear IS 'Base governor gear pieces (6 total: head, amulet, chest, legs, ring, staff)';
COMMENT ON COLUMN governor_gear.gear_id IS 'Unique gear identifier (head, amulet, chest, legs, ring, staff)';
COMMENT ON COLUMN governor_gear.slot IS 'Display name for equipment slot';
COMMENT ON COLUMN governor_gear.troop_type IS 'Troop type this gear benefits (Infantry, Cavalry, Archer)';
COMMENT ON COLUMN governor_gear.max_charms IS 'Maximum charm slots available (always 3)';
COMMENT ON COLUMN governor_gear.default_bonus_keys IS 'Default bonus stat keys provided by this gear (e.g., ["attack_pct", "defense_pct"])';

COMMENT ON TABLE governor_gear_levels IS 'Governor gear progression levels (46 total levels across rarities and tiers)';
COMMENT ON COLUMN governor_gear_levels.level IS 'Absolute progression level (1-46)';
COMMENT ON COLUMN governor_gear_levels.rarity IS 'Gear rarity (Uncommon, Rare, Epic, Mythic, Legendary)';
COMMENT ON COLUMN governor_gear_levels.tier IS 'Tier within rarity (0-4, higher tiers available at higher rarities)';
COMMENT ON COLUMN governor_gear_levels.stars IS 'Star level within tier (0-5)';
COMMENT ON COLUMN governor_gear_levels.name IS 'Display name for gear at this rarity (same across all tiers/stars of same rarity)';
COMMENT ON COLUMN governor_gear_levels.bonuses IS 'Combat stat bonuses as JSONB object (e.g., {"attack_pct": 34.0, "defense_pct": 34.0})';

COMMENT ON TABLE governor_gear_charm_slots IS 'Charm slot definitions for each gear piece (18 total: 6 gear × 3 slots)';
COMMENT ON COLUMN governor_gear_charm_slots.gear_id IS 'Reference to governor_gear piece';
COMMENT ON COLUMN governor_gear_charm_slots.slot_index IS 'Slot position (1-3)';
COMMENT ON COLUMN governor_gear_charm_slots.troop_type IS 'Troop type for this slot (inherited from gear)';
COMMENT ON COLUMN governor_gear_charm_slots.bonus_keys IS 'Stat keys provided by charms in this slot (e.g., ["troop_lethality_pct", "troop_health_pct"])';

COMMENT ON TABLE governor_gear_charm_levels IS 'Charm progression levels (16 total levels)';
COMMENT ON COLUMN governor_gear_charm_levels.level IS 'Charm level (1-16)';
COMMENT ON COLUMN governor_gear_charm_levels.bonuses IS 'Combat stat bonuses as JSONB object (e.g., {"troop_lethality_pct": 9.0, "troop_health_pct": 9.0})';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Governor Gear base table indexes
CREATE INDEX idx_governor_gear_troop_type ON governor_gear(troop_type);

-- Governor Gear levels indexes
CREATE INDEX idx_governor_gear_levels_rarity ON governor_gear_levels(rarity);
CREATE INDEX idx_governor_gear_levels_tier ON governor_gear_levels(tier);
CREATE INDEX idx_governor_gear_levels_rarity_tier ON governor_gear_levels(rarity, tier, stars);

-- Charm slots indexes
CREATE INDEX idx_governor_gear_charm_slots_gear_id ON governor_gear_charm_slots(gear_id);
CREATE INDEX idx_governor_gear_charm_slots_troop_type ON governor_gear_charm_slots(troop_type);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_governor_gear_updated_at
    BEFORE UPDATE ON governor_gear
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_governor_gear_levels_updated_at
    BEFORE UPDATE ON governor_gear_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_governor_gear_charm_slots_updated_at
    BEFORE UPDATE ON governor_gear_charm_slots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_governor_gear_charm_levels_updated_at
    BEFORE UPDATE ON governor_gear_charm_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
