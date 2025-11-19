-- Add Troop Training Resources and Event Points System
-- Normalizes resources and event types for reusability across features
-- Created: 2025-11-18

BEGIN;

-- =============================================================================
-- RESOURCES TABLE
-- =============================================================================

CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    resource_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    image_path TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT unique_resource_id UNIQUE(resource_id)
);

-- =============================================================================
-- TROOP TRAINING COSTS TABLE
-- =============================================================================

CREATE TABLE troop_training_costs (
    id SERIAL PRIMARY KEY,
    
    -- Link to troop
    troop_type hero_class NOT NULL,
    troop_level INTEGER NOT NULL CHECK (troop_level >= 1 AND troop_level <= 11),
    
    -- Link to resource
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    
    -- Cost amount per single troop
    cost INTEGER NOT NULL CHECK (cost >= 0),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure unique combination
    UNIQUE(troop_type, troop_level, resource_id)
);

-- =============================================================================
-- EVENT TYPES TABLE
-- =============================================================================

CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER NOT NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    CONSTRAINT unique_event_id UNIQUE(event_id)
);

-- =============================================================================
-- TROOP EVENT POINTS TABLE
-- =============================================================================

CREATE TABLE troop_event_points (
    id SERIAL PRIMARY KEY,
    
    -- Link to troop
    troop_type hero_class NOT NULL,
    troop_level INTEGER NOT NULL CHECK (troop_level >= 1 AND troop_level <= 11),
    
    -- Link to event
    event_id TEXT NOT NULL REFERENCES event_types(event_id),
    
    -- Base points per single troop (before True Gold modifiers)
    base_points INTEGER NOT NULL CHECK (base_points >= 0),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure unique combination
    UNIQUE(troop_type, troop_level, event_id)
);

-- =============================================================================
-- ADD TRAINING COLUMNS TO TROOPS TABLE
-- =============================================================================

ALTER TABLE troops
    ADD COLUMN IF NOT EXISTS training_time_seconds INTEGER CHECK (training_time_seconds >= 0),
    ADD COLUMN IF NOT EXISTS training_power INTEGER CHECK (training_power >= 0);

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE resources IS 'Game resources (bread, wood, stone, iron, etc.) used across different features';
COMMENT ON TABLE troop_training_costs IS 'Resource costs per troop type and level for training';
COMMENT ON TABLE event_types IS 'Game events that award points for training troops';
COMMENT ON TABLE troop_event_points IS 'Event points awarded per troop type and level';

COMMENT ON COLUMN resources.resource_id IS 'Unique identifier (bread, wood, stone, iron)';
COMMENT ON COLUMN resources.display_order IS 'Order for UI display';
COMMENT ON COLUMN resources.image_path IS 'Path to resource icon in Supabase storage';

COMMENT ON COLUMN troop_training_costs.cost IS 'Resource amount needed to train one troop';

COMMENT ON COLUMN event_types.event_id IS 'Unique identifier (hog, kvk, sg)';
COMMENT ON COLUMN troop_event_points.base_points IS 'Base points before True Gold modifiers (SG only)';

COMMENT ON COLUMN troops.training_time_seconds IS 'Time to train one troop in seconds';
COMMENT ON COLUMN troops.training_power IS 'Power gained from training one troop';

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_troop_training_costs_lookup ON troop_training_costs(troop_type, troop_level);
CREATE INDEX idx_troop_training_costs_resource ON troop_training_costs(resource_id);

CREATE INDEX idx_troop_event_points_lookup ON troop_event_points(troop_type, troop_level);
CREATE INDEX idx_troop_event_points_event ON troop_event_points(event_id);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_resources_updated_at
    BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_troop_training_costs_updated_at
    BEFORE UPDATE ON troop_training_costs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_event_types_updated_at
    BEFORE UPDATE ON event_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_troop_event_points_updated_at
    BEFORE UPDATE ON troop_event_points
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
