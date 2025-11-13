# Kingshot Heroes API - Database Schema

## Overview

This database schema is designed to support a comprehensive Hero API for the Kingshot game, optimized for battle simulator consumption. The schema properly models all hero data including stats, skills, talents, and exclusive gear with their progression systems.

## Schema Design Principles

1. **Battle Simulator Ready**: All data is structured to support battle simulation calculations
2. **Separation of Concerns**: Conquest and Expedition data are properly separated
3. **Complete Progression**: All leveling systems (skills 1-5, gear 1-10) are fully modeled
4. **Performance Optimized**: Includes strategic indexes and RPC functions for efficient data retrieval
5. **Data Integrity**: Foreign keys, constraints, and validation triggers ensure data consistency

## Key Tables

### Heroes (`heroes`)

Core hero information including:

- `hero_id_slug`: URL-safe unique identifier
- `name`, `rarity`, `generation`, `class`: Basic hero attributes
- `image_path`: Asset reference
- `sources`: JSON array of acquisition methods

### Combat Stats

#### Conquest Stats (`hero_conquest_stats`)

Base stats for Conquest battles:

- `attack`, `defense`, `health`: Absolute stat values

#### Expedition Stats (`hero_expedition_stats`)

Percentage bonuses for Expedition battles:

- `troop_type`: Infantry, Cavalry, or Archer
- `attack_pct`, `defense_pct`, `lethality_pct`, `health_pct`: Percentage bonuses

### Skills (`hero_skills` + `hero_skill_levels`)

Hero skills for different battle types:

- Separate entries for Conquest and Expedition skills
- 5 levels per skill with effects stored as JSONB
- `effect_category` and `effect_op`: For skill stacking calculations (see Battle Formula)

### Talents (`hero_talents`)

Special passive abilities:

- One talent per hero
- `max_level_effects`: JSONB containing maxed talent effects

### Exclusive Gear System

#### Gear Base (`hero_exclusive_gear`)

One exclusive gear item per hero

#### Gear Levels (`hero_exclusive_gear_levels`)

10 levels of progression with:

- Hero stat bonuses (`hero_attack`, `hero_defense`, `hero_health`)
- Troop bonuses (`troop_lethality_bonus`, `troop_health_bonus`)
- Skill effects for both battle types

#### Gear Skills (`hero_exclusive_gear_skills`)

Two skills per gear (Conquest + Expedition):

- Skill descriptions and maximum effects

#### Gear Skill Progression (`hero_exclusive_gear_skill_levels`)

Tracks skill tier upgrades through gear levels:

- Conquest skills upgrade on odd levels (1,3,5,7,9) → tiers 1-5
- Expedition skills upgrade on even levels (2,4,6,8,10) → tiers 1-5

## Battle Formula Support

The schema supports the Kingshot battle damage formula:

```
Kills = √Troops × (Attack × Lethality) / (Enemy Defense × Enemy Health) × SkillMod
```

Where `SkillMod = (DamageUp × OppDefenseDown) / (OppDamageDown × DefenseUp)`

### Skill Stacking

- Skills with the same `effect_op` add together
- Skills with different `effect_op` values multiply
- This is why mixing different heroes (e.g., Amane + Chenko) provides more damage

## RPC Functions

### `get_hero_complete(hero_slug)`

Returns complete hero data including all stats, skills, talents, and gear in a single JSON object.

### `get_all_expedition_heroes()`

Returns all heroes with expedition-relevant data optimized for battle simulators.

### `get_heroes_by_class(class)`

Filter heroes by class (Infantry, Cavalry, Archer).

### `search_heroes(query)`

Full-text search across hero names and slugs.

## Migrations

Run migrations in order:

1. `20251113000000_comprehensive_hero_schema.sql` - Core schema
2. `20251113000001_rpc_functions.sql` - RPC functions
3. `20251113000002_fulltext_search.sql` - Search capabilities

## Seeding Data

Generate and apply seed data:

```bash
# Generate seed SQL from JSON data files
uv run python scripts/generate_seed_sql.py

# Apply to Supabase (local)
supabase db reset

# Or apply directly
psql -f supabase/seed.sql
```

## Data Sources

The seed generator processes:

- `data/heroes.json` - Core hero info
- `data/heroes_conquest_base.json` - Conquest base stats
- `data/heroes_expedition_base.json` - Expedition base stats
- `data/hero_skills.json` - All skills and talents
- `data/exclusive_gear.json` - Exclusive gear with progression

## API Usage Examples

### Get Complete Hero Data

```sql
SELECT get_hero_complete('jabel');
```

### Get All Expedition Heroes

```sql
SELECT get_all_expedition_heroes();
```

### Search Heroes

```sql
SELECT search_heroes('cavalry');
```

## Performance Considerations

- All foreign key relationships are indexed
- GIN indexes for JSONB columns and full-text search
- Composite indexes for common query patterns
- RPC functions pre-aggregate data to reduce round trips

## Future Enhancements

Potential additions:

- Hero awakening/breakthrough systems
- Equipment sets and synergies
- PvP-specific stats and modifiers
- Historical stat tracking (buffs/nerfs over time)
- User-specific hero progression tracking
