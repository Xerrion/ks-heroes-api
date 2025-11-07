drop table if exists hero_exclusive_gear_skills cascade;

create table hero_exclusive_gear_skills
(
    id          uuid primary key default gen_random_uuid(),
    gear_id     uuid not null references hero_exclusive_gear (id) on delete cascade,
    skill_type  text not null check (skill_type in ('Conquest', 'Expedition')),
    name        text not null,
    description text not null,
    created_at  timestamptz      default now(),
    updated_at  timestamptz      default now(),
    unique(gear_id, skill_type)
);

create index hero_exclusive_gear_skills_gear_id_idx on hero_exclusive_gear_skills (gear_id);
create index hero_exclusive_gear_skills_type_idx on hero_exclusive_gear_skills (skill_type);