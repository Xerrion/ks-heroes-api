-- VIP System
-- Normalized naming based on in-game terminology
-- Created: 2025-11-13

BEGIN;

-- =============================================================================
-- VIP LEVELS TABLE
-- =============================================================================

CREATE TABLE vip_levels (
    level INTEGER PRIMARY KEY CHECK (level >= 1 AND level <= 12),
    
    -- Resource production (generic bonus for all resources)
    -- In-game: "Bread/Wood/Stone/Iron Output (Percentage)"
    resource_production_speed_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Storage capacity
    -- In-game: "Storehouse Capacity"
    storehouse_capacity INTEGER NOT NULL DEFAULT 0,
    
    -- Speed bonuses
    -- In-game: "Construction Speed (Percentage)"
    construction_speed_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Gameplay features (counts)
    -- In-game: Formation slots
    formations INTEGER NOT NULL DEFAULT 0,
    
    -- In-game: "March Queue (Flat number)"
    march_queue INTEGER NOT NULL DEFAULT 0,
    
    -- Combat bonuses (all troops)
    -- In-game: "Squads' Attack (Percentage)"
    squads_attack_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- In-game: "Squads' Defense (Percentage)"
    squads_defense_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- In-game: "Squads' Health (Percentage)"
    squads_health_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- In-game: "Squads' Lethality (Percentage)"
    squads_lethality_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Cosmetic features
    -- Negative value indicates cooldown reduction in hours
    custom_avatar_upload_cooldown_hours INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE vip_levels IS 'VIP level bonuses (cumulative totals, not incremental). Based on in-game terminology.';

COMMENT ON COLUMN vip_levels.level IS 'VIP level (1-12)';
COMMENT ON COLUMN vip_levels.resource_production_speed_pct IS 'Generic resource production speed bonus - applies to Bread/Wood/Stone/Iron Output (Percentage)';
COMMENT ON COLUMN vip_levels.storehouse_capacity IS 'Storehouse capacity increase (flat number)';
COMMENT ON COLUMN vip_levels.construction_speed_pct IS 'Construction Speed (Percentage)';
COMMENT ON COLUMN vip_levels.formations IS 'Number of formation slots available';
COMMENT ON COLUMN vip_levels.march_queue IS 'March Queue (Flat number) - number of concurrent marches allowed';
COMMENT ON COLUMN vip_levels.squads_attack_pct IS 'Squads'' Attack (Percentage) - applies to all troop types';
COMMENT ON COLUMN vip_levels.squads_defense_pct IS 'Squads'' Defense (Percentage) - applies to all troop types';
COMMENT ON COLUMN vip_levels.squads_health_pct IS 'Squads'' Health (Percentage) - applies to all troop types';
COMMENT ON COLUMN vip_levels.squads_lethality_pct IS 'Squads'' Lethality (Percentage) - applies to all troop types';
COMMENT ON COLUMN vip_levels.custom_avatar_upload_cooldown_hours IS 'Avatar upload cooldown modification. Negative values indicate reduction (e.g., -48 = 48 hours less cooldown)';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Index for filtering VIP levels by combat bonus thresholds
CREATE INDEX idx_vip_levels_combat_bonuses ON vip_levels(
    squads_attack_pct, 
    squads_defense_pct, 
    squads_health_pct, 
    squads_lethality_pct
) WHERE squads_attack_pct > 0 OR squads_defense_pct > 0 OR squads_health_pct > 0 OR squads_lethality_pct > 0;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_vip_levels_updated_at
    BEFORE UPDATE ON vip_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
