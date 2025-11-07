drop table if exists hero_skills cascade;

create table hero_skills
(
    id          uuid primary key default gen_random_uuid(),
    hero_id     uuid       not null references heroes (id) on delete cascade,
    name        text       not null,
    skill_type  skill_type not null, -- Active / Passive / Talent
    battle_type text       not null check (battle_type in ('Base', 'Conquest', 'Expedition')),
    description text,
    icon_path   text,
    created_at  timestamptz      default now(),
    updated_at  timestamptz      default now(),
    unique (hero_id, name)
);

-- Indexes for faster lookups
create index hero_skills_hero_id_idx on hero_skills (hero_id);
create index hero_skills_battle_type_idx on hero_skills (battle_type);