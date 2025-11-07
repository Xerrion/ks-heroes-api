drop table if exists hero_skill_levels cascade;

create table hero_skill_levels
(
    id         uuid primary key default gen_random_uuid(),
    skill_id   uuid  not null references hero_skills (id) on delete cascade,
    level      int   not null check (level between 1 and 5),
    effects    jsonb not null, -- Example: { "damage_pct": 120, "heal_pct": 15 }
    created_at timestamptz      default now(),
    updated_at timestamptz      default now(),
    unique (skill_id, level)
);

create index hero_skill_levels_skill_id_idx on hero_skill_levels (skill_id);
create index hero_skill_levels_effects_gin on hero_skill_levels using gin (effects);