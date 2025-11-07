drop table if exists hero_exclusive_gear cascade;

create table hero_exclusive_gear
(
    id         uuid primary key default gen_random_uuid(),
    hero_id    uuid not null unique references heroes (id) on delete cascade,
    name       text not null,
    image_path text,
    created_at timestamptz      default now(),
    updated_at timestamptz      default now()
);

create index hero_exclusive_gear_hero_id_idx on hero_exclusive_gear (hero_id);