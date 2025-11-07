-- 008_create_hero_exclusive_gear_levels.sql

drop table if exists hero_exclusive_gear_levels cascade;

create table hero_exclusive_gear_levels
(
    id                      uuid primary key default gen_random_uuid(),
    gear_id                 uuid      not null references hero_exclusive_gear (id) on delete cascade,
    level                   int       not null check (level between 1 and 10),
    hero_attack             int,
    hero_defense            int,
    hero_health             int,
    troop_lethality_bonus   jsonb, -- Example: {"type": "Cavalry", "value_pct": 12.5}
    troop_health_bonus      jsonb, -- Example: {"type": "Archer", "value_pct": 15.0}
    conquest_skill_effect   jsonb, -- Per-level effect of the Conquest skill (skill_1)
    expedition_skill_effect jsonb, -- Per-level effect of the Expedition skill (skill_2)
    created_at              timestamptz      default now(),
    updated_at              timestamptz      default now(),
    unique (gear_id, level)
);

create index hero_exclusive_gear_levels_gear_id_idx on hero_exclusive_gear_levels (gear_id);
create index hero_exclusive_gear_levels_lethality_gin on hero_exclusive_gear_levels using gin (troop_lethality_bonus);
create index hero_exclusive_gear_levels_health_gin on hero_exclusive_gear_levels using gin (troop_health_bonus);